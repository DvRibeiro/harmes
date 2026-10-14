"""Gerenciamento de configurações e caminhos do Hermes."""

import json
import os
from pathlib import Path

SRC_DIR = Path(__file__).parent.resolve()
ROOT_DIR = SRC_DIR.parent.resolve()
ASSETS_DIR = ROOT_DIR / "assets"
CONFIG_FILE = ROOT_DIR / "config.json"
EXAMPLE_CONFIG_FILE = ROOT_DIR / "config.example.json"


def get_default_api_key() -> str:
    """Obtém a chave da API Gemini das variáveis de ambiente."""
    return (
        os.environ.get("GEMINI_API_KEY", "") or
        os.environ.get("GOOGLE_API_KEY", "") or
        ""
    )


def get_default_config() -> dict:
    """Configuração padrão do orquestrador."""
    return {
        "default_provider": "gemini",
        "gemini_api_key": get_default_api_key(),
        "model": "auto",
        "orchestration": {
            "enable_local_fallback": True,
            "system_commands": True
        },
        "services": {
            "ollama": {
                "enabled": False,
                "base_url": "http://localhost:11434",
                "model": "llama3"
            },
            "comfyui": {
                "enabled": False,
                "base_url": "http://localhost:8188"
            }
        }
    }


def load_config() -> dict:
    """Carrega as configurações salvas em config.json com fallback para padrões."""
    cfg = get_default_config()

    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                if isinstance(saved, dict):
                    cfg.update(saved)
        except Exception as e:
            print(f"[Hermes Config] Aviso ao ler config.json: {e}")
    elif EXAMPLE_CONFIG_FILE.exists():
        try:
            with open(EXAMPLE_CONFIG_FILE, "r", encoding="utf-8") as f:
                example = json.load(f)
                if isinstance(example, dict):
                    cfg.update(example)
        except Exception:
            pass

    return cfg


def save_config(cfg: dict) -> bool:
    """Salva o dicionário de configurações em config.json."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[Hermes Config] Erro ao salvar config.json: {e}")
        return False
