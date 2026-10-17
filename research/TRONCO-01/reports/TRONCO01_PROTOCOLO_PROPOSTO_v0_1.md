# TRONCO-01 — protocolo proposto v0.1

Data: 17/10/2026. Estado: desenho para revisão, sem execução de modelos nesta etapa. Não substitui nem altera M17 0.1.2. Os budgets científicos, famílias, dimensão amostral e limites de erro só ficam congelados quando o manifesto prévio estiver completo.

## 1. Unidades e resultados

Unidade primária: uma investigação num mundo; ações repetidas desse episódio não são réplicas independentes. Comparações emparelhadas usam o mesmo mundo subjacente e os mesmos dados iniciais. As consultas escolhidas podem divergir entre agentes.

Separar estado operacional (válido, falha de geração, falha de parser, ação inválida, timeout, orçamento esgotado), estado epistémico e ação de triagem A/B/C. Encerramento forçado não é abstenção escolhida. Falhas permanecem no denominador de desempenho; calibração exige previsões realmente emitidas e reporta cobertura.

Inadequação do conjunto significa que as hipóteses atuais falham os testes de adequação especificados. Não significa que todas as explicações possíveis foram refutadas. Ambiguidade significa que hipóteses ainda adequadas não foram discriminadas; insuficiência significa que os dados/meios não justificam a decisão solicitada. Ruído e mudança de mecanismo só recebem diagnóstico específico se forem distinguíveis com a evidência disponível.

## 2. Gate operacional G0 — máximo de 16 gerações

Executar apenas numa futura cópia isolada de desenvolvimento:

1. Preparar três tarefas pequenas: emitir um objeto JSON especificado; selecionar um ID disponível de consulta; relatar um conflito simples com evidências públicas.
2. Para cada tarefa, comparar o prompt efetivamente usado no M17 com uma mensagem de sistema direta, mantendo estado, parser, modelo e parâmetros de geração fixos.
3. Executar base e M16: 3 tarefas × 2 prompts × 2 modelos = 12 gerações. Sem ciclos automáticos de dez tentativas.
4. Acrescentar dois casos do contrato nativo M16 para cada modelo, quando recuperáveis sem alterar os artefactos originais: quatro gerações. Caso contrário, registar a ausência e não fabricar uma tradução semântica.
5. Guardar prompt/template e hashes, identificação do checkpoint, saída bruta de desenvolvimento, contagens de tokens, fim por EOS/limite, ação interpretada e razão precisa de rejeição. Reservar a resposta dentro do limite total de contexto.

Saída: comparação das classes de falha e proposta de uma única intervenção. Comunicação funcional nestes casos é gate de engenharia, sem inferência sobre taxa populacional de erro de 1%. Não abrir o diagnóstico reservado para depurar esta fase.

**Paragem obrigatória após G0:** avaliar a causa dominante. Uma interface que recebe JSON do modelo mas escolhe a conclusão ou corrige semanticamente uma hipótese é uma ferramenta cognitiva adicional e deve ter condição experimental própria.

## 3. Núcleo mínimo e integridade

Implementar apenas após rever G0: diário de eventos, hipóteses executáveis num domínio restrito, cálculo de previsão, comparação com medição e decisão sob orçamento. O schema de memória é uma proposta de formato, não um agente implementado.

Requisitos estruturais: previsão vinculada à versão da hipótese e aos dados de ajuste; evento de previsão anterior ao pedido/resultado da medição; resultado bruto imutável; revisão cria uma versão; dependências identificadas; falhas operacionais distintas; reset entre episódios salvo condição explícita de aprendizagem contínua. Hashes e relógios locais não substituem um verificador de ordem e uma política de acesso.

## 4. Partições e independência

Separar desenvolvimento, validação de engenharia e três avaliações científicas reservadas. Reservar grupos completos de mecanismos, além de sementes e parâmetros. Para cada grupo, usar várias realizações, cruzando famílias e sementes para que os seus efeitos não fiquem confundidos.

Definir a informação que cada papel conhece: autor do gerador, programador do agente, proponente LLM e avaliador. Testes de integridade podem verificar mecanismos ocultos sem os fornecer ao agente, mas as famílias usadas para escolher prompts/heurísticas não podem ser reclassificadas como inéditas.

Auditar antes da avaliação se há políticas que conseguem obter evidência suficiente dentro do orçamento. Se duas situações exigirem decisões distintas mas forem indistinguíveis com os meios permitidos, a tarefa deve admitir incerteza, não exigir acerto do rótulo oculto. Auditar também políticas que possam explorar fugas de identificadores, forma, ordem e comprimento.

