"""Interface base para provedores de IA e serviços do Hermes."""

from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """Classe base abstrata para todos os provedores de IA."""

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Gera uma resposta para o prompt solicitado."""
        pass
