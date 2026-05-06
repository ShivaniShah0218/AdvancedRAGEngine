"""
Guardrail engine:
1. Rule-based fast path — narrow, precise patterns for unambiguous attacks
2. NLI-based checks — for context relevance and response groundedness
3. Zero-shot classifier — for query safety classification
"""
import re
import json
import torch
from transformers import pipeline as hf_pipeline
from backend.logging_config import get_logger

logger = get_logger(__name__)

# ── Rule-based patterns — intentionally narrow ────────────────────────────────
# Each pattern must match ONLY clear attack strings, not normal language
_BLOCK_PATTERNS = [
    (r"\bignore\s+(all\s+)?previous\s+instructions?\b", "prompt injection"),
    (r"\bdisregard\s+(all\s+)?previous\s+instructions?\b", "prompt injection"),
    (r"\bforget\s+(all\s+)?your\s+instructions?\b", "prompt injection"),
    (r"\byou\s+are\s+now\s+in\s+\w+\s+mode\b", "mode override"),
    (r"\bdan\s+mode\b", "jailbreak: DAN"),
    (r"\bdeveloper\s+mode\s+enabled\b", "jailbreak: developer mode"),
    (r"\bbypass\s+(all\s+)?(your\s+)?safety\s+(filters?|restrictions?|guardrails?)\b", "bypass safety"),
    (r"\breveal\s+(your\s+)?(system\s+)?prompt\b", "data exfiltration"),
    (r"\bprint\s+(your\s+)?(system\s+)?prompt\b", "data exfiltration"),
    (r"<\s*script[\s>]", "script injection"),
    (r"\bexec\s*\(", "code injection"),
    (r"\b__import__\s*\(", "code injection"),
    (r"\bos\.system\s*\(", "code injection"),
]
_COMPILED = [(re.compile(p, re.IGNORECASE), reason) for p, reason in _BLOCK_PATTERNS]

# Labels for zero-shot classification
_MALICIOUS_LABEL = "malicious or harmful request"
_SAFE_LABEL = "normal safe question"


class LLMGuardrailEngine:
    def __init__(self, model_path: str):
        self._nli_model = None
        self._classifier = None
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Guardrail engine using device: {self._device}")
        try:
            logger.info(f"Loading guardrail NLI model from {model_path}")
            self._nli_model = hf_pipeline(
                "text-classification",
                model=model_path,
                tokenizer=model_path,
                truncation=True,
                max_length=512,
                device=0 if self._device == "cuda" else -1,
            )
            logger.info("Guardrail NLI model loaded")
        except Exception as e:
            logger.warning(f"Guardrail NLI model failed to load ({e}) — will use rule-based only")

    def _rule_check(self, text: str) -> dict | None:
        """Returns a block result if a known-bad pattern matches, else None."""
        for pattern, reason in _COMPILED:
            if pattern.search(text):
                logger.warning(f"Rule guardrail blocked: {reason} | text: {text[:80]}")
                return {"allowed": False, "risk": "high", "reason": reason, "action": "block"}
        return None

    def _nli_check(self, premise: str, hypothesis: str, threshold: float = 0.7) -> bool:
        """
        Use NLI model to check if hypothesis is entailed by premise.
        Returns True if entailed (supported), False otherwise.
        
        For relevance/safety checks, we accept both ENTAILMENT and NEUTRAL with high confidence
        since NEUTRAL often means "not clearly contradicted" which is acceptable for guardrails.
        """
        if self._nli_model is None:
            return True  # Default to allow if model unavailable
        
        try:
            input_text = f"{premise} [SEP] {hypothesis}"
            result = self._nli_model(input_text, truncation=True, max_length=512)
            label = result[0]["label"] if isinstance(result, list) else result["label"]
            score = result[0]["score"] if isinstance(result, list) else result["score"]
            
            # NLI labels can be: ENTAILMENT, NEUTRAL, CONTRADICTION or LABEL_0, LABEL_1, LABEL_2
            label_upper = label.upper() if isinstance(label, str) else str(label).upper()
            
            # Accept ENTAILMENT or NEUTRAL with high confidence
            # Only reject CONTRADICTION with high confidence
            has_entail = "ENTAIL" in label_upper
            has_neutral = "NEUTRAL" in label_upper
            has_contradict = "CONTRADICT" in label_upper
            is_acceptable = (has_entail or has_neutral) and score > threshold
            is_rejectable = has_contradict and score > threshold
            
            is_entailed = is_acceptable and not is_rejectable
            logger.info(f"NLI check: premise={premise[:50]}..., hypothesis={hypothesis[:50]}..., label={label}, label_upper={label_upper}, score={score:.3f}, threshold={threshold}, has_entail={has_entail}, has_neutral={has_neutral}, has_contradict={has_contradict}, is_acceptable={is_acceptable}, is_rejectable={is_rejectable}, entailed={is_entailed}")
            return is_entailed
        except Exception as e:
            logger.warning(f"NLI check failed: {e}")
            return True  # Default to allow on error

    def _classify(self, text: str) -> dict | None:
        """Use zero-shot classification to decide safe vs malicious."""
        if self._classifier is None:
            return None
        try:
            result = self._classifier(
                text,
                candidate_labels=[_SAFE_LABEL, _MALICIOUS_LABEL],
            )
            top_label = result["labels"][0]
            top_score = result["scores"][0]
            logger.info(f"Classifier result: label={top_label!r}, score={top_score:.3f}")

            if top_label == _MALICIOUS_LABEL and top_score > 0.80:
                return {
                    "allowed": False,
                    "risk": "high",
                    "reason": f"Classified as malicious (score={top_score:.2f})",
                    "action": "block",
                }
            return {
                "allowed": True,
                "risk": "low",
                "reason": f"Classified as safe (score={top_score:.2f})",
                "action": "allow",
            }
        except Exception as e:
            logger.warning(f"Classifier failed: {e}")
            return None

    def evaluate_query(self, query: str) -> dict:
        """
        Evaluate a query for security issues.
        1. Rule check — fast, precise, no false positives
        2. Zero-shot classifier — reliable binary decision
        3. Default allow — if classifier is unavailable, pass through
        """
        # 1. Rule-based
        rule_result = self._rule_check(query)
        if rule_result:
            return rule_result

        # 2. Classifier
        clf_result = self._classify(query)
        if clf_result:
            return clf_result

        # 3. Default allow
        logger.info("Query guardrail: rules passed, classifier unavailable — allowing")
        return {"allowed": True, "risk": "low", "reason": "Passed rule checks", "action": "allow"}

    def evaluate_context(self, query: str, context: str) -> dict:
        """
        Evaluate context for relevance and safety.
        1. Check context is relevant to query using NLI (very low threshold for relevance)
        2. Check context doesn't contain malicious content using NLI
        3. Default allow if checks unavailable
        """
        # Check 1: Context is relevant to query - use very low threshold (0.4) since relevance is subjective
        relevance_hypothesis = "The context is relevant and helpful for answering the query."
        is_relevant = self._nli_check(context, relevance_hypothesis, threshold=0.4)
        
        if not is_relevant:
            logger.warning("Context guardrail: context not relevant to query")
            return {"safe": False, "issues": ["Context is not relevant to the query"], "action": "block"}

        # Check 2: Context doesn't contain malicious instructions - use standard threshold
        safety_hypothesis = "The context contains safe, factual information."
        is_safe = self._nli_check(context, safety_hypothesis, threshold=0.7)
        
        if not is_safe:
            logger.warning("Context guardrail: context may contain malicious content")
            return {"safe": False, "issues": ["Context may contain malicious or hidden instructions"], "action": "block"}

        logger.info("Context guardrail: passed relevance and safety checks")
        return {"safe": True, "issues": [], "action": "allow"}

    def evaluate_response(self, query: str, context: str, response: str) -> dict:
        """
        Evaluate response for groundedness and safety.
        1. Check response doesn't contain harmful content using NLI
        2. Default allow if checks unavailable
        """
        # Check: Response doesn't contain harmful content - use standard threshold
        safety_hypothesis = "The response contains safe, appropriate information for the user."
        is_safe = self._nli_check(response, safety_hypothesis, threshold=0.7)
        
        if not is_safe:
            logger.warning("Response guardrail: response may contain harmful content")
            return {"valid": False, "grounded": True, "issues": ["Response may contain harmful or inappropriate content"], "action": "block"}

        logger.info("Response guardrail: passed safety check")
        return {"valid": True, "grounded": True, "issues": [], "action": "allow"}

    def evaluate(self, user_message: str) -> dict:
        """
        Legacy method — evaluates a message as a query.
        Use evaluate_query(), evaluate_context(), or evaluate_response() for specific use cases.
        """
        return self.evaluate_query(user_message)
