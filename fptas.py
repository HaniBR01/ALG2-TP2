def approximate_knapsack(valores, pesos, capacidade):
    epsilon = 0.5
    n = len(valores)
    v_max = max(valores) if valores else 0

    if v_max == 0:
        return 0, []

    mu = (epsilon * v_max) / n

    scaled_valores = [int(v / mu) for v in valores]
    
    max_scaled_value = sum(scaled_valores)

    dp = [float('inf')] * (max_scaled_value + 1)
    dp[0] = 0
    
    item_selection = [[False] * (max_scaled_value + 1) for _ in range(n + 1)]

    for i in range(n):
        for v in range(max_scaled_value, scaled_valores[i] - 1, -1):
            if dp[v - scaled_valores[i]] != float('inf'):
                new_weight = dp[v - scaled_valores[i]] + pesos[i]
                if new_weight < dp[v]:
                    dp[v] = new_weight
                    item_selection[i+1][v] = True


    best_scaled_value = 0
    for v in range(max_scaled_value, -1, -1):
        if dp[v] <= capacidade:
            best_scaled_value = v
            break

    selected_items_indices = []
    total_value = 0
    temp_v = best_scaled_value
    for i in range(n, 0, -1):
        if item_selection[i][temp_v]:
            selected_items_indices.append(i - 1)
            temp_v -= scaled_valores[i-1]

    selected_items_indices.reverse()
    
    for index in selected_items_indices:
        total_value += valores[index]

    return total_value, selected_items_indices

# Exemplo de uso:
if __name__ == '__main__':
    valores = [70, 20, 39, 37, 7, 5, 10]
    pesos = [31, 10, 20, 19, 4, 3, 6]
    capacidade = 50
    epsilon = 0.5

    approx_value, approx_items = approximate_knapsack(valores, pesos, capacidade)

    print(f"Problema da Mochila com FPTAS (epsilon = {epsilon})")
    print("-" * 50)
    print(f"Capacidade da mochila: {capacidade}")
    print(f"Valor total aproximado: {approx_value}")
    print(f"Índices dos itens selecionados: {approx_items}")
    
    selected_pesos = sum(pesos[i] for i in approx_items)
    print(f"Peso total dos itens selecionados: {selected_pesos}")