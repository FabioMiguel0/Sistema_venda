from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from protudo import Produto


class ProdutoJaCadastradoError(Exception):
    pass


class ProdutoNaoEncontradoError(Exception):
    pass


class QuantidadeInvalidaError(Exception):
    pass


class EstoqueInsuficienteError(Exception):
    pass


@dataclass(slots=True)
class ItemEstoque:
    produto: Produto
    quantidade: int


class Estoque:
    """Gerencia o inventário de produtos."""

    def __init__(self) -> None:
        self._produtos: Dict[str, Produto] = {}
        self._quantidades: Dict[str, int] = {}

    def cadastrar_produto(self, produto: Produto, quantidade_inicial: int = 0) -> None:
        if produto.codigo in self._produtos:
            raise ProdutoJaCadastradoError(f"Produto {produto.codigo} já cadastrado.")
        if quantidade_inicial < 0:
            raise QuantidadeInvalidaError("Quantidade inicial não pode ser negativa.")
        self._produtos[produto.codigo] = produto
        self._quantidades[produto.codigo] = int(quantidade_inicial)

    def atualizar_preco(self, codigo: str, novo_preco) -> None:
        produto = self.obter_produto(codigo)
        produto.atualizar_preco(novo_preco)

    def adicionar(self, codigo: str, quantidade: int) -> None:
        if quantidade <= 0:
            raise QuantidadeInvalidaError("Quantidade a adicionar deve ser positiva.")
        self._assert_produto_existe(codigo)
        self._quantidades[codigo] += int(quantidade)

    def remover(self, codigo: str, quantidade: int) -> None:
        if quantidade <= 0:
            raise QuantidadeInvalidaError("Quantidade a remover deve ser positiva.")
        self._assert_produto_existe(codigo)
        if self._quantidades[codigo] < quantidade:
            raise EstoqueInsuficienteError(
                f"Estoque insuficiente para {codigo}. Disponível: {self._quantidades[codigo]}, solicitado: {quantidade}."
            )
        self._quantidades[codigo] -= int(quantidade)

    def obter_quantidade(self, codigo: str) -> int:
        self._assert_produto_existe(codigo)
        return self._quantidades[codigo]

    def obter_produto(self, codigo: str) -> Produto:
        self._assert_produto_existe(codigo)
        return self._produtos[codigo]

    def listar(self) -> List[ItemEstoque]:
        return [ItemEstoque(produto=self._produtos[c], quantidade=q) for c, q in self._quantidades.items()]

    def _assert_produto_existe(self, codigo: str) -> None:
        if codigo not in self._produtos:
            raise ProdutoNaoEncontradoError(f"Produto {codigo} não encontrado.")