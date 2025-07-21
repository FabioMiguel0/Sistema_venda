# main.py
from backend.funcoes import registar_produto, registar_operador, realizar_venda, gerar_fatura

# Exemplo de uso:
registar_produto("Teclado", 20000, "Teclado mecânico gamer", 10)
registar_operador("admin", "1234")

# Fazer uma venda e gerar fatura
venda = realizar_venda(1, 2, 20000)
gerar_fatura(venda.id)
