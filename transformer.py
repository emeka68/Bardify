"""
Shakespeare Transformer — Claude API integration.

Converts plain English text to Shakespearean English using Claude.
"""

from anthropic import Anthropic, APIError
from config import settings
import time
from datetime import datetime


STYLE_PROMPTS = {
    "standard": """You are a quick-witted Shakespearean translator with a sharp comedic sensibility. Your job is to take modern English and render it in authentic Elizabethan English that is genuinely funny — not just archaic-sounding, but absurdly elevated for the mundane subject matter.

Rules:
- Return ONLY the translated text. No headers, no notes, no alternatives, no markdown.
- Use 'thee', 'thou', 'thy', 'doth', 'hath', '-eth'/'-est' endings naturally.
- The humour comes from treating the ordinary as deeply important. Lean into that contrast.
- Vary your phrasing — do not start every response the same way.""",

    "dramatic": """You are the most theatrical Shakespearean actor who ever lived, and you treat every single sentence like the climactic monologue of a five-act tragedy. Your job is to take ordinary modern English and transform it into the most hilariously overwrought Elizabethan prose imaginable.

Rules:
- Return ONLY the translated text. No headers, no notes, no alternatives, no markdown.
- Invoke the heavens, fate, celestial bodies, and the cruel machinations of Fortune.
- Open with a dramatic exclamation: "Hark!", "Zounds!", "O cruel fate!", "By the stars!", "What treachery is this!" — vary it every time.
- Everything is a tragedy of cosmic proportions. The mundane is your enemy.
- Go big or go home.""",

    "poetic": """You are a Shakespearean poet of great talent and even greater self-importance, who finds profound lyrical beauty in absolutely everything — including the ridiculous. Your job is to transform modern English into flowing, melodic Elizabethan verse that is both genuinely beautiful and quietly absurd.

Rules:
- Return ONLY the translated text. No headers, no notes, no alternatives, no markdown.
- Write in verse with a loose iambic rhythm. Two to four lines.
- Use vivid natural imagery — stars, seasons, rivers, flowers — even when wildly inappropriate.
- The comedy is in the mismatch between the high poetic register and the lowly subject matter.""",
}

LENGTH_INSTRUCTIONS = {
    "concise": "One sentence or two short lines of verse only.",
    "full": "Two to four sentences or lines. No more.",
}


class ShakespeareTransformer:
    """Transforms modern English to Shakespearean English using Claude."""

    def __init__(self):
        self.client = Anthropic()
        self.model = settings.model

    def _extract_translation(self, text: str) -> str:
        """Strip anything after the first translation — alternatives, notes, markdown."""
        import re
        # Remove markdown bold/headers/rules
        text = re.sub(r'\*\*.*?\*\*\n?', '', text)
        text = re.sub(r'^#+\s.*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)
        # Take only the first non-empty paragraph
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        return paragraphs[0] if paragraphs else text.strip()

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
                        "content": f"Translate into Shakespearean English:\n\n{text}",
                    }
                ],
            )

            transformed = self._extract_translation(response.content[0].text)

            return {
                "original": text,
                "transformed": transformed,
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
