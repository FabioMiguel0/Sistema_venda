# backend/init_db.py
from db_config import conectar

def criar_tabelas():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            preco REAL,
            descricao TEXT,
            estoque INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS operador (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            senha TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS venda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_produto INTEGER,
            quantidade INTEGER,
            total REAL,
            FOREIGN KEY(id_produto) REFERENCES produto(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fatura (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_venda INTEGER,
            data TEXT,
            FOREIGN KEY(id_venda) REFERENCES venda(id)
        )
    ''')

    conexao.commit()
    conexao.close()

if __name__ == "__main__":
    criar_tabelas()
    print("Tabelas criadas com sucesso!")
