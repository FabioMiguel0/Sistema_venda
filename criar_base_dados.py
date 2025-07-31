#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar e inicializar a base de dados do Sistema de Vendas
"""

import sqlite3
import hashlib
from datetime import datetime, date
import os

def criar_hash_senha(senha):
    """Criar hash da senha usando SHA-256"""
    return hashlib.sha256(senha.encode()).hexdigest()

def criar_base_dados():
    """Criar a base de dados e todas as tabelas"""
    
    # Conectar à base de dados (será criada se não existir)
    conn = sqlite3.connect('sistema_vendas.db')
    cursor = conn.cursor()
    
    print("Criando estrutura da base de dados...")
    
    # Tabela de Categorias
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome VARCHAR(100) NOT NULL UNIQUE,
        descricao TEXT,
        ativo BOOLEAN DEFAULT 1,
        data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Tabela de Utilizadores/Funcionários
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS utilizadores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome VARCHAR(150) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        senha VARCHAR(255) NOT NULL,
        tipo_utilizador VARCHAR(20) DEFAULT 'vendedor',
        ativo BOOLEAN DEFAULT 1,
        data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
        ultimo_login DATETIME
    )
    ''')
    
    # Tabela de Clientes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome VARCHAR(150) NOT NULL,
        email VARCHAR(100),
        telefone VARCHAR(20),
        nif VARCHAR(20),
        endereco TEXT,
        cidade VARCHAR(100),
        codigo_postal VARCHAR(10),
        data_nascimento DATE,
        ativo BOOLEAN DEFAULT 1,
        data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Tabela de Fornecedores
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fornecedores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome VARCHAR(150) NOT NULL,
        email VARCHAR(100),
        telefone VARCHAR(20),
        nif VARCHAR(20),
        endereco TEXT,
        cidade VARCHAR(100),
        codigo_postal VARCHAR(10),
        contacto_principal VARCHAR(100),
        ativo BOOLEAN DEFAULT 1,
        data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Tabela de Produtos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome VARCHAR(150) NOT NULL,
        descricao TEXT,
        categoria_id INTEGER,
        fornecedor_id INTEGER,
        codigo_barras VARCHAR(50),
        preco_compra DECIMAL(10,2),
        preco_venda DECIMAL(10,2) NOT NULL,
        margem_lucro DECIMAL(5,2),
        stock_atual INTEGER DEFAULT 0,
        stock_minimo INTEGER DEFAULT 0,
        unidade VARCHAR(20) DEFAULT 'unidade',
        ativo BOOLEAN DEFAULT 1,
        data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (categoria_id) REFERENCES categorias(id),
        FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id)
    )
    ''')
    
    # Tabela de Vendas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_venda VARCHAR(20) UNIQUE NOT NULL,
        cliente_id INTEGER,
        utilizador_id INTEGER NOT NULL,
        data_venda DATETIME DEFAULT CURRENT_TIMESTAMP,
        subtotal DECIMAL(10,2) NOT NULL,
        desconto DECIMAL(10,2) DEFAULT 0,
        iva DECIMAL(10,2) DEFAULT 0,
        total DECIMAL(10,2) NOT NULL,
        metodo_pagamento VARCHAR(50),
        estado VARCHAR(20) DEFAULT 'finalizada',
        observacoes TEXT,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id),
        FOREIGN KEY (utilizador_id) REFERENCES utilizadores(id)
    )
    ''')
    
    # Tabela de Itens de Venda
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS itens_venda (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venda_id INTEGER NOT NULL,
        produto_id INTEGER NOT NULL,
        quantidade INTEGER NOT NULL,
        preco_unitario DECIMAL(10,2) NOT NULL,
        desconto_item DECIMAL(10,2) DEFAULT 0,
        subtotal DECIMAL(10,2) NOT NULL,
        FOREIGN KEY (venda_id) REFERENCES vendas(id) ON DELETE CASCADE,
        FOREIGN KEY (produto_id) REFERENCES produtos(id)
    )
    ''')
    
    # Tabela de Movimentos de Stock
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS movimentos_stock (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER NOT NULL,
        tipo_movimento VARCHAR(20) NOT NULL,
        quantidade INTEGER NOT NULL,
        motivo VARCHAR(100),
        utilizador_id INTEGER,
        data_movimento DATETIME DEFAULT CURRENT_TIMESTAMP,
        observacoes TEXT,
        FOREIGN KEY (produto_id) REFERENCES produtos(id),
        FOREIGN KEY (utilizador_id) REFERENCES utilizadores(id)
    )
    ''')
    
    # Tabela de Configurações
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS configuracoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chave VARCHAR(100) UNIQUE NOT NULL,
        valor TEXT,
        descricao TEXT,
        data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    print("Criando índices...")
    
    # Índices para melhor performance
    indices = [
        "CREATE INDEX IF NOT EXISTS idx_produtos_categoria ON produtos(categoria_id)",
        "CREATE INDEX IF NOT EXISTS idx_produtos_fornecedor ON produtos(fornecedor_id)",
        "CREATE INDEX IF NOT EXISTS idx_vendas_cliente ON vendas(cliente_id)",
        "CREATE INDEX IF NOT EXISTS idx_vendas_utilizador ON vendas(utilizador_id)",
        "CREATE INDEX IF NOT EXISTS idx_vendas_data ON vendas(data_venda)",
        "CREATE INDEX IF NOT EXISTS idx_itens_venda ON itens_venda(venda_id)",
        "CREATE INDEX IF NOT EXISTS idx_itens_produto ON itens_venda(produto_id)",
        "CREATE INDEX IF NOT EXISTS idx_movimentos_produto ON movimentos_stock(produto_id)"
    ]
    
    for indice in indices:
        cursor.execute(indice)
    
    print("Criando triggers...")
    
    # Trigger para atualizar stock automaticamente na venda
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS atualizar_stock_venda
    AFTER INSERT ON itens_venda
    BEGIN
        UPDATE produtos 
        SET stock_atual = stock_atual - NEW.quantidade
        WHERE id = NEW.produto_id;
        
        INSERT INTO movimentos_stock (produto_id, tipo_movimento, quantidade, motivo)
        VALUES (NEW.produto_id, 'saida', NEW.quantidade, 
                'Venda #' || (SELECT numero_venda FROM vendas WHERE id = NEW.venda_id));
    END
    ''')
    
    # Trigger para reverter stock no cancelamento
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS reverter_stock_cancelamento
    AFTER DELETE ON itens_venda
    BEGIN
        UPDATE produtos 
        SET stock_atual = stock_atual + OLD.quantidade
        WHERE id = OLD.produto_id;
        
        INSERT INTO movimentos_stock (produto_id, tipo_movimento, quantidade, motivo)
        VALUES (OLD.produto_id, 'entrada', OLD.quantidade, 'Cancelamento de venda');
    END
    ''')
    
    conn.commit()
    return conn, cursor

def inserir_dados_exemplo(cursor):
    """Inserir dados de exemplo para testar o sistema"""
    
    print("Inserindo dados de exemplo...")
    
    # Categorias
    categorias = [
        ('Electrónicos', 'Produtos electrónicos e tecnologia'),
        ('Roupas', 'Vestuário e acessórios'),
        ('Casa e Jardim', 'Produtos para casa e jardim'),
        ('Alimentação', 'Produtos alimentares'),
        ('Saúde e Beleza', 'Produtos de saúde e beleza'),
        ('Desporto', 'Artigos desportivos'),
        ('Livros', 'Livros e material educativo'),
        ('Brinquedos', 'Brinquedos e jogos')
    ]
    
    cursor.executemany(
        "INSERT OR IGNORE INTO categorias (nome, descricao) VALUES (?, ?)",
        categorias
    )
    
    # Utilizadores
    utilizadores = [
        ('Admin Sistema', 'admin@sistema.pt', criar_hash_senha('admin123'), 'admin'),
        ('João Silva', 'joao.silva@sistema.pt', criar_hash_senha('joao123'), 'vendedor'),
        ('Maria Santos', 'maria.santos@sistema.pt', criar_hash_senha('maria123'), 'vendedor'),
        ('Pedro Costa', 'pedro.costa@sistema.pt', criar_hash_senha('pedro123'), 'caixa'),
        ('Ana Pereira', 'ana.pereira@sistema.pt', criar_hash_senha('ana123'), 'vendedor')
    ]
    
    cursor.executemany(
        "INSERT OR IGNORE INTO utilizadores (nome, email, senha, tipo_utilizador) VALUES (?, ?, ?, ?)",
        utilizadores
    )
    
    # Fornecedores
    fornecedores = [
        ('TechDistrib Lda', 'vendas@techdistrib.pt', '123456789', '123456789', 
         'Rua da Tecnologia, 123', 'Lisboa', '1000-001', 'Carlos Mendes'),
        ('Moda & Estilo', 'comercial@modaestilo.pt', '987654321', '987654321',
         'Av. da Moda, 456', 'Porto', '4000-002', 'Sofia Rodrigues'),
        ('Casa Confort', 'info@casaconfort.pt', '555666777', '555666777',
         'Rua do Lar, 789', 'Coimbra', '3000-003', 'Miguel Ferreira'),
        ('Alimentar Plus', 'vendas@alimentarplus.pt', '111222333', '111222333',
         'Estrada dos Alimentos, 321', 'Braga', '4700-004', 'Rita Sousa')
    ]
    
    cursor.executemany(
        """INSERT OR IGNORE INTO fornecedores 
           (nome, email, telefone, nif, endereco, cidade, codigo_postal, contacto_principal) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        fornecedores
    )
    
    # Clientes
    clientes = [
        ('Cliente Geral', None, None, None, None, None, None, None),
        ('António Ferreira', 'antonio@email.pt', '912345678', '123456789',
         'Rua das Flores, 12', 'Lisboa', '1200-001', '1980-05-15'),
        ('Catarina Lopes', 'catarina@email.pt', '923456789', '234567890',
         'Av. Central, 34', 'Porto', '4100-002', '1985-08-22'),
        ('Rui Tavares', 'rui@email.pt', '934567890', '345678901',
         'Praça da República, 56', 'Coimbra', '3000-003', '1975-12-03'),
        ('Susana Martins', 'susana@email.pt', '945678901', '456789012',
         'Rua Nova, 78', 'Faro', '8000-004', '1990-03-18')
    ]
    
    cursor.executemany(
        """INSERT OR IGNORE INTO clientes 
           (nome, email, telefone, nif, endereco, cidade, codigo_postal, data_nascimento) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        clientes
    )
    
    # Produtos
    produtos = [
        # Electrónicos
        ('Smartphone Samsung A54', 'Smartphone Android com 128GB', 1, 1, '8806094667394', 250.00, 349.99, 39.99, 15, 5, 'unidade'),
        ('Laptop HP Pavilion', 'Laptop 15.6" Intel i5, 8GB RAM, 512GB SSD', 1, 1, '194850123456', 450.00, 649.99, 44.44, 8, 2, 'unidade'),
        ('Auriculares Bluetooth', 'Auriculares sem fios com cancelamento de ruído', 1, 1, '123456789012', 35.00, 59.99, 71.40, 25, 10, 'unidade'),
        
        # Roupas
        ('T-shirt Algodão M', 'T-shirt 100% algodão, tamanho M', 2, 2, '234567890123', 8.00, 19.99, 149.88, 50, 20, 'unidade'),
        ('Calças de Ganga 32', 'Calças de ganga azul, tamanho 32', 2, 2, '345678901234', 25.00, 49.99, 99.96, 30, 10, 'unidade'),
        ('Sapatos Desportivos 42', 'Ténis para corrida, tamanho 42', 2, 2, '456789012345', 40.00, 79.99, 99.98, 20, 5, 'par'),
        
        # Casa e Jardim
        ('Aspirador Robot', 'Aspirador automático com mapeamento', 3, 3, '567890123456', 180.00, 299.99, 66.66, 5, 2, 'unidade'),
        ('Conjunto de Panelas', 'Set de 5 panelas antiaderentes', 3, 3, '678901234567', 45.00, 89.99, 99.98, 12, 5, 'conjunto'),
        
        # Alimentação
        ('Azeite Extra Virgem 500ml', 'Azeite português premium', 4, 4, '789012345678', 4.50, 8.99, 99.78, 100, 20, 'garrafa'),
        ('Café Torrado 1kg', 'Café 100% arábica torrado', 4, 4, '890123456789', 6.00, 12.99, 116.50, 80, 15, 'kg'),
        
        # Saúde e Beleza
        ('Creme Hidratante', 'Creme facial hidratante 50ml', 5, 2, '901234567890', 8.00, 24.99, 212.38, 40, 10, 'unidade'),
        ('Champô Anticaspa', 'Champô tratamento anticaspa 400ml', 5, 2, '012345678901', 5.50, 14.99, 172.55, 60, 15, 'garrafa')
    ]
    
    cursor.executemany(
        """INSERT OR IGNORE INTO produtos 
           (nome, descricao, categoria_id, fornecedor_id, codigo_barras, preco_compra, 
            preco_venda, margem_lucro, stock_atual, stock_minimo, unidade) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        produtos
    )
    
    # Configurações do sistema
    configuracoes = [
        ('empresa_nome', 'Minha Loja Lda', 'Nome da empresa'),
        ('empresa_nif', '123456789', 'NIF da empresa'),
        ('empresa_morada', 'Rua Principal, 123', 'Morada da empresa'),
        ('empresa_telefone', '219876543', 'Telefone da empresa'),
        ('empresa_email', 'info@minhaloja.pt', 'Email da empresa'),
        ('iva_taxa', '23', 'Taxa de IVA padrão (%)'),
        ('moeda', 'EUR', 'Moeda utilizada'),
        ('proximo_numero_venda', '1', 'Próximo número de venda sequencial')
    ]
    
    cursor.executemany(
        "INSERT OR IGNORE INTO configuracoes (chave, valor, descricao) VALUES (?, ?, ?)",
        configuracoes
    )

