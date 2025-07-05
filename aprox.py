def knapsack_2_approx_guloso(valor, peso, capacidade):
    """
    Args:
        Uma lista de valores (valor) e uma lista de pesos (peso),
        capacidade (int): A capacidade máxima de peso da mochila.

    Returns:
        Uma tupla contendo o valor total máximo e a lista de itens escolhidos.
        Onde cada elemento da lista é uma tupla contendo (valor, peso, index).
    """

    # --- GULOSA POR DENSIDADE ---

    razao = [(valor[i]/ peso[i],i) for i in range(len(valor))]
    razao.sort(reverse=True)

    valor_guloso = 0
    peso_atual = 0
    itens_gulosos = []

    for item in razao:
        densidade, i = item
        if peso_atual + peso[i] <= capacidade:
            itens_gulosos.append((valor[i], peso[i], i))
            peso_atual += peso[i]
            valor_guloso += valor[i]

    # --- ITEM DE MAIOR VALOR ---

    valor_max = 0
    item_max_valor = None

    for i in range(len(valor)):
        # Verifica se o item cabe e se tem o maior valor até agora
        if peso[i] <= capacidade and valor[i] > valor_max:
            valor_max = valor[i]
            item_max_valor = i

    # --- COMPARAÇÃO E RESULTADO FINAL ---

    # Compara o valor total da solução gulosa com o valor do item único
    if valor_guloso > valor_max:
        return valor_guloso, itens_gulosos
    else:
        return valor_max, [(valor[item_max_valor], peso[item_max_valor], item_max_valor)]

def __main__():
    # --- Exemplo de Uso 1: ---

    print("--- Exemplo 1: Caso onde a densidade vence ---")

    peso = [20,30,50]
    valor = [60,75,110]
    capacidade1 = 50

    valor_final1, itens_finais1 = knapsack_2_approx_guloso(valor,peso, capacidade1)

    print(f"Capacidade da Mochila: {capacidade1}")
    print(f"Valor Final Encontrado: {valor_final1}")
    print(f"Itens Escolhidos: {itens_finais1}\n")

    # --- Exemplo de Uso 2: ---
    print("--- Exemplo 2: Caso onde o item de maior valor vence ---")

    peso2 = [10, 100]
    valor2 = [20, 101]
    capacidade2 = 100

    valor_final2, itens_finais2 = knapsack_2_approx_guloso(valor2,peso2, capacidade2)

    print(f"Capacidade da Mochila: {capacidade2}")
    print(f"Valor Final Encontrado: {valor_final2}")
    print(f"Itens Escolhidos: {itens_finais2}\n")

    # --- Exemplo de Uso 3: ---
    print("--- Exemplo 3: Caso onde a densidade vence ---")

    peso3 = [2, 3, 5]
    valor3 = [100, 120, 150]
    capacidade3 = 6

    valor_final3, itens_finais3 = knapsack_2_approx_guloso(valor3,peso3, capacidade3)

    print(f"Capacidade da Mochila: {capacidade3}")
    print(f"Valor Final Encontrado: {valor_final3}")
    print(f"Itens Escolhidos: {itens_finais3}")

if __name__ == "__main__":
    __main__()