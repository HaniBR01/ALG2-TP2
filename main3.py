import os
from greedy import knapsack_2_approx_guloso

def ler_instancia(caminho_arquivo, caminho_otimo, ignorar_ultima_linha=False):
    with open(caminho_arquivo, 'r') as f:
        linhas = f.readlines()
        n, capacidade = map(int, linhas[0].strip().split())
        valores = []
        pesos = []
        linhas_itens = linhas[1:-1] if ignorar_ultima_linha else linhas[1:]
        for linha in linhas_itens:
            v, p = map(int, linha.strip().split())
            valores.append(v)
            pesos.append(p)
        with open(caminho_otimo, 'r') as f:
            otimo = int(f.read().strip())
    return n, capacidade, valores, pesos, otimo

if __name__ == "__main__":
    base_dir = "instances_01_KP"
    subdirs = ["low-dimensional", "large_scale"]

    for subdir in subdirs:
        pasta = os.path.join(base_dir, subdir)
        log_dir = os.path.join("results", "greedy")
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, f"greedy_results_{subdir}.csv")
        resultados = []
        for nome_arquivo in os.listdir(pasta):
            caminho_arquivo = os.path.join(pasta, nome_arquivo)
            caminho_otimo = os.path.join(base_dir, subdir + "-optimum", nome_arquivo)
            if os.path.isfile(caminho_arquivo):
                ignorar_ultima = (subdir == "large_scale")
                try:
                    n, capacidade, valores, pesos, otimo = ler_instancia(
                        caminho_arquivo, caminho_otimo, ignorar_ultima_linha=ignorar_ultima
                    )
                    print(f"arquivo: {nome_arquivo}")
                    valor_greedy, itens_greedy = knapsack_2_approx_guloso(valores, pesos, capacidade)
                    itens_indices = [i[2] for i in itens_greedy]
                    resultados.append(f"{nome_arquivo};{otimo};{valor_greedy};{itens_indices}\n")
                    print(f"Arquivo '{nome_arquivo}' processado: Valor ótimo = {otimo}, Valor greedy = {valor_greedy}")
                except Exception as e:
                    print(f"Erro ao processar '{nome_arquivo}': {e}")
        with open(log_path, "w", encoding="utf-8") as log_file:
            log_file.write(";optimal_profit;greedy_profit;selected_items\n")
            log_file.writelines(resultados)