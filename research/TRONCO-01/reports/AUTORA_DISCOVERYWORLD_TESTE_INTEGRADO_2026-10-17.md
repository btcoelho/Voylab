# Ensaio de integração AutoRA + DiscoveryWorld

## Resultado inicial: navegação

O encaixe técnico de um seletor AutoRA com uma ação executada no DiscoveryWorld funcionou num ensaio de um passo. A observação usada para escolher a ação foi pública; não foi consultado o scorecard-oráculo.

No cenário `Small Skills: Instrument Measurement Test`, Normal, seed 0, a tarefa pedia medir o espectro de uma semente. A observação inicial colocava a semente a distância 3, a sudeste, e o espectrómetro a distância 4, a nordeste. O AutoRA `model_disagreement_sample`, perante duas heurísticas direcionais explícitas — aproximar-se do objeto ou do instrumento — escolheu `north`. DiscoveryWorld aceitou o movimento. Na observação seguinte, o espectrómetro ficou a distância 3 e a semente a distância 4; a tarefa continuou incompleta.

Como referência de uma única amostra, o `random_pool` do AutoRA escolheu `west` numa instância nova com o mesmo seed. DiscoveryWorld aceitou a ação e as distâncias observadas passaram para 5 (espectrómetro) e 4 (semente). Isto mostra que o adaptador transmitiu uma escolha e observou a consequência. **Não** demonstra superioridade estatística, descoberta científica, aprendizagem de hipóteses, nem valida TRONCO-01/M17 ou G1/G2. As duas heurísticas representam objetivos de navegação e não modelos científicos validados.

## Problema reproduzido

`DiscoveryWorldAPI.listKnownActions(limited=True)` falha com `KeyError: 'DISCOVERY_FEED_GET_ARTICLES'` na versão do checkout testado. A chamada sem limitação funciona. O ensaio contornou a falha usando a lista pública de movimentos permitidos pela observação e verificou a presença de `MOVE_DIRECTION` na lista completa.

## Reprodução

No PowerShell, a partir da pasta do projeto:

```powershell
$repo = (Resolve-Path 'work/autora_smoke/discoveryworld').Path
$python = (Resolve-Path 'work/autora_smoke/.venv/Scripts/python.exe').Path
$env:PYTHONPATH = $repo
$env:SDL_VIDEODRIVER = 'dummy'
$env:PYGAME_HIDE_SUPPORT_PROMPT = '1'
Push-Location $repo
try { & $python '..\run_joint_discoveryworld_autora.py' }
finally { Pop-Location }
```

O script de navegação e o respetivo JSON acompanham este relatório. O código executou em Python 3.12.10, AutoRA 4.2.0, `autora-experimentalist-model-disagreement` 2.2.0, NumPy 1.26.4, pandas 3.0.6 e pygame 2.6.1. O checkout DiscoveryWorld estava no commit `fd591323920be0d3786ef350955de1945aa571e5`.

## Ensaio ampliado: seleção e medição

Para testar o caminho científico, executei cinco réplicas do cenário `Plant Nutrients`, dificuldade Easy, seeds 0–4. Em cada réplica, o `random_pool` do AutoRA escolheu uma amostra de solo entre as amostras visíveis na observação pública. O adaptador recolheu o medidor também pela observação pública, posicionou o agente ao lado da amostra com `TELEPORT_TO_OBJECT` como atalho do harness e realizou `USE` do medidor sobre o solo. A leitura regressou pela mensagem pública da interface. **As cinco réplicas produziram uma leitura estruturada para os cinco nutrientes.** Não foi consultado o scorecard-oráculo.

O script deste ensaio é `run_autora_discoveryworld_assay.py`; a saída completa está em `AUTORA_DISCOVERYWORLD_RESULTADO_2026-10-17.json`. Para o reproduzir, use a mesma preparação do bloco anterior e execute `& $python '..\run_autora_discoveryworld_assay.py'` dentro do checkout DiscoveryWorld.

Exemplo seed 0: a amostra escolhida devolveu potássio `high` e os outros quatro nutrientes `zero`. A tarefa não foi marcada como concluída, como esperado: o ensaio só mediu, não submeteu uma resposta ao controlador.

## Decisão

Os dois projetos conseguem participar no mesmo ciclo mínimo: AutoRA escolhe uma condição observável e DiscoveryWorld executa a ação de medição e devolve dados. Isso justifica manter ambos disponíveis para construir um adaptador. **Ainda não justifica usar a combinação como método científico validado.** Nesta execução o AutoRA usou amostragem aleatória; não testámos ganho da seleção por desacordo contra aleatório.

O ensaio Easy apresenta uma limitação concreta para essa comparação: as amostras têm perfis fixos no mundo; o medidor revela os cinco nutrientes numa só ação; e a interface do controlador apresentada neste cenário pede a identificação do nutriente. Assim, não há aqui cinco intervenções separadas que correspondam a “medir um nutriente” cada. Os UUIDs das amostras são identificadores opacos, sem covariáveis públicas que autorizem o modelo de desacordo a prever qual amostra será mais informativa. Escolher por desacordo sobre esses IDs daria uma aparência de atividade sem fundamento experimental.

Conclusão do bloco: **integração técnica demonstrada; contribuição científica do AutoRA ainda por demonstrar.** Manter AutoRA para desenho de experiências só quando encontrarmos um cenário DiscoveryWorld com condições manipuláveis e observações que variem conforme a condição escolhida. O próximo estudo deve congelar antes o mapa entre condição AutoRA, sequência de ações legais e resposta pública; depois comparar desacordo, aleatório e uma regra simples em mundos/seeds emparelhados, com o mesmo orçamento. Reservar o oráculo para pontuação final independente.

## Próximo passo recomendado

O relatório, os dois scripts e os respetivos JSON representam o estado final deste ensaio. Antes de usar a combinação num estudo científico, escolher um cenário com intervenções controláveis e definir o contrato do adaptador. A falha de `limited=True` deve ser reportada ao projeto de origem ou evitada no adaptador.
