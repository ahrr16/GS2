# Citizen Assist AI — Guia digital de documentos

**Nome completo:** Arthur Henrique Ruiz Ramos  **RM:**  
**Vídeo (YouTube, não listado):** 568738

Atividade Substitutiva de Global Solution 2026.2 (FIAP) — desafio CitizenTech.

## 1. Problema, temas e público
Quem precisa de um documento costuma procurar em várias páginas. O Citizen Assist AI é um protótipo de terminal que responde dúvidas frequentes a partir de uma base verificável, mostrando **fonte** e **data de verificação**, e avisa quando não há resposta confiável.

- **Tema 1 – CPF** (Receita Federal): inscrição e situação cadastral.
- **Tema 2 – Passaporte** (Polícia Federal): tipos, solicitação, taxas, prazos e validade.
- **Público:** qualquer cidadão que queira entender o procedimento antes de acessar o canal oficial.

Hierarquia (gerada a partir da base):
```
CPF
├── Inscrição: CPF01 quem pode · CPF02 documentos · CPF03 como solicitar/prazo · CPF04 custo
└── Situação cadastral: CPF05 consultar · CPF06 regularizar
Passaporte
├── Tipos e requisitos: PAS01
├── Solicitação: PAS02 passo a passo · PAS03 documentos
├── Taxas: PAS04
├── Prazos e retirada: PAS05
└── Validade: PAS06
```

## 2. Como executar
```
python src/sistema.py                      # aplicação
python src/avaliacao.py                    # testes de desempenho -> docs/resultados_testes.md
python -m unittest discover -s tests -v    # testes automatizados
```
Python 3.9+ (somente biblioteca padrão).

## 3. Estrutura do repositório
```
README.md
src/        base.py (leitura/validação) · busca.py · apresentacao.py · sistema.py (menu) · avaliacao.py
data/       base_orientacoes.json · perguntas_teste.json
docs/       resultados_testes.md · comparacao_formatos.md · roteiro_uso.md · exemplo_execucao.txt · uso_ia.md
tests/      test_sistema.py
```
> O enunciado cita um repositório modelo da coordenação; confira se os nomes de pastas coincidem e ajuste se necessário.

## 4. Base de conhecimento
Arquivo JSON com uma lista `orientacoes` de dicionários. Campos obrigatórios: `codigo`, `tema`, `pergunta`, `palavras_chave` (lista, mínimo 2), `orientacao`, `fonte` (URL), `data_verificacao` (AAAA-MM-DD). Opcionais: `subassunto` (monta a hierarquia) e `passos` (lista usada no formato passo a passo). A base tem 12 registros (6 por tema).

Para incluir ou corrigir uma orientação basta editar o JSON ou chamar `base.incluir_ou_corrigir(caminho, registro)`; nenhuma função de busca muda. Arquivo ausente, vazio, JSON inválido ou registros com campos faltando são tratados (registro inválido é ignorado com aviso; base inutilizável encerra com mensagem).

## 5. Busca e ordenação
1. A consulta é normalizada: minúsculas, sem acentos e pontuação, sem palavras vazias ("de", "como"…) e no singular simples.
2. Uma palavra-chave **casa** se todos os seus termos aparecem na consulta (ex.: `custa passaporte`). Usar palavras-chave de 2 termos evita falsos positivos (a palavra "tirar" sozinha não dispara nada).
3. Pontuação = número de palavras-chave que casaram. Ordenação: maior pontuação → mais termos cobertos → código.
4. Mostra até 3 sugestões; com uma só, exibe a resposta; com nenhuma, informa que a base não tem resposta suficiente.

## 6. Validação e modelos de resposta
Consulta rejeitada se: vazia, > 200 caracteres, parecer dado pessoal (número longo/e-mail) ou sem termos úteis. Opção de menu inválida ou vazia gera aviso (3 tentativas). `sair` encerra em qualquer prompt.

Dois formatos (alternáveis na opção 4 do menu), ambos com fonte e data:
- **Resumido:** parágrafo curto e direto, só com o texto da base.
- **Passo a passo:** lista numerada das etapas da base.

Comparação em `docs/comparacao_formatos.md`: o passo a passo foi mais claro para procedimentos; o resumido serve para respostas de um único dado.

## 7. Testes e resultados
18 perguntas (diretas, variações e fora da base) + 4 testes de falha. Resultado da última execução (`docs/resultados_testes.md`):
- **Taxa de acerto: 17/18 = 94,4%** (100% se contarmos as 3 sugestões).
- **Tempo médio de busca: ≈ 0,013 ms** (média de 200 repetições por pergunta com `time.perf_counter`; não inclui o tempo do usuário digitando).
- Único erro (T15): "Como pagar a tarifa para fazer meu CPF num cartório?" devolveu CPF01 antes de CPF04 (empate de pontuação; "tarifa" e "cartório" não são palavras-chave).

**Melhorias propostas:** (1) tabela de sinônimos (tarifa/taxa/custo, cartório/conveniada) para reduzir empates; (2) desempate por similaridade com a pergunta cadastrada ou peso por palavra-chave.
**Limitações dos testes:** perguntas escritas pela mesma pessoa que escreveu as palavras-chave (viés otimista); só 18 casos; tempos medem apenas a busca; a base cobre 12 perguntas e não acompanha mudanças nas páginas oficiais.

## 8. Exemplos
Veja `docs/exemplo_execucao.txt`: consulta vazia, duas sugestões ("tirar cpf e passaporte"), pergunta sem resposta ("Como renovar a CNH?"), opção inválida e retorno ao menu.

## 9. Clareza, acessibilidade, privacidade e informação não oficial
- Interface em texto simples, linguagem direta, menu numerado, compatível com leitores de tela.
- Não solicita nem armazena dados pessoais; rejeita consultas que pareçam conter números longos ou e-mail.
- Exibe em toda resposta o aviso de que **não é canal oficial** e a fonte para conferência. Valores e prazos podem mudar: confirme sempre no site oficial.

## 10.Vídeo
#https://www.youtube.com/watch?v=D7d9kHWh-wo
