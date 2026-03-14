"""
LLM Service Abstraction Layer — supports OpenAI, Google Gemini, and mock fallback.

Provides a unified interface for chat, structured output, and vision extraction.
Includes token usage tracking and simple in-memory rate limiting.
"""

import time
import json
import base64
import logging
from typing import Optional, Any, Dict, List
from collections import deque

from src.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple sliding-window rate limiter (in-memory)."""

    def __init__(self, max_calls: int = 60, window_seconds: int = 60):
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self._timestamps: deque = deque()

    def acquire(self) -> bool:
        """Return True if a call is allowed, False if rate-limited."""
        now = time.time()
        # Remove timestamps outside the window
        while self._timestamps and self._timestamps[0] < now - self.window_seconds:
            self._timestamps.popleft()
        if len(self._timestamps) >= self.max_calls:
            return False
        self._timestamps.append(now)
        return True

    def wait_and_acquire(self):
        """Block until a call is allowed."""
        while not self.acquire():
            time.sleep(0.5)


class UsageTracker:
    """Tracks token usage across calls."""

    def __init__(self):
        self.total_prompt_tokens: int = 0
        self.total_completion_tokens: int = 0
        self.total_calls: int = 0
        self.calls_by_provider: Dict[str, int] = {"openai": 0, "gemini": 0, "mock": 0}
        self._call_log: List[Dict[str, Any]] = []

    def record(self, provider: str, prompt_tokens: int, completion_tokens: int):
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        self.total_calls += 1
        self.calls_by_provider[provider] = self.calls_by_provider.get(provider, 0) + 1
        self._call_log.append({
            "provider": provider,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "timestamp": time.time(),
        })

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_prompt_tokens + self.total_completion_tokens,
            "total_calls": self.total_calls,
            "calls_by_provider": dict(self.calls_by_provider),
        }


class LLMService:
    """Unified LLM service supporting OpenAI and Google Gemini with fallback."""

    def __init__(self):
        self.provider = self._detect_provider()
        self._openai_client = None
        self._gemini_configured = False
        self._rate_limiter = RateLimiter(
            max_calls=settings.llm_rate_limit, window_seconds=60
        )
        self._usage = UsageTracker()

    # ------------------------------------------------------------------
    # Provider detection
    # ------------------------------------------------------------------

    def _detect_provider(self) -> str:
        forced = settings.llm_provider
        if forced and forced != "auto":
            if forced == "openai" and settings.openai_api_key:
                return "openai"
            if forced == "gemini" and settings.google_ai_api_key:
                return "gemini"
            if forced == "mock":
                return "mock"
            # Forced provider but no key -> fall through to auto
        # Auto-detect
        if settings.openai_api_key:
            return "openai"
        if settings.google_ai_api_key:
            return "gemini"
        return "mock"

    # ------------------------------------------------------------------
    # Client factories (lazy init)
    # ------------------------------------------------------------------

    def _get_openai_client(self):
        if self._openai_client is None:
            from openai import OpenAI
            self._openai_client = OpenAI(api_key=settings.openai_api_key)
        return self._openai_client

    def _get_gemini_model(self, model_name: str = "gemini-1.5-flash"):
        if not self._gemini_configured:
            import google.generativeai as genai
            genai.configure(api_key=settings.google_ai_api_key)
            self._gemini_configured = True
        import google.generativeai as genai
        return genai.GenerativeModel(model_name)

    # ------------------------------------------------------------------
    # Core chat
    # ------------------------------------------------------------------

    async def chat(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.4,
        max_tokens: int = 1024,
    ) -> str:
        """Send a single chat message and return the response text."""
        providers = self._provider_order()
        last_error: Optional[Exception] = None

        for prov in providers:
            try:
                self._rate_limiter.wait_and_acquire()
                if prov == "openai":
                    return self._chat_openai(system_prompt, user_message, temperature, max_tokens)
                elif prov == "gemini":
                    return self._chat_gemini(system_prompt, user_message, temperature, max_tokens)
                else:
                    return self._chat_mock(system_prompt, user_message)
            except Exception as exc:
                last_error = exc
                logger.warning("LLM provider %s failed: %s. Trying next.", prov, exc)
                continue

        # Should not happen because mock never fails, but just in case
        logger.error("All LLM providers failed. Last error: %s", last_error)
        return self._chat_mock(system_prompt, user_message)

    async def chat_with_history(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.4,
        max_tokens: int = 1024,
    ) -> str:
        """Chat with conversation history. Messages are [{role, content}, ...]."""
        providers = self._provider_order()
        last_error: Optional[Exception] = None

        for prov in providers:
            try:
                self._rate_limiter.wait_and_acquire()
                if prov == "openai":
                    return self._chat_history_openai(system_prompt, messages, temperature, max_tokens)
                elif prov == "gemini":
                    return self._chat_history_gemini(system_prompt, messages, temperature, max_tokens)
                else:
                    user_msg = messages[-1]["content"] if messages else ""
                    return self._chat_mock(system_prompt, user_msg)
            except Exception as exc:
                last_error = exc
                logger.warning("LLM provider %s failed (history): %s. Trying next.", prov, exc)
                continue

        user_msg = messages[-1]["content"] if messages else ""
        return self._chat_mock(system_prompt, user_msg)

    # ------------------------------------------------------------------
    # Structured output (instructor)
    # ------------------------------------------------------------------

    async def structured_output(
        self,
        system_prompt: str,
        user_message: str,
        response_model: Any,
        temperature: float = 0.2,
    ) -> Any:
        """Get structured output using the instructor library (Pydantic model)."""
        providers = self._provider_order()
        last_error: Optional[Exception] = None

        for prov in providers:
            try:
                self._rate_limiter.wait_and_acquire()
                if prov == "openai":
                    return self._structured_openai(system_prompt, user_message, response_model, temperature)
                elif prov == "gemini":
                    return self._structured_gemini(system_prompt, user_message, response_model, temperature)
                else:
                    return self._structured_mock(response_model)
            except Exception as exc:
                last_error = exc
                logger.warning("LLM structured output via %s failed: %s", prov, exc)
                continue

        # Fallback to mock
        return self._structured_mock(response_model)

    # ------------------------------------------------------------------
    # Vision extraction
    # ------------------------------------------------------------------

    async def vision_extract(self, image_path: str, prompt: str) -> str:
        """Extract text/data from an image using a vision model."""
        providers = self._provider_order()
        last_error: Optional[Exception] = None

        for prov in providers:
            try:
                self._rate_limiter.wait_and_acquire()
                if prov == "openai":
                    return self._vision_openai(image_path, prompt)
                elif prov == "gemini":
                    return self._vision_gemini(image_path, prompt)
                else:
                    return self._vision_mock(prompt)
            except Exception as exc:
                last_error = exc
                logger.warning("Vision extraction via %s failed: %s", prov, exc)
                continue

        return self._vision_mock(prompt)

    # ------------------------------------------------------------------
    # Usage stats
    # ------------------------------------------------------------------

    def get_usage_stats(self) -> Dict[str, Any]:
        """Return token usage statistics."""
        stats = self._usage.get_stats()
        stats["active_provider"] = self.provider
        return stats

    # ------------------------------------------------------------------
    # Provider ordering (primary -> secondary -> mock)
    # ------------------------------------------------------------------

    def _provider_order(self) -> List[str]:
        """Return the list of providers to try in order."""
        order: List[str] = []
        if self.provider != "mock":
            order.append(self.provider)
        # Add secondary
        if self.provider == "openai" and settings.google_ai_api_key:
            order.append("gemini")
        elif self.provider == "gemini" and settings.openai_api_key:
            order.append("openai")
        order.append("mock")
        return order

    # ==================================================================
    # OpenAI implementations
    # ==================================================================

    def _chat_openai(self, system_prompt: str, user_message: str, temperature: float, max_tokens: int) -> str:
        client = self._get_openai_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        usage = response.usage
        if usage:
            self._usage.record("openai", usage.prompt_tokens, usage.completion_tokens)
        return response.choices[0].message.content

    def _chat_history_openai(
        self, system_prompt: str, messages: List[Dict[str, str]], temperature: float, max_tokens: int
    ) -> str:
        client = self._get_openai_client()
        oai_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            oai_messages.append({"role": msg["role"], "content": msg["content"]})
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=oai_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        usage = response.usage
        if usage:
            self._usage.record("openai", usage.prompt_tokens, usage.completion_tokens)
        return response.choices[0].message.content

    def _structured_openai(self, system_prompt: str, user_message: str, response_model: Any, temperature: float) -> Any:
        import instructor
        client = instructor.from_openai(self._get_openai_client())
        result = client.chat.completions.create(
            model="gpt-4o-mini",
            response_model=response_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
        )
        # instructor doesn't expose raw usage easily; estimate
        self._usage.record("openai", 200, 300)
        return result

    def _vision_openai(self, image_path: str, prompt: str) -> str:
        import os
        client = self._get_openai_client()

        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        ext = os.path.splitext(image_path)[1].lower()
        mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".gif": "image/gif"}
        mime_type = mime_map.get(ext, "image/png")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime_type};base64,{image_data}"},
                        },
                    ],
                }
            ],
            max_tokens=1024,
        )
        usage = response.usage
        if usage:
            self._usage.record("openai", usage.prompt_tokens, usage.completion_tokens)
        return response.choices[0].message.content

    # ==================================================================
    # Gemini implementations
    # ==================================================================

    def _chat_gemini(self, system_prompt: str, user_message: str, temperature: float, max_tokens: int) -> str:
        import google.generativeai as genai

        model = self._get_gemini_model("gemini-1.5-flash")
        full_prompt = f"{system_prompt}\n\nUser: {user_message}"
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        response = model.generate_content(full_prompt, generation_config=generation_config)
        # Estimate tokens
        prompt_tokens = len(full_prompt.split()) * 2
        completion_tokens = len(response.text.split()) * 2 if response.text else 0
        self._usage.record("gemini", prompt_tokens, completion_tokens)
        return response.text

    def _chat_history_gemini(
        self, system_prompt: str, messages: List[Dict[str, str]], temperature: float, max_tokens: int
    ) -> str:
        import google.generativeai as genai

        model = self._get_gemini_model("gemini-1.5-flash")
        # Build conversation as text
        parts = [system_prompt, ""]
        for msg in messages:
            role_label = "User" if msg["role"] == "user" else "Assistant"
            parts.append(f"{role_label}: {msg['content']}")
        full_prompt = "\n".join(parts)
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        response = model.generate_content(full_prompt, generation_config=generation_config)
        prompt_tokens = len(full_prompt.split()) * 2
        completion_tokens = len(response.text.split()) * 2 if response.text else 0
        self._usage.record("gemini", prompt_tokens, completion_tokens)
        return response.text

    def _structured_gemini(self, system_prompt: str, user_message: str, response_model: Any, temperature: float) -> Any:
        """Structured output via Gemini: ask for JSON, parse into Pydantic model."""
        import google.generativeai as genai

        model = self._get_gemini_model("gemini-1.5-flash")
        schema_hint = ""
        if hasattr(response_model, "model_json_schema"):
            schema_hint = f"\n\nRespond ONLY with valid JSON matching this schema:\n{json.dumps(response_model.model_json_schema(), indent=2)}"

        full_prompt = f"{system_prompt}{schema_hint}\n\nUser: {user_message}"
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=2048,
        )
        response = model.generate_content(full_prompt, generation_config=generation_config)
        text = response.text.strip()
        # Strip markdown code fences if present
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:])
            if text.endswith("```"):
                text = text[:-3].strip()
        prompt_tokens = len(full_prompt.split()) * 2
        completion_tokens = len(text.split()) * 2
        self._usage.record("gemini", prompt_tokens, completion_tokens)
        data = json.loads(text)
        return response_model(**data)

    def _vision_gemini(self, image_path: str, prompt: str) -> str:
        import google.generativeai as genai
        import PIL.Image

        model = self._get_gemini_model("gemini-1.5-flash")
        img = PIL.Image.open(image_path)
        response = model.generate_content([prompt, img])
        prompt_tokens = len(prompt.split()) * 2 + 500  # image tokens estimate
        completion_tokens = len(response.text.split()) * 2 if response.text else 0
        self._usage.record("gemini", prompt_tokens, completion_tokens)
        return response.text

    # ==================================================================
    # Mock implementations (no API key required)
    # ==================================================================

    def _chat_mock(self, system_prompt: str, user_message: str) -> str:
        """Return a reasonable mock response for development."""
        self._usage.record("mock", 0, 0)
        msg_lower = user_message.lower()

        if any(word in msg_lower for word in ["company", "incorporate", "register"]):
            return (
                "Based on Indian company law, I can help you with incorporation. "
                "The process typically involves: 1) Obtaining DSC and DIN, "
                "2) Name reservation via RUN, 3) Filing SPICe+ (INC-32), "
                "4) Receiving Certificate of Incorporation. "
                "The timeline is usually 7-15 business days."
            )
        if any(word in msg_lower for word in ["document", "pan", "aadhaar", "passport"]):
            return (
                "For company incorporation, you typically need: PAN card, Aadhaar card, "
                "passport-size photograph, address proof, and bank statement for each director. "
                "For the registered office, you need a utility bill and NOC from the owner."
            )
        if any(word in msg_lower for word in ["name", "suggest", "naming"]):
            return (
                "Company names must follow MCA naming guidelines. The name should be unique, "
                "not identical or similar to existing companies, and must end with "
                "'Private Limited' for Pvt Ltd companies. Avoid prohibited words like "
                "'President', 'Republic', 'Government', etc."
            )
        if any(word in msg_lower for word in ["cost", "price", "fee"]):
            return (
                "The total cost of incorporation depends on the entity type and authorized capital. "
                "Government fees include: RUN fee (~Rs 1,000), SPICe+ filing fee (varies by capital), "
                "stamp duty (varies by state), and DSC (~Rs 1,500 per director)."
            )
        return (
            "I'm an AI assistant for Companies Made Simple India. I can help you with "
            "company incorporation, compliance requirements, entity selection, and "
            "MCA filing guidance. How can I assist you today?"
        )

    def _structured_mock(self, response_model: Any) -> Any:
        """Return a mock instance of the response model with default values."""
        self._usage.record("mock", 0, 0)
        # Build default values based on field types
        if hasattr(response_model, "model_fields"):
            defaults: Dict[str, Any] = {}
            for field_name, field_info in response_model.model_fields.items():
                annotation = field_info.annotation
                if annotation is str or (hasattr(annotation, "__origin__") and annotation.__origin__ is str):
                    defaults[field_name] = f"mock_{field_name}"
                elif annotation is int:
                    defaults[field_name] = 0
                elif annotation is float:
                    defaults[field_name] = 0.85
                elif annotation is bool:
                    defaults[field_name] = True
                elif annotation is list or (hasattr(annotation, "__origin__") and annotation.__origin__ is list):
                    defaults[field_name] = []
                elif annotation is dict or (hasattr(annotation, "__origin__") and annotation.__origin__ is dict):
                    defaults[field_name] = {}
                else:
                    # Try None for Optional fields
                    defaults[field_name] = None
            try:
                return response_model(**defaults)
            except Exception:
                pass
        # If we can't construct, raise so the fallback chain continues
        raise ValueError("Cannot construct mock for response model")

    def _vision_mock(self, prompt: str) -> str:
        """Return mock vision extraction results."""
        self._usage.record("mock", 0, 0)
        prompt_lower = prompt.lower()
        if "pan" in prompt_lower:
            return json.dumps({
                "document_type": "PAN Card",
                "name": "RAJESH KUMAR SHARMA",
                "pan_number": "ABCPS1234K",
                "date_of_birth": "15/05/1990",
                "fathers_name": "SURESH KUMAR SHARMA",
                "confidence": 0.92,
            })
        if "aadhaar" in prompt_lower or "aadhar" in prompt_lower:
            return json.dumps({
                "document_type": "Aadhaar Card",
                "name": "RAJESH KUMAR SHARMA",
                "aadhaar_number": "XXXX XXXX 1234",
                "address": "123, MG Road, Bengaluru, Karnataka 560001",
                "date_of_birth": "15/05/1990",
                "confidence": 0.90,
            })
        if "passport" in prompt_lower:
            return json.dumps({
                "document_type": "Passport",
                "name": "RAJESH KUMAR SHARMA",
                "passport_number": "J8765432",
                "nationality": "INDIAN",
                "date_of_birth": "15/05/1990",
                "confidence": 0.93,
            })
        if "utility" in prompt_lower or "bill" in prompt_lower:
            return json.dumps({
                "document_type": "Utility Bill",
                "name": "RAJESH KUMAR SHARMA",
                "address": "123, MG Road, Bengaluru, Karnataka 560001",
                "date": "01/01/2024",
                "confidence": 0.88,
            })
        return json.dumps({
            "document_type": "Unknown",
            "raw_text": "Mock OCR extraction - document content would appear here.",
            "confidence": 0.75,
        })


# ---------------------------------------------------------------------------
# Singleton instance
# ---------------------------------------------------------------------------
llm_service = LLMService()
