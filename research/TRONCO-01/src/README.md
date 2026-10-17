# Código de trabalho (fora dos ZIPs)

Cópias de trabalho do código arquivado, para poder editar, testar e comparar versões. **Os ZIPs em `../packages/` continuam a ser o registo histórico e não foram alterados.**

| Pasta | Origem | Nota |
|---|---|---|
| `tronco01_v2_7/` | `TRONCO01_ENSAIO_MODELO_V2_7_REPRODUCIBLE` → `work/TRONCO01_TRIAL_v2_7` | 37 testes e 4 mutações passam a partir daqui. Sem pesos nem inferência |
| `m17/` | `TRONCO01_G2_SENTINELA_REPRODUCIBLE` → `work/M17_DESCOBERTA_DIAGNOSTICO` | Gerador, ambiente e avaliador M17 sem alterações |
| `m17_audit/` | novo | Auditoria de identificabilidade do veredicto esperado do M17 (só partição de desenvolvimento) |

Alterações a `tronco01_v2_7/` e `m17/` não alteram os resultados históricos: esses ficam nos ZIPs e nos relatórios.
`tronco01_v2_7/development_reference_private.jsonl` já estava exposto no arquivo; é a referência dos dez estados de desenvolvimento, não uma reserva.
