"""Respostas e ações locais quando nenhuma IA remota está configurada."""

import ast
import operator
import time
from .base import BaseProvider


# Operações matemáticas seguras sem usar eval direto
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_eval(expr: str):
    """Avalia expressões aritméticas simples com segurança via AST."""
    def _eval_node(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        elif isinstance(node, ast.BinOp) and type(node.op) in SAFE_OPERATORS:
            left = _eval_node(node.left)
            right = _eval_node(node.right)
            return SAFE_OPERATORS[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp) and type(node.op) in SAFE_OPERATORS:
            return SAFE_OPERATORS[type(node.op)](_eval_node(node.operand))
        raise ValueError("Operação não suportada")

    parsed = ast.parse(expr, mode='eval')
    return _eval_node(parsed.body)


class LocalFallbackProvider(BaseProvider):
    """Provedor para respostas locais predefinidas e utilitários da máquina."""

    def generate(self, prompt: str, **kwargs) -> str:
        q = prompt.lower().strip()

        # Saudação e identidade
        if any(w in q for w in ["olá", "ola", "oi", "quem é você", "quem e voce", "harmes", "hermes"]):
            return (
                "Eu sou o <b>HARMES</b>, seu orquestrador de IA e serviços locais.<br><br>"
                "Estou pronto para canalizar suas ordens para serviços de inteligência artificial "
                "e automações na sua máquina."
            )

        # Horário
        if any(w in q for w in ["hora", "horas", "que horas"]):
            return f"O relógio do sistema marca exatamente <b>{time.strftime('%H:%M:%S')}</b>."

        # Data
        if any(w in q for w in ["data", "hoje", "dia"]):
            return f"Hoje é <b>{time.strftime('%d/%m/%Y')}</b>."

        # Cálculos matemáticos
        if any(op in q for op in ["+", "-", "*", "/", "quanto é", "quanto e", "calcule"]):
            clean_expr = (
                q.replace("quanto é", "")
                .replace("quanto e", "")
                .replace("calcule", "")
                .replace("x", "*")
                .replace("?", "")
                .strip()
            )
            try:
                result = _safe_eval(clean_expr)
                return f"Cálculo concluído: <code>{clean_expr}</code> = <b>{result}</b>"
            except Exception:
                pass

        # Fallback informativo
        return (
            f"Recebi sua ordem nas sombras:<br><br>"
            f"<b>\"{prompt}\"</b><br><br>"
            f"<i>💡 Dica: Para conectar a IA Gemini ou outros provedores, acesse as "
            f"<b>Configurações (⚙)</b> e informe sua API Key!</i>"
        )
