"""
Define function for generating the response based on context and query
"""
import torch
from dotenv import load_dotenv
from backend.rag.config import tokenizer, model, DEVICE
from backend.logging_config import get_logger

load_dotenv()

logger = get_logger(__name__)

def generate_answer(context, query, max_tokens=100):
    try:
        logger.info(f"Generating the answer for query {query}")
        logger.info(f"Context length: {len(context) if context else 0}")
        logger.info(f"Context preview: {context[:200] if context else 'None'}...")
        
        # Check if context is empty or too short
        if not context or len(context.strip()) < 10:
            logger.warning("Context is empty or too short, returning placeholder")
            return "I cannot find relevant information in the context to answer this question."
        
        prompt = f"""Answer the question using ONLY the information in the context below. Do not generate any new information.

Context:
{context}

Question:
{query}

Instructions:
- Use ONLY the information from the context above
- Do not add any information not in the context
- If the context does not contain the answer, say "I cannot find the answer in the context"
- Be concise and direct
- Do not generate generic responses
- The answer must be derived from the context provided above

Answer:"""
        inputs = tokenizer(prompt, return_tensors="pt", enable_thinking=False)
        inputs = inputs.to(DEVICE)
        outputs = model.generate(**inputs, max_new_tokens=max_tokens, do_sample=False,
                                 temperature=0.0, top_p=1.0, no_repeat_ngram_size=3,
                                 repetition_penalty=1.5, length_penalty=0.8)
        result = tokenizer.decode(outputs[0], skip_special_tokens=True, enable_thinking=False)
        logger.info(f"RAG Model generated result {result}")

        # Keep only the answer part (after the prompt)
        if result.startswith(prompt):
            answer = result[len(prompt):].strip()
        else:
            # Fallback: extract after "Answer:" marker
            if "Answer:" in result:
                answer = result.split("Answer:")[-1].strip()
            else:
                answer = result

        # Clean up: stop at first newline or double newline
        # answer = answer.split("\n\n")[0].strip()
        # answer = answer.split("\n")[0].strip()
        
        # Clean up: add spaces between words that are concatenated
        # This handles cases like "PieChart" -> "Pie Chart"
        import re
        # Add space before uppercase letters that follow lowercase letters
        answer = re.sub(r'([a-z])([A-Z])', r'\1 \2', answer)
        # Add space before uppercase letters that are followed by lowercase letters
        answer = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', answer)

        logger.info(f"Answer extracted, length: {len(answer)}")
        logger.info(f"Response generated for query {query}")
        return answer
    except Exception as e:
        logger.error(f"Error in generating answer for {query}: {str(e)}")
        return None
