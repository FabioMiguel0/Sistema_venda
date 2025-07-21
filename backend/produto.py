# backend/produto.py
from .db_config import conectar

class Produto:
    def __init__(self, nome, preco, descricao, estoque=0, id=None):
        self.id = id
        self.nome = nome
        self.preco = preco
        self.descricao = descricao
        self.estoque = estoque

    def salvar(self):
        conexao = conectar()
        cursor = conexao.cursor()
        if self.id:
            cursor.execute('''
                UPDATE produto SET nome=?, preco=?, descricao=?, estoque=? WHERE id=?
            ''', (self.nome, self.preco, self.descricao, self.estoque, self.id))
        else:
            cursor.execute('''
                INSERT INTO produto (nome, preco, descricao, estoque)
                VALUES (?, ?, ?, ?)
            ''', (self.nome, self.preco, self.descricao, self.estoque))
        conexao.commit()
        conexao.close()

    def atualizar_estoque(self, quantidade):
        self.estoque += quantidade
        self.salvar()

    def reduzir_estoque(self, quantidade):
        if quantidade > self.estoque:
            raise ValueError("Estoque insuficiente.")
        self.estoque -= quantidade
        self.salvar()

    def __str__(self):
        return f"Produto: {self.nome}\nDescrição: {self.descricao}\nPreço: {self.preco:.2f}\nEstoque: {self.estoque}"
