# backend/operador.py
from .db_config import conectar

class Operador:
    def __init__(self, nome, senha, id=None):
        self.id = id
        self.nome = nome
        self.senha = senha

    def salvar(self):
        conexao = conectar()
        cursor = conexao.cursor()
        if self.id:
            cursor.execute("UPDATE operador SET nome=?, senha=? WHERE id=?", (self.nome, self.senha, self.id))
        else:
            cursor.execute("INSERT INTO operador (nome, senha) VALUES (?, ?)", (self.nome, self.senha))
        conexao.commit()
        conexao.close()
