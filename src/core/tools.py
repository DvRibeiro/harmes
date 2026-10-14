"""Ferramentas e utilitários de diagnóstico de rede e infraestrutura do HERMES."""

import json
import socket
import time
from pathlib import Path
from typing import Dict, Any, List, Optional


class SystemTools:
    """Ferramentas de diagnóstico local e homelab."""

    HOMELAB_MONITOR_CONFIG = Path("z:/homelab/services/monitor/config.json")

    @classmethod
    def get_homelab_config(cls) -> Optional[Dict[str, Any]]:
        """Lê a configuração do serviço de monitor do homelab, se presente."""
        if cls.HOMELAB_MONITOR_CONFIG.exists():
            try:
                with open(cls.HOMELAB_MONITOR_CONFIG, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return None
        return None

    @classmethod
    def check_tcp_service(cls, host: str, port: int, timeout: float = 2.5) -> Dict[str, Any]:
        """Testa a conectividade de um serviço TCP com medição de latência."""
        start = time.perf_counter()
        try:
            with socket.create_connection((host, int(port)), timeout=timeout):
                latency_ms = round((time.perf_counter() - start) * 1000, 1)
                return {
                    "online": True,
                    "host": host,
                    "port": port,
                    "latency_ms": latency_ms,
                    "status": "ONLINE",
                    "error": None,
                }
        except socket.timeout:
            return {
                "online": False,
                "host": host,
                "port": port,
                "latency_ms": None,
                "status": "TIMEOUT",
                "error": f"Tempo esgotado ({timeout}s) ao tentar conectar a {host}:{port}.",
            }
        except Exception as exc:
            return {
                "online": False,
                "host": host,
                "port": port,
                "latency_ms": None,
                "status": "OFFLINE",
                "error": str(exc),
            }

    @classmethod
    def check_minecraft(cls) -> Dict[str, Any]:
        """Verifica o status atual do servidor de Minecraft configurado no homelab."""
        host = "100.71.76.124"
        port = 25565

        # Tentar extrair do config do homelab se disponível
        cfg = cls.get_homelab_config()
        if cfg and "services" in cfg:
            for s in cfg["services"]:
                if s.get("id") == "minecraft":
                    host = s.get("host", host)
                    port = s.get("port", port)
                    break

        result = cls.check_tcp_service(host, port)
        result["service_id"] = "minecraft"
        result["service_name"] = "Minecraft Server"
        return result

    @classmethod
    def list_monitored_services(cls) -> List[Dict[str, Any]]:
        """Retorna a lista de serviços cadastrados no homelab."""
        cfg = cls.get_homelab_config()
        if cfg and "services" in cfg:
            return cfg["services"]
        return []
