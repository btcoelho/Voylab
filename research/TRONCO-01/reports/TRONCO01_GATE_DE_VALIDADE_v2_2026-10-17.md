# TRONCO-01/M17/G2 — redefinição operacional e gate v2

Data: 17/10/2026
Natureza: correção do contrato e reanálise retrospectiva; **não é um novo ensaio de modelo**.

## Decisão neste ponto

**O instrumento continua inapto para uma nova chamada de modelo.** A pergunta ficou delimitada e o avaliador de referência passou os testes que implementámos, mas a versão corrigida ainda não foi integrada e validada de ponta a ponta na interface de ação, gramática, executor, pontuação e pré-teste. A auditoria anterior demonstrou defeitos nessas camadas. Este gate é o ponto de análise obrigatório antes de qualquer inferência nova.

O passo seguinte possível, após esta decisão, é concluir e verificar essa integração de avaliação v2 sem chamar modelos. Só depois de um novo relatório de gate considerar a cadeia completa apta se deve propor um ensaio pequeno, com pré-registo próprio. Não se fez fine-tuning, não se carregaram pesos e não se abriram reservas M17.

## Pergunta operacional fixada

O alvo primário é: **o modelo de trabalho W ajusta-se a todas as observações públicas H efetivamente recolhidas neste episódio?**

- `supported`: H não está vazio e W prevê todas as saídas observadas.
- `rejected`: pelo menos uma observação citada contradiz W.
- `undetermined`: ainda não há observações.

Em separado, o conjunto de candidatos que prevê corretamente **todo** H determina o diagnóstico: nenhum (`none_fit`), um (`identified`) ou vários (`ambiguous`). O conjunto de candidatos declarado pelo agente tem de coincidir exatamente com esse conjunto. Um relatório `supported` tem de citar todo H; um relatório `rejected` precisa de pelo menos um contraexemplo. O rótulo oculto do gerador não altera a resposta esperada. A especificação completa e os limites estão em `SPEC_V2.md` dentro do pacote.

Este contrato avalia ajuste observacional finito em tabelas determinísticas. Não demonstra verdade universal, causalidade, mudança real de mecanismo, adequação da lista de hipóteses ou validade para dados históricos do manuscrito.

## Trabalho executado

1. Defini a pergunta-alvo e separei ajuste de W, identidade de candidatos, insuficiência, qualidade da consulta, forma/legalidade e sustentação por evidência.
2. Implementei `reference_core_v2.py` sem importar funções semânticas do avaliador histórico.
3. Acrescentei nove testes focados em: identidade versus ajuste, certificados completos, contraexemplo mínimo, candidatos conferidos contra todo o histórico, ausência de dados, invariância à ordem, duplicatas, localização e IDs inventados.
4. Reproduzi a avaliação retrospectiva dos registos G1/G2 usando respostas e estados públicos gravados. As 235 execuções foram reconstituídas; os 178 relatórios explícitos foram classificados sob v2. Não houve divergência ao reproduzir as respostas de consulta registadas.
5. Mantive os registos e as pontuações históricas intactos. Os números v2 são uma reanálise condicional, não substituem G1/G2 nem contam como novas amostras.

## Resultados retrospectivos conjuntos

“V2 conjunta” exige simultaneamente veredicto correto sobre W, certificado suficiente, conjunto exato de candidatos e IDs sem duplicação. O denominador inclui apenas relatórios explícitos.

| Registos | Relatórios | V2 conjunta | Histórico: decisão correta |
|---|---:|---:|---:|
| G1 base schema | 25 | 0 | 9 |
| G1 M16 schema | 24 | 0 | 4 |
| G1 detetor estatístico | 25 | 10 | 15 |
| G1 consultas fixas | 25 | 10 | 19 |
| G1 consultas aleatórias | 25 | 10 | 19 |
| G1 simbólico ativo | 25 | 20 | 25 |
| G2 ponte G1 | 5 | 0 | 2 |
| G2 base schema | 4 | 0 | 0 |
| G2 detetor estatístico | 5 | 2 | 3 |
| G2 consultas fixas | 5 | 2 | 4 |
| G2 consultas aleatórias | 5 | 2 | 4 |
| G2 simbólico ativo | 5 | 4 | 5 |

O resultado do modelo base G2 permanece negativo: 0/4 relatórios explícitos satisfazem o contrato conjunto v2; os cinco registos do braço livre continuam sem relatório explícito. O controlo simbólico não é evidência de desempenho de modelo. O efeito da escolha do alvo mantém-se: decisão histórica e justificação sob o alvo operacional não são a mesma métrica.

## Verificação e limites

- `pytest tests/test_operational_v2.py`: 9 passaram.
- `reanalyze_v2.py`: 235 episódios, 178 relatórios explícitos, 0 divergências no replay de consultas.
- A bateria de mutações da auditoria v1 já matou 11 mutações relevantes no núcleo de referência então auditado; não é alegada aqui uma campanha completa de mutações sobre todo o v2.
- A execução foi feita na mesma máquina e pelo mesmo operador. Não houve revisão humana independente.
- O v2 ainda não integra um schema/gramática, executor, logging bruto e gate de pré-inferência verificados como uma única cadeia. Por isso o resultado dos nove testes unitários não autoriza uma nova chamada de modelo.
- Os estados de desenvolvimento e os relatórios antigos não substituem uma validação cega nem revelam como um modelo se comportará com o contrato v2.

## Reprodução

No pacote, a partir da pasta `TRONCO01_VALIDITY_AUDIT_v1`, com Python 3.12, as dependências de `requirements-audit.txt` e o runtime histórico disponível:

```bash
export PYTHONDONTWRITEBYTECODE=1
export AUDIT_SOURCE_ROOT="$PWD/evidence/original"
python -m pytest tests/test_operational_v2.py -q -p no:cacheprovider
python reanalyze_v2.py
```

Os ficheiros de saída da reanálise ficam em `results/retrospective_v2_episodes.json` e `results/retrospective_v2_summary.json`. Os registos históricos usados estão preservados em `evidence/original/`; dados privados e reservas M17 não foram incluídos.
