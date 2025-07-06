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
    subdirs = ["large_scale", "low-dimensional"]

    for subdir in subdirs:
        pasta = os.path.join(base_dir, subdir)
        log_dir = os.path.join("results", "fptas")
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, f"fptas_results_{subdir}.csv")
        with open(log_path, "w", encoding="utf-8") as log_file:
            log_file.write(";optimal_profit;approximate_profit;selected_items;time_taken\n")
            for nome_arquivo in os.listdir(pasta):
                caminho_arquivo = os.path.join(pasta, nome_arquivo)
                caminho_otimo = os.path.join(base_dir, subdir + "-optimum", nome_arquivo)
                if os.path.isfile(caminho_arquivo):
                    ignorar_ultima = (subdir == "large_scale")
                    try:
                        n, capacidade, valores, pesos, otimo = ler_instancia(
                            caminho_arquivo, caminho_otimo, ignorar_ultima_linha=ignorar_ultima
                        )
                        inicio = time.time()
                        valor_aprox, itens_aprox = approximate_knapsack(valores, pesos, capacidade)
                        fim = time.time()
                        tempo = fim - inicio
                        print(f"Arquivo: {nome_arquivo}")
                        print(f"  Valor ótimo: {otimo}")
                        print(f"  Valor aproximado: {valor_aprox}")
                        print(f"  Diferença: {otimo - valor_aprox}")
                        print(f"  Tempo gasto: {tempo:.4f} segundos")
                        print("-" * 40)
                        # Escreve no log com o novo cabeçalho
                        log_file.write(f"{nome_arquivo};{otimo};{valor_aprox};{itens_aprox};{tempo}\n")
                    except Exception as e:
                        print(f"Erro ao processar '{nome_arquivo}': {e}")