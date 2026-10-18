# TRONCO-01: estado atual (18/10/2026)

Página curta de orientação. Os detalhes e os números estão nos documentos ligados; nada aqui substitui um resultado registado.

## O que vale agora
- **Instrumento (grelha ITT, fases 1–3):** validado para leitura, inferência e revisão. [V3_INSTRUMENTO.md](V3_INSTRUMENTO.md)
- **V4 (orçamento 1, menu de 16):** escolhida e validada como tarefa completa; verificador independente 0/12 836, políticas plantadas 0/2 250, mutação 36/36; gap mediano 0,438. [V3_CONSULTAS.md](V3_CONSULTAS.md) §10–12
- **Referência congelada:** `results/instrumento/REFERENCIA.json`, com verificação no CI.
- **Piloto humano:** protocolo revisto (duas condições contrabalançadas, leitura passa/falha/inconclusivo), análise escrita e testada antes de haver respostas. [V3_CONSULTAS.md](V3_CONSULTAS.md) §11, §13

## O que foi retirado
- **Pista de posição de 58%:** vinha de um defeito na medição com empates; não existe.
- **Interpretação da escada sob o enunciado ambíguo** (prompt anterior à v3.1): não é lida como capacidade.
- **Escolha de consultas na tarefa antiga (gap 0,087):** não mede capacidade; ver a adenda de V3_INSTRUMENTO.md.

## Pendente
1. Piloto humano (Bruno e participantes P1–P3), com a página partilhada com acesso "interact".
2. Análise com `instrument/analyse_human.py`. Por pessoa e condição (n = 10) o resultado só pode ser "inconclusivo" ou "falha"; só o agregado pode passar.
3. Só depois: teto com um modelo de fronteira (aprovação caso a caso). DiscoveryWorld adiado.
4. Partição cega: reservada para a validação final.

## Limitações registadas
- **As respostas não podem ser escondidas dos participantes.** A página grava num documento partilhado (`db`); um documento que a análise consegue ler também é legível por quem participa, e os episódios incluem a referência. Mitigação: o piloto é feito só com pessoas colaborativas que aceitam não consultar o código nem os dados, e esta ressalva acompanha qualquer resultado.

## Ligações
[DECISOES_2026-10-18.md](DECISOES_2026-10-18.md) · [DECISOES_2026-10-18_11h21.md](DECISOES_2026-10-18_11h21.md) · [V3_ESPECIFICACAO.md](V3_ESPECIFICACAO.md) · [V3_PLANO_ANALISE.md](V3_PLANO_ANALISE.md)
