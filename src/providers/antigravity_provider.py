"""Provedor de integração com o Google AntiGravity via Python SDK."""

import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List

try:
    from google.antigravity import Agent, LocalAgentConfig, CapabilitiesConfig
    ANTIGRAVITY_SDK_AVAILABLE = True
except ImportError:
    ANTIGRAVITY_SDK_AVAILABLE = False


class AntiGravityError(Exception):
    pass


class AntiGravityProvider:
    """Encapsula a orquestração e execução de tarefas através do AntiGravity Python SDK."""

    def __init__(self, api_key: str = "", default_workspace: Optional[str] = None):
        self.api_key = api_key
        # Se z:\homelab existir, adota como workspace padrão de infraestrutura
        homelab_path = Path("z:/homelab")
        if default_workspace:
            self.default_workspace = str(Path(default_workspace).resolve())
        elif homelab_path.exists():
            self.default_workspace = str(homelab_path.resolve())
        else:
            self.default_workspace = str(Path.cwd().resolve())

    def is_available(self) -> bool:
        """Indica se a biblioteca do SDK está instalada no ambiente."""
        return ANTIGRAVITY_SDK_AVAILABLE

    async def _run_async(self, prompt: str, workspace: str) -> Dict[str, Any]:
        if not ANTIGRAVITY_SDK_AVAILABLE:
            raise AntiGravityError("O pacote google-antigravity não está instalado no ambiente.")

        workspaces = [workspace] if workspace else [self.default_workspace]

        config = LocalAgentConfig(
            api_key=self.api_key.strip() or None,
            workspaces=workspaces,
            system_instructions=(
                "Você é o AntiGravity, o agente técnico de infraestrutura, código e automação "
                "que atua em conjunto com o assistente HERMES. "
                "Execute as tarefas com alto rigor técnico, analisando arquivos, configurações, logs "
                "e status de serviços. Forneça diagnósticos objetivos, causa raiz e códigos ou comandos "
                "necessários para correção. Responda em português."
            ),
            capabilities=CapabilitiesConfig(),
        )

        tokens: List[str] = []
        async with Agent(config) as agent:
            response = await agent.chat(prompt)
            async for token in response:
                tokens.append(token)

        full_output = "".join(tokens).strip()
        return {
            "success": True,
            "output": full_output,
            "workspace": workspace,
            "error": None,
        }

    def run_task(self, prompt: str, workspace: Optional[str] = None) -> Dict[str, Any]:
        """Executa a tarefa sincronicamente em uma nova thread/loop assíncrono.

        Args:
            prompt: Instrução do que o AntiGravity deve fazer.
            workspace: Diretório raiz no qual o agente deve operar.

        Returns:
            Dicionário com 'success', 'output', 'workspace' e 'error'.
        """
        target_ws = workspace or self.default_workspace
        try:
            return asyncio.run(self._run_async(prompt, target_ws))
        except Exception as exc:
            return {
                "success": False,
                "output": f"Falha na comunicação com o AntiGravity: {exc}",
                "workspace": target_ws,
                "error": str(exc),
            }
