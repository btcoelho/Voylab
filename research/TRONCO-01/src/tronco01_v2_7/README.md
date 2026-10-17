# TRONCO-01 v2.7 — verificação pré-modelo

Esta cópia integra as verificações semânticas, testa o percurso completo do runner com saídas fixas e fecha a cobertura dos ficheiros e versões do runtime. Pára no ponto obrigatório de análise; não carrega pesos nem executa inferência.

## Reproduzir

```powershell
python -m unittest discover -s tests -v
python mutation_check.py
python replay.py --trial-dir fixtures/v23
```

No WSL com o runtime registado, preparar e verificar o manifesto draft:

```bash
python prepare_analysis_gate.py --weights PATH_TO_MODEL_SAFETENSORS
python verify_draft_manifest.py
```

O protocolo candidato usa os dez estados já expostos, uma chamada e nenhuma consulta. Não estima generalização. O runner confere o diário antes de carregar o backend, as versões registadas e todos os ficheiros do snapshot. A pré-registração e o manifesto permanecem em rascunho até à análise obrigatória.

G1/G2, a reprodução histórica v2.3 e a cópia v2.6 são preservados. Não há fine-tuning, modelo maior ou chamada de modelo neste pacote.
