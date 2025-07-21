# backend/estoque.py
from produto import Produto

class Estoque:
    @staticmethod
    def atualizar(produto: Produto, quantidade):
        produto.atualizar_estoque(quantidade)

    @staticmethod
    def reduzir(produto: Produto, quantidade):
        produto.reduzir_estoque(quantidade)