def main():
    """Função principal"""
    print("=== Criação da Base de Dados do Sistema de Vendas ===")
    print()
    
    # Verificar se já existe base de dados
    if os.path.exists('sistema_vendas.db'):
        resposta = input("A base de dados já existe. Deseja recriar? (s/N): ")
        if resposta.lower() != 's':
            print("Operação cancelada.")
            return
        os.remove('sistema_vendas.db')
    
    try:
        # Criar base de dados
        conn, cursor = criar_base_dados()
        
        # Inserir dados de exemplo
        inserir_dados_exemplo(cursor)
        
        # Commit final
        conn.commit()
        
        print()
        print("✅ Base de dados criada com sucesso!")
        print("📁 Ficheiro: sistema_vendas.db")
        print("📊 Dados de exemplo inseridos")
        print()
        print("Credenciais de acesso:")
        print("👤 Admin: admin@sistema.pt / admin123")
        print("👤 Vendedor: joao.silva@sistema.pt / joao123")
        print()
        
        # Mostrar estatísticas
        cursor.execute("SELECT COUNT(*) FROM categorias")
        print(f"📋 Categorias: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM produtos")
        print(f"📦 Produtos: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM utilizadores")
        print(f"👥 Utilizadores: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM clientes")
        print(f"🏪 Clientes: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM fornecedores")
        print(f"🚚 Fornecedores: {cursor.fetchone()[0]}")
        
    except Exception as e:
        print(f"❌ Erro ao criar base de dados: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()