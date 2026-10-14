"""Orquestrador Central do HARMES.

Coordena o roteamento inteligente de solicitações entre provedores de IA,
delegação para o Google AntiGravity com relatórios em disco e serviços do Homelab.
"""

import re
from pathlib import Path
from typing import Dict, Any, Optional

from ..providers.gemini import GeminiProvider, GeminiError
from ..providers.local_fallback import LocalFallbackProvider
from ..providers.antigravity_provider import AntiGravityProvider
from .task_logger import TaskLogger
from .tools import SystemTools


class AIOrchestrator:
    """Orquestrador responsável por selecionar e executar serviços, agentes e IAs."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.local_fallback = LocalFallbackProvider()
        self.task_logger = TaskLogger()
        self.last_report_path: Optional[Path] = None

        api_key = self.config.get("gemini_api_key", "").strip()
        self.antigravity = AntiGravityProvider(api_key=api_key)

    def update_config(self, new_config: Dict[str, Any]):
        """Atualiza a configuração ativa do orquestrador."""
        self.config = new_config
        self.antigravity.api_key = new_config.get("gemini_api_key", "").strip()

    def _is_antigravity_intent(self, prompt: str) -> bool:
        """Verifica se o usuário solicitou explicitamente a ação do AntiGravity."""
        patterns = [
            r"\b(antigravity|anti-gravity|anti gravity)\b",
            r"\bpe[çc]a\s+ao\s+agente\b",
            r"\bdeleg(ar|ue)\b",
        ]
        return any(re.search(p, prompt, re.IGNORECASE) for p in patterns)

    def _is_server_intent(self, prompt: str) -> bool:
        """Verifica se a pergunta envolve checagem/diagnóstico de servidores do homelab."""
        has_subject = bool(re.search(r"\b(minecraft|mine\b|servidor|homelab|jellyfin|pihole)\b", prompt, re.IGNORECASE))
        has_action = bool(re.search(
            r"\b(verifi(que|car)|checa(r)?|aconteceu|status|caiu|offline|online|porta|como\s+est[aá]|olh(a|ar))\b",
            prompt, re.IGNORECASE
        ))
        return has_subject and has_action

    def _extract_task(self, prompt: str) -> str:
        """Extrai a instrução central de um comando com prefixos de delegação."""
        cleaned = prompt
        # Remove saudações e comandos comuns como "Hermes, peça para o AntiGravity..."
        cleaned = re.sub(r"^(\s*hermes\s*[,:]?\s*)?", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(
            r"^(pe[çc]a\s+(para|pro|ao)\s+(o\s+)?antigravity\s+(para\s+|de\s+|que\s+)?)",
            "",
            cleaned,
            flags=re.IGNORECASE
        )
        cleaned = re.sub(r"^(antigravity\s*[,:]?\s*)", "", cleaned, flags=re.IGNORECASE)
        return cleaned.strip() or prompt.strip()

    def _handle_antigravity_delegation(self, task_prompt: str, original_prompt: str) -> str:
        """Executa a delegação técnica para o AntiGravity e gera o relatório completo em disco."""
        target_task = self._extract_task(task_prompt)
        metadata: Dict[str, Any] = {}
        context_notes = []

        # Se envolver Minecraft, executa teste preliminar de conectividade via SystemTools
        if re.search(r"\bminecraft\b", original_prompt, re.IGNORECASE):
            mc_info = SystemTools.check_minecraft()
            metadata["Minecraft Socket"] = mc_info["status"]
            metadata["Host"] = mc_info["host"]
            metadata["Port"] = mc_info["port"]
            if mc_info.get("latency_ms"):
                metadata["Latência"] = f"{mc_info['latency_ms']}ms"

            status_desc = "ONLINE" if mc_info["online"] else f"OFFLINE ({mc_info.get('error', 'Sem resposta')})"
            context_notes.append(
                f"[Diagnóstico Preliminar de Rede HARMES]:\n"
                f"Tentativa de conexão TCP em {mc_info['host']}:{mc_info['port']} -> Status: {status_desc}."
            )

        full_instruction = target_task
        if context_notes:
            full_instruction = f"{target_task}\n\n" + "\n".join(context_notes)

        # Escolhe workspace: prioriza z:\homelab se existir para infraestrutura
        homelab_ws = Path("z:/homelab")
        workspace_dir = str(homelab_ws.resolve()) if homelab_ws.exists() else None

        # Executa no AntiGravity via Python SDK
        result = self.antigravity.run_task(full_instruction, workspace=workspace_dir)
        raw_output = result.get("output", "")
        success = result.get("success", False)

        # Gerar Síntese Executiva no tom do HARMES
        summary = self._generate_executive_summary(target_task, raw_output)

        # Gravar Relatório Completo em disco
        report_file = self.task_logger.log_task(
            user_prompt=original_prompt,
            task_name=target_task[:50],
            raw_output=raw_output,
            summary=summary,
            workspace=result.get("workspace", "Homelab"),
            metadata=metadata
        )
        self.last_report_path = report_file

        # Formatação do balão de fala compacto com link para o relatório
        report_link = f"file:///{report_file.as_posix().lstrip('/')}"
        icon_badge = "🛡️" if success else "⚠️"

        reply_html = (
            f"<b>{icon_badge} Missão AntiGravity Concluída:</b><br><br>"
            f"{summary}<br><br>"
            f"<div style='margin-top: 6px; padding: 6px 10px; background: rgba(168, 85, 247, 0.18); "
            f"border: 1px solid rgba(168, 85, 247, 0.45); border-radius: 6px;'>"
            f"📄 <a href='{report_link}' style='color: #d8b4fe; text-decoration: none; font-weight: bold;'>"
            f"Abrir Relatório Completo (.md)</a>"
            f"</div>"
        )
        return reply_html

    def _generate_executive_summary(self, task: str, raw_output: str) -> str:
        """Gera um resumo executivo de 2-3 frases para exibição no balão."""
        api_key = self.config.get("gemini_api_key", "").strip()
        model = self.config.get("model", "auto")

        # Tenta sintetizar via Gemini se disponível
        if api_key and len(raw_output) > 200:
            try:
                provider = GeminiProvider(api_key=api_key, model=model)
                synth_prompt = (
                    "Você é o HARMES, assistente místico e eficiente. "
                    "Resuma o seguinte relatório do AntiGravity em exatamente 2 ou 3 frases objetivas "
                    "e elegantes em português para o usuário. Foque na causa raiz ou resultado principal:\n\n"
                    f"{raw_output[:2500]}"
                )
                return provider.generate(synth_prompt)
            except Exception:
                pass

        # Fallback de síntese local baseado no próprio texto do AntiGravity
        lines = [line.strip() for line in raw_output.splitlines() if line.strip() and not line.startswith("#")]
        first_meaningful = " ".join(lines[:3]) if lines else raw_output[:200]
        if len(first_meaningful) > 250:
            first_meaningful = first_meaningful[:247] + "..."
        return first_meaningful or "Análise técnica concluída pelo AntiGravity."

    def process(self, prompt: str) -> str:
        """Processa a solicitação do usuário através do provedor, agente ou serviço adequado.

        Args:
            prompt: Texto da solicitação digitado pelo usuário.

        Returns:
            Texto formatado em HTML/Markdown da resposta para exibição no balão.
        """
        self.last_report_path = None
        clean_prompt = prompt.strip()
        if not clean_prompt:
            return ""

        # 1. Comandos com prefixos explícitos
        if clean_prompt.startswith("/antigravity ") or clean_prompt.startswith("!antigravity "):
            sub_task = clean_prompt.split(" ", 1)[1]
            return self._handle_antigravity_delegation(sub_task, clean_prompt)

        if clean_prompt.startswith("/local ") or clean_prompt.startswith("!local "):
            return self.local_fallback.generate(clean_prompt.split(" ", 1)[1])

        # 2. Detecção de intenção: Delegação para o AntiGravity
        if self._is_antigravity_intent(clean_prompt):
            return self._handle_antigravity_delegation(clean_prompt, clean_prompt)

        # 3. Detecção de diagnóstico de servidor do homelab
        if self._is_server_intent(clean_prompt):
            # Se for checagem de servidor, aciona o AntiGravity para análise aprofundada
            return self._handle_antigravity_delegation(clean_prompt, clean_prompt)

        # 4. Provedor padrão (Google Gemini)
        target_provider = self.config.get("default_provider", "gemini")
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

        # 5. Fallback local para perguntas casuais sem chave de API
        return self.local_fallback.generate(clean_prompt)
