from __future__ import annotations

from decimal import Decimal
from typing import Optional

from estoque import (
    Estoque,
    ProdutoJaCadastradoError,
    ProdutoNaoEncontradoError,
    QuantidadeInvalidaError,
    EstoqueInsuficienteError,
)
from protudo import Produto
from venda import Venda


def ler_inteiro(mensagem: str) -> int:
    while True:
        try:
            valor = int(input(mensagem).strip())
            return valor
        except ValueError:
            print("Entrada inválida. Digite um número inteiro.")


def ler_decimal(mensagem: str) -> Decimal:
    while True:
        valor = input(mensagem).strip().replace(",", ".")
        try:
            return Decimal(valor)
        except Exception:
            print("Entrada inválida. Use número (ex.: 10.50).")


def ler_texto(mensagem: str) -> str:
    while True:
        valor = input(mensagem).strip()
        if valor:
            return valor
        print("Campo obrigatório.")


def menu() -> None:
    estoque = Estoque()

    opcoes = {
        "1": "Cadastrar produto",
        "2": "Listar estoque",
        "3": "Repor estoque",
        "4": "Registrar venda",
        "5": "Atualizar preço",
        "0": "Sair",
    }

    while True:
        print("\n=== Sistema de Estoque e Vendas ===")
        for k, v in opcoes.items():
            print(f"{k} - {v}")
        escolha = input("Escolha: ").strip()

        try:
            if escolha == "1":
                codigo = ler_texto("Código: ")
                nome = ler_texto("Nome: ")
                preco = ler_decimal("Preço unitário: ")
                categoria: Optional[str] = input("Categoria (opcional): ").strip() or None
                produto = Produto(codigo=codigo, nome=nome, preco_unitario=preco, categoria=categoria)
                qtd_inicial = ler_inteiro("Quantidade inicial (0 se não houver): ")
                estoque.cadastrar_produto(produto, quantidade_inicial=qtd_inicial)
                print("Produto cadastrado com sucesso.")

            elif escolha == "2":
                itens = estoque.listar()
                if not itens:
                    print("Estoque vazio.")
                else:
                    print("\nCódigo | Nome | Quantidade | Preço")
                    for item in itens:
                        print(
                            f"{item.produto.codigo} | {item.produto.nome} | {item.quantidade} | R$ {item.produto.preco_unitario}"
                        )

            elif escolha == "3":
                codigo = ler_texto("Código do produto: ")
                qtd = ler_inteiro("Quantidade a adicionar: ")
                estoque.adicionar(codigo, qtd)
                print("Estoque atualizado.")

            elif escolha == "4":
                venda = Venda()
                print("Adicionar itens à venda (deixe código vazio para finalizar adição)")
                while True:
                    codigo = input("Código do produto: ").strip()
                    if not codigo:
                        break
                    qtd = ler_inteiro("Quantidade: ")
                    produto = estoque.obter_produto(codigo)
                    venda.adicionar_item(produto, qtd)
                if not venda.itens:
                    print("Nenhum item adicionado. Venda cancelada.")
                else:
                    venda.finalizar(estoque)
                    print(f"Venda {venda.identificador} finalizada. Total: R$ {venda.total}")

            elif escolha == "5":
                codigo = ler_texto("Código do produto: ")
                novo = ler_decimal("Novo preço: ")
                estoque.atualizar_preco(codigo, novo)
                print("Preço atualizado.")

            elif escolha == "0":
                print("Saindo...")
                break

            else:
                print("Opção inválida.")

        except ProdutoJaCadastradoError as e:
            print(f"Erro: {e}")
        except ProdutoNaoEncontradoError as e:
            print(f"Erro: {e}")
        except QuantidadeInvalidaError as e:
            print(f"Erro: {e}")
        except EstoqueInsuficienteError as e:
            print(f"Erro: {e}")
        except Exception as e:
            print(f"Erro inesperado: {e}")


if __name__ == "__main__":
    menu()