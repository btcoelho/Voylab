# Conferência v2.5 e próximos passos

## Decisão

As alterações melhoraram a infraestrutura nos casos verificados. A preparação ainda exige uma correção pequena no gate de carregamento e um executor final ligado ao avaliador antes de iniciar o piloto. Não há resultados de um modelo na v2.5, nem demonstração de melhoria científica. Nesta revisão não houve carregamento de checkpoint, geração por modelo, fine-tuning ou acesso às reservas M17.

## O que foi confirmado

Os 25 testes originais voltaram a passar. O arquivo original foi conferido pelos hashes dos seus membros e pelos ficheiros atuais; o replay independente reproduziu o resumo v2.3: 10 episódios, 19 chamadas, quatro saídas malformadas, 12 ações ilegais, três relatórios legais, nenhuma consulta e 0/10 sucessos conjuntos. Os ficheiros originais foram preservados.

A retoma agora verifica o manifesto inclusive em execuções concluídas e compara o fingerprint da agenda, do limite de chamadas e da pré-registração. As regressões direcionadas para esses comportamentos passam. A rejeição de IDs duplicados funciona no validador final; a gramática LMFE continua a permiti-los, como declarado. Esta última característica foi delimitada por uma política de pós-validação, não eliminada da gramática.

O smoke test guardado da v2.5 verifica um backend próprio que constrói o seu TokenEnforcer. Não chama `Qwen25Generator.__call__` nem o avaliador científico real: o `apply` desse teste devolve uma avaliação fixa com `joint_success=false`. Portanto, ele sustenta a integração simulada do harness, mas não toda a cadeia de produção.

Para fechar parte dessa lacuna, esta revisão chamou o `Qwen25Generator.__call__` original com tokenizer e tensores CPU reais e um `model.generate` simulado. O callback Transformers/LMFE original admitiu a saída fixa até EOS; o adaptador devolveu o texto e os metadados esperados: prompt de 509 tokens e 46 tokens de saída incluindo EOS. Esse teste não carregou checkpoint, não executou Unsloth e não demonstra geração real ou validade do resultado científico.

## Correção de uma conclusão anterior

O relatório original afirmou que três mutações foram detetadas. Os três registos arquivados mostram `ModuleNotFoundError: No module named 'model_backend'`: os testes não chegaram a executar o comportamento em análise. O verificador tratava qualquer código de saída diferente de zero como mutação morta e o gerador de relatórios aceitava esse booleano. A conclusão anterior era inválida; os dados originais conservam o erro e permitem reproduzi-lo.

Criei um verificador corrigido separado, preservando o pacote v2.5. Copia as dependências, executa cada teste sem mutação primeiro e só conta como deteção uma execução com um teste, zero erros de infraestrutura/importação e falhas de asserção. A mutação do guard foi afinada para saltar a verificação apenas na retoma, evitando que uma falha artificial na primeira entrada seja confundida com a regressão pretendida.

**Resultado corrigido:** três controlos sem mutação passaram; os três mutantes relevantes foram efetivamente detetados por asserções. Esta é evidência nova desta revisão, não validação retroativa das execuções defeituosas anteriores.

## Lacuna adicional no gate do carregador

O guard normal recusa `draft_not_frozen`. Contudo, `Qwen25Generator.from_verified_checkpoint` verifica os hashes recebidos mas não verifica explicitamente `__manifest_status__`. Ao receber `partial(guard.verify, allow_draft=True)`, o mesmo mecanismo permissivo dos testes offline, a chamada chega a `FastLanguageModel.from_pretrained` mesmo com um manifesto em rascunho.

O contraexemplo usou ficheiros de bytes fictícios com hashes consistentes e um módulo Unsloth substituído por uma função que interrompe logo à entrada do carregador. Nenhum peso real foi carregado. Isto demonstra uma defesa incompleta na fronteira da API; não demonstra que o guard normal aceite rascunhos nem que tenha ocorrido uma inferência histórica indevida.

Correção mínima proposta: antes de processar os hashes ou importar o carregador, o adaptador deve exigir um dicionário de verificação com `__manifest_status__ == "frozen_before_inference"`. O guard permissivo fica restrito ao backend simulado. Uma regressão deve demonstrar zero chamadas ao carregador com estado de rascunho, mesmo quando os hashes estão corretos.

## Bloco seguinte recomendado

1. Integrar o verificador de mutações corrigido e fazer o relatório distinguir `detetado`, `sobreviveu` e `execução inválida`. Integrar também a exigência explícita de manifesto congelado no carregador e o contraexemplo como regressão. São reparações localizadas.
2. Completar um único executor de ensaio que ligue a agenda, `Qwen25Generator`, o prompt público, o harness e o avaliador real. Verificar esse mesmo executor com respostas fixas corretas e erradas, EOS, falha técnica e retoma; não voltar a usar uma pontuação constante como demonstração da integração científica.
3. Congelar a pré-registração e a configuração efetivamente utilizadas. Recomendo manter os dez casos expostos como painel de regressão de desenvolvimento: são úteis para saber se deixaram de ocorrer as falhas antigas. Não precisam de ser apresentados como validação independente. As consultas foram desativadas e o limite passou de quatro chamadas para uma; por isso uma diferença futura face a v2.3 será uma diferença entre configurações completas, sem atribuição causal exclusiva ao prompt ou à gramática.
4. Após o ponto de análise pré-inferência, executar uma única vez os dez casos com o mesmo checkpoint, sem ajuste durante o lote. Falhas de resposta contam e o lote continua; falhas técnicas ou de proveniência interrompem pela sentinela. Entregar formato, legalidade e componentes científicos separadamente, com uma única análise obrigatória no final. Uma agenda nova para generalização só se justifica depois de a interface e a resposta científica direta funcionarem.

Este pedido foi de verificação e planeamento: não congelei o rascunho nem iniciei o lote. G1/G2, v2.3 e M17 conservam o seu estatuto.

## Reprodução

O pacote de revisão inclui os scripts em `work/TRONCO01_V25_RESULT_REVIEW`, a cópia original v2.5 e os resultados da revisão. `verify_mutations_corrected.py` requer apenas Python padrão. `verify_actual_adapter_fake_model.py` requer PyTorch, Transformers, LMFE e o tokenizer local; `TRONCO_TOKENIZER_PATH` permite indicar outra localização do mesmo tokenizer. `verify_draft_loader_gate.py` interceta o carregador e usa apenas bytes fictícios. Nenhum desses verificadores executa um modelo aprendido.
