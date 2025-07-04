import os
import openai
from typing import List, Optional

class AzureOpenAIClient:
    def __init__(self, api_key: str, endpoint: str, api_version: str = "2023-05-15"):
        self.api_key = api_key
        self.endpoint = endpoint
        self.api_version = api_version
        openai.api_type = "azure"
        openai.api_key = api_key
        openai.api_base = endpoint
        openai.api_version = api_version

    def generate_code(self, prompt: str, context: Optional[str], coding_approach_samples: Optional[List[str]], model: str, extraction_requirements: Optional[str] = None) -> str:
        # Compose the full prompt
        full_prompt = ""
        if coding_approach_samples:
            full_prompt += "\n\n".join([f"Sample:\n{sample}" for sample in coding_approach_samples]) + "\n\n"
        if context:
            full_prompt += f"Context:\n{context}\n\n"
        if extraction_requirements:
            full_prompt += f"Extraction Requirements:\n{extraction_requirements}\n\n"
        full_prompt += f"Task:\n{prompt}\n\nGenerate code:"

        response = openai.ChatCompletion.create(
            engine=model,
            messages=[
                {"role": "system", "content": "You are an expert code generator."},
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=1024,
            temperature=0.2,
        )
        return response["choices"][0]["message"]["content"] 