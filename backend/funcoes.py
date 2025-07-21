# backend/funcoes.py
from .produto import Produto
from .operador import Operador
from .venda import Venda
from .fatura import Fatura
from datetime import datetime

def registar_produto(nome, preco, descricao, estoque):
    p = Produto(nome, preco, descricao, estoque)
    p.salvar()
    print(f"Produto '{nome}' registado com sucesso!")

def registar_operador(nome, senha):
    o = Operador(nome, senha)
    o.salvar()
    print(f"Operador '{nome}' registado com sucesso!")

def realizar_venda(id_produto, quantidade, preco_unitario):
    total = quantidade * preco_unitario
    v = Venda(id_produto, quantidade, total)
    v.salvar()
    print("Venda registada com sucesso.")
    return v

def gerar_fatura(id_venda):
    data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    f = Fatura(id_venda, data)
    f.salvar()
    print("Fatura gerada.")
