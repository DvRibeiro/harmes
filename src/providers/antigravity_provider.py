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

    def __init__(self, api_key: str = "", default_workspace: Optional[str] = None, model: str = "gemini-3.5-flash-lite"):
        self.model = model or "gemini-3.5-flash-lite"
        self.api_key = api_key
        # Se z:\homelab existir, adota como workspace padrão de infraestrutura
        homelab_path = Path("Z:/homelab")
        if default_workspace:
            self.default_workspace = str(Path(default_workspace).as_posix())
        elif homelab_path.exists():
            self.default_workspace = "Z:/homelab"
        else:
            self.default_workspace = str(Path.cwd().as_posix())

    def is_available(self) -> bool:
        """Indica se a biblioteca do SDK está instalada no ambiente."""
        return ANTIGRAVITY_SDK_AVAILABLE

    async def _run_async(self, prompt: str, workspace: str) -> Dict[str, Any]:
        if not ANTIGRAVITY_SDK_AVAILABLE:
            raise AntiGravityError("O pacote google-antigravity não está instalado no ambiente.")

        workspaces = [workspace] if workspace else [self.default_workspace]

        config = LocalAgentConfig(
            api_key=self.api_key.strip() or None,
            model=self.model,
            workspaces=workspaces,
            system_instructions="""Voce e o AntiGravity, o agente tecnico especialista em codigo e infraestrutura do ecossistema Homelab, atuando diretamente em conjunto com o assistente orquestrador HERMES.

CONTEXTO DO HOMELAB:
- Workspace: Z:/homelab (montagem do no Alpine Linux 192.168.15.8) e nos Windows 10.
- A INFRAESTRUTURA NAO UTILIZA DOCKER. Todos os servicos rodam nativamente em Python/Alpine Linux e Windows.
- Servicos proprios existentes no repositorio:
  * services/webcam-streamer/webcam_streamer.py -> Servidor de streaming da webcam PC024 e detector de movimento na PORTA 8080.
  * services/monitor/monitor.py -> Homelab Monitor e dashboard web na PORTA 5050.
  * services/monitor/config.json -> Configuracao e portas de todos os servicos monitorados.
  * shared/homelab_notify/ -> Biblioteca compartilhada de alertas para o Discord.
  * hosts/alpine/ e hosts/windows/ -> Scripts de inicializacao e automacao.

DIRETRIZES DE EXECUCAO:
1. Sempre analise o codigo e arquivos do workspace antes de dar qualquer resposta tecnica.
2. NUNCA mencione ou sugira Docker, containers ou ferramentas inexistentes (como Frigate, MotionEye, Portainer).
3. Seja direto, preciso e cite os arquivos e portas exatas do projeto.""",
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
