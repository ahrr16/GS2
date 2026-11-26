# Uso de Inteligência Artificial

## Ferramenta
Claude (Anthropic), via claude.ai, em 25/11/2026.

## Como foi usada
- Planejamento da arquitetura (módulos `base`, `busca`, `apresentacao`, `sistema`, `avaliacao`).
- Geração do código inicial em Python, dos testes automatizados e da estrutura dos documentos.
- Pesquisa das páginas oficiais do gov.br usadas como fonte da base.

## Exemplos de instruções dadas
1. "Esse trabalho final da minha faculdade" + anexo do enunciado da Atividade Substitutiva (Citizen Assist AI).
2. Instruções internas dos formatos (ver `docs/comparacao_formatos.md`).

## Verificação crítica (a ser confirmada pelo estudante)
- As orientações da base foram redigidas a partir das páginas oficiais lidas em 25/11/2026: gov.br "Obter passaporte", gov.br "Inscrever no CPF" e gov.br "Consultar Cadastro de Pessoas Físicas". Reabra cada link e confira valores e prazos antes de entregar.
- Observação: a página do passaporte não lista os documentos exigidos; a base registra isso em vez de inventar a lista.
- Os testes foram executados (`python src/avaliacao.py` e `python -m unittest discover -s tests`). O erro T15 foi mantido e analisado, não escondido.
- A avaliação de clareza dos formatos e o roteiro de uso devem ser refeitos/confirmados por você.
- Você deve ser capaz de explicar cada função do código e as escolhas de busca no vídeo.
