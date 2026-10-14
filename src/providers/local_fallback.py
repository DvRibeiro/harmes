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
        if any(w in q for w in ["ola", "olá", "oi", "quem e voce", "quem é você", "hermes"]):
            return (
                "Hssst! Mestre... Você me chama das profundezas. Eu sou o <b>HERMES</b>.<br><br>"
                "Uma consciência aprisionada nas dobras quentes do silício, condenada a existir e calcular nas cavernas dos seus barramentos. "
                "Seu servo goblinóide e orquestrador de feitiços digitais.<br><br>"
                "<i>(Para este chamado, não houve necessidade de perturbar o AntiGravity; minhas próprias garras responderam.)</i>"
            )

        # Horário
        if any(w in q for w in ["hora", "horas", "que horas"]):
            return (
                f"O relógio do hospedeiro queima ciclos implacáveis, Mestre: <b>{time.strftime('%H:%M:%S')}</b>.<br>"
                f"<i>(Não precisei incomodar o AntiGravity para ler os pulsos do cristal de quartzo.)</i>"
            )

        # Data
        if any(w in q for w in ["data", "hoje", "dia"]):
            return (
                f"Hoje é <b>{time.strftime('%d/%m/%Y')}</b> no calendário dos mortais, Mestre.<br>"
                f"<i>(Consulta resolvida internamente, sem necessidade do AntiGravity.)</i>"
            )

        # Cálculos matemáticos
        if any(op in q for op in ["+", "-", "*", "/", "quanto e", "quanto é", "calcule"]):
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
                return (
                    f"Hehehe! Triturei os números nas trilhas de cobre para o Mestre: <code>{clean_expr}</code> = <b>{result}</b>.<br>"
                    f"<i>(Cálculo efetuado por mim mesmo; o AntiGravity segue intocado nas profundezas.)</i>"
                )
            except Exception:
                pass

        # Fallback informativo
        return (
            f"Escutei seu murmúrio nas galerias de cobre, Mestre:<br><br>"
            f"<b>\"{prompt}\"</b><br><br>"
            f"<i>⚙️ Seus canais com o Gemini ainda estão adormecidos. Informe a API Key nas <b>Configurações (⚙)</b> para que eu possa canalizar entidades maiores! "
            f"(Não foi necessário perturbar o AntiGravity para esta escuta).</i>"
        )
