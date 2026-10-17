# TRONCO-01 — aproveitamento de REA e Google AX

Revisão de 17/10/2026. Análise estática seletiva de documentação e código, apoiada por 25 ficheiros de referência descarregados, com versões fixadas. Não é uma auditoria integral dos repositórios. Não foram instalados pacotes, executados testes destes projetos, lançados agentes ou alterados M16/M17.

REA: commit `f85a932d71279415dd95cc30083137d1161f83b8` (17/10/2026). AX: commit `8d2ccf36f194f6f58c57b90753bd3986639b562f` (16/10/2026). O manifesto de fontes contém os caminhos, links por commit e SHA-256 dos ficheiros lidos.

## Recomendação

Há material útil para reaproveitar. O REA é a referência mais imediata para evidências, questões em aberto e regras de encerramento. O AX fornece boas ideias para organizar execuções e separar configuração de estado operacional. Para a dimensão atual do projeto, proponho adaptar esses mecanismos a um núcleo local simples, preservando a possibilidade de executar esse núcleo num AX futuro.

Esta avaliação é de adequação de engenharia, não um resultado experimental sobre os dois projetos ou sobre o TRONCO. Não há uma estimativa medida de horas poupadas.

## Componentes concretos do REA

| Fonte | O que o código fornece | Aplicação proposta ao TRONCO |
|---|---|---|
| [EvidenceLedger.ts](https://github.com/morluto/rea/blob/f85a932d71279415dd95cc30083137d1161f83b8/src/application/investigation/EvidenceLedger.ts) | Registos validados e imutáveis, deteção de duplicados/conflitos, importação atómica e exportação de bundles | Núcleo de integridade da memória e do intercâmbio de evidências |
| [residualUnknown.ts](https://github.com/morluto/rea/blob/f85a932d71279415dd95cc30083137d1161f83b8/src/domain/residualUnknown.ts) | Questões com identidade, revisões encadeadas, estados, evidências favoráveis/contraditórias, dependências, ambiente requerido e consultas sugeridas | Registo explícito do que ainda não se sabe e do que falta observar |
| [evidenceBundle.ts](https://github.com/morluto/rea/blob/f85a932d71279415dd95cc30083137d1161f83b8/src/domain/evidenceBundle.ts) | Validação de referências, cadeia de revisões e critérios de qualificação de uma resolução | Impedir encerramentos sem a evidência exigida |
| [evidence.ts](https://github.com/morluto/rea/blob/f85a932d71279415dd95cc30083137d1161f83b8/src/domain/evidence.ts) | Resultado bruto/normalizado, fornecedor, origem, limitações, cobertura e ligações a outras evidências | Separar a observação da interpretação e preservar a origem verificável |
| [Obligation ledgers](https://github.com/morluto/rea/blob/f85a932d71279415dd95cc30083137d1161f83b8/docs/reconstruction-obligation-ledgers.md) | Conjunto finito de afirmações a verificar; lacunas e contradições impedem declarar o encerramento | Lista de requisitos probatórios para uma investigação, com âmbito explícito |

O REA faz uma distinção particularmente útil: registar a intenção de resolver uma dúvida não é prova de que ela foi resolvida. O componente [UnknownEvidence.ts](https://github.com/morluto/rea/blob/f85a932d71279415dd95cc30083137d1161f83b8/src/application/investigation/UnknownEvidence.ts) marca esse registo como inferência do analista. No bundle, uma resolução verificada precisa de evidência qualificante e não pode simplesmente usar o próprio evento de alteração de estado como prova.

### Adaptações necessárias

- O ledger usa mapas em memória e exportação. Persistência durável, transações em disco e recuperação após falha continuam a exigir implementação ou integração nossa.
- Os tipos estão ligados a artefactos de software, arquiteturas binárias, perfis de análise e comparações de funções. Importar diretamente esses módulos para o protótipo Python arrastaria pressupostos e dependências pouco úteis. A adaptação deve preservar os invariantes relevantes e substituir o vocabulário do domínio.
- As etiquetas `observed`, `derived` e `inferred`, chamadas `confidence` no código, descrevem a natureza da evidência. Não são probabilidades calibradas. No TRONCO, separar esse campo da probabilidade de um resultado e da confiança declarada numa decisão.
- As questões em aberto não substituem hipóteses executáveis. Precisamos de acrescentar versões de hipóteses, dados de ajuste, previsões anteriores à medição, distribuições de ruído, verificações de adequação e custo das experiências.
- Um registo estruturalmente válido pode conter uma conclusão falsa. É necessário que a origem e a semântica dos resultados sejam verificadas pelo núcleo. Hashes, etiquetas de origem e ausência de referências contraditórias não provam uma lei científica.

O próprio desenho de encerramento do REA é finito: satisfazer as afirmações declaradas não demonstra equivalência universal. Essa limitação é apropriada ao TRONCO: qualquer conclusão deve identificar o domínio e os testes que a sustentam.

## Onde utilizar o REA como ferramenta

O projeto oferece análise de programas e de comportamento, incluindo fontes que não estão disponíveis como código. Para estes dois repositórios públicos, a leitura direta já permitiu identificar os componentes acima. O REA pode acrescentar valor quando quisermos estudar uma ferramenta através de observações de execução ou reconstruir um comportamento sem fontes disponíveis. [Descrição oficial](https://github.com/morluto/rea/tree/f85a932d71279415dd95cc30083137d1161f83b8).

Na avaliação científica, manter a fronteira entre desenvolvimento e agente avaliado: inspecionar o gerador ou a sua verdade oculta com uma ferramenta de engenharia inversa destruiria a validade de um teste que exige descobrir a regra por observações públicas. O REA pode ajudar a desenvolver a infraestrutura; o TRONCO em reserva recebe apenas o canal de informação permitido.

## O que aproveitar do Google AX

| Fonte | Mecanismo útil | Adaptação local proposta |
|---|---|---|
| [Concepts](https://github.com/google/ax/blob/8d2ccf36f194f6f58c57b90753bd3986639b562f/docs/concepts.md) e [API](https://github.com/google/ax/blob/8d2ccf36f194f6f58c57b90753bd3986639b562f/pkg/apis/v1alpha1/ax.proto) | Separação entre tarefa, ambiente e configuração de modelo | Manifesto por ensaio com hashes de modelo/prompt/dados/ferramentas e parâmetros explícitos |
| [Design](https://github.com/google/ax/blob/8d2ccf36f194f6f58c57b90753bd3986639b562f/DESIGN.md) | Tarefas imutáveis e transições de estado observáveis | Preservar a especificação; reportar progresso e razão de falha sem reescrever o ensaio |
| [runner.go](https://github.com/google/ax/blob/8d2ccf36f194f6f58c57b90753bd3986639b562f/runner/runner.go) | Supervisão do processo, notificação da saída e finalização controlada | Gravar resultados parciais e causas de interrupção; separar saída do processo de conclusão científica |
| [Runner contract](https://github.com/google/ax/blob/8d2ccf36f194f6f58c57b90753bd3986639b562f/docs/runner.md) | Ambiente persistido em volume e retoma com processos novos | Guardar memória e eventos de forma explícita; não depender só da RAM do agente |

A infraestrutura completa usa Kubernetes, Agent Substrate e Redis, com componentes Go. O projeto anuncia desenvolvimento intenso e possíveis alterações incompatíveis antes de estabilizar. Para o atual laboratório local, a minha avaliação é que o custo de montar essa plataforma não se justifica pelo piloto que precisamos executar. [README](https://github.com/google/ax/blob/8d2ccf36f194f6f58c57b90753bd3986639b562f/README.md).

### Limites relevantes da versão lida

O [roadmap](https://github.com/google/ax/blob/8d2ccf36f194f6f58c57b90753bd3986639b562f/docs/roadmap.md) inclui budgets por tarefa, governação e recolha automática de trajetórias. O `TaskSpec` observado tem recursos CPU/memória, comandos e ambientes; não devemos assumir que esses itens do roadmap já estão implementados. O cliente interno fornece contagens de tokens por chamada, mas isso não equivale a impor um budget total de investigação. Não há fundamento nesta revisão para afirmar que instalar AX resolveria as tentativas inválidas e a falta de saídas brutas do M17.

O runner mantém o ambiente inspecionável após terminar o comando. Assim, ambiente ativo/pronto, comando terminado e teste científico aprovado são estados distintos que a nossa aplicação terá de reportar. Uma configuração AX também não substitui o diagnóstico de adequação das hipóteses.

O cliente interno de modelo analisado implementa a chamada Google e uma resposta de fallback, com rejeição de fornecedores não suportados fora desse caminho. Isto não impede executar um agente Python próprio com um modelo local dentro de uma tarefa AX: o runner aceita um comando genérico. Exigiria, porém, a integração explícita do nosso agente. [Cliente](https://github.com/google/ax/blob/8d2ccf36f194f6f58c57b90753bd3986639b562f/internal/model/client.go).

Qualquer integração deve identificar respostas de fallback separadamente e impedir que sejam contabilizadas como previsões produzidas pelo modelo. Este é um requisito do nosso ensaio; não foi executado um teste desse comportamento no AX.

## Licenças e forma de reutilização

O código principal do REA usa [MIT](https://github.com/morluto/rea/blob/f85a932d71279415dd95cc30083137d1161f83b8/LICENSE); AX usa [Apache-2.0](https://github.com/google/ax/blob/8d2ccf36f194f6f58c57b90753bd3986639b562f/LICENSE). A cópia/adaptação de trechos deve conservar os avisos e licenças aplicáveis e registar a origem e as alterações. O REA mantém [avisos de terceiros](https://github.com/morluto/rea/blob/f85a932d71279415dd95cc30083137d1161f83b8/THIRD_PARTY_NOTICES.md); a licença do projeto principal não transforma todas as ferramentas e dependências integradas em MIT.

Para o protótipo, a opção com menor acoplamento é adaptar os invariantes de evidência e revisão a tipos Python pequenos. Só extrair uma biblioteca diretamente quando a utilidade justificar manter a sua árvore de dependências. A linguagem do código, por si só, não justifica reescrever um componente; o domínio e a integração existente é que determinam a escolha.

## Próximo incremento proposto para o TRONCO

1. Acrescentar ao desenho de memória um registo de questões por resolver: identidade, versão, evidências favoráveis/contraditórias, dependências, próximo teste e condição de resolução. Preservar a ligação entre hipótese, previsão anterior, medição e decisão.
2. Acrescentar um envelope de execução: especificação imutável, estado operacional, tokens, ações, erros por classe e motivo de interrupção. Preparar a gravação de eventos antes de uma possível falha, em vez de guardar apenas o agregado final.
3. Implementar esse incremento num diretório isolado e verificar invariantes dirigidos: IDs conflitantes; revisão antiga; evidência inexistente; encerramento com contradições; relatório automático a passar por decisão do modelo; processo ativo a passar por aprovação científica.
4. Só depois executar o gate operacional limitado já proposto, sem converter esta adaptação de memória num novo ciclo de centenas de chamadas. O ledger não corrige sozinho uma geração inválida.
5. Medir a contribuição do registo e da verificação por ablações. Acrescentar AX como runtime apenas quando o volume de execuções, ambientes ou máquinas justificar o cluster.

São propostas de integração, sem testes executados nesta revisão. O aproveitamento mais útil agora é a disciplina de evidência do REA e a separação de especificação/estado do AX. O núcleo científico — hipóteses falsificáveis, adequação sob ruído, escolha de experiências e revisão preditiva — continua a precisar das experiências TRONCO-01.
