import os
import time
from fptas import approximate_knapsack

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
        log_dir = os.path.join("results", "fptas")
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, f"fptas_results_{subdir}.csv")
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
                    if n >= 5000:
                        print(f"Arquivo '{nome_arquivo}' ignorado: mais de 5000 entradas (n={n})")
                        continue
                    print(f"arquivo: {nome_arquivo}")
                    inicio = time.time()
                    valor_aprox, itens_aprox = approximate_knapsack(valores, pesos, capacidade)
                    fim = time.time()
                    tempo = fim - inicio
                    resultados.append(f"{nome_arquivo};{otimo};{valor_aprox};{itens_aprox};{tempo}\n")
                    print(f"Arquivo '{nome_arquivo}' processado: Valor ótimo = {otimo}, Valor aproximado = {valor_aprox}, Tempo = {tempo:.6f} segundos")
                except Exception as e:
                    print(f"Erro ao processar '{nome_arquivo}': {e}")
        # Escreve todos os resultados de uma vez ao final
        with open(log_path, "w", encoding="utf-8") as log_file:
            log_file.write(";optimal_profit;approximate_profit;selected_items;time_taken\n")
            log_file.writelines(resultados)