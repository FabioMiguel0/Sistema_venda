from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from protudo import Produto
from estoque import Estoque, EstoqueInsuficienteError, ProdutoNaoEncontradoError, QuantidadeInvalidaError


@dataclass(slots=True)
class ItemVenda:
    produto: Produto
    quantidade: int
    preco_unitario: Decimal

    @property
    def subtotal(self) -> Decimal:
        return self.preco_unitario * Decimal(self.quantidade)


@dataclass(slots=True)
class Venda:
    """Representa uma venda composta por vários itens."""

    identificador: str = field(default_factory=lambda: datetime.now().strftime("VEN-%Y%m%d-%H%M%S%f"))
    data: datetime = field(default_factory=datetime.now)
    itens: List[ItemVenda] = field(default_factory=list)
    finalizada: bool = False

    def adicionar_item(self, produto: Produto, quantidade: int, preco_unitario: Optional[Decimal] = None) -> None:
        if self.finalizada:
            raise RuntimeError("Venda já finalizada.")
        if quantidade <= 0:
            raise QuantidadeInvalidaError("Quantidade do item deve ser positiva.")
        if not produto.ativo:
            raise ValueError("Produto inativo.")
        unitario = produto.preco_unitario if preco_unitario is None else Decimal(preco_unitario)
        if unitario < 0:
            raise ValueError("Preço unitário inválido.")
        self.itens.append(ItemVenda(produto=produto, quantidade=int(quantidade), preco_unitario=unitario))

    @property
    def total(self) -> Decimal:
        total = Decimal("0.00")
        for item in self.itens:
            total += item.subtotal
        return total

    def validar_estoque(self, estoque: Estoque) -> None:
        for item in self.itens:
            # Vai lançar se não existir
            _ = estoque.obter_produto(item.produto.codigo)
            disponivel = estoque.obter_quantidade(item.produto.codigo)
            if disponivel < item.quantidade:
                raise EstoqueInsuficienteError(
                    f"Insuficiente para {item.produto.codigo}. Disponível {disponivel}, necessário {item.quantidade}."
                )

    def finalizar(self, estoque: Estoque) -> None:
        if self.finalizada:
            raise RuntimeError("Venda já finalizada.")
        if not self.itens:
            raise RuntimeError("Venda vazia.")
        self.validar_estoque(estoque)
        # Debita após validar tudo
        for item in self.itens:
            estoque.remover(item.produto.codigo, item.quantidade)
        self.finalizada = True