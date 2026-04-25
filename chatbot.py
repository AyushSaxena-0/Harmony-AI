from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import Iterable
from urllib import error, request


OLLAMA_URL = "http://127.0.0.1:11434"


@dataclass(slots=True)
class ChatMessage:
    role: str
    content: str


@dataclass(slots=True)
class Verse:
    title: str
    reference: str
    theme: str
    text: str
    reflection: str


GITA_VERSES: tuple[Verse, ...] = (
    Verse(
        title="Steady in Difficult Times",
        reference="Bhagavad Gita 2.14",
        theme="endurance",
        text="Difficult feelings come and go, just as changing seasons pass.",
        reflection="This is useful when someone feels overwhelmed and needs help surviving the moment without assuming it will last forever.",
    ),
    Verse(
        title="Action Over Helplessness",
        reference="Bhagavad Gita 2.47",
        theme="action",
        text="You can focus on your effort and choices, even when outcomes feel uncertain.",
        reflection="This helps turn rumination into one kind, concrete next step.",
    ),
    Verse(
        title="Lift Yourself Gently",
        reference="Bhagavad Gita 6.5",
        theme="self_support",
        text="A person can slowly raise themselves through patient self-support, not self-hatred.",
        reflection="This supports compassionate self-talk and discourages shame spirals.",
    ),
    Verse(
        title="A Calm Mind Matters",
        reference="Bhagavad Gita 6.26",
        theme="focus",
        text="When the mind wanders into pain or fear, bring it back with patience rather than force.",
        reflection="This is good for anxious loops, overthinking, and emotional flooding.",
    ),
    Verse(
        title="You Are Not Alone",
        reference="Bhagavad Gita 9.22",
        theme="trust",
        text="There can be support, care, and protection available even when the heart feels isolated.",
        reflection="This helps when someone feels abandoned or emotionally disconnected.",
    ),
)

CRISIS_KEYWORDS = (
    "suicide",
    "kill myself",
    "end my life",
    "want to die",
    "self harm",
    "hurt myself",
    "harm myself",
    "no reason to live",
)


class OllamaConnectionError(RuntimeError):
    pass


class LocalLlamaClient:
    def __init__(self, base_url: str = OLLAMA_URL, timeout: float = 90.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def list_models(self) -> list[str]:
        payload = self._request_json("GET", "/api/tags")
        models = payload.get("models", [])
        return [model.get("name", "") for model in models if model.get("name")]

    def chat(self, model: str, messages: Iterable[ChatMessage]) -> str:
        payload = {
            "model": model,
            "messages": [
                {"role": message.role, "content": message.content}
                for message in messages
            ],
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
            },
        }
        response = self._request_json("POST", "/api/chat", payload)
        message = response.get("message", {})
        return str(message.get("content", "")).strip()

    def _request_json(self, method: str, path: str, payload: dict | None = None) -> dict:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        req = request.Request(
            f"{self.base_url}{path}",
            method=method,
            data=data,
            headers={"Content-Type": "application/json"},
        )
        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
        except error.URLError as exc:
            raise OllamaConnectionError(
                "Could not reach the local Ollama server at 127.0.0.1:11434. Start Ollama and make sure the llama3 model is available."
            ) from exc

        if not raw.strip():
            return {}
        return json.loads(raw)


class BhagavadGitaSupportBot:
    def __init__(self, client: LocalLlamaClient, default_model: str = "llama3") -> None:
        self.client = client
        self.default_model = default_model

    def available_models(self) -> list[str]:
        return self.client.list_models()

    def choose_model(self, models: list[str]) -> str:
        if not models:
            return self.default_model

        priorities = ("llama3", "llama3:latest", "llama3.1", "llama3.2")
        lowered = {model.lower(): model for model in models}
        for candidate in priorities:
            if candidate in lowered:
                return lowered[candidate]
        return models[0]

    def pick_verse(self, text: str) -> Verse:
        lowered = text.lower()
        if any(word in lowered for word in ("hopeless", "tired", "empty", "depressed", "sad")):
            return GITA_VERSES[2]
        if any(word in lowered for word in ("afraid", "panic", "anxious", "worry", "overthink")):
            return GITA_VERSES[3]
        if any(word in lowered for word in ("fail", "stuck", "career", "future", "result")):
            return GITA_VERSES[1]
        if any(word in lowered for word in ("alone", "abandoned", "nobody", "lonely")):
            return GITA_VERSES[4]
        return GITA_VERSES[0]

    def needs_crisis_support(self, text: str) -> bool:
        lowered = re.sub(r"\s+", " ", text.lower())
        return any(keyword in lowered for keyword in CRISIS_KEYWORDS)

    def crisis_response(self) -> str:
        return (
            "I'm really glad you said something. I can offer support, but I'm not enough for immediate safety needs.\n\n"
            "Please contact emergency help or a crisis line right now if you may act on these feelings. "
            "If you are in the U.S. or Canada, call or text 988 now. If you are elsewhere, contact your local emergency number or the nearest crisis service. "
            "If possible, move closer to a trusted person and tell them plainly: 'I don't feel safe being alone right now.'\n\n"
            "While you wait, do only the next tiny safe step: put distance between yourself and anything sharp, sit near a door or another person, and keep breathing slowly with me."
        )

    def build_messages(
        self,
        user_text: str,
        history: list[ChatMessage],
        verse: Verse,
    ) -> list[ChatMessage]:
        system_prompt = (
            "You are an offline emotional support chatbot inspired by the Bhagavad Gita. "
            "Your tone is calm, warm, grounded, and practical. "
            "You are not a doctor and you must not claim to diagnose, cure, or replace professional care. "
            "Use Bhagavad Gita wisdom as gentle motivation, not preachy moralizing. "
            "Keep replies supportive and readable. "
            "Always include:\n"
            "1. One validating sentence.\n"
            "2. One short Gita-inspired insight in plain language.\n"
            "3. One practical next step the user can do in under 10 minutes.\n"
            "4. A brief closing line of encouragement.\n"
            "Avoid long lectures, guilt, superstition, or extreme certainty.\n"
            f"Today's grounding verse: {verse.reference} - {verse.text}\n"
            f"Why it fits: {verse.reflection}"
        )

        trimmed_history = history[-8:]
        return [ChatMessage("system", system_prompt), *trimmed_history, ChatMessage("user", user_text)]

    def reply(
        self,
        user_text: str,
        history: list[ChatMessage],
        model: str,
    ) -> tuple[str, Verse]:
        verse = self.pick_verse(user_text)
        if self.needs_crisis_support(user_text):
            return self.crisis_response(), verse

        response = self.client.chat(model, self.build_messages(user_text, history, verse))
        if not response:
            response = (
                "I'm here with you. Let's keep this very small: take one slow breath, relax your shoulders, "
                "and write one sentence about what hurts most right now."
            )
        return response, verse
