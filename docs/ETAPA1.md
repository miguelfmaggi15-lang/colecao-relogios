# Etapa 1 — Coleção de Relógios

O projeto organiza uma coleção pessoal de relógios. Cada relógio tem marca, modelo,
referência, mecanismo e cor do mostrador. Data de aquisição, preço e observações são
opcionais. Um relógio pode ter várias fotos e aparecer em mais de uma pasta.

## Banco de dados

| Tabela | O que guarda |
| --- | --- |
| `usuario` | Contas dos colecionadores |
| `marca` | Catálogo de marcas |
| `relogio` | Relógios da coleção |
| `foto` | Fotos de cada relógio |
| `pasta` | Pastas de cada colecionador |
| `relogio_pasta` | Vínculos entre relógios e pastas |

A chave composta de `relogio_pasta` impede que o mesmo relógio seja adicionado duas
vezes à mesma pasta.

## Verificação

O script foi executado no MySQL 8.4.13. A conexão em Python confirmou as seis
tabelas e as dez marcas iniciais.
