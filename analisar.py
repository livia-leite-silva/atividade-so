#!/usr/bin/env python3
"""
analisar.py

Le results.csv (gerado por run_experiments.sh) e produz:
  - tabela resumo (percentual de "bateu" e media de inversoes por N/modo)
  - resumo.csv com os numeros agregados
  - grafico grafico_resultados.png comparando os dois modos
"""

import csv
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import math

dados = defaultdict(list)  # (n, modo) -> lista de (bateu, inversoes)

with open("results.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        n = int(row["n"])
        modo = int(row["modo"])
        bateu = int(row["bateu"])
        inversoes = int(row["inversoes"])
        dados[(n, modo)].append((bateu, inversoes))

linhas_resumo = []
print(f"{'N':>3} {'modo':>5} {'execucoes':>10} {'%bateu':>8} {'media_inversoes':>17} {'1/N! teorico':>14}")
for (n, modo) in sorted(dados.keys()):
    amostras = dados[(n, modo)]
    total = len(amostras)
    pct_bateu = 100.0 * sum(b for b, _ in amostras) / total
    media_inv = sum(i for _, i in amostras) / total
    prob_teorica = 100.0 / math.factorial(n)
    print(f"{n:>3} {modo:>5} {total:>10} {pct_bateu:>7.2f}% {media_inv:>17.2f} {prob_teorica:>13.4f}%")
    linhas_resumo.append([n, modo, total, round(pct_bateu, 2), round(media_inv, 2), round(prob_teorica, 4)])

with open("resumo.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["n", "modo", "execucoes", "pct_bateu", "media_inversoes", "prob_teorica_pct"])
    w.writerows(linhas_resumo)

# --- Grafico: % de execucoes em que a ordem bateu, por N, separado por modo ---
ns = sorted(set(n for (n, _m) in dados.keys()))
pct_modo0 = [100.0 * sum(b for b, _ in dados[(n, 0)]) / len(dados[(n, 0)]) for n in ns]
pct_modo1 = [100.0 * sum(b for b, _ in dados[(n, 1)]) / len(dados[(n, 1)]) for n in ns]

x = range(len(ns))
width = 0.35
fig, ax = plt.subplots(figsize=(6, 4))
ax.bar([i - width/2 for i in x], pct_modo0, width, label="Modo 0 (sem carga)")
ax.bar([i + width/2 for i in x], pct_modo1, width, label="Modo 1 (carga variavel)")
ax.set_xticks(list(x))
ax.set_xticklabels([str(n) for n in ns])
ax.set_xlabel("N (numero de processos filhos)")
ax.set_ylabel("% de execucoes em que a ordem de termino\nbateu com a ordem de criacao")
ax.set_title("Ordem de criacao vs. ordem de termino dos filhos")
ax.legend()
fig.tight_layout()
fig.savefig("grafico_resultados.png", dpi=150)
print("\nGrafico salvo em grafico_resultados.png")
print("Resumo salvo em resumo.csv")