import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
import tempfile
import shutil

from src.core.task_logger import TaskLogger
from src.core.tools import SystemTools
from src.core.orchestrator import AIOrchestrator


class OrchestratorTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_task_logger_creates_markdown_report(self):
        logger = TaskLogger(base_dir=self.temp_dir)
        report_path = logger.log_task(
            user_prompt="Hermes, verifique o servidor de minecraft",
            task_name="verificar minecraft",
            raw_output="Porta 25565 ativa. 0 erros encontrados.",
            summary="Servidor operacional.",
            workspace=r"z:\homelab",
            metadata={"Status": "ONLINE", "Ping": "12ms"}
        )

        self.assertTrue(report_path.exists())
        self.assertEqual(logger.latest_report_path, report_path)

        content = report_path.read_text(encoding="utf-8")
        self.assertIn("# 🛡️ Relatório de Missão — HARMES & AntiGravity", content)
        self.assertIn("Hermes, verifique o servidor de minecraft", content)
        self.assertIn("Porta 25565 ativa", content)
        self.assertIn("- **Status**: `ONLINE`", content)

    def test_orchestrator_intent_detection(self):
        orch = AIOrchestrator(config={})

        # Teste intenção AntiGravity
        self.assertTrue(orch._is_antigravity_intent("Hermes, peça para o AntiGravity verificar o servidor"))
        self.assertTrue(orch._is_antigravity_intent("antigravity verifique os logs"))
        self.assertTrue(orch._is_antigravity_intent("delegue ao agente a checagem"))
        self.assertFalse(orch._is_antigravity_intent("Qual a capital da França?"))

        # Teste intenção Servidor Homelab
        self.assertTrue(orch._is_server_intent("o que aconteceu com o servidor de minecraft?"))
        self.assertTrue(orch._is_server_intent("verifique o status do minecraft"))
        self.assertFalse(orch._is_server_intent("quanto é 2 + 2?"))

    def test_task_extraction(self):
        orch = AIOrchestrator(config={})
        task = orch._extract_task("Hermes, peça para o AntiGravity verificar o que aconteceu com o servidor de minecraft")
        self.assertEqual(task, "verificar o que aconteceu com o servidor de minecraft")

        task2 = orch._extract_task("/antigravity analisar logs")
        self.assertEqual(task2, "/antigravity analisar logs")

    @patch("src.core.orchestrator.AntiGravityProvider")
    @patch("src.core.orchestrator.SystemTools.check_minecraft")
    def test_antigravity_delegation_flow(self, mock_mc, mock_ag_cls):
        mock_mc.return_value = {
            "online": True,
            "host": "100.71.76.124",
            "port": 25565,
            "latency_ms": 15.2,
            "status": "ONLINE",
            "error": None
        }

        mock_ag_instance = MagicMock()
        mock_ag_instance.run_task.return_value = {
            "success": True,
            "output": "Minecraft rodando normalmente com 3 jogadores conectados.",
            "workspace": "z:/homelab",
            "error": None
        }
        mock_ag_cls.return_value = mock_ag_instance

        orch = AIOrchestrator(config={"gemini_api_key": "test_key"})
        orch.task_logger = TaskLogger(base_dir=self.temp_dir)
        orch.antigravity = mock_ag_instance

        reply = orch.process("Hermes, peça para o AntiGravity verificar o que aconteceu com o servidor de minecraft")

        self.assertIn("Missão AntiGravity Concluída", reply)
        self.assertIn("Abrir Relatório Completo (.md)", reply)
        self.assertIsNotNone(orch.last_report_path)
        self.assertTrue(orch.last_report_path.exists())


if __name__ == "__main__":
    unittest.main()
