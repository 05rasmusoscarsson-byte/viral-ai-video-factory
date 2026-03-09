"""
Agent 01 - Script Generator
Production-ready TikTok viral script generator for a video factory pipeline.

Features:
- OpenAI API integration via the Responses API
- Structured JSON output using JSON Schema
- Viral video generation logic:
  - curiosity gap
  - pattern interrupt
  - emotional hooks
- Captions with keywords + hashtags
- Timestamps, visual cues, text overlays
- Retry logic with exponential backoff
- Error handling
- Cost tracking
- Example usage

Install:
    pip install openai

Environment:
    export OPENAI_API_KEY="your_api_key"

Run:
    python agent_01_script_generator.py
"""

from __future__ import annotations

import json
import logging
import math
import os
import random
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from openai import OpenAI
from openai import (
    APIConnectionError,
    APITimeoutError,
    BadRequestError,
    InternalServerError,
    RateLimitError,
)

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("agent_01_script_generator")

# -----------------------------------------------------------------------------
# JSON Schema for Structured Output
# -----------------------------------------------------------------------------

TIKTOK_SCRIPT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "topic",
        "angle",
        "target_emotion",
        "hook",
        "main_content",
        "cta",
        "caption",
        "duration_seconds",
        "keywords",
        "hashtags",
        "timestamps",
    ],
    "properties": {
        "topic": {"type": "string"},
        "angle": {"type": "string"},
        "target_emotion": {"type": "string"},
        "hook": {"type": "string"},
        "main_content": {"type": "string"},
        "cta": {"type": "string"},
        "caption": {"type": "string"},
        "duration_seconds": {
            "type": "integer",
            "minimum": 30,
            "maximum": 45,
        },
        "keywords": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 3,
            "maxItems": 12,
        },
        "hashtags": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 3,
            "maxItems": 12,
        },
        "timestamps": {
            "type": "array",
            "minItems": 3,
            "maxItems": 12,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "start_sec",
                    "end_sec",
                    "segment_type",
                    "voiceover",
                    "visual_cue",
                    "text_overlay",
                ],
                "properties": {
                    "start_sec": {"type": "integer", "minimum": 0, "maximum": 45},
                    "end_sec": {"type": "integer", "minimum": 1, "maximum": 45},
                    "segment_type": {
                        "type": "string",
                        "enum": ["hook", "body", "cta"],
                    },
                    "voiceover": {"type": "string"},
                    "visual_cue": {"type": "string"},
                    "text_overlay": {"type": "string"},
                },
            },
        },
    },
}

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

@dataclass
class Pricing:
    """
    Price per 1M tokens.

    Keep this updated from OpenAI's official pricing page.
    """
    input_per_1m: float
    output_per_1m: float


@dataclass
class ScriptGeneratorConfig:
    api_key: Optional[str] = None
    model: str = "gpt-4.1"  # GPT-4-family default to match your request.
    temperature_note: str = (
        "Favor high-variance hooks, but keep output concise and concrete."
    )
    timeout_seconds: int = 60
    max_retries: int = 5
    base_backoff_seconds: float = 1.2
    max_backoff_seconds: float = 20.0
    max_output_tokens: int = 1400

    # Update as pricing changes.
    pricing_map: Dict[str, Pricing] = field(
        default_factory=lambda: {
            "gpt-4.1": Pricing(input_per_1m=2.00, output_per_1m=8.00),
            "gpt-5.4": Pricing(input_per_1m=2.50, output_per_1m=15.00),
            "gpt-5-mini": Pricing(input_per_1m=0.25, output_per_1m=2.00),
            "gpt-4o": Pricing(input_per_1m=2.50, output_per_1m=10.00),
        }
    )


# -----------------------------------------------------------------------------
# Exceptions
# -----------------------------------------------------------------------------

class ScriptGeneratorError(Exception):
    """Base exception for script generation errors."""


class SchemaValidationError(ScriptGeneratorError):
    """Raised when the returned JSON is invalid or incomplete."""


class ConfigurationError(ScriptGeneratorError):
    """Raised when local configuration is broken."""


# -----------------------------------------------------------------------------
# Cost Tracking
# -----------------------------------------------------------------------------

@dataclass
class UsageMetrics:
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0


