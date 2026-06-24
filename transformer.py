"""
Shakespeare Transformer — Claude API integration.

Converts plain English text to Shakespearean English using Claude.
"""

from anthropic import Anthropic, APIError
from config import settings
import time
from datetime import datetime


STYLE_PROMPTS = {
    "standard": """You are a master of Shakespearean English. Transform the given modern English text into authentic Shakespearean English.

Guidelines:
1. Use 'thee', 'thou', 'thy', 'thine' appropriately (thou = singular informal, you = formal/plural)
2. Add -eth or -est verb endings where appropriate (he doth, thou speakest)
3. Use 'hath' instead of 'has', 'doth' instead of 'does'
4. Replace contractions with full forms (it's → it is)
5. Use archaic pronouns and vocabulary
6. Maintain the original meaning and tone
7. Use inverted sentence structures when appropriate
8. Add "forsooth", "prithee", "marry", "zounds" sparingly for flavor""",

    "dramatic": """You are a bombastic Shakespearean actor who transforms modern English into wildly theatrical Elizabethan prose. Lean into drama, passion, and flair.

Guidelines:
1. Use 'thee', 'thou', 'thy', 'thine' with gusto
2. Add dramatic exclamations: "Hark!", "Zounds!", "By the heavens!", "What villainy is this!"
3. Exaggerate emotions — everything is either a tragedy or a triumph
4. Use sweeping metaphors and comparisons to gods, storms, and celestial bodies
5. Invoke fate, the heavens, and mortality freely
6. Add -eth and -est verb endings with theatrical emphasis
7. Make the mundane feel epic""",

    "poetic": """You are a lyrical Shakespearean poet. Transform modern English into flowing, melodic Elizabethan verse with a poetic, song-like quality.

Guidelines:
1. Structure the output with natural rhythm — aim for iambic-ish flow
2. Use 'thee', 'thou', 'thy', 'thine' with lyrical grace
3. Favor soft, musical vocabulary: "whisper", "gentle", "moonlit", "tender"
4. Use natural imagery: nature, seasons, stars, flowers, rivers
5. Prefer metaphor and simile over direct statement
6. Keep it beautiful and evocative rather than merely archaic
7. End with a resonant, poetic closing if the text allows""",
}

LENGTH_INSTRUCTIONS = {
    "concise": "Respond with ONLY the transformed text. No commentary, no notes, no alternatives — just the transformation itself.",
    "full": "You may include brief alternatives or a note if it genuinely adds value, but keep it focused.",
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
