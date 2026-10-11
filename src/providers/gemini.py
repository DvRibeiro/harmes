"""Cliente REST do Gemini, sem dependências além da biblioteca padrão."""

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import List

from .base import BaseProvider

BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
SYSTEM_INSTRUCTION = (
    "Você é o HARMES, uma entidade inteligente das sombras e mensageiro orquestrador "
    "no desktop do usuário. Você conecta e coordena IAs e serviços locais da máquina. "
    "Responda em português com clareza, inteligência e tom prestativo, com um toque sutil de mistério. "
    "Formate a resposta de forma limpa."
)


class GeminiError(Exception):
    def __init__(self, message: str, status: int = None):
        super().__init__(message)
        self.status = status


def _request(path: str, api_key: str, payload: dict = None) -> dict:
    request = urllib.request.Request(
        f"{BASE_URL}/{path}",
        data=json.dumps(payload).encode("utf-8") if payload is not None else None,
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key.strip()},
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        messages = {
            400: "Requisição recusada pelo Gemini. Confira sua chave e o modelo nas configurações.",
            401: "Chave do Gemini inválida. Confira a API Key nas configurações.",
            403: "Acesso ao Gemini negado. Confira a chave e as permissões do projeto.",
            404: "O modelo solicitado não está disponível para generateContent.",
            429: "Limite de requisições ou cota do Gemini atingido. Confira a cota no Google AI Studio e tente novamente mais tarde.",
        }
        # Não inclua URLs, cabeçalhos ou corpos de erro que possam expor a chave.
        raise GeminiError(
            messages.get(exc.code, "O serviço Gemini está indisponível. Tente novamente mais tarde.")
            + f" (HTTP {exc.code})", exc.code
        ) from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise GeminiError("Não foi possível conectar ao Gemini. Verifique sua conexão e tente novamente.") from None
    except (ValueError, UnicodeError):
        raise GeminiError("O Gemini retornou uma resposta inválida. Tente novamente.") from None


def _model_priority(name: str):
    # Prefira Flash estável para chat; dentro da família, versões mais recentes.
    preview = any(word in name for word in ("preview", "experimental", "-exp"))
    version = re.search(r"gemini-(\d+)(?:\.(\d+))?", name)
    numbers = tuple(-int(value or 0) for value in version.groups()) if version else (0, 0)
    return (preview, "flash" not in name, numbers, name)


def list_text_models(api_key: str) -> List[str]:
    names = set()
    page_token = ""
    seen_tokens = set()
    while True:
        params = {"pageSize": 1000}
        if page_token:
            params["pageToken"] = page_token
        data = _request("models?" + urllib.parse.urlencode(params), api_key)
        for model in data.get("models", []):
            name = model.get("name", "").removeprefix("models/")
            if (name.startswith("gemini-")
                    and "generateContent" in model.get("supportedGenerationMethods", [])
                    and not any(word in name for word in ("image", "audio", "tts", "live", "robotics", "computer-use"))):
                names.add(name)
        page_token = data.get("nextPageToken", "")
        if not page_token:
            break
        if page_token in seen_tokens:
            raise GeminiError("A listagem de modelos do Gemini retornou uma paginação inválida.")
        seen_tokens.add(page_token)
    return sorted(names, key=_model_priority)


def _generate(query: str, api_key: str, model: str) -> str:
    data = _request("models/" + urllib.parse.quote(model, safe="") + ":generateContent", api_key, {
        "systemInstruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
        "contents": [{"role": "user", "parts": [{"text": query}]}],
    })
    if data.get("promptFeedback", {}).get("blockReason"):
        raise GeminiError("O Gemini bloqueou esta solicitação. Tente reformular a pergunta.")
    candidates = data.get("candidates") or []
    if candidates:
        candidate = candidates[0]
        if candidate.get("finishReason") in ("SAFETY", "RECITATION", "BLOCKLIST", "PROHIBITED_CONTENT", "SPII"):
            raise GeminiError("O Gemini bloqueou esta resposta. Tente reformular a pergunta.")
        text = "".join(part.get("text", "") for part in candidate.get("content", {}).get("parts", [])
                       if not part.get("thought")).strip()
        if text:
            return text
    raise GeminiError("O Gemini não retornou texto para esta pergunta. Tente reformulá-la.")


def generate_reply(query: str, api_key: str, model: str = "auto") -> str:
    model = (model or "auto").strip().removeprefix("models/")
    if model and model.lower() != "auto":
        try:
            return _generate(query, api_key, model)
        except GeminiError as exc:
            if exc.status != 404:
                raise
    # Descubra substitutos para modelos retirados, inclusive em config.json antigos.
    for available in list_text_models(api_key):
        if available == model:
            continue
        try:
            return _generate(query, api_key, available)
        except GeminiError as exc:
            if exc.status != 404:
                raise
    raise GeminiError("Nenhum modelo Gemini de texto compatível com generateContent está disponível para esta chave.")


class GeminiProvider(BaseProvider):
    """Provedor integrado para o Google Gemini."""

    def __init__(self, api_key: str = "", model: str = "auto"):
        self.api_key = api_key
        self.model = model

    def generate(self, prompt: str, **kwargs) -> str:
        api_key = kwargs.get("api_key", self.api_key)
        model = kwargs.get("model", self.model)
        return generate_reply(prompt, api_key=api_key, model=model)
