# Ordem de criação vs. ordem de término de processos filhos (fork/wait)

Experimento para investigar a hipótese:

> A ordem em que processos filhos são criados (via `fork()` sequencial)
> determina a ordem em que eles são executados e terminam, de modo que
> `wait()` os devolve ao pai na mesma ordem em que foram criados.

## Como reproduzir

Pré-requisitos: `gcc`, `python3`, `matplotlib` (`pip install matplotlib`).

```bash
gcc -O2 -Wall -Wextra -o fork_order fork_order.c
python3 run_analyze.py           # gera resultados, resumo.csv e grafico_resultados.png
```