#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Vendas - Versão com Bugs
Este sistema contém bugs intencionais que serão corrigidos
"""

import json
import datetime
import hashlib

class Produto:
    def __init__(self, id_produto, nome, preco, estoque):
        self.id_produto = id_produto
        self.nome = nome
        self.preco = preco
        self.estoque = estoque
    
    def __str__(self):
        return f"ID: {self.id_produto}, Nome: {self.nome}, Preço: R${self.preco}, Estoque: {self.estoque}"

class Cliente:
    def __init__(self, id_cliente, nome, email, senha):
        self.id_cliente = id_cliente
        self.nome = nome
        self.email = email
        # BUG 1: Armazenamento de senha em texto plano (vulnerabilidade de segurança)
        self.senha = senha
        self.historico_compras = []
    
    def autenticar(self, senha_input):
        # BUG 1: Comparação direta de senha sem hash
        return self.senha == senha_input

class ItemVenda:
    def __init__(self, produto, quantidade):
        self.produto = produto
        self.quantidade = quantidade
        self.subtotal = self.calcular_subtotal()
    
    def calcular_subtotal(self):
        return self.produto.preco * self.quantidade

class Venda:
    def __init__(self, cliente):
        self.cliente = cliente
        self.itens = []
        self.data_venda = datetime.datetime.now()
        self.total = 0
        self.desconto = 0
    
    def adicionar_item(self, produto, quantidade):
        # BUG 2: Não verifica se há estoque suficiente antes de adicionar
        item = ItemVenda(produto, quantidade)
        self.itens.append(item)
        # BUG 2: Atualiza estoque imediatamente, mesmo antes de finalizar venda
        produto.estoque -= quantidade
        self.calcular_total()
    
    def calcular_total(self):
        self.total = 0
        for item in self.itens:
            self.total += item.subtotal
        
        # Aplicar desconto
        self.total -= self.desconto
    
    def aplicar_desconto(self, percentual):
        # BUG 3: Não valida se o percentual é válido (0-100)
        self.desconto = (self.total * percentual) / 100
        self.calcular_total()

class SistemaVendas:
    def __init__(self):
        self.produtos = []
        self.clientes = []
        self.vendas = []
        self.carregar_dados()
    
    def carregar_dados(self):
        # Dados de exemplo
        self.produtos = [
            Produto(1, "Notebook Dell", 2500.00, 10),
            Produto(2, "Mouse Logitech", 50.00, 25),
            Produto(3, "Teclado Mecânico", 200.00, 15),
            Produto(4, "Monitor 24''", 800.00, 8)
        ]
        
        self.clientes = [
            Cliente(1, "João Silva", "joao@email.com", "123456"),
            Cliente(2, "Maria Santos", "maria@email.com", "password"),
            Cliente(3, "Pedro Oliveira", "pedro@email.com", "qwerty")
        ]
    
    def buscar_produto_por_id(self, id_produto):
        for produto in self.produtos:
            if produto.id_produto == id_produto:
                return produto
        return None
    
    def buscar_cliente_por_id(self, id_cliente):
        for cliente in self.clientes:
            if cliente.id_cliente == id_cliente:
                return cliente
        return None
    
    def autenticar_cliente(self, email, senha):
        for cliente in self.clientes:
            if cliente.email == email and cliente.autenticar(senha):
                return cliente
        return None
    
    def processar_venda(self, cliente, itens_pedido):
        """
        itens_pedido: lista de dicionários com 'id_produto' e 'quantidade'
        """
        venda = Venda(cliente)
        
        for item_pedido in itens_pedido:
            produto = self.buscar_produto_por_id(item_pedido['id_produto'])
            if produto:
                venda.adicionar_item(produto, item_pedido['quantidade'])
        
        self.vendas.append(venda)
        cliente.historico_compras.append(venda)
        
        return venda
    
    def relatorio_estoque_baixo(self, limite=5):
        """Produtos com estoque abaixo do limite"""
        produtos_baixo_estoque = []
        for produto in self.produtos:
            if produto.estoque < limite:
                produtos_baixo_estoque.append(produto)
        return produtos_baixo_estoque
    
    def salvar_venda_arquivo(self, venda, nome_arquivo):
        """Salva venda em arquivo JSON"""
        try:
            dados_venda = {
                'cliente': venda.cliente.nome,
                'email': venda.cliente.email,
                'data': venda.data_venda.isoformat(),
                'itens': [],
                'total': venda.total
            }
            
            for item in venda.itens:
                dados_venda['itens'].append({
                    'produto': item.produto.nome,
                    'quantidade': item.quantidade,
                    'preco_unitario': item.produto.preco,
                    'subtotal': item.subtotal
                })
            
            with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
                json.dump(dados_venda, arquivo, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Erro ao salvar arquivo: {e}")

def demonstrar_bugs():
    """Função para demonstrar os bugs do sistema"""
    print("=== DEMONSTRAÇÃO DO SISTEMA DE VENDAS COM BUGS ===\n")
    
    sistema = SistemaVendas()
    
    # Demonstrar Bug 1: Vulnerabilidade de segurança
    print("1. VULNERABILIDADE DE SEGURANÇA:")
    print("Senhas armazenadas em texto plano:")
    for cliente in sistema.clientes:
        print(f"Cliente: {cliente.nome}, Senha: {cliente.senha}")
    print()
    
    # Demonstrar Bug 2: Problema de lógica no estoque
    print("2. PROBLEMA DE LÓGICA NO ESTOQUE:")
    notebook = sistema.buscar_produto_por_id(1)
    print(f"Estoque inicial do Notebook: {notebook.estoque}")
    
    cliente = sistema.clientes[0]
    
    # Tentar vender mais do que há em estoque
    pedido = [{'id_produto': 1, 'quantidade': 15}]  # Mais que o estoque de 10
    print(f"Tentando vender 15 notebooks (estoque: {notebook.estoque})")
    
    venda = sistema.processar_venda(cliente, pedido)
    print(f"Estoque após venda: {notebook.estoque}")  # Vai ficar negativo!
    print(f"Total da venda: R${venda.total}")
    print()
    
    # Demonstrar Bug 3: Problema de performance/lógica no desconto
    print("3. PROBLEMA NO DESCONTO:")
    print(f"Total antes do desconto: R${venda.total}")
    venda.aplicar_desconto(150)  # Desconto inválido de 150%
    print(f"Total após desconto de 150%: R${venda.total}")  # Vai ficar negativo!
    print()

if __name__ == "__main__":
    demonstrar_bugs()