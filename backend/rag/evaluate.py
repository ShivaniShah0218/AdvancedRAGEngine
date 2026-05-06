"""
Define functions for evaluating the response of the RAG model
"""
from dotenv import load_dotenv
from backend.rag.config import evaluator_rouge
from backend.logging_config import get_logger

load_dotenv()

logger = get_logger(__name__)


def evaluate_rouge(generated_answer, ground_truth):
	"""
	Evaluate the generated answer using ROUGE metrics.
	"""
	try:
		logger.info(f"Evaluating the response")
		rouge_scores = evaluator_rouge.score(ground_truth, generated_answer)
		logger.info(f"Evaluated the response")
		return {"rouge1": rouge_scores['rouge1'].fmeasure, "rougeL": rouge_scores['rougeL'].fmeasure}		
	except Exception as e:
		logger.error(f"Error in evaluation: {e}")
		return None

# def detect_hallucination(generated_answer, ground_truth):
# 	"""
# 	Checks if generated response is hallucinated or not using the hallucination detector.
# 	"""
# 	try:
# 		logger.info(f"Detecting hallucination")
# 		result=hallucination_detector(generated_answer, ground_truth,eval_mode="HALLUCINATION")
# 		logger.info(f"The answer {generated_answer} is {result.label}")
# 		return result.label
# 	except Exception as e:
# 		logger.error(f"Error in hallucination detection: {e}")
# 		return None

