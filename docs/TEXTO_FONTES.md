<!-- Pesquisa de 19/10/2026 (agente de pesquisa); nada descarregado nem corrido. V = verificado na fonte; I = indireto. -->

# TRONCO-01: trabalhos, código e corpora para as lacunas 1–7

**Resumo.** Encontrei material útil e verificável para todas as lacunas exceto a 6. Na lacuna 6 só há um projeto próximo do que queremos, o `ms408`, e foca-se no Voynich. Seguem dois avisos importantes, a tabela por lacuna e as 5 recomendações.

**Aviso de fuga de dados.** Três dos melhores geradores foram afinados sobre o próprio Voynich:
- As tabelas do Naibbe foram ajustadas à distribuição de frequências das palavras do Voynich. Quem o diz é T. Timm, que cita "fitted to VMS word frequency distribution (p. 7, Supp. Mat. 3)" num fórum.
- As grelhas de Rugg foram desenhadas para produzir "voynichês".
- O gerador de Timm & Schinner também foi feito para o Voynich (pela minha leitura).

Podemos usá-los como geradores com verdade conhecida. Devemos correr os nossos próprios textos simples e parâmetros, e o sucesso deve medir-se pela recuperação dos parâmetros e da língua, nunca pela semelhança com o Voynich.

**Limite técnico.** Neste ambiente, o leitor de páginas só abria URLs que já tivessem aparecido numa pesquisa ou noutra página lida. Por isso não consegui abrir estas páginas: github.com/greshko/naibbe-cipher, github.com/TorstenTimm/SelfCitationTextgenerator, zenodo.org/records/2531632, github.com/lrozanova/voynich-units, github.com/labyrinthinesecurity/currier-signatures, github.com/DireLabs/ms408 (só a página de releases), a PMC8794160 e o artigo do Naibbe na Taylor & Francis (deu erro). Quando os cito, assinalo de onde vem a referência.

Legenda: **V** = verifiquei na fonte primária ou na página oficial. **I** = referência indireta (outro artigo, um fórum, um título de pesquisa).

---

## Lacuna 1: textos longos com fronteiras de palavra (Zipf, dependência entre palavras, posição, entropia condicional)

