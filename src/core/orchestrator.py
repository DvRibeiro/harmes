"""Orquestrador Central do HARMES.

Coordena o roteamento de solicitações do usuário entre diferentes provedores
de IA (Google Gemini, modelos locais via Ollama/LM Studio) e serviços na máquina.
"""

from typing import Dict, Any
from ..providers.gemini import GeminiProvider, GeminiError
from ..providers.local_fallback import LocalFallbackProvider


class AIOrchestrator:
    """Orquestrador responsável por selecionar e executar serviços e IAs."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.local_fallback = LocalFallbackProvider()

    def update_config(self, new_config: Dict[str, Any]):
        """Atualiza a configuração ativa."""
        self.config = new_config

    def process(self, prompt: str) -> str:
        """Processa a solicitação do usuário através do provedor ou serviço mais adequado.

        Args:
            prompt: Texto da solicitação digitado pelo usuário.

        Returns:
            Texto formatado da resposta para exibição no balão.
        """
        clean_prompt = prompt.strip()
        if not clean_prompt:
            return ""

        # Roteamento por prefixos explícitos (se o usuário desejar direcionar manualmente)
        target_provider = self.config.get("default_provider", "gemini")
        if clean_prompt.startswith("/local ") or clean_prompt.startswith("!local "):
            return self.local_fallback.generate(clean_prompt.split(" ", 1)[1])

        # Se houver chave do Gemini configurada e for o provedor ativo
        api_key = self.config.get("gemini_api_key", "").strip()
        model = self.config.get("model", "auto")

        if target_provider == "gemini" and api_key:
            try:
                provider = GeminiProvider(api_key=api_key, model=model)
                return provider.generate(clean_prompt)
            except GeminiError as exc:
                return f"<b>Erro ao consultar o Gemini:</b><br><br>{exc}"
            except Exception as e:
                return f"<b>Falha inesperada no processamento:</b><br><br>{str(e)}"

        # Sem chave de API ou com modo local ativado
        return self.local_fallback.generate(clean_prompt)
