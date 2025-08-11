from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Optional


def _to_decimal_2(value: Decimal | str | float | int) -> Decimal:
    """Converte valores para Decimal com 2 casas decimais, validando não-negativo."""
    try:
        if isinstance(value, str):
            value = value.strip().replace(",", ".")
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError("Preço inválido. Use número com até 2 casas decimais.")

    if amount < 0:
        raise ValueError("Preço não pode ser negativo.")

    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass(slots=True)
class Produto:
    """Representa um produto vendável no sistema."""

    codigo: str
    nome: str
    preco_unitario: Decimal
    categoria: Optional[str] = None
    ativo: bool = True

    def __post_init__(self) -> None:
        if not self.codigo or not isinstance(self.codigo, str):
            raise ValueError("Código do produto é obrigatório.")
        if not self.nome or not isinstance(self.nome, str):
            raise ValueError("Nome do produto é obrigatório.")
        self.preco_unitario = _to_decimal_2(self.preco_unitario)

    def atualizar_preco(self, novo_preco: Decimal | str | float | int) -> None:
        self.preco_unitario = _to_decimal_2(novo_preco)

    def desativar(self) -> None:
        self.ativo = False

    def ativar(self) -> None:
        self.ativo = True

    def __repr__(self) -> str:  # útil para logs e listagens
        status = "ativo" if self.ativo else "inativo"
        return (
            f"Produto(codigo={self.codigo!r}, nome={self.nome!r}, "
            f"preco_unitario={self.preco_unitario}, categoria={self.categoria!r}, {status})"
        )