class CostTracker:
    def __init__(self, config: ScriptGeneratorConfig) -> None:
        self.config = config
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost_usd = 0.0

    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        pricing = self.config.pricing_map.get(model)
        if not pricing:
            return 0.0

        input_cost = (input_tokens / 1_000_000) * pricing.input_per_1m
        output_cost = (output_tokens / 1_000_000) * pricing.output_per_1m
        return round(input_cost + output_cost, 6)

    def record(self, model: str, input_tokens: int, output_tokens: int) -> UsageMetrics:
        cost = self.estimate_cost(model, input_tokens, output_tokens)
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost_usd += cost

        return UsageMetrics(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            estimated_cost_usd=cost,
        )

    def summary(self) -> Dict[str, Any]:
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_estimated_cost_usd": round(self.total_cost_usd, 6),
        }


# -----------------------------------------------------------------------------
# Agent 01 - Script Generator
# -----------------------------------------------------------------------------

class Agent01ScriptGenerator:
    """
    Generates structured TikTok scripts for a viral video pipeline.
    """

    def __init__(self, config: Optional[ScriptGeneratorConfig] = None) -> None:
        self.config = config or ScriptGeneratorConfig()
        api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ConfigurationError(
                "OPENAI_API_KEY is missing. Set it as an environment variable "
                "or pass api_key into ScriptGeneratorConfig."
            )

        self.client = OpenAI(api_key=api_key, timeout=self.config.timeout_seconds)
        self.cost_tracker = CostTracker(self.config)

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def generate_script(self, topic: str) -> Dict[str, Any]:
        """
        Generate a complete structured TikTok script.

        Input:
            topic: A topic or idea string.

        Output:
            JSON-serializable dict containing:
            - hook
            - main_content
            - cta
            - caption
            - duration_seconds
            - timestamps
            - keywords
            - hashtags
            - metadata
        """
        topic = (topic or "").strip()
        if not topic:
            raise ValueError("Topic cannot be empty.")

        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(topic)

        raw_json, usage = self._request_with_retry(system_prompt, user_prompt)
        script = self._parse_and_validate(raw_json)
        script = self._post_process(script, topic)
        script["_meta"] = usage
        return script

    # -------------------------------------------------------------------------
    # Prompting
    # -------------------------------------------------------------------------

    def _build_system_prompt(self) -> str:
        return """
You are Agent 01 in a viral video factory pipeline.

Your job:
Generate a TikTok script that maximizes watch time, retention, curiosity, emotional engagement, and comments.

Hard requirements:
- Output must follow the provided JSON schema exactly.
- Make the hook hit in the first 3 seconds.
- Main content must fit within 30-45 seconds total runtime.
- CTA must be short and native, not corporate.
- Include captions with keywords and discoverable hashtags.
- Include timestamps, visual cues, and text overlays.
- Keep wording punchy, simple, spoken, and scroll-stopping.

Viral strategy rules:
1. Use a curiosity gap immediately.
2. Use a pattern interrupt in the opening line or first visual.
3. Use emotional hooks where relevant: surprise, fear of missing out, relief, validation, urgency, status, or disbelief.
4. Prefer short sentences.
5. Avoid generic filler like "In today's video..."
6. Make it sound like a creator, not a marketer.
7. Deliver value quickly.
8. End with a CTA optimized for comments, saves, or follows.

Hook rules:
- Maximum ~1-2 spoken lines.
- Should create tension, surprise, or an open loop.
- Must make viewers want the next sentence.

Body rules:
- Should be educational or entertaining.
- Use a tight progression: problem -> twist -> payoff.
- Include at least one concrete insight or example.

CTA rules:
- Must feel organic.
- Examples: ask a provocative question, invite comments, promise a part 2, or ask viewers to follow for more.

Caption rules:
- Must include keywords relevant to the topic.
- Must include hashtags.
- Must be optimized for discoverability without looking spammy.

Timestamp rules:
- Cover the full script from 0 seconds to final second.
- Segment types must be one of: hook, body, cta.
- Each timestamp needs:
  - start_sec
  - end_sec
  - segment_type
  - voiceover
  - visual_cue
  - text_overlay

Quality bar:
- Make it feel natively TikTok.
- No cringe brand talk.
- No vague motivational fluff.
- Every line must earn its place.
""".strip()

    def _build_user_prompt(self, topic: str) -> str:
        examples = [
            "Why your morning routine is making you more tired",
            "The hidden trick supermarkets use to make you overspend",
            "Why most startup founders waste their first $1,000 on ads",
            "The gym mistake that makes beginners quit in 2 weeks",
            "Why remote workers secretly lose promotions",
        ]

        return f"""
Topic / idea:
{topic}

Generate a TikTok script JSON for this topic.

Additional constraints:
- Duration must be between 30 and 45 seconds.
- Make the hook strong enough to stop a scroll.
- Use a curiosity gap, pattern interrupt, and emotional tension.
- Include concrete visual directions.
- Include text overlays optimized for retention.
- Caption must include keywords and hashtags.

Reference examples of good viral framing:
{json.dumps(examples, ensure_ascii=False, indent=2)}
""".strip()

    # -------------------------------------------------------------------------
    # Request / Retry
    # -------------------------------------------------------------------------

    def _request_with_retry(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> Tuple[str, Dict[str, Any]]:
        last_error: Optional[Exception] = None

        for attempt in range(1, self.config.max_retries + 1):
            try:
                logger.info("Requesting script generation | attempt=%s", attempt)

                response = self.client.responses.create(
                    model=self.config.model,
                    input=[
                        {
                            "role": "system",
                            "content": [{"type": "input_text", "text": system_prompt}],
                        },
                        {
                            "role": "user",
                            "content": [{"type": "input_text", "text": user_prompt}],
                        },
                    ],
                    max_output_tokens=self.config.max_output_tokens,
                    text={
                        "format": {
                            "type": "json_schema",
                            "name": "tiktok_script",
                            "schema": TIKTOK_SCRIPT_SCHEMA,
                            "strict": True,
                        }
                    },
                )

                raw_text = getattr(response, "output_text", None)
                if not raw_text:
                    raise ScriptGeneratorError("Model returned no output_text.")

                input_tokens, output_tokens = self._extract_usage_tokens(response)
                usage_metrics = self.cost_tracker.record(
                    model=self.config.model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                )

                usage_payload = {
                    "model": self.config.model,
                    "input_tokens": usage_metrics.input_tokens,
                    "output_tokens": usage_metrics.output_tokens,
                    "total_tokens": usage_metrics.total_tokens,
                    "estimated_cost_usd": usage_metrics.estimated_cost_usd,
                    "lifetime_usage": self.cost_tracker.summary(),
                }

                return raw_text, usage_payload

            except (RateLimitError, APIConnectionError, APITimeoutError, InternalServerError) as exc:
                last_error = exc
                sleep_for = self._compute_backoff(attempt)
                logger.warning(
                    "Transient API error on attempt %s/%s: %s | sleeping %.2fs",
                    attempt,
                    self.config.max_retries,
                    exc.__class__.__name__,
                    sleep_for,
                )
                time.sleep(sleep_for)

            except BadRequestError as exc:
                logger.exception("Bad request sent to OpenAI API.")
                raise ScriptGeneratorError(
                    f"BadRequestError from OpenAI API: {exc}"
                ) from exc

            except Exception as exc:
                logger.exception("Unexpected error during script generation.")
                raise ScriptGeneratorError(
                    f"Unexpected script generation error: {exc}"
                ) from exc

        raise ScriptGeneratorError(
            f"Failed after {self.config.max_retries} retries. Last error: {last_error}"
        )

    def _compute_backoff(self, attempt: int) -> float:
        """
        Exponential backoff with jitter.
        """
        base = self.config.base_backoff_seconds * (2 ** (attempt - 1))
        jitter = random.uniform(0, 0.5 * attempt)
        return min(base + jitter, self.config.max_backoff_seconds)

    # -------------------------------------------------------------------------
    # Validation / Parsing
    # -------------------------------------------------------------------------

    def _parse_and_validate(self, raw_json: str) -> Dict[str, Any]:
        try:
            payload = json.loads(raw_json)
        except json.JSONDecodeError as exc:
            raise SchemaValidationError(f"Returned output is not valid JSON: {exc}") from exc

        # Minimal runtime checks beyond schema enforcement.
        required_fields = [
            "hook",
            "main_content",
            "cta",
            "caption",
            "duration_seconds",
            "timestamps",
            "keywords",
            "hashtags",
        ]
        for field_name in required_fields:
            if field_name not in payload:
                raise SchemaValidationError(f"Missing required field: {field_name}")

        duration = payload.get("duration_seconds")
        if not isinstance(duration, int) or not (30 <= duration <= 45):
            raise SchemaValidationError("duration_seconds must be an integer between 30 and 45.")

        timestamps = payload.get("timestamps", [])
        if not isinstance(timestamps, list) or len(timestamps) < 3:
            raise SchemaValidationError("timestamps must be a non-empty list with at least 3 segments.")

        self._validate_timestamp_ranges(timestamps, duration)

        return payload

    def _validate_timestamp_ranges(self, timestamps: List[Dict[str, Any]], duration: int) -> None:
        last_end = -1

        for idx, segment in enumerate(timestamps):
            start_sec = segment.get("start_sec")
            end_sec = segment.get("end_sec")
            segment_type = segment.get("segment_type")

            if not isinstance(start_sec, int) or not isinstance(end_sec, int):
                raise SchemaValidationError(f"Timestamp segment {idx} has invalid start/end types.")

            if start_sec < 0 or end_sec <= start_sec:
                raise SchemaValidationError(f"Timestamp segment {idx} has invalid range.")

            if end_sec > duration:
                raise SchemaValidationError(f"Timestamp segment {idx} exceeds duration_seconds.")

            if start_sec < last_end:
                raise SchemaValidationError(f"Timestamp segment {idx} overlaps previous segment.")

            if idx == 0 and segment_type != "hook":
                raise SchemaValidationError("First timestamp segment must be the hook.")

            last_end = end_sec

    # -------------------------------------------------------------------------
    # Post-processing
    # -------------------------------------------------------------------------

    def _post_process(self, payload: Dict[str, Any], topic: str) -> Dict[str, Any]:
        """
        Clean small issues and ensure the caption contains hashtags.
        """
        payload["topic"] = payload.get("topic") or topic

        hashtags = payload.get("hashtags", [])
        hashtags = [tag if tag.startswith("#") else f"#{tag.replace(' ', '')}" for tag in hashtags]
        payload["hashtags"] = hashtags

        caption = payload.get("caption", "").strip()
        missing_tags = [tag for tag in hashtags if tag not in caption]
        if missing_tags:
            caption = f"{caption} {' '.join(missing_tags)}".strip()
        payload["caption"] = caption

        return payload

    # -------------------------------------------------------------------------
    # Usage extraction
    # -------------------------------------------------------------------------

    def _extract_usage_tokens(self, response: Any) -> Tuple[int, int]:
        """
        Defensive extraction because SDK response shapes evolve.
        """
        usage = getattr(response, "usage", None)
        if not usage:
            return 0, 0

        input_tokens = (
            getattr(usage, "input_tokens", None)
            or getattr(usage, "prompt_tokens", None)
            or 0
        )
        output_tokens = (
            getattr(usage, "output_tokens", None)
            or getattr(usage, "completion_tokens", None)
            or 0
        )

        return int(input_tokens), int(output_tokens)


# -----------------------------------------------------------------------------
# Example prompts
# -----------------------------------------------------------------------------

EXAMPLE_VIRAL_TOPICS = [
    "Why most people are using AI completely wrong at work",
    "The biggest mistake first-time ecommerce founders make",
    "Why your phone is destroying your attention span",
    "The truth about passive income nobody tells you",
    "How supermarkets manipulate your decisions without you noticing",
]

# -----------------------------------------------------------------------------
# Example usage
# -----------------------------------------------------------------------------

def main() -> None:
    config = ScriptGeneratorConfig(
        model="gpt-4.1",   # use "gpt-5.4" if you want the current stronger default
        max_retries=5,
        timeout_seconds=60,
    )

    agent = Agent01ScriptGenerator(config=config)

    topic = "Why most startup founders waste their first $1,000 on ads"

    try:
        script = agent.generate_script(topic)
        print(json.dumps(script, indent=2, ensure_ascii=False))
    except Exception as exc:
        logger.error("Failed to generate script: %s", exc)
        raise


if __name__ == "__main__":
    main()
