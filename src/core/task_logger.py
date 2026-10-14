"""Gerenciador e auditor de relatórios de tarefas executadas pelo HERMES e AntiGravity."""

import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from ..config import ROOT_DIR


class TaskLogger:
    """Gerencia o registro em disco de missões delegadas e permite abri-las no SO."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.reports_dir = (base_dir or ROOT_DIR) / "reports" / "tasks"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.latest_report_path: Optional[Path] = None

    def log_task(
        self,
        user_prompt: str,
        task_name: str,
        raw_output: str,
        summary: str = "",
        workspace: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Path:
        """Salva a execução detalhada em um arquivo Markdown estruturado.

        Args:
            user_prompt: O que o usuário digitou originalmente no HERMES.
            task_name: Título ou descrição curta da missão delegada.
            raw_output: Saída textual integral retornada pelo AntiGravity (código, logs, etc).
            summary: Síntese executiva dita pelo HERMES.
            workspace: Diretório de trabalho onde o agente operou.
            metadata: Informações extras (ex: status da porta, latência).

        Returns:
            Caminho absoluto do arquivo Markdown gerado.
        """
        now = datetime.now()
        timestamp_str = now.strftime("%Y-%m-%d_%H-%M-%S")
        slug = re.sub(r"[^\w\-]", "_", task_name.strip().lower())[:35].strip("_") or "task"
        file_path = self.reports_dir / f"{timestamp_str}_{slug}.md"

        meta_lines = []
        if metadata:
            for k, v in metadata.items():
                meta_lines.append(f"- **{k.title()}**: `{v}`")
        meta_section = "\n".join(meta_lines) if meta_lines else "- **Status**: Concluído"

        markdown_content = f"""# 📜 Registro de Missão — HERMES & AntiGravity

- **Data / Hora**: {now.strftime("%d/%m/%Y às %H:%M:%S")}
- **Pedido do Usuário**: "{user_prompt}"
- **Missão Delegada**: {task_name}
- **Workspace**: `{workspace or 'Padrão'}`
{meta_section}

---

## 👁️ Veredito do HERMES
{summary.strip() if summary else "Diagnóstico e operações finalizados com sucesso."}

---

## 🤖 Saída Integral do AntiGravity
{raw_output.strip()}

---
*Relatório gerado automaticamente pelo Orquestrador HERMES.*
"""
        file_path.write_text(markdown_content, encoding="utf-8")
        self.latest_report_path = file_path
        return file_path

    def open_report(self, path: Optional[Path | str] = None) -> bool:
        """Abre o relatório no editor ou visualizador padrão do sistema operacional."""
        target = Path(path) if path else self.latest_report_path
        if not target or not target.exists():
            return False

        try:
            if sys.platform == "win32":
                os.startfile(str(target))
                return True
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(target)])
                return True
            else:
                subprocess.Popen(["xdg-open", str(target)])
                return True
        except Exception as exc:
            print(f"[TaskLogger] Erro ao abrir relatório: {exc}")
            return False
