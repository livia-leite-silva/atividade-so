#!/usr/bin/env python3
"""

Pre-requisito: ja ter compilado o binario com
    gcc -O2 -Wall -Wextra -o fork_order fork_order.c

Uso:
    python3 run_analyze.py
"""

import subprocess
import csv
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BINARIO = "./fork_order"
REPETICOES = 200
VALORES_N = [2, 4, 8, 16]
MODOS = [0, 1]


dados = {}
linhas_brutas = [] 

for modo in MODOS:
    for n in VALORES_N:
        chave = (n, modo)
        dados[chave] = [] 

        for repeticao in range(REPETICOES):
            resultado = subprocess.run(
                [BINARIO, str(n), str(modo)],
                capture_output=True,
                text=True
            )
            linha = resultado.stdout.strip()
            linhas_brutas.append(linha)

            partes = linha.split(",")
            bateu = int(partes[4])
            inversoes = int(partes[5])
            dados[chave].append((bateu, inversoes))

        print("Concluido: N =", n, " modo =", modo, " (", REPETICOES, "execucoes)")

# salva os dados brutos em results.csv
with open("results.csv", "w", newline="") as arquivo:
    arquivo.write("n,modo,ordem_criacao,ordem_termino,bateu,inversoes\n")
    for linha in linhas_brutas:
        arquivo.write(linha + "\n")

#  resumo, com loops explicitos 
linhas_resumo = []

for modo in MODOS:
    for n in VALORES_N:
        amostras = dados[(n, modo)]
        total = len(amostras)

        soma_bateu = 0
        soma_inversoes = 0
        for bateu, inversoes in amostras:
            soma_bateu = soma_bateu + bateu
            soma_inversoes = soma_inversoes + inversoes

        pct_bateu = 100.0 * soma_bateu / total
        media_inversoes = soma_inversoes / total
        prob_teorica = 100.0 / math.factorial(n)

        print("N =", n, "modo =", modo,
              "| % bateu =", round(pct_bateu, 2),
              "| media inversoes =", round(media_inversoes, 2),
              "| 1/N! teorico =", round(prob_teorica, 4))

        linhas_resumo.append([n, modo, total, round(pct_bateu, 2),
                               round(media_inversoes, 2), round(prob_teorica, 4)])

with open("resumo.csv", "w", newline="") as arquivo:
    escritor = csv.writer(arquivo)
    escritor.writerow(["n", "modo", "execucoes", "pct_bateu", "media_inversoes", "prob_teorica_pct"])
    for linha in linhas_resumo:
        escritor.writerow(linha)

# monta o grafico de barras comparando os dois modos, para cada valor de N
pct_modo0 = []
pct_modo1 = []

for n in VALORES_N:
    amostras0 = dados[(n, 0)]
    soma0 = 0
    for bateu, inversoes in amostras0:
        soma0 = soma0 + bateu
    pct_modo0.append(100.0 * soma0 / len(amostras0))

    amostras1 = dados[(n, 1)]
    soma1 = 0
    for bateu, inversoes in amostras1:
        soma1 = soma1 + bateu
    pct_modo1.append(100.0 * soma1 / len(amostras1))

posicoes = range(len(VALORES_N))
largura = 0.35

fig, eixo = plt.subplots(figsize=(6, 4))
barras0 = eixo.bar([p - largura / 2 for p in posicoes], pct_modo0, largura, label="Modo 0 (sem carga)")
barras1 = eixo.bar([p + largura / 2 for p in posicoes], pct_modo1, largura, label="Modo 1 (carga variável)")
eixo.set_xticks(list(posicoes))
eixo.set_xticklabels([str(n) for n in VALORES_N])
eixo.set_xlabel("N (número de processos filhos)")
eixo.set_ylabel("% de execuções em que a ordem bateu")
eixo.set_title("Ordem de criação vs. ordem de término dos filhos")
eixo.set_ylim(0, 105)  
eixo.legend()

for grupo_de_barras in (barras0, barras1):
    for barra in grupo_de_barras:
        altura = barra.get_height()
        eixo.text(barra.get_x() + barra.get_width() / 2, altura + 1.5,
                   f"{altura:.1f}", ha="center", va="bottom", fontsize=8)

fig.tight_layout()
fig.savefig("grafico_resultados.png", dpi=150)

print("")
print("Resumo salvo em resumo.csv")
print("Dados brutos salvos em results.csv")
print("Grafico salvo em grafico_resultados.png")