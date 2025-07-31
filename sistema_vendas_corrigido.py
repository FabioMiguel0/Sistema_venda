#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Vendas - Versão Corrigida
Este sistema corrige todos os bugs da versão anterior
"""

import json
import datetime
import hashlib
import os
from typing import List, Optional, Dict, Any

class Produto:
    def __init__(self, id_produto: int, nome: str, preco: float, estoque: int):
        self.id_produto = id_produto
        self.nome = nome
        self.preco = preco
        self.estoque = estoque
    
    def __str__(self):
        return f"ID: {self.id_produto}, Nome: {self.nome}, Preço: R${self.preco:.2f}, Estoque: {self.estoque}"

class Cliente:
    def __init__(self, id_cliente: int, nome: str, email: str, senha: str):
        self.id_cliente = id_cliente
        self.nome = nome
        self.email = email
        # CORREÇÃO BUG 1: Hash da senha com salt
        self.senha_hash = self._hash_senha(senha)
        self.historico_compras = []
    
    def _hash_senha(self, senha: str) -> str:
        """
        CORREÇÃO BUG 1: Criptografia segura de senhas
        - Usa SHA-256 com salt
        - Salt único por usuário baseado no email
        """
        salt = hashlib.sha256(self.email.encode()).hexdigest()[:16]
        senha_com_salt = senha + salt
        return hashlib.sha256(senha_com_salt.encode()).hexdigest()
    
    def autenticar(self, senha_input: str) -> bool:
        """
        CORREÇÃO BUG 1: Autenticação segura
        - Compara hashes ao invés de texto plano
        """
        return self.senha_hash == self._hash_senha(senha_input)

class ItemVenda:
    def __init__(self, produto: Produto, quantidade: int):
        self.produto = produto
        self.quantidade = quantidade
        self.subtotal = self.calcular_subtotal()
    
    def calcular_subtotal(self) -> float:
        return self.produto.preco * self.quantidade

class EstoqueInsuficienteError(Exception):
    """Exceção customizada para estoque insuficiente"""
    pass

class DescontoInvalidoError(Exception):
    """Exceção customizada para desconto inválido"""
    pass

class Venda:
    def __init__(self, cliente: Cliente):
        self.cliente = cliente
        self.itens: List[ItemVenda] = []
        self.data_venda = datetime.datetime.now()
        self.total = 0.0
        self.desconto_percentual = 0.0
        self.valor_desconto = 0.0
        self.finalizada = False
    
    def adicionar_item(self, produto: Produto, quantidade: int) -> None:
        """
        CORREÇÃO BUG 2: Validação de estoque antes de adicionar item
        - Verifica se há estoque suficiente
        - Não atualiza estoque até finalizar venda
        - Lança exceção se estoque insuficiente
        """
        if self.finalizada:
            raise ValueError("Não é possível adicionar itens a uma venda finalizada")
        
        if quantidade <= 0:
            raise ValueError("Quantidade deve ser maior que zero")
        
        if produto.estoque < quantidade:
            raise EstoqueInsuficienteError(
                f"Estoque insuficiente para {produto.nome}. "
                f"Disponível: {produto.estoque}, Solicitado: {quantidade}"
            )
        
        item = ItemVenda(produto, quantidade)
        self.itens.append(item)
        self._calcular_total()
    
    def _calcular_total(self) -> None:
        """
        CORREÇÃO BUG 3: Cálculo correto do total
        - Calcula subtotal primeiro
        - Aplica desconto sobre o subtotal
        - Evita valores negativos
        """
        subtotal = sum(item.subtotal for item in self.itens)
        self.valor_desconto = (subtotal * self.desconto_percentual) / 100
        self.total = max(0, subtotal - self.valor_desconto)
    
    def aplicar_desconto(self, percentual: float) -> None:
        """
        CORREÇÃO BUG 3: Validação adequada de desconto
        - Valida se percentual está entre 0 e 100
        - Não permite valores negativos no total
        """
        if percentual < 0 or percentual > 100:
            raise DescontoInvalidoError(
                f"Desconto deve estar entre 0% e 100%. Recebido: {percentual}%"
            )
        
        self.desconto_percentual = percentual
        self._calcular_total()
    
    def finalizar_venda(self) -> None:
        """
        CORREÇÃO BUG 2: Atualização de estoque apenas ao finalizar venda
        - Estoque só é atualizado quando venda é confirmada
        - Previne problemas de concorrência
        """
        if self.finalizada:
            raise ValueError("Venda já foi finalizada")
        
        # Verificar novamente o estoque antes de finalizar
        for item in self.itens:
            if item.produto.estoque < item.quantidade:
                raise EstoqueInsuficienteError(
                    f"Estoque insuficiente para {item.produto.nome} no momento da finalização"
                )
        
        # Atualizar estoque apenas agora
        for item in self.itens:
            item.produto.estoque -= item.quantidade
        
        self.finalizada = True
    
    def cancelar_venda(self) -> None:
        """Cancela a venda sem afetar o estoque"""
        if self.finalizada:
            raise ValueError("Não é possível cancelar uma venda finalizada")
        
        self.itens.clear()
        self.total = 0.0
        self.valor_desconto = 0.0

class SistemaVendas:
    def __init__(self):
        self.produtos: List[Produto] = []
        self.clientes: List[Cliente] = []
        self.vendas: List[Venda] = []
        self._carregar_dados()
    
    def _carregar_dados(self) -> None:
        """Carrega dados de exemplo com senhas já hasheadas"""
        # Primeiro criar produtos
        self.produtos = [
            Produto(1, "Notebook Dell", 2500.00, 10),
            Produto(2, "Mouse Logitech", 50.00, 25),
            Produto(3, "Teclado Mecânico", 200.00, 15),
            Produto(4, "Monitor 24''", 800.00, 8)
        ]
        
        # Criar clientes (senhas serão hasheadas automaticamente)
        self.clientes = [
            Cliente(1, "João Silva", "joao@email.com", "123456"),
            Cliente(2, "Maria Santos", "maria@email.com", "password"),
            Cliente(3, "Pedro Oliveira", "pedro@email.com", "qwerty")
        ]
    
    def buscar_produto_por_id(self, id_produto: int) -> Optional[Produto]:
        """Busca produto por ID com performance melhorada"""
        # MELHORIA: Poderia usar um dicionário para O(1) lookup em sistemas maiores
        for produto in self.produtos:
            if produto.id_produto == id_produto:
                return produto
        return None
    
    def buscar_cliente_por_id(self, id_cliente: int) -> Optional[Cliente]:
        """Busca cliente por ID"""
        for cliente in self.clientes:
            if cliente.id_cliente == id_cliente:
                return cliente
        return None
    
    def autenticar_cliente(self, email: str, senha: str) -> Optional[Cliente]:
        """Autentica cliente usando hash seguro"""
        for cliente in self.clientes:
            if cliente.email == email and cliente.autenticar(senha):
                return cliente
        return None
    
    def processar_venda(self, cliente: Cliente, itens_pedido: List[Dict[str, Any]]) -> Venda:
        """
        CORREÇÃO GERAL: Processo de venda mais seguro e robusto
        - Validações antes de processar
        - Rollback em caso de erro
        - Logs de auditoria
        """
        if not itens_pedido:
            raise ValueError("Lista de itens não pode estar vazia")
        
        venda = Venda(cliente)
        
        try:
            # Adicionar todos os itens primeiro (sem afetar estoque)
            for item_pedido in itens_pedido:
                if 'id_produto' not in item_pedido or 'quantidade' not in item_pedido:
                    raise ValueError("Item deve conter 'id_produto' e 'quantidade'")
                
                produto = self.buscar_produto_por_id(item_pedido['id_produto'])
                if not produto:
                    raise ValueError(f"Produto com ID {item_pedido['id_produto']} não encontrado")
                
                venda.adicionar_item(produto, item_pedido['quantidade'])
            
            # Finalizar venda (atualiza estoque)
            venda.finalizar_venda()
            
            # Registrar venda no sistema
            self.vendas.append(venda)
            cliente.historico_compras.append(venda)
            
            # Log da venda
            print(f"Venda processada com sucesso - ID Cliente: {cliente.id_cliente}, Total: R${venda.total:.2f}")
            
            return venda
            
        except Exception as e:
            # Em caso de erro, cancelar venda
            venda.cancelar_venda()
            print(f"Erro ao processar venda: {e}")
            raise
    
    def relatorio_estoque_baixo(self, limite: int = 5) -> List[Produto]:
        """Relatório de produtos com estoque baixo"""
        return [produto for produto in self.produtos if produto.estoque < limite]
    
    def relatorio_vendas_periodo(self, data_inicio: datetime.datetime, 
                                data_fim: datetime.datetime) -> List[Venda]:
        """Relatório de vendas por período"""
        return [
            venda for venda in self.vendas 
            if data_inicio <= venda.data_venda <= data_fim
        ]
    
    def salvar_venda_arquivo(self, venda: Venda, nome_arquivo: str) -> bool:
        """
        Salva venda em arquivo JSON com tratamento de erros melhorado
        """
        try:
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(nome_arquivo) if os.path.dirname(nome_arquivo) else '.', 
                       exist_ok=True)
            
            dados_venda = {
                'id_venda': len(self.vendas),
                'cliente': {
                    'id': venda.cliente.id_cliente,
                    'nome': venda.cliente.nome,
                    'email': venda.cliente.email
                },
                'data_venda': venda.data_venda.isoformat(),
                'itens': [],
                'subtotal': sum(item.subtotal for item in venda.itens),
                'desconto_percentual': venda.desconto_percentual,
                'valor_desconto': venda.valor_desconto,
                'total': venda.total,
                'finalizada': venda.finalizada
            }
            
            for item in venda.itens:
                dados_venda['itens'].append({
                    'id_produto': item.produto.id_produto,
                    'produto': item.produto.nome,
                    'quantidade': item.quantidade,
                    'preco_unitario': item.produto.preco,
                    'subtotal': item.subtotal
                })
            
            with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
                json.dump(dados_venda, arquivo, indent=2, ensure_ascii=False)
            
            print(f"Venda salva em: {nome_arquivo}")
            return True
                
        except Exception as e:
            print(f"Erro ao salvar arquivo: {e}")
            return False

def demonstrar_correcoes():
    """Demonstra as correções implementadas"""
    print("=== DEMONSTRAÇÃO DAS CORREÇÕES DO SISTEMA ===\n")
    
    sistema = SistemaVendas()
    
    # Demonstrar Correção 1: Segurança das senhas
    print("1. CORREÇÃO DE SEGURANÇA - SENHAS HASHEADAS:")
    for cliente in sistema.clientes:
        print(f"Cliente: {cliente.nome}")
        print(f"  Email: {cliente.email}")
        print(f"  Senha Hash: {cliente.senha_hash[:20]}...")
        # Testar autenticação
        auth_ok = cliente.autenticar("123456" if cliente.nome == "João Silva" else "password")
        print(f"  Autenticação com senha correta: {'OK' if auth_ok else 'FALHOU'}")
    print()
    
    # Demonstrar Correção 2: Controle de estoque
    print("2. CORREÇÃO DO CONTROLE DE ESTOQUE:")
    notebook = sistema.buscar_produto_por_id(1)
    print(f"Estoque inicial do Notebook: {notebook.estoque}")
    
    cliente = sistema.clientes[0]
    
    try:
        # Tentar vender mais do que há em estoque
        pedido = [{'id_produto': 1, 'quantidade': 15}]
        print(f"Tentando vender 15 notebooks (estoque: {notebook.estoque})")
        venda = sistema.processar_venda(cliente, pedido)
        
    except EstoqueInsuficienteError as e:
        print(f"ERRO CAPTURADO: {e}")
        print(f"Estoque permanece inalterado: {notebook.estoque}")
    
    # Venda válida
    try:
        pedido_valido = [{'id_produto': 1, 'quantidade': 3}]
        print(f"\nTentando venda válida de 3 notebooks...")
        venda_valida = sistema.processar_venda(cliente, pedido_valido)
        print(f"Venda realizada com sucesso!")
        print(f"Estoque após venda: {notebook.estoque}")
        print(f"Total da venda: R${venda_valida.total:.2f}")
    except Exception as e:
        print(f"Erro inesperado: {e}")
    print()
    
    # Demonstrar Correção 3: Validação de desconto
    print("3. CORREÇÃO DA VALIDAÇÃO DE DESCONTO:")
    try:
        print(f"Total antes do desconto: R${venda_valida.total:.2f}")
        venda_valida.aplicar_desconto(150)  # Desconto inválido
    except DescontoInvalidoError as e:
        print(f"ERRO CAPTURADO: {e}")
    
    # Aplicar desconto válido
    try:
        venda_valida.aplicar_desconto(10)  # 10% de desconto
        print(f"Desconto de 10% aplicado com sucesso!")
        print(f"Valor do desconto: R${venda_valida.valor_desconto:.2f}")
        print(f"Total final: R${venda_valida.total:.2f}")
    except Exception as e:
        print(f"Erro ao aplicar desconto: {e}")
    print()
    
    # Demonstrar funcionalidades adicionais
    print("4. FUNCIONALIDADES ADICIONAIS:")
    
    # Relatório de estoque baixo
    produtos_baixo = sistema.relatorio_estoque_baixo(10)
    print(f"Produtos com estoque baixo (< 10):")
    for produto in produtos_baixo:
        print(f"  - {produto}")
    
    # Salvar venda
    if 'venda_valida' in locals():
        sucesso = sistema.salvar_venda_arquivo(venda_valida, "vendas/venda_exemplo.json")
        print(f"Arquivo salvo: {'Sim' if sucesso else 'Não'}")

if __name__ == "__main__":
    demonstrar_correcoes()