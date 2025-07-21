# backend/fatura.py
from .db_config import conectar

class Fatura:
    def __init__(self, id_venda, data, id=None):
        self.id = id
        self.id_venda = id_venda
        self.data = data

    def salvar(self):
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute('''
            INSERT INTO fatura (id_venda, data)
            VALUES (?, ?)
        ''', (self.id_venda, self.data))
        conexao.commit()
        conexao.close()
