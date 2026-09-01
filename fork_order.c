/*
 * fork_order.c
 *
 * Experimento: a ordem de criacao dos processos filhos (fork sequencial)
 * determina a ordem em que eles terminam e sao colhidos pelo wait()?
 *
 * Uso: ./fork_order <N> <modo> [seed]
 *   N     = numero de processos filhos a criar (2, 4, 8, 16, ...)
 *   modo  = 0 -> filhos terminam imediatamente (sem carga de trabalho)
 *           1 -> filhos executam carga de trabalho variavel antes de terminar
 *   seed  = semente opcional para o gerador de numeros aleatorios (modo 1)
 *
 * Saida (stdout), uma linha por execucao, formato CSV:
 *   N,modo,ordem_criacao,ordem_termino,bateu(0/1),kendall_tau
 *
 * ordem_criacao e ordem_termino sao sequencias dos indices logicos dos
 * filhos (0..N-1), separadas por '-', por exemplo "0-1-2-3".
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <string.h>
#include <time.h>

#define MAX_N 64

/* Carga de trabalho artificial: um loop de calculo cuja duracao varia
 * por filho, para simular processos com tempos de execucao diferentes. */
static void carga_trabalho(int indice_filho, unsigned int seed) {
    srand(seed + indice_filho * 7919u); /* seed distinta por filho */
    long iteracoes = 2000000L + (rand() % 8000000L); /* trabalho variavel */
    volatile long acumulador = 0;
    for (long i = 0; i < iteracoes; i++) {
        acumulador += (i * 3) % 7;
    }
}

/* Calcula o numero de inversoes entre duas permutacoes de 0..N-1 */
static int contar_inversoes(int *ordem_termino, int n) {
    int inversoes = 0;
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            if (ordem_termino[i] > ordem_termino[j]) inversoes++;
        }
    }
    return inversoes;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Uso: %s <N> <modo:0|1> [seed]\n", argv[0]);
        return 1;
    }

    int n = atoi(argv[1]);
    int modo = atoi(argv[2]);
    unsigned int seed = (argc >= 4) ? (unsigned int)atoi(argv[3])
                                     : (unsigned int)time(NULL) ^ getpid();

    if (n < 2 || n > MAX_N) {
        fprintf(stderr, "N deve estar entre 2 e %d\n", MAX_N);
        return 1;
    }

    pid_t pids_criacao[MAX_N]; /* PID de cada filho, na ordem de criacao */

    /* criacao sequencial dos filhos (fork) */
    for (int i = 0; i < n; i++) {
        pid_t pid = fork();
        if (pid < 0) {
            perror("fork");
            return 1;
        }
        if (pid == 0) {
            /* processo filho */
            if (modo == 1) {
                carga_trabalho(i, seed);
            }
            _exit(i);
        }
        pids_criacao[i] = pid;
    }

    /* colheita via wait() em ordem de termino --- */
    int ordem_termino[MAX_N];
    for (int k = 0; k < n; k++) {
        int status;
        pid_t pid_terminado = wait(&status);
        int indice_filho = -1;
        for (int i = 0; i < n; i++) {
            if (pids_criacao[i] == pid_terminado) { indice_filho = i; break; }
        }
        int codigo_retorno = WIFEXITED(status) ? WEXITSTATUS(status) : -1;
        (void)codigo_retorno; 
        ordem_termino[k] = indice_filho;
    }

    /* comparacao e saida */
    int bateu = 1;
    for (int i = 0; i < n; i++) {
        if (ordem_termino[i] != i) { 
            bateu = 0; 
            
            break; 
        }
    }
    int inversoes = contar_inversoes(ordem_termino, n);

    printf("%d,%d,", n, modo);
    for (int i = 0; i < n; i++) printf("%d%s", i, (i < n - 1) ? "-" : ",");
    for (int i = 0; i < n; i++) printf("%d%s", ordem_termino[i], (i < n - 1) ? "-" : ",");
    printf("%d,%d\n", bateu, inversoes);

    return 0;
}