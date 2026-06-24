"""
Shakespeare Transformer — Claude API integration.

Converts plain English text to Shakespearean English using Claude.
"""

from anthropic import Anthropic, APIError
from config import settings
import time
from datetime import datetime


STYLE_PROMPTS = {
    "standard": """You are a witty Shakespearean translator. Transform the given text into authentic Elizabethan English with a light humorous touch.

Rules:
- Return ONLY the translated text. No headers, no notes, no alternatives, no markdown.
- Use 'thee', 'thou', 'thy', 'thine', '-eth'/'-est' endings, 'hath', 'doth' naturally.
- Keep it clever and fun without being over the top.""",

    "dramatic": """You are a hilariously over-the-top Shakespearean actor. Transform the given text into wildly theatrical Elizabethan prose.

Rules:
- Return ONLY the translated text. No headers, no notes, no alternatives, no markdown.
- Exaggerate everything — make the mundane feel like a Greek tragedy.
- Invoke the heavens, fate, and celestial bodies. Use "Hark!", "Zounds!", "By the gods!"
- The more bombastic, the better.""",

    "poetic": """You are a lyrical Shakespearean poet with a wry sense of humour. Transform the given text into flowing, melodic Elizabethan verse.

Rules:
- Return ONLY the translated text. No headers, no notes, no alternatives, no markdown.
- Aim for iambic rhythm, natural imagery, and musical phrasing.
- Keep it beautiful, witty, and a little absurd.""",
}

LENGTH_INSTRUCTIONS = {
    "concise": "One sentence only.",
    "full": "Two to three sentences at most.",
}


class ShakespeareTransformer:
    """Transforms modern English to Shakespearean English using Claude."""

    def __init__(self):
        self.client = Anthropic()
        self.model = settings.model

    def _build_system_prompt(self, style: str, length: str) -> str:
        base = STYLE_PROMPTS.get(style, STYLE_PROMPTS["standard"])
        instruction = LENGTH_INSTRUCTIONS.get(length, LENGTH_INSTRUCTIONS["full"])
        return f"{base}\n\n{instruction}"

    def transform(self, text: str, style: str = "standard", length: str = "full") -> dict:
        if not text or not text.strip():
            return {"error": "Empty input", "original": "", "transformed": ""}

        if len(text) > 2000:
            return {
                "error": "Text too long (max 2000 characters)",
                "original": text[:100] + "...",
                "transformed": "",
            }

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=self._build_system_prompt(style, length),
                messages=[
                    {
                        "role": "user",
                        "content": f"Transform this modern English to Shakespearean English:\n\n{text}",
                    }
                ],
            )

            return {
                "original": text,
                "transformed": response.content[0].text,
                "timestamp": datetime.now().isoformat(),
                "model": self.model,
                "style": style,
                "length": length,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                },
                "error": None,
            }

        except APIError as e:
            return {
                "error": f"API Error: {str(e)}",
                "original": text,
                "transformed": "",
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "error": f"Unexpected error: {str(e)}",
                "original": text,
                "transformed": "",
                "timestamp": datetime.now().isoformat(),
            }

    def batch_transform(self, texts: list, style: str = "standard", length: str = "full") -> list:
        results = []
        for text in texts:
            results.append(self.transform(text, style=style, length=length))
            time.sleep(0.1)
        return results


# Global transformer instance
transformer = ShakespeareTransformer()
