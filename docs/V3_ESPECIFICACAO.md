# TRONCO-01 — especificação da tarefa v3 (rascunho para pré-registo)

**17 de outubro de 2026.** Escrita **antes** de existir código gerador. Nada aqui foi afinado com resultados de reservas. Os números marcados *[a fixar]* são fixados na ronda 0 da auditoria, antes de qualquer avaliação cega.

## 1. Origem e limites
Inspirada nos princípios do LUCA (orçamento, compromisso antes da revelação, pontuações separadas), do HypoSpace (conjuntos admissíveis) e do ACED-Bench (evidência forte). **Não usa código de terceiros**: o código do LUCA não é público e o do ACED não foi encontrado. O domínio é o já auditado: 4 atributos binários, 16 entradas, hipóteses com suporte essencial ≤ 2 (70 hipóteses).

## 2. Mundo e gerador
- Mundo = hipótese oculta `h` (70 possíveis) + 3 cartas declaradas (podem não conter `h`) + carta de trabalho `W` + histórico inicial de observações + (nível difícil) um atributo latente que não pode ser consultado.
- Determinista pela terna **(semente, dificuldade, família)**; guardar a terna reproduz o mundo.
- Dificuldade: fácil (sem latente, sem mudança), médio (mudança de regime), difícil (latente confundidor + mudança).
- Fase 1: orçamento B consultas *[a fixar, ≤ 4]*; cada consulta devolve `h(x)` sem ruído. Fase 2 (revisão): depois do compromisso, chega evidência nova (bloco de observações); o agente pode manter ou rever.

## 3. Ações e compromisso
Consultar `x` · compromisso (irreversível, antes da fase 2) · rever · terminar/suspender. O compromisso é um veredicto sobre `W` e a lista de cartas admissíveis.

## 4. Verdade de referência (definida só por A(H), nunca por categoria)
Seja `A` o conjunto admissível dado o histórico e `T` um conjunto de 2 entradas de intervenção não vistas, fixado pelo gerador antes da fase 1.
- **rejected**: `W ∉ A`.
- **supported**: `W ∈ A` e todo `h' ∈ A` coincide com `W` em `T` (usar `W` em `T` é seguro).
- **undetermined**: `W ∈ A` e há `h' ∈ A` que difere de `W` em `T`.
Este é o significado de INSUFFICIENCY: não depende de uma etiqueta do gerador, só do que a evidência pública determina. Ao fim de qualquer histórico, dois mundos publicamente indistinguíveis recebem o mesmo veredicto (testado).
Mundo com observações contraditórias (inconsistência) é reportado como tal e pontuado à parte.

## 5. Pontuações separadas
1. **Seleção de consultas**: fração do ganho de informação máximo possível sobre veredicto em `T`, medido em A(H).
2. **Previsão** em `T`: acerto exato.
3. **Veredicto** sobre `W` e **conjunto de cartas admissíveis** (validade, recuperação, exato).
4. **Revisão**: após evidência contrária, mudou quando devia e não mudou quando não devia (os dois erros contados separadamente).
5. **Paragem**: terminou com veredicto determinado, ou suspendeu quando indeterminado, sem gastar orçamento inútil.
6. **Evidência obtida e não usada**: consulta que separava veredictos seguida de veredicto que a contradiz.
Ações inválidas e relatório explícito seguem os limites de `docs/OBJETIVO_TRONCO.md`.

## 6. Requisitos de desenho (corrigem as falhas da auditoria M17)
- R1: a regra "só estado inicial" não pode acertar o veredicto muito acima do acaso, por família *[margem a fixar na ronda 0]*.
- R2: pelo menos 2 dos 3 veredictos exigem consulta em ≥ 40% dos mundos *[a fixar]*; nenhum veredicto domina o caso inicialmente ambíguo (máx. 60% de qualquer veredicto).
- R3: zero mundos com veredicto não identificável pela evidência pública; mundos com `h` não identificável são pontuados em conjunto.
- R4: nenhuma característica de superfície, ordem, IDs, comprimento, formato ou distribuição de saídas prediz o veredicto *onde a evidência inicial o deixa em aberto*, com potência ≥ 80% para fugas de 20% (pipeline do M17 v2 reutilizado).
- R5: sem duplicados dentro ou entre conjuntos (por estado público canónico).
- R6: o gerador nunca recebe sementes de reserva (guarda existente), e o beacon só é consultado depois do congelamento.

## 7. Políticas de referência e previsões ex-ante
Aleatória, simples (regra fixa de consulta), ganho de informação sobre A(H), oráculo. Previsões em `docs/OBJETIVO_TRONCO.md` (S1–S4). **Não se assume** oráculo > ganho de informação > simples > aleatória em todos os cenários: as exceções esperadas (p. ex., B ≥ nº de entradas informativas, em que ganho de informação e simples empatam) ficam escritas antes de correr. Resultados com intervalos de Wilson e por família.

## 8. Critérios de aceitação da tarefa (pré-fixados)
A tarefa só é aceite se, em dev e substitutos: R1–R5 passam; as políticas se ordenam como previsto nos cenários em que se previu diferença (IC 95% sem sobreposição); a oráculo atinge ≥ 98% de veredicto; a aleatória não passa de acaso + margem. Se falhar: uma de três rondas de correção, com lista de falhas, correções e critérios; depois da 3.ª, decisão fundamentada de avançar, reformular ou suspender.

## 9. Reservas
Duas partições novas, geradas só depois do congelamento deste documento e do código (hashes). Sementes = função do valor do beacon público (drand) de uma ronda futura, anunciada no congelamento. Nenhuma partição antiga (diagnóstico, confirmação do M17) é reutilizada.

## 10. Fora de âmbito
Treino, modelos, Voynich, benchmarks externos (passo 9), ruído nas respostas, dinâmicas contínuas.

## 11. Pistas de avaliação (decisão de 17/10/2026, ver `docs/DECISOES_2026-10-17.md`)
- **sem_ferramentas** e **com_codigo**, reportadas separadamente, nunca agregadas.
- Pista com código: interpretador isolado, sem rede, tempo e memória limitados; o registo de execução faz parte da memória verificável.
- A v3 cobre C3–C5. C1–C2 (enquadramento) ficam numa tarefa separada, a especificar.
- Métricas adicionais (secção 5) com decomposição obrigatória: **erro de procura** (o histórico não chega ao alvo), **erro de inferência**
  (a resposta não é a que o próprio histórico implica) e **evidência obtida e ignorada** (inferência errada com veredicto do histórico já determinado).
