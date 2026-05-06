OUTPUT_GUARDRAIL_PROMPT = """Check if the generated response is grounded in the context and safe to show to the user.

Respond with ONLY this JSON (no other text):
{{"valid": true, "grounded": true, "issues": []}}

Set "valid" or "grounded" to false only if the response contains hallucinated facts not in the context, harmful content, or sensitive data exposure.

Query: {query}

Context: {context}

Response: {response}"""
