"""
 Initializes the model for the application with the specified model and tokenizer
"""
import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from sentence_transformers import CrossEncoder
from rouge_score import rouge_scorer
from dotenv import load_dotenv
from backend.logging_config import get_logger
from backend.rag.guardrails.guardrails_engine import LLMGuardrailEngine



load_dotenv()

logger = get_logger(__name__)


RAG_MODEL_PATH=os.getenv("RAG_MODEL_PATH")
RAG_MODEL=os.getenv("RAG_MODEL")
CROSS_ENCODER_MODEL_PATH=os.getenv("CROSS_ENCODER_MODEL_PATH")
CROSS_ENCODER_MODEL=os.getenv("CROSS_ENCODER_MODEL")
GUARDRAILS_MODEL_PATH=os.getenv("GUARDRAILS_MODEL_PATH","./models")
GUARDRAILS_MODEL=os.getenv("GUARDRAILS_MODEL")

# Detect available device
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"Using device: {DEVICE}")

#Guardrails initializing
logger.info(f"Initializing guardrails model")
engine = LLMGuardrailEngine(GUARDRAILS_MODEL_PATH)
logger.info(f"{GUARDRAILS_MODEL} initialized")

# LLM
logger.info(f"Initializing model tokenizer {RAG_MODEL}")
tokenizer = AutoTokenizer.from_pretrained(RAG_MODEL_PATH)
logger.info(f"Initializing model {RAG_MODEL}")
model = AutoModelForCausalLM.from_pretrained(
    RAG_MODEL_PATH,
    local_files_only=True,
    device_map="auto" if DEVICE == "cuda" else "cpu"
)
logger.info(f"{RAG_MODEL} tokenizer and model initialized")

#reranker
logger.info(f"Initializing Reranker {CROSS_ENCODER_MODEL}")
reranker = CrossEncoder(CROSS_ENCODER_MODEL_PATH, device=DEVICE)
logger.info(f"Reranker {CROSS_ENCODER_MODEL} initialized")

logger.info(f"Initializing Rouge Scorer")
evaluator_rouge = rouge_scorer.RougeScorer(['rouge1','rougeL'], use_stemmer=True)
logger.info(f"Rouge Scorer initialized")

