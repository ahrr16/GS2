# Resultados dos testes (gerado por `python src/avaliacao.py`)

## 1. Perguntas de teste

| ID | Tipo | Pergunta | Esperado | Obtido (1º) | Resultado | Tempo (ms) |
|---|---|---|---|---|---|---|
| T01 | direta | Quem pode se inscrever no CPF? | CPF01 | CPF01 | acerto | 0.011 |
| T02 | direta | Quais documentos preciso apresentar para o CPF? | CPF02 | CPF02 | acerto | 0.013 |
| T03 | direta | Como solicitar o CPF pelo formulário na internet? | CPF03 | CPF03 | acerto | 0.015 |
| T04 | direta | O CPF é gratuito ou tem custo? | CPF04 | CPF04 | acerto | 0.011 |
| T05 | direta | Como consultar a situação cadastral do meu CPF? | CPF05 | CPF05 | acerto | 0.014 |
| T06 | direta | Meu CPF está pendente, como regularizar? | CPF06 | CPF06 | acerto | 0.012 |
| T07 | variacao | Como tirar CPF? | CPF01 | CPF01 | acerto | 0.008 |
| T08 | direta | Quais tipos de passaporte existem? | PAS01 | PAS01 | acerto | 0.011 |
| T09 | direta | Qual o passo a passo para tirar passaporte? | PAS02 | PAS02 | acerto | 0.012 |
| T10 | direta | Quais documentos levar para o passaporte? | PAS03 | PAS03 | acerto | 0.013 |
| T11 | direta | Qual o valor da taxa do passaporte? | PAS04 | PAS04 | acerto | 0.013 |
| T12 | variacao | Quantos dias demora para receber o passaporte? | PAS05 | PAS05 | acerto | 0.014 |
| T13 | variacao | Qual a validade do passaporte para maior de 18 anos? | PAS06 | PAS06 | acerto | 0.015 |
| T14 | variacao | Quanto custa o passaporte com urgência? | PAS04 | PAS04 | acerto | 0.013 |
| T15 | variacao | Como pagar a tarifa para fazer meu CPF num cartório? | CPF04 | CPF01 | ERRO | 0.017 |
| T16 | fora_da_base | Como renovar a CNH? | sem resposta | sem resposta | acerto | 0.008 |
| T17 | fora_da_base | Qual a previsão do tempo para amanhã? | sem resposta | sem resposta | acerto | 0.011 |
| T18 | fora_da_base | Como emitir segunda via do título de eleitor? | sem resposta | sem resposta | acerto | 0.013 |

- Perguntas: **18**; acertos (1ª sugestão): **17**; **taxa de acerto = 17/18 = 94.4%**.
- Acerto considerando as 3 sugestões: 18/18 = 100.0%.
- **Tempo médio por consulta = 0.013 ms** (média das médias; cada busca repetida 200 vezes com `time.perf_counter`; mede só a busca, não a digitação do usuário).
- Critério de acerto: a 1ª sugestão é o código esperado; para perguntas fora da base, acerto = nenhuma sugestão.

## 2. Testes de falhas e limitações

| Teste | Esperado | Exibido | Resultado |
|---|---|---|---|
| Entrada vazia (consulta '   ') | rejeitar com mensagem | rejeitada: consulta vazia | acerto |
| Opção inválida no menu ('9', 'abc', vazio) | avisar e continuar; encerrar sem erro | 2 avisos de opção inválida + 1 de entrada vazia; encerrou | acerto |
| Pergunta sem resposta na base ('Como renovar a CNH?') | informar limitação, sem inventar | mensagem de limitação exibida | acerto |
| Dado pessoal na consulta (número de 11 dígitos) | rejeitar | rejeitada: a consulta parece conter dado pessoal (número longo ou e-mail); não digite dados pessoais | acerto |

## 3. Comparação objetiva dos formatos (3 perguntas)

| Pergunta | Registro | Resumido (caracteres/linhas) | Passo a passo (caracteres/linhas) |
|---|---|---|---|
| Qual o passo a passo para tirar passaporte? | PAS02 | 505/6 | 814/11 |
| Meu CPF está pendente, como regularizar? | CPF06 | 436/6 | 398/9 |
| Qual o valor da taxa do passaporte? | PAS04 | 418/6 | 518/9 |

A avaliação de clareza (qual formato foi mais claro e por quê) está em `docs/comparacao_formatos.md`.
