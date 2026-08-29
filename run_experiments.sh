#!/bin/bash
# run_experiments.sh
# Executa fork_order repetidamente para varias combinacoes de N e modo,
# salvando todos os resultados em results.csv

set -e
cd "$(dirname "$0")"

BIN=./fork_order
OUT=results.csv
REPETICOES=200          # execucoes por combinacao (N, modo)
VALORES_N="2 4 8 16"
MODOS="0 1"

echo "n,modo,ordem_criacao,ordem_termino,bateu,inversoes" > "$OUT"

total=0
for modo in $MODOS; do
  for n in $VALORES_N; do
    for rep in $(seq 1 $REPETICOES); do
      # seed variando por repeticao para diversidade real no modo 1
      seed=$((RANDOM * RANDOM + rep))
      "$BIN" "$n" "$modo" "$seed" >> "$OUT"
      total=$((total + 1))
    done
    echo "Concluido: N=$n modo=$modo ($REPETICOES execucoes)" >&2
  done
done

echo "Total de execucoes: $total" >&2
echo "Resultados salvos em $OUT" >&2