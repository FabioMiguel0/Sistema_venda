# backend/venda.py
from .db_config import conectar
class Venda:
    def __init__(self, id_produto, quantidade, total, id=None):
        self.id = id
        self.id_produto = id_produto
        self.quantidade = quantidade
        self.total = total

    def salvar(self):
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute('''
            INSERT INTO venda (id_produto, quantidade, total)
            VALUES (?, ?, ?)
        ''', (self.id_produto, self.quantidade, self.total))
        conexao.commit()
        conexao.close()