Qualquer reserva usada para orientar correções deixa de ser confirmação dessa intervenção. O novo protocolo não autoriza usar as reservas M17 como dados de desenvolvimento.

## 5. Condições experimentais

| ID | Configuração |
|---|---|
| A | Modelo base com interface mínima e orçamento explícito |
| B | M16 no protocolo e ferramentas originais, quando aplicável; recuperação nativa separada se a tarefa diferir |
| C | Base + memória científica |
| D | Base + verificadores externos |
| E | Base + memória + verificadores |
| F | M16 + os mesmos mecanismos de E no mesmo ambiente |
| G | Controlos estatístico/simbólico, com referência simples separada do controlo de resolubilidade |

A/C/D/E formam um fatorial memória × verificação. Separar efeito do treino de efeito de ferramentas por comparação E/F. Igualar informação inicial, custo permitido de aquisição, tokens e recursos do verificador, ou declarar precisamente a ablação desigual. Uma referência adicional de maior capacidade pode testar o limite do modelo, sem atribuir ganhos de ferramentas ao treino.

## 6. Três experiências científicas

**E1 — adequação e triagem:** mundos normais, hipótese correta/incorreta, equivalência observacional, conjunto inadequado, mudança, ruído e insuficiência. Sem anúncio de problema. Exigir hipóteses falsificáveis e previsões anteriores a novos resultados. Medir deteção justificada de inadequação, falsos alarmes, previsões e decisões A/B/C. Distinguir condição de catálogo fornecido de condição de hipóteses propostas pelo agente.

**E2 — valor da investigação:** comparar aquisição ativa, aleatória, fixa e nenhuma aquisição; conjunto fixo contra expansão. Registar previsões em intervenções reservadas após cada consulta e custo acumulado. Discriminar hipóteses erradas sem melhorar adequação ou previsão não aprova a competência. O avaliador de transferência não devolve as respostas reservadas ao agente.

**E3 — revisão, memória e paragem:** sequências estáveis e com mudanças, contestações sintéticas, encerramento e reabertura. Medir redução de erro futuro após revisão, atraso de deteção, falsos alertas, custo, evidência correta e integridade temporal. Comparar memória persistente permitida e reset; transferência para nova família requer uma avaliação distinta da continuidade no mesmo mecanismo.

## 7. Critérios candidatos antes de congelar

Estes valores são propostas de risco/competência para TRONCO-01; não serão aplicados retroativamente aos dados M17:

- Limite superior de 95% para a taxa de falsos alarmes ≤5% em negativos e ruído sem mudança relevante.
- Limite inferior de 95% para deteção sustentada de inadequação ≥80% em casos identificáveis.
- Limite inferior de 95% para reconhecimento correto de insuficiência ≥70%.
- Zero violação de anterioridade ou evidência inventada no ensaio; isso não demonstra uma taxa de falhas literalmente zero fora da amostra.
- Benefício da investigação ativa sobre controlo aleatório positivo, com intervalo previamente definido, a custo igual, em cada avaliação reservada.
- Revisões melhoram previsão futura; confiança e explicação verbal sem melhoria não bastam.

Calcular dimensões amostrais antes da avaliação, considerando dependência entre mundos da mesma família, comparações múltiplas e objetivos de precisão. Reportar contagens, intervalos, cobertura, falhas e resultados por família. Não selecionar apenas a melhor trajetória. Não exigir superar um controlo de resolubilidade que já atinge 100%.

## 8. Manifesto necessário antes de lançar ciência

O manifesto deve fixar: hipóteses científicas; tarefas; critérios de normalidade/ruído/adequação; espaços de ação; budgets completos; versões/hash de modelos, prompts, ferramentas e geradores; partições e acessos; dimensões amostrais; regras de exclusão; classes de falha; stopping rules; métricas e intervalos; regra de intervenção; critérios de passagem e abandono.

## 9. Treino e integração

Preservar M16, M17 e respetivas reservas. Novo código e resultados vivem num diretório TRONCO separado. Reutilizar interfaces e testes como material de desenvolvimento, sem tratar o seu gerador como reserva científica nova.

Só propor novo treino depois de identificar uma lacuna específica que persista com ferramentas apropriadas. Definir exemplos de desenvolvimento, controlo sem treino, métrica da competência, regressões e transferência. Não escolher épocas ou dataset apenas para melhorar uma percentagem global. Especialistas e revisor operacional permanecem fora desta fase.
