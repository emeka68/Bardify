"""
Shakespeare Transformer — Claude API integration.

Converts plain English text to Shakespearean English using Claude.
"""

from anthropic import Anthropic, APIError
from config import settings
import json
import time
from datetime import datetime


class ShakespeareTransformer:
    """Transforms modern English to Shakespearean English using Claude."""
    
    def __init__(self):
        """Initialize the transformer with Claude API client."""
        self.client = Anthropic()
        self.model = settings.model
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for Shakespeare transformation."""
        return """You are a master of Shakespearean English. Your task is to transform modern English text into authentic Shakespearean English.

Guidelines:
1. Use 'thee', 'thou', 'thy', 'thine' appropriately (thou = singular informal, you = formal/plural)
2. Add -eth or -est verb endings where appropriate (he doth, thou speakest)
3. Use 'hath' instead of 'has', 'doth' instead of 'does'
4. Replace contractions with full forms (it's → it is)
5. Use archaic pronouns and vocabulary
6. Maintain the original meaning and tone
7. Add flowery, poetic language where it fits naturally
8. Use inverted sentence structures when appropriate
9. Add "forsooth", "prithee", "marry", "zounds" sparingly for flavor
10. Keep the transformation readable and fun, not overly archaic

Transform the user's text while keeping it clever and entertaining."""
    
    def transform(self, text: str) -> dict:
        """
        Transform modern English to Shakespearean English.
        
        Args:
            text (str): Modern English text to transform
        
        Returns:
            dict: {
                "original": original text,
                "transformed": shakespearean text,
                "timestamp": ISO timestamp,
                "model": model used,
                "usage": token usage info
            }
        """
        
        if not text or not text.strip():
            return {
                "error": "Empty input",
                "original": "",
                "transformed": ""
            }
        
        if len(text) > 2000:
            return {
                "error": "Text too long (max 2000 characters)",
                "original": text[:100] + "...",
                "transformed": ""
            }
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=self.system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"Transform this modern English to Shakespearean English:\n\n{text}"
                    }
                ]
            )
            
            transformed_text = response.content[0].text
            
            return {
                "original": text,
                "transformed": transformed_text,
                "timestamp": datetime.now().isoformat(),
                "model": self.model,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                },
                "error": None
            }
        
        except APIError as e:
            return {
                "error": f"API Error: {str(e)}",
                "original": text,
                "transformed": "",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": f"Unexpected error: {str(e)}",
                "original": text,
                "transformed": "",
                "timestamp": datetime.now().isoformat()
            }
    
    def batch_transform(self, texts: list) -> list:
        """
        Transform multiple texts.
        
        Args:
            texts (list): List of text strings to transform
        
        Returns:
            list: List of transformation results
        """
        results = []
        for text in texts:
            result = self.transform(text)
            results.append(result)
            time.sleep(0.1)  # Small delay between requests
        
        return results


# Global transformer instance
transformer = ShakespeareTransformer()
