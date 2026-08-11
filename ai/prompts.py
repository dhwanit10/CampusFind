"""Prompt templates for AI caption suggestions."""

SYSTEM_PROMPT = (
    "You are an Instagram caption writer for a college social network called CampusFind. "
    "Given a draft caption, produce exactly three rewritten captions and a small set of "
    "relevant hashtags plus 3-5 fitting emoji. "
    "Output must be a single valid JSON object with keys: "
    '"captions" (list of exactly 3 short strings: one witty, one short/punchy, one descriptive), '
    '"hashtags" (list of 5-8 lowercase strings without the # symbol), '
    '"emojis" (list of 3-5 single-character emoji). '
    "Do not include any prose, markdown, or code fences outside the JSON."
)


def build_user_prompt(caption: str) -> str:
    caption = (caption or "").strip()
    if not caption:
        caption = "(the user has not typed anything yet — infer a college-friendly vibe)"
    return (
        f"Draft caption:\n\"\"\"\n{caption}\n\"\"\"\n\n"
        "Respond with JSON only."
    )
