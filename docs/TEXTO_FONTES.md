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