| Nome | Link primário | Ano | O que oferece | Licença | Utilidade | V/I |
|---|---|---|---|---|---|---|
| Montemurro & Zanette, "Universal entropy of word ordering across linguistic families" | [PMC3094390](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3094390/) | 2011 | Método: entropia da ordem das palavras, comparada com o mesmo texto baralhado; aplicado a muitas famílias linguísticas | PLoS ONE, CC BY | **Alta**: é exatamente o teste "dependência entre palavras vs. palavras reais em ordem aleatória" | I (título e revista vistos na pesquisa) |
| Parisel, "Evidence of Layered Positional and Directional Constraints…" | [arXiv 2604.19762](https://arxiv.org/pdf/2604.19762) | 2026 (v2, 17 jun.) | Código (repositório currier-signatures); medidas de entropia condicional direcional, informação mútua entre fronteiras de palavra, extremidade posicional, forma Zipf das fronteiras; bootstrap e 20 sementes; controlos: cadeias aleatórias, baralhado dentro da frase, Moby Dick, Monte Cristo, hebraico e árabe | Não vista | **Alta**: as medidas são diretamente aplicáveis a textos com verdade conhecida | V (artigo); I (repositório) |
| Stanisz, Drożdż, Kwapień, "Complex systems approach to natural language" | [arXiv 2401.02772](https://arxiv.org/pdf/2401.02772) | 2024 | Revisão: leis de Zipf e Heaps, correlações de longo alcance, entropia, multifractalidade, redes de adjacência. Sem código | arXiv | **Média**: catálogo de medidas para o nosso módulo estatístico | V |
| Rozanova & Temerev, "A Glyph Is Not a Letter…" | [arXiv 2608.17096](https://arxiv.org/pdf/2608.17096) | 2026 (17 ago.) | Pacote público com corpora de controlo (Gutenberg EN/FR/DE/IT, latim Tesserae/Perseus, chinês, hebraico via Sefaria), resultados com semente fixa, um script por análise | Não vista | **Média-alta**: os controlos e os scripts servem-nos; a parte Voynich é para ignorar | V (artigo); I (repositório) |
| Lindemann & Bowern, "Character entropy in modern and historical texts" | [PDF Yale](https://alumniacademy.yale.edu/sites/default/files/2021-07/Character%20Entropy%20in%20Modern%20and%20Historical%20Texts%20Comparison%20Metrics%20for%20an%20Undeciphered%20Manuscript.pdf), [lingbuzz](https://lingbuzz.net/lingbuzz/005522/v1.pdf) | 2020/21 | Entropia condicional de caracteres em muitas línguas modernas e históricas: valores de referência | Não vista | **Média**: dá valores esperados para calibrar | I |
| Tanaka-Ishii, *Statistical Universals of Language* | [Springer](https://link.springer.com/10.1007/978-3-030-59377-3) | 2021 | Livro sobre universais estatísticos da linguagem (leis de potência, correlações de longo alcance) | Comercial | **Média** | I |
| Lin & Tegmark (decaimento da informação mútua) | [arXiv 1606.06737](https://arxiv.org/pdf/1606.06737.pdf) | 2016 | Decaimento da informação mútua com a distância, como assinatura de língua natural | arXiv | **Média** | I |

## Lacuna 2: cifras verbosas (uma letra → vários glifos)

| Nome | Link primário | Ano | O que oferece | Licença | Utilidade | V/I |
|---|---|---|---|---|---|---|
| Greshko, "The Naibbe cipher…" (*Cryptologia*) | [DOI 10.1080/01611194.2025.2566408](https://www.tandfonline.com/doi/full/10.1080/01611194.2025.2566408) | Online a 26 nov. 2025 | Cifra homofónica verbosa feita à mão: o texto é partido em unidades de 1 ou 2 letras com dados, e 6 tabelas são escolhidas com cartas. Os textos cifrados continuam decifráveis. Materiais suplementares 2 e 3 | O autor diz que é acesso aberto; licença exata não vista | **Alta**: gerador de cifra verbosa com texto simples conhecido. Atenção: as tabelas foram ajustadas ao Voynich | I (metadados via [Sci.News](https://www.sci.news/othersciences/linguistics/voynich-manuscript-cipher-14466.html) e [Schneier](https://www.schneier.com/blog/archives/2025/12/substitution-cipher-based-on-the-voynich-manuscript.html); a página do artigo deu erro) |
| Código e tabelas do Naibbe | github.com/greshko/naibbe-cipher; Zenodo 10.5281/zenodo.16415087 | 2025 | Código e tabelas | ? | **Alta** | I (citado em arXiv 2608.17096; não abri) |
| Biblioteca Python "pykeedy" (Greshko) | Não encontrei a fonte primária | 2025 | Usada para demonstrar o Naibbe em texto alemão | ? | ? | I (mencionada no [fórum](https://www.voynich.ninja/printthread.php?tid=5081)) |

Outras propostas de cifra verbosa com gerador público: não encontrei nenhuma com fonte primária verificável.

## Lacuna 3: texto mecânico sem significado (grelhas de Cardano, auto-cópia)

| Nome | Link primário | Ano | O que oferece | Licença | Utilidade | V/I |
|---|---|---|---|---|---|---|
| Timm & Schinner, "A possible generating algorithm of the Voynich manuscript" (*Cryptologia*) | DOI 10.1080/01611194.2019.1596999 | 2019 online / 2020 | Algoritmo de auto-cópia (self-citation) | Pago | **Alta** (o método) | I (DOI tirado de [apresentação em Colónia](https://lehre.idh.uni-koeln.de/site/assets/files/1443/vms-text_als_hoax.pdf)) |
| Gerador de Timm & Schinner | github.com/TorstenTimm/SelfCitationTextgenerator; Zenodo 10.5281/zenodo.2531632 | 2019 | Implementação de referência, que o arXiv 2608.17096 descreve como Java; os autores desse artigo portaram-na para Python | ? | **Alta**: gerador pronto com parâmetros controláveis | I (citado em dois documentos; não abri) |
| Timm, artigo original sobre auto-cópia | [arXiv 1407.6639](https://arxiv.org/ftp/arxiv/papers/1407/1407.6639.pdf) | 2014 | Descrição do método | arXiv | Média | I |
| Rugg, "An elegant hoax?" (*Cryptologia*) | Não encontrei a fonte primária (só [bib Stolfi](https://ic.unicamp.br/~stolfi/EXPORT/bibliography/split-bib/2004/rug-04-voyn-cryp.bib)) | 2004 | Tabelas mais grelha de Cardano | Pago | Média: o código oficial não existe publicamente | I |
| Rugg & Taylor, "Hoaxing statistical features…" | Não encontrei a fonte primária | 2016 | Continuação do trabalho de 2004 | Pago | Baixa | I |
| Implementação Cardano, slot e Markov (Parisel) | repositório currier-signatures (ver lacuna 1) | 2026 | Grelha de Cardano nos modos random, shift, rotate e sequential; gerador de slots com 12 ablações; Markov de ordem 1 e 2 | ? | **Alta**: a única implementação aberta de Cardano que encontrei | V (descrição no artigo) |
| Gaskell & Bowern, "Gibberish after all?" | [CEUR Vol-3313 paper4](https://ceur-ws.org/Vol-3313/paper4.pdf); [README do repositório](https://raw.githubusercontent.com/danielgaskell/voynich/main/README.md) | 2022 | 42 amostras de gibberish escrito à mão por humanos (transcrições Unicode); 42 métricas sobre excertos de 200 palavras; classificador random forest gibberish vs. significativo; resultados completos | Código e dados: MIT modificado (obriga a citar o artigo) | **Alta**: verdade conhecida de "sem significado humano", mais uma bateria de métricas | V |

## Lacuna 4: palavras reais em ordem aleatória, nulos, homofónicas

| Nome | Link primário | Ano | O que oferece | Licença | Utilidade | V/I |
|---|---|---|---|---|---|---|
| Amancio et al., "Probing the statistical properties of unknown texts" | [arXiv 1303.0347](https://arxiv.org/pdf/1303.0347), [PMC3699599](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3699599/) | 2013 | Método: cada medida é normalizada pela média de 10 versões baralhadas (frequências mantidas); redes de coocorrência (clustering, caminhos, motivos); intermitência; Novo Testamento em 15 línguas. Sem código | PLoS ONE, CC BY | **Alta**: protocolo concreto para "ordem aleatória" | V |
| Hauer & Kondrak, anagramas | [ACL Q16-1006](https://aclanthology.org/Q16-1006/) | 2016 | Decifra cifras de substituição com letras baralhadas dentro da palavra; 93% de precisão por palavra (50 textos, 5 línguas) | ACL, CC BY | Média-alta | V |
| Aldarrab & May, "Can seq2seq models crack substitution ciphers?" | [arXiv 2012.15229](https://arxiv.org/pdf/2012.15229); [ACL 2021](https://aclanthology.org/2021.acl-long.561/) | 2021 | Testa ruído (inserções, apagamentos, substituições, o que se aproxima de nulos) sobre cifras 1:1 em 14 línguas. Dataset em github.com/NadaAldarrab/s2s-decipherment. Não trata homofónicas | ? | Média | V (artigo); I (dataset) |
| Kambhatla, Mansouri, Sarkar, cifras de substituição com modelos de língua neurais | [ACL D18-1102](https://aclanthology.org/D18-1102/) | 2018 | Pesquisa em feixe (beam search) com modelo de língua neural, incluindo homofónicas | ACL | Média | I |
| Nuhn, Schamper, Ney, homofónicas | [EMNLP 2014 PDF](https://mirror.aclweb.org/emnlp2014/papers/pdf/EMNLP2014184.pdf) | 2014 | Pesquisa em feixe para homofónicas | ACL | Média | I |
| Megyesi et al., "Historical Language Models in Cryptanalysis" | [HistoCrypt 2023](https://ecp.ep.liu.se/index.php/histocrypt/article/view/701) | 2023 | Homofónicas inglesas e alemãs com hill-climbing e simulated annealing; modelos históricos por século batem os modernos | CC BY 4.0 | Média-alta | V |
| CrypTool 2 (analisador de homofónicas, Kopal) | [cryptool.org/ct2](https://www.cryptool.org/ct2); [workshop PDF](https://www.cryptool.org/download/ct2/WS-2019_Breaking-Homophonic-Substitution-Ciphers-with-CrypTool-2.pdf) | 2019+ | Ferramenta para gerar e atacar homofónicas | Open source; Apache 2.0 só confirmado para o projeto em geral | Média: serve como solver de referência | I |

## Lacuna 5: métodos para distinguir língua natural de cifra/gibberish e para identificar a língua cifrada

| Nome | Link primário | Ano | O que oferece | Licença | Utilidade | V/I |
|---|---|---|---|---|---|---|
| Montemurro & Zanette, "Keywords and co-occurrence patterns…" | [PMC3689824](https://pmc.ncbi.nlm.nih.gov/articles/PMC3689824) | 2013 | Palavras-chave por informação da distribuição entre secções, com significância contra texto baralhado; redes de cosseno. Controlos: Agostinho (latim), Darwin, Sima Qian, código Fortran, ADN de levedura. Sem código | CC BY | **Alta**: os controlos não-linguísticos (Fortran, ADN) são ótimos | V |
| Hauer & Kondrak, identificação de língua de texto cifrado | [ACL Q16-1006](https://aclanthology.org/Q16-1006/) | 2016 | 3 métodos para identificar a língua de uma cifra monoalfabética; 97% em 380 línguas. Sem código listado | CC BY | **Alta**: é exatamente a tarefa | V |
| Reddy & Knight, "What we know about the Voynich manuscript" | [ACL W11-1511](https://aclanthology.org/W11-1511/) | 2011 | Bateria de testes (entropia, comprimento de palavra, relação com a página) contra várias línguas | ACL | Média | I |
| Bowern & Lindemann, "The linguistics of the Voynich manuscript" | [PDF Yale](https://alumniacademy.yale.edu/sites/default/files/2021-07/The%20Linguistics%20of%20the%20Voynich%20Manuscript.pdf) | 2021 | Revisão crítica de métodos e erros comuns | Annual Review | Média: lista de armadilhas | I |
| Gaskell & Bowern | ver lacuna 3 | 2022 | Classificador gibberish vs. significativo mais 42 métricas | MIT modificado | **Alta** | V |
| Parisel | ver lacuna 1 | 2026 | 4 assinaturas posicionais como referência para geradores | ? | Alta | V |
| Matlach et al., "The Voynich manuscript: Symbol roles revisited" | [PMC8794160](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8794160/) | 2022 | Papéis posicionais dos símbolos (a página não abriu) | PLoS, CC BY | Média | I |
| Sterneck, Polish, Bowern, "Topic Modeling in the Voynich Manuscript" | [arXiv 2107.02858](https://arxiv.org/abs/2107.02858v1) | 2021 | Modelação de tópicos | arXiv | Baixa | I |

## Lacuna 6: agentes e ferramentas com LLM e verificação por código

| Nome | Link primário | Ano | O que oferece | Licença | Utilidade | V/I |
|---|---|---|---|---|---|---|
| **ms408** (Tim Walsh / DireLabs) | [PyPI](https://pypi.org/project/ms408/); [releases](https://github.com/DireLabs/ms408/releases) | v0.1 a 4 ago. 2026; v0.2 a 11 set. 2026 | Avaliador reprodutível de hipóteses: `python -m ms408.verify` recalcula os números publicados; fontes fixadas por checksum com registo de licenças; geradores de controlo (língua real, auto-cópia, tipo Naibbe, nulos/sem significado, posicionais); afirmações graduadas de A a D; protocolo de revisão adversarial com LLM. Limitações declaradas: 25 de 36 experiências não se regeneram; Zipf passou a eixo só consultivo porque o intervalo de confiança era enviesado | Apache 2.0 | **Alta como arquitetura**, mas as bandas de referência são do Voynich e não podemos usá-las como critério | V |
| Projeto Megyesi, "Historical language models and cipher type detection" (NAISS) | [supr.naiss.se](https://supr.naiss.se/public/project/36901/) | fev. 2026 – fev. 2027 | Projeto em curso: reconhecimento de escrita, deteção de língua, adaptação de LLM, decifração. Sem código público | – | Média: vale a pena seguir | V |
| DECRYPT, Cifra Borg | [notícia](https://letsdatascience.com/news/swedish-ai-decodes-17th-century-borg-cipher-38671b24) | jun. 2026 | Pipeline com TranscripTool, CrypTool, DECODE e HistCorp; sem código ligado | – | Baixa | I |
| AICrypto | [arXiv 2507.09580](https://arxiv.org/abs/2507.09580); github.com/wangyu-ovo/aicrypto-agent | 2025–26 | Benchmark de criptografia moderna para LLMs | ? | Baixa: não é criptografia clássica | V |
| Maskey et al., benchmark de criptoanálise com LLMs | [arXiv 2505.24621](https://arxiv.org/pdf/2505.24621v1.pdf) | 2025 | Cifras clássicas simples; só uma amostra do dataset está disponível | ? | Baixa-média | V |
| CipherBank | [arXiv 2504.19093](https://arxiv.org/pdf/2504.19093) | 2025 | Benchmark de raciocínio sobre cifras | ? | Baixa | I |
| OracleAgent | [arXiv 2510.26114](https://arxiv.org/html/2510.26114v1) | 2025 | Agente LLM com ferramentas para escrita em ossos oraculares; código prometido; não executa código | ? | Baixa: só como padrão de orquestração | V |
| Shih et al., "Reasoning Over the Glyphs" | [arXiv 2501.17785](https://arxiv.org/html/2501.17785v1) | 2025 | Avaliação de LLMs em escritas raras; dados prometidos | – | Baixa | V |

Contraexemplos (o que não queremos ser): no fórum Voynich Ninja, uma alegada decifração gerada por LLM foi fechada e o link GitHub dava 404 ([tópico 5118](https://www.voynich.ninja/archive/index.php/thread-5118.html)). Há também depósitos Zenodo com alegações não verificadas (por exemplo [19574356](https://zenodo.org/records/19574356), licença CC BY-NC-ND). Não encontrei nenhum agente LLM publicado que faça análise linguística e cripto genérica com recálculo obrigatório por código além do `ms408`.

## Lacuna 7: corpora longos multilíngues de domínio público

| Nome | Link primário | Ano | O que oferece | Licença | Utilidade | V/I |
|---|---|---|---|---|---|---|
| **HistCorp** (Pettersson / Uppsala) | [sprakbanken-clarin.lingfil.uu.se/histcorp](https://sprakbanken-clarin.lingfil.uu.se/histcorp/) | 2018+ | 17 línguas históricas, incluindo **português**, latim, italiano, alemão e outras; texto simples, tokenizado e normalizado, descarregável via Zenodo; alguns corpora não são descarregáveis | Por corpus: sobretudo CC; algumas "free for research" | **Alta**: texto histórico real, próximo das cifras de época | V |
| Perseus canonical (latim, grego e outras) | [github.com/PerseusDL/canonical](https://github.com/PerseusDL/canonical) | contínuo | TEI XML, agora repartido por língua | CC BY-SA 3.0 US, salvo indicação | Alta: textos latinos longos | V |
| Project Gutenberg | [gutenberg.org/license](https://gutenberg.org/license) | – | Dezenas de milhares de livros, muitas línguas | Livre nos EUA se se retirar a licença e todas as menções a PG. Fora dos EUA: confirmar a lei portuguesa (morte do autor + 70 anos) | Alta | V |
| eBible / BibleNLP | [github.com/BibleNLP/ebible](https://github.com/BibleNLP/ebible) | contínuo | Corpus paralelo, um versículo por linha, alinhado | Por tradução, em metadata/licenses | Alta: o paralelismo permite comparar línguas com o mesmo conteúdo | V |
| UDHR in Unicode | [HF udhr](https://huggingface.co/datasets/community-datasets/udhr) | – | Declaração Universal dos Direitos Humanos em cerca de 400 línguas (base de Hauer & Kondrak) | Copyright OHCHR mais licença Unicode | Média: textos curtos, só para identificação de língua | V |
| Leipzig Corpora Collection | [wortschatz.uni-leipzig.de](https://wortschatz.uni-leipzig.de/en/download) | – | Frases em muitas línguas | Não confirmei: página bloqueada por anti-bot | Média: são frases soltas, não texto contínuo | I |
| DECODE (cifras históricas) | [HistoCrypt 2022](https://ecp.ep.liu.se/index.php/histocrypt/article/view/397) | 2022 | Cifras, chaves e documentos anotados | Artigo CC BY; licença da base não indicada | Média: complemento ao Cipher Corpus | V |

---

## As 5 recomendações mais úteis, por ordem

1. **Gaskell & Bowern 2022 (repositório danielgaskell/voynich).** É o único dataset aberto de gibberish humano com verdade conhecida. Traz 42 métricas e um classificador random forest, e a licença é permissiva. Serve de imediato como classe negativa e como teste de regressão das nossas métricas.
2. **Geradores mecânicos: Timm & Schinner (GitHub/Zenodo 2531632) e repositório currier-signatures de Parisel (Cardano, slots, Markov, controlos baralhados).** Com sementes e parâmetros conhecidos, o agente tem de descobrir que "não há texto simples". Devemos usá-los com vocabulários de origem nossos, não do Voynich.
3. **Naibbe (Greshko, *Cryptologia* 2025, acesso aberto, tabelas e código em greshko/naibbe-cipher).** É a única cifra verbosa homofónica bem documentada que encontrei. Devemos cifrar textos de HistCorp e Perseus e avaliar se o agente recupera a segmentação de 1/2 letras e a língua. As tabelas originais estão afinadas ao Voynich, por isso convém também criar variantes com tabelas aleatórias.
4. **Hauer & Kondrak 2016, UDHR e eBible.** Juntos formam um protocolo de identificação da língua de um texto cifrado com verdade conhecida em centenas de línguas. Os testes de ruído de Aldarrab & May 2021 cobrem os nulos.
5. **`ms408` (Apache 2.0) como modelo de arquitetura, não de dados.** Copiar o recálculo por `verify`, as fontes fixadas por checksum com licenças, a graduação A–D e a revisão adversarial com LLM. Descartar explicitamente as bandas de referência do Voynich. Os geradores de controlo podem ser reutilizados depois de os auditarmos.

Como corpus base de texto simples, sugiro **HistCorp** (inclui português histórico) mais **Perseus**, e Gutenberg/eBible para textos de dezenas de milhares de palavras.

**Por fazer:** confirmar no browser os repositórios GitHub e Zenodo que não consegui abrir (Naibbe, Timm, Rozanova, currier-signatures, o repositório principal do `ms408`) e a licença do artigo do Naibbe.
---

## Auditoria inicial do Cipher Corpus v0.6 (19/10/2026, aprovada pelo Bruno)

Descarregados do Zenodo (registo 23297920, CC0 para os registos sintéticos) os 12 ficheiros do depósito (≈ 105 MB), todos com md5 conforme. Os dados ficam fora do repositório; esta secção regista só agregados.

| Ponto | Resultado |
|---|---|
| Registos | 100 326 (100 272 sintéticos, 54 históricos); 85 tipos |
| Comprimento (letras, sem espaços) | mediana 48; 90% ≤ 143; 414 registos ≥ 300; 5 ≥ 1000; máximo 1065 |
| Espaços entre palavras | retirados em 74 327 (74%); preservados em 25 996 |
| Línguas | inglês 96 671 (96%); latim, alemão, espanhol, francês ≈ 800 cada; italiano 480 |
| Texto simples distintos | só **882** para 100 326 registos; o mais repetido aparece 522 vezes |
| Fuga entre partições | **499 dos 882** textos simples aparecem tanto em `public` como em `blind` |
| Tipos que cabem nas nossas hipóteses | 18 de 85 (SUB 5, POL 8, TRA 5), 39 596 registos |
| … desses, com ≥ 300 letras | **0** (SUB, POL e TRA) |
| … com espaços preservados | SUB 14 285 de 14 329; POL 373 de 16 302; TRA 34 de 8 965 |
| Verificação independente (Vigenère, nosso código) | 4 835 decifram exatamente; 142 não (por ver: o corpus declara 526 desvios conhecidos) |
| VER, TAB, BAR, NUL (no nosso sentido) | ausentes; `null_cipher` (234) é esteganografia, não nulos inseridos; `homophonic` 107 |

**Previsões de 06:14:** (1) textos curtos: **confirmada**, e pior do que previ (nenhum registo das nossas famílias chega a 300 letras); (2) sem espaços: **confirmada** (74%); (3) 20–40% dos tipos cabem: **confirmada** (18/85 = 21%); (4) VER/TAB/BAR/NUL ausentes: **confirmada**; (5) risco de memorização: agravado pela repetição de textos simples; (6) qualidade: as soluções verificáveis decifram em 97% dos Vigenère testados.

**Decisão proposta.** O Cipher Corpus serve só para um teste auxiliar de **identificação de tipo em textos curtos**, com partições refeitas por texto simples (as `public`/`blind` do corpus não são independentes). Não serve para as medidas linguísticas nem para as hipóteses do manuscrito. O corpus principal tem de ser texto longo (HistCorp, Perseus, Gutenberg) cifrado por nós e pelos geradores da lacuna 2–4.


---

## Porque é que o agente não investiga: o que outros projetos fazem (pesquisa de 19/10, 06:50)

Encontrei padrões suficientes para três opções sustentadas, mas a base empírica é mais fraca do que parece. Nenhuma fonte testa o nosso caso exato: modelo sem raciocínio, uma tarefa de classificação com ferramentas e a resposta "indeterminada" como saída fácil. Não descarreguei nem corri nada.

Três notas antes da tabela:
- **V** quer dizer que li a página original (resumo do arXiv, página HTML, PyPI ou README). **I** quer dizer que só vi o título ou o link nos resultados de pesquisa, ou que é conhecimento geral.
- A ferramenta de leitura bloqueou três páginas do GitHub (snap-stanford/POPPER, DireLabs/ms408) e o HTML do POPPER no arXiv. Por isso não confirmei os pormenores nem as licenças do POPPER e do ms408.
- O ms408 avalia hipóteses sobre o Manuscrito Voynich (Beinecke MS 408). É o projeto mais próximo do nosso domínio.

## Tabela

| # | Nome | Link primário | Ano | Mecanismo concreto | Evidência quantitativa | Licença | Utilidade | V/I |
|---|---|---|---|---|---|---|---|---|
| 1 | POPPER (snap-stanford) | [arXiv 2502.09858](https://arxiv.org/abs/2502.09858) · [PMLR v267](https://proceedings.mlr.press/v267/huang25n.html) | 2025 (ICML) | Por cada hipótese, um agente desenha experiências de falsificação sobre as consequências mensuráveis e outro corre-as. O teste sequencial acumula evidência e controla o erro de tipo I, e só pára quando há evidência suficiente para rejeitar. | Comparável a cientistas humanos em hipóteses biológicas; validação ~10× mais rápida; 6 domínios. Não confirmei os números de potência e erro. | Não verificada | **Alta**: a regra de paragem passa a ser estatística e deixa de depender da vontade do LLM. | V (resumo); repositório não lido |
| 2 | ms408 (DireLabs, Tim Walsh) | [PyPI ms408](https://pypi.org/project/ms408/) · repositório [github.com/DireLabs/ms408](https://github.com/DireLabs/ms408) | 2025–26 (v0.2.0) | Avaliador "frio" e reprodutível. Recebe ≥ ~1000 tokens e compara-os com bandas de referência separadas por dialeto Currier A/B. Por cada eixo dá valor, banda e se está dentro dela, com ressalvas. Conta só os eixos "hard" dentro da banda (exclui os confundidos, "soft" e consultivos) e dá o dialeto mais próximo. Não há pontuação única: cada afirmação tem um grau de evidência de A a D. "Cumprir as bandas é necessário, não suficiente." Há um protocolo de revisão adversarial por um LLM, apresentado "como disciplina, não oráculo". | Nenhuma publicada | Apache-2.0 (PyPI) | **Alta**: é uma bateria fixa de eixos aplicada sempre, e o LLM fica fora do cálculo. | V (PyPI); a página não diz explicitamente se a bateria é fixa |
| 3 | Agents Explore but Agents Ignore | [arXiv 2604.17609](https://www.alphaxiv.org/abs/2604.17609) | 2026 | Põe uma solução completa no ambiente do agente e mede se a descobre e se a usa. | Terminal-Bench: descobrem 79–81%, usam 37–50%. AppWorld (gpt-oss-120b): descobre 97,5%, usa 0,53%. Raciocínio alto ≈ 3× mais uso. Quando lhes dizem explicitamente para usar, o sucesso sobe muito. | n/d | **Alta**: é exatamente o nosso sintoma (a medida estava lá e não foi usada) e confirma o efeito do modo de raciocínio. | V (alphaXiv) |
| 4 | LLMs Think Too Fast To Explore Effectively | [arXiv 2501.18009](https://arxiv.org/abs/2501.18009v2) | 2025 (NeurIPS) | Análise com autoencoders esparsos: os modelos decidem nas camadas iniciais, com base na incerteza, antes de pesar o valor de ganhar opções ("empowerment"). | Só o o1 supera os humanos a explorar; o DeepSeek de raciocínio explora mais. Não há números no resumo. | n/d | **Média**: explica o mecanismo, mas não dá solução. | V (resumo) |
| 5 | Do Reasoning Models Ask Better Questions? | [arXiv 2601.17716](https://arxiv.org/html/2601.17716) | 2026 | Jogo de perguntas sim/não; mede o ganho de informação (IG) por turno com e sem cadeia de raciocínio (CoT). | Qwen3-8B com CoT: vitórias 0,94 e IG 0,41/turno. Sem CoT: 0,08 e 0,17. | n/d | **Alta**: quantifica o efeito que já vimos. Tem um só domínio. | V |
| 6 | Uncertainty of Thoughts (UoT) | [NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/2b0e14abd8128e6bf98b6b0bec1cfcbf-Abstract.html) · [arXiv 2402.03271](https://web3.arxiv.org/pdf/2402.03271v2) | 2024 | Simula cenários com probabilidades, recompensa o ganho de informação e escolhe a pergunta que maximiza a recompensa esperada. | +38,1% de sucesso face ao prompting direto, com menos perguntas. | Não verificada | **Média-alta**: no nosso caso o ganho de informação de cada medida por hipótese pode ser calculado por código. | V (resumo) |
| 7 | Calibrate-Then-Act | [arXiv 2602.16699](https://www.opentrain.ai/papers/calibrate-then-act-cost-aware-exploration-in-llm-agents--arxiv-2602.16699) | 2026 | Dá ao agente uma distribuição prévia sobre o estado latente para pesar o custo de explorar mais contra o custo de errar. | Não há números na página que li. | n/d | **Média**: a ideia de dar a distribuição prévia é barata de testar. | V (página secundária) |
| 8 | AutoDiscovery | [arXiv 2507.00310](https://arxiv.org/abs/2507.00310) | 2025 (NeurIPS) | Pesquisa em árvore Monte Carlo sobre hipóteses; a recompensa é a "surpresa bayesiana" (mudança entre a crença antes e depois). | 5–29% mais descobertas com orçamento fixo; ~2/3 surpreendentes para especialistas. | Não verificada | **Média**: o critério de mudança de crença é útil. A pesquisa em árvore é excessiva para nós. | V (resumo) |
| 9 | Data Interpreter (MetaGPT) | [arXiv 2402.18679](https://arxiv.org/html/2402.18679v1) | 2024 | Grafo hierárquico de tarefas, plano dinâmico regenerado após cada tarefa, ferramentas recomendadas por tipo de tarefa e verificação do resultado com código. | Ablação: o plano dinâmico subiu de 0,37 para 0,85 e as ferramentas para 0,94. Tarefas abertas: 0,97 contra 0,46 do AutoGen. | Não verificada (o código está no MetaGPT) | **Alta**: mostra que o plano explícito é o que mais pesa. | V |
| 10 | s1 budget forcing | [arXiv 2501.19393](https://arxiv.org/abs/2501.19393v2) | 2025 | Quando o modelo tenta parar, acrescenta-se "Wait" e ele continua e corrige-se. | AIME24 de 50% para 57%. | Não verificada | **Média**: é análogo a recusar o "indeterminada" e obrigar a mais um passo. | V |
| 11 | DS-Agent | [arXiv 2402.17453](https://arxiv.org/abs/2402.17453v1) | 2024 (ICML) | Raciocínio por casos: recupera planos de casos anteriores e revê-os com feedback da execução. | Não li números | Não verificada | **Média**: equivale a dar ao agente sequências de medidas que já resolveram casos parecidos. | I |
| 12 | Agent Laboratory | [GitHub](https://github.com/SamuelSchmidgall/AgentLaboratory) · [arXiv 2501.04227](https://arxiv.org/abs/2501.04227v1) | 2025 | Três fases fixas (revisão de literatura, experiências, relatório); o humano guia por notas de tarefa. | Não há números no README | MIT | **Baixa**: não tem um mecanismo que force experimentação. | V (README) |
| 13 | AI Scientist (Sakana) e a sua avaliação | [arXiv 2502.14297](https://arxiv.org/pdf/2502.14297) | 2024–25 | Ciclo ideia, código, experiência, artigo. A avaliação independente descreve "resultados mistos". | Não li números | n/d | **Baixa**: só serve como alerta de que a autonomia sozinha não garante investigação. | I |
| 14 | ToolFailBench | [arXiv 2607.04686](https://arxiv.org/abs/2607.04686) | 2026 (ICML) | Taxonomia de falhas: "Tool-Skip" (não chamar uma ferramenta necessária) e "Result-Ignore" (chamar e não usar o resultado). | 19 modelos; o melhor tem 86,3% de uso limpo. | n/d | **Média**: dá-nos categorias para etiquetar as 72 amostras. | V (resumo) |
| 15 | ReAct / Reflexion / plan-and-execute | ReAct arXiv 2210.03629; Reflexion arXiv 2303.11366 | 2022–23 | Alternância raciocínio–ação; autocrítica verbal entre tentativas; planear antes de executar. | Conhecidos, não os verifiquei agora | — | **Baixa-média**: sem raciocínio, o ReAct é o que já temos. | I |
| 16 | When May an Agent Stop? Evidence-Carrying Termination | [arXiv 2608.23623](https://arxiv.org/pdf/2608.23623) | 2026 | Pelo título: só se pode terminar se a paragem vier acompanhada de evidência. | Não consegui ler o PDF | n/d | **Potencialmente alta**, mas não verificada. | I |

## As 3 opções de desenho mais sustentadas, por ordem

**1. A bateria fixa corre em código e o LLM só interpreta (modelo ms408 com plano explícito, à Data Interpreter)**
- **Base:** o ms408 aplica todos os eixos sempre e conta só os "hard". O Data Interpreter mostra que o plano explícito é o fator principal (0,37 para 0,85). O "Agents Ignore" mostra que o modelo não usa espontaneamente o que tem, mas usa-o bem quando o recebe pronto.
- **O que mudar:** antes do LLM, o código corre todas as medidas (entropia, índice de coincidência, Kasiski, Zipf, dependência, posições, …) e produz uma tabela por hipótese com valor, banda de referência, dentro ou fora e grau de evidência. O LLM recebe a tabela e só redige os veredictos. "Indeterminada" só é permitida quando nenhum eixo "hard" separa as hipóteses, e o verificador por código confirma essa condição.
- **Previsão testável:** nas 72 amostras, "indeterminada" desce para perto da fração em que a bateria de facto não discrimina, que se pode calcular à parte. Nos casos em que a medida discriminante existia, a exatidão sobe para níveis próximos do modo com raciocínio. Se não subir, o problema está na interpretação e não na recolha de evidência.

**2. Falsificação sequencial com regra de paragem em código (POPPER e budget forcing)**
- **Base:** POPPER, s1 e o efeito do raciocínio nos itens 3 e 5.
- **O que mudar:** quem decide se o agente pode parar passa a ser o código. Por cada hipótese ainda viva, o agente tem de propor um teste que a possa falsificar. O código executa-o e acumula um valor-e ou uma razão de verosimilhança. Uma resposta prematura ou um "indeterminada" sem evidência suficiente é devolvido com a lista das medidas ainda não pedidas, ao estilo do "Wait". Fixa-se um mínimo de medidas e um orçamento máximo.
- **Previsão testável:** a média de medidas por caso sobe de 2,3 para ≥ 5, e a variedade de medidas pedidas aumenta (deixa de ser sempre o mesmo par). A exatidão sobe menos do que na opção 1 se o modelo continuar a interpretar mal. O controlo do erro de tipo I mantém-se, o que se testa com textos-controlo de hipótese conhecida.

**3. O código escolhe a próxima medida pelo ganho de informação (UoT, Calibrate-Then-Act, AutoDiscovery)**
- **Base:** UoT (+38%) e a diferença de ganho de informação com e sem CoT no item 5.
- **O que mudar:** com distribuições de referência por tipo de cifra, o código calcula para cada medida não pedida o ganho de informação esperado sobre a distribuição atual das hipóteses. Ou mostra o ranking ao LLM, ou corre ele próprio a melhor medida. É uma versão adaptativa da opção 1, mais barata quando as medidas são caras.
- **Previsão testável:** com o mesmo número de medidas da opção 1 (ou menos), a exatidão é equivalente, e a entropia da distribuição das hipóteses desce mais por medida do que com a escolha do LLM. Se as medidas forem baratas, a vantagem sobre a opção 1 desaparece. Nesse caso fica-se pela opção 1.

Antes de mudar, o passo mais barato é etiquetar as 72 amostras com as categorias do ToolFailBench ("Tool-Skip" contra "Result-Ignore"). Isso diz se o problema é recolher a evidência (opções 2 e 3) ou interpretá-la (opção 1 com veredictos fixados por regras).


---

## Baterias de medidas para identificar cifras e texto sem significado (pesquisa de 19/10, 06:50)

Encontrei o que existe e verifiquei nas fontes a maior parte do que se segue, mas há quatro lacunas a ter em conta:

- **Parisel 2026 "currier-signatures":** não encontrei. As pesquisas não devolveram nenhum repositório nem artigo com esse nome.
- **Precisão por classe:** nenhuma fonte a reporta para as nossas 9 famílias. Só há números globais (NCID) e alguns números por classe de um projeto anterior (CANN).
- **Detetor de nulos:** nenhuma fonte tem um detetor publicado de nulos inseridos dentro das palavras.
- **Rugg e CrypTool 2:** não consegui verificar a referência primária de Rugg nem a lista de componentes "Analysis" do CrypTool 2.

V = verificado na fonte; I = indireto (resultado de pesquisa, resumo de terceiros ou memória).

| Item | Link primário | Ano | Medidas / features | Precisão reportada | Licença | Utilidade (nulos / tabela / baralhado) | V/I |
|---|---|---|---|---|---|---|---|
| **NCID** (Leierzopf, Kopal, Esslinger, Lampesberger, Hermann), "A Massive Machine-Learning Approach For Classical Cipher Type Detection Using Feature Engineering", HistoCrypt | [artigo](https://ecp.ep.liu.se/index.php/histocrypt/article/view/164) · [PDF](https://ecp.ep.liu.se/index.php/histocrypt/article/download/164/120) · [código](https://github.com/ernstleierzopf/ncid) · [online](https://legacy.cryptool.org/en/cto/ncid) | 2021 | Tabela 5, com 32 siglas (o texto diz que 28 foram implementadas): FREQ, SDD, CHI2, LDI, RDI, IoC, DIC, SHAN (entropia), NOMOR, REP (n=2..5), LR (long repeat), AUTO (autocorrelação), MIC (IoC máximo, períodos 1–15), BDI, CDD, NIC, SSTD, MKA (kappa máximo, desvios 1–15), PHIC, DBL ("has double letters"), HAS 0/H/J/X/SP, A_/B_/P_/S_/V_LDI, PTX, ROD (repetições com espaçamento ímpar). O melhor conjunto tem 20 features. | Só global. FFNN 80,24%; RF 71,15%; RF pequeno 74,35%; árvores 61,68%; Naive Bayes 54,17%. 56 classes ACA (55 cifras + texto claro). | GPLv3, com restrições adicionais no README: não comercial e publicação na web só com autorização. | Baixa / baixa / baixa. É ao nível do carácter, sem palavras nem classe "sem significado", e foi treinado com 100 caracteres de inglês do Gutenberg. | V |
| Tese de mestrado de Leierzopf (NCID) | [PDF](https://www.cryptool.org/media/publications/theses/MA_Leierzopf.pdf) | I (≈2021) | As mesmas features | FFNN 78,31%, ensemble 82,78% (10 milhões de registos de teste). Por classe, só no projeto anterior CANN: transposição e substituição simples >99%, Playfair >95%; Hill e Vigenère confundem-se entre si. | Não indicada | Baixa / baixa / baixa | V |
| **Dataset ACA** | Não há um dataset ACA descarregável: o NCID gera os cifrados na hora a partir do Gutenberg, segundo as definições de tipos da ACA. | — | 56 tipos | — | — | Baixa | V |
| **dCode Cipher Identifier** | [dcode.fr/cipher-identifier](https://dcode.fr/cipher-identifier) | atual | Frequências de 1-, 2- e 3-gramas, IC, "assinaturas" (por exemplo Base64), repetições, comprimento de palavra. Rede MLP sobre n-gramas. | Não reporta números. Diz que deteta "mais de 300" cifras, e noutro ponto da mesma página "mais 200" (inconsistente). | Código proprietário e fechado; o conteúdo e os resultados podem ser reutilizados em CC-BY. | Baixa / baixa / baixa | V |
| **Estatísticas ACA / BION** (implementadas no CryptoCrack) | [CryptoCrack Identify](https://www.sites.google.com/site/cryptocrackprogram/user-guide/tools-tab/identify-cipher). Fonte primária: BION, "Reference Statistics", *The Cryptogram*, mai–jun 2005 (não consultada). | 2005 | IC×1000; MIC (IC máximo, períodos 1–15); MKA (kappa máximo, 1–15); DIC×10000; EDI (DIC dos pares pares); raiz da % de repetições de trigramas; % de repetições com espaçamento ímpar (=ROD); log-digrama médio (=LDI, tabela de AAHJU, 2001); discrepância letra/digrama (≈SDD). LR, ROD, LDI e SDD aparecem definidos no NCID. | Não reportada | Freeware; licença não indicada | Baixa / baixa / baixa. Úteis só para Vigenère e transposição. | V (página); I (artigo BION) |
| **CrypTool 2**, componentes de análise | [cryptool.org](https://www.cryptool.org) | — | Não verifiquei a lista de componentes. | — | I: open source | Baixa | I |
| **Gaskell & Bowern**, "Gibberish after all? Voynichese is statistically similar to human-produced samples of meaningless text" | [CEUR Vol-3313 paper4](https://ceur-ws.org/Vol-3313/paper4.pdf) · [repositório](https://github.com/danielgaskell/voynich) | 2022 | 42 métricas, listadas a seguir à tabela. Corpus de texto sem significado escrito à mão por humanos. | Não há precisão numérica; só a figura 2 e "low confidence". | "Modified MIT": citação obrigatória. Os dados de texto com significado e os dados Voynich têm licença à parte. | **Alta / alta / média** | V |
| **Amancio, Altmann, Rybski, Oliveira Jr, Costa**, "Probing the statistical properties of unknown texts" | [arXiv 1303.0347](https://ar5iv.arxiv.org/html/1303.0347) | 2013 | Vocabulário M; frequência; seletividade s_i; bigramas repetidos B; intermitência I_i; rede de adjacência (assortatividade r, clustering C, caminho médio L, diâmetro d, 13 motivos). **Normalização: cada medida a dividir pela média de 10 versões baralhadas por palavras**; um valor próximo de 1 indica uma medida sem informação. As mais discriminantes são assortatividade, grau e seletividade. | Sem precisão | Sem código visível | Baixa / média / **alta** | V |
| **Montemurro & Zanette**, "Keywords and Co-Occurrence Patterns in the Voynich Manuscript", PLoS ONE 8(6): e66344 | [PMC3689824](https://pmc.ncbi.nlm.nih.gov/articles/PMC3689824) | 2013 | Informação mútua entre palavras e secções de comprimento s, **menos a mesma quantidade em texto baralhado**, decomposta por palavra (palavras-chave). Depende da escala s. | Sem precisão | Sem código visível | Baixa / **alta** / **alta** | V |
| **Lin & Tegmark**, "Criticality in Formal Languages and Statistical Physics", Entropy 19, 299 | [arXiv 1606.06737](https://arxiv.org/abs/1606.06737v2) | 2016/2017 | Decaimento da informação mútua I(d) com a distância d: lei de potência na língua natural e decaimento exponencial em processos de Markov. | Sem precisão | — | Baixa / **alta** / média | I (título, link e ano vêm da pesquisa; não li o PDF) |
| **Timm**, "How the Voynich Manuscript was created" (arXiv); **Timm & Schinner**, "A possible generating algorithm of the Voynich manuscript", *Cryptologia* | [perfil Timm](https://independent.academia.edu/TorstenTimm) | 2014; 2020 | Rede de palavras com distância de edição 1; distância média de string em função da distância entre linhas; palavras iguais ou semelhantes nas 20 linhas anteriores; Zipf 1.ª e 2.ª leis; flutuação RMS de passeio aleatório; distribuição de comprimentos. Em 2026: correlação entre a frequência de uma palavra e o número de formas semelhantes. | Sem precisão | — | Baixa / **alta** (auto-cópia) / média | V (página); I (coautoria de Schinner) |
| **Rugg**, Cryptologia ("An elegant hoax?"), grelha de Cardano | [Wikipedia](https://en.wikipedia.org/wiki/Gordon_Rugg) · [análise crítica de Schmeh](https://scienceblogs.de/klausis-krypto-kolumne/2016/10/26/has-gordon-rugg-solved-the-mystery-of-the-voynich-manuscript-text-part-1/?all=1) | I: 2004 | É um método de geração, não uma bateria de medidas. | — | — | Média (gerar dados de teste da família "tabela") / — | I |
| **Parisel 2026, currier-signatures** | não encontrado | — | — | — | — | — | — |
| **Benchmark por classe para as nossas 9 famílias** | não existe | — | — | — | — | — | — |

**As 42 métricas de Gaskell & Bowern (V):**
- **Posição do carácter:** charbias_mean/std/skew, charbias_words_mean/std/skew.
- **Distribuição de caracteres:** chardist_max/shape.
- **Compressão e entropia:** compression, entropy.
- **Pares e n-gramas:** flipped_pairs, ngramdist_max/shape.
- **Repetições:** repeated_chars, tripled_chars, repeated_words, tripled_words.
- **Contagens únicas:** unique_chars, unique_ngrams, unique_words.
- **Posição da palavra:** wordbias_lines_mean/std/skew, wordbias_mean/std/skew.
- **Mudança entre palavras:** wordchange_mean/std/skew.
- **Distribuição de palavras:** worddist_max/shape.
- **Comprimento de palavra:** wordlen_autocorr, wordlen_mean/std/skew, wordlen_unique_mean/std/skew.
- **Unicidade de palavras:** wordunique_mean/std/skew.
- **Zipf:** zipf.

O random forest deles destaca como mais importantes para separar texto sem significado: charbias_mean, wordbias_mean, wordbias_skew, wordbias_std, compression, repeated_words, repeated_chars, charbias_words_skew, charbias_std e wordlen_autocorr. Segundo os autores, o texto sem significado tende a ter menos informação, mais repetição, mais viés de posição, autocorrelação positiva dos comprimentos de palavra e pior ajuste a Zipf. Alguns exemplos, porém, coincidem com a língua natural em quase todas as métricas. O corpus de texto sem significado pode servir como dado de desenvolvimento; os dados Voynich do repositório devem ficar de fora.

**Medidas candidatas a acrescentar:**

1. **Razão medida/baralhado (normalização de Amancio).** Aplicar às nossas medidas de dependência entre palavras, como h2 entre palavras, assortatividade e clustering da rede de adjacência. Um valor próximo de 1 indica ordem aleatória. Resolve **baralhado**.
2. **Informação de palavras por secção menos baralhado (Montemurro & Zanette).** Num texto baralhado fica próxima de 0. Num texto gerado por tabela, a distribuição tende a ser homogénea ou a ter estrutura atípica. Resolve **baralhado e tabela**.
3. **Curva de decaimento I(d) (Lin & Tegmark),** ao nível do glifo e da palavra. Distinguir lei de potência de decaimento exponencial ou cauda nula. A cauda é nula entre palavras no texto baralhado e exponencial num gerador por tabela tipo Markov. Resolve **tabela e baralhado**.
4. **wordbias_* e wordbias_lines_*** (Gaskell & Bowern): viés de posição da palavra na secção e na linha. Resolve **tabela**.
5. **charbias_words_*** (Gaskell & Bowern): viés de posição do glifo dentro da palavra. Na substituição simples mantém-se o perfil da língua; os nulos inseridos achatam ou deslocam esse perfil. Resolve **nulos**, mas é proposta nossa: a fonte não a testa para nulos.
6. **wordlen_mean/std/skew e wordlen_autocorr** (Gaskell & Bowern). Os nulos alongam as palavras e alargam a distribuição de comprimentos sem alterar a ordem das palavras. A autocorrelação também ajuda na tabela. Resolve **nulos e tabela**.
7. **compression, repeated_words, tripled_words, flipped_pairs, wordchange_*** (Gaskell & Bowern): repetição e mudança local, típicas de texto gerado. Resolve **tabela**.
8. **Vizinhança por distância de edição 1** (Timm; Timm & Schinner): proporção de palavras com uma palavra a distância 1 nas 20 linhas anteriores, e correlação entre a frequência de uma palavra e o número de formas semelhantes. Deteta auto-cópia e geração por grelha. Resolve **tabela**.
9. **unique_ngrams e DIC/SDD** (Gaskell & Bowern; NCID/BION), calculados dentro das palavras. Os nulos diluem a estrutura de digramas em relação à substituição simples. Resolve **nulos**, de forma fraca. Também é proposta nossa: nenhuma fonte valida isto para nulos.
10. **MKA/MIC/ROD** (NCID/BION): só servem para separar Vigenère e transposição. **Não** resolvem nenhuma das três falhas.

Para os nulos não há medida publicada e validada. Os pontos 5, 6 e 9 são extrapolações. Para treinar e testar, o caminho é gerar nós próprios o corpus de nulos e o corpus de tabela (com grelha à Rugg ou auto-cópia à Timm).

Fontes: as ligações estão na tabela; a pesquisa de Parisel 2026 não devolveu resultados relevantes.
