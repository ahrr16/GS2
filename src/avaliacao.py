"""Avaliação do assistente: acerto, tempo médio, falhas e comparação de formatos.

Uso: python src/avaliacao.py   (gera docs/resultados_testes.md)
"""
import json
import os
import time

from apresentacao import formatar
from base import carregar_base
from busca import buscar, indexar, validar_consulta
from sistema import BASE_PADRAO, RAIZ, Sessao

PERGUNTAS = os.path.join(RAIZ, "data", "perguntas_teste.json")
SAIDA = os.path.join(RAIZ, "docs", "resultados_testes.md")
REPETICOES = 200  # repete cada busca para medir tempo com precisão


def _roteiro(respostas):
    """Simula o teclado: devolve as respostas em ordem (EOF ao acabar)."""
    it = iter(respostas)

    def entrada(_prompt=""):
        try:
            return next(it)
        except StopIteration:
            raise EOFError
    return entrada


def rodar_perguntas(indice):
    with open(PERGUNTAS, encoding="utf-8") as f:
        casos = json.load(f)
    linhas = []
    for c in casos:
        ok, _ = validar_consulta(c["pergunta"])
        t0 = time.perf_counter()
        for _ in range(REPETICOES):
            res = buscar(c["pergunta"], indice)
        ms = (time.perf_counter() - t0) / REPETICOES * 1000
        obtido = res[0][0]["codigo"] if (ok and res) else None
        top3 = [r[0]["codigo"] for r in res]
        linhas.append({
            "id": c["id"], "tipo": c["tipo"], "pergunta": c["pergunta"],
            "esperado": c["esperado"], "obtido": obtido, "top3": top3,
            "acerto": obtido == c["esperado"],
            "acerto_top3": (c["esperado"] in top3) if c["esperado"] else not top3,
            "ms": ms})
    return linhas


def rodar_falhas(registros):
    """Testes de falha: entrada vazia, opção inválida, pergunta sem resposta."""
    resultados = []

    # 1) consulta vazia
    ok, motivo = validar_consulta("   ")
    resultados.append(("Entrada vazia (consulta '   ')", "rejeitar com mensagem",
                       f"rejeitada: {motivo}", not ok))

    # 2) opção inválida no menu (depois encerra)
    saida = []
    Sessao(registros, entrada=_roteiro(["9", "abc", "", "0"]),
           saida=saida.append).executar()
    texto = "\n".join(saida)
    passou = texto.count("Opção inválida") == 2 and "Entrada vazia" in texto \
        and "Encerrando" in texto
    resultados.append(("Opção inválida no menu ('9', 'abc', vazio)",
                       "avisar e continuar; encerrar sem erro",
                       "2 avisos de opção inválida + 1 de entrada vazia; encerrou" if passou
                       else "comportamento inesperado", passou))

    # 3) pergunta sem resposta verificada
    saida = []
    Sessao(registros, entrada=_roteiro(["3", "Como renovar a CNH?", "0"]),
           saida=saida.append).executar()
    texto = "\n".join(saida)
    passou = "Não encontrei na base" in texto
    resultados.append(("Pergunta sem resposta na base ('Como renovar a CNH?')",
                       "informar limitação, sem inventar",
                       "mensagem de limitação exibida" if passou else "falhou", passou))

    # 4) dado pessoal digitado
    ok, motivo = validar_consulta("meu cpf é 123.456.789-09 como regularizar")
    resultados.append(("Dado pessoal na consulta (número de 11 dígitos)",
                       "rejeitar", f"rejeitada: {motivo}", not ok))
    return resultados


def comparar_formatos(registros):
    indice = indexar(registros)
    perguntas = ["Qual o passo a passo para tirar passaporte?",
                 "Meu CPF está pendente, como regularizar?",
                 "Qual o valor da taxa do passaporte?"]
    saida = []
    for p in perguntas:
        reg = buscar(p, indice)[0][0]
        r, s = formatar(reg, "resumido"), formatar(reg, "passos")
        saida.append((p, reg["codigo"], len(r), len(r.splitlines()),
                      len(s), len(s.splitlines())))
    return saida


def gerar_relatorio():
    registros, _ = carregar_base(BASE_PADRAO)
    indice = indexar(registros)
    linhas = rodar_perguntas(indice)
    falhas = rodar_falhas(registros)
    formatos = comparar_formatos(registros)

    n = len(linhas)
    acertos = sum(l["acerto"] for l in linhas)
    acertos3 = sum(l["acerto_top3"] for l in linhas)
    tempo = sum(l["ms"] for l in linhas) / n
    md = ["# Resultados dos testes (gerado por `python src/avaliacao.py`)\n",
          "## 1. Perguntas de teste\n",
          "| ID | Tipo | Pergunta | Esperado | Obtido (1º) | Resultado | Tempo (ms) |",
          "|---|---|---|---|---|---|---|"]
    for l in linhas:
        md.append(f"| {l['id']} | {l['tipo']} | {l['pergunta']} | "
                  f"{l['esperado'] or 'sem resposta'} | {l['obtido'] or 'sem resposta'} | "
                  f"{'acerto' if l['acerto'] else 'ERRO'} | {l['ms']:.3f} |")
    md += ["", f"- Perguntas: **{n}**; acertos (1ª sugestão): **{acertos}**; "
           f"**taxa de acerto = {acertos}/{n} = {acertos / n * 100:.1f}%**.",
           f"- Acerto considerando as 3 sugestões: {acertos3}/{n} = {acertos3 / n * 100:.1f}%.",
           f"- **Tempo médio por consulta = {tempo:.3f} ms** (média das médias; cada "
           f"busca repetida {REPETICOES} vezes com `time.perf_counter`; mede só a busca, "
           "não a digitação do usuário).",
           "- Critério de acerto: a 1ª sugestão é o código esperado; para perguntas fora "
           "da base, acerto = nenhuma sugestão.", "",
           "## 2. Testes de falhas e limitações\n",
           "| Teste | Esperado | Exibido | Resultado |", "|---|---|---|---|"]
    for nome, esp, exi, ok in falhas:
        md.append(f"| {nome} | {esp} | {exi} | {'acerto' if ok else 'ERRO'} |")
    md += ["", "## 3. Comparação objetiva dos formatos (3 perguntas)\n",
           "| Pergunta | Registro | Resumido (caracteres/linhas) | Passo a passo (caracteres/linhas) |",
           "|---|---|---|---|"]
    for p, cod, c1, l1, c2, l2 in formatos:
        md.append(f"| {p} | {cod} | {c1}/{l1} | {c2}/{l2} |")
    md.append("\nA avaliação de clareza (qual formato foi mais claro e por quê) "
              "está em `docs/comparacao_formatos.md`.")
    with open(SAIDA, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    return linhas, falhas, acertos, n, tempo


if __name__ == "__main__":
    linhas, falhas, acertos, n, tempo = gerar_relatorio()
    for l in linhas:
        print(f"{l['id']} {'OK  ' if l['acerto'] else 'ERRO'} esperado={l['esperado']} "
              f"obtido={l['obtido']} top3={l['top3']} {l['ms']:.3f}ms")
    for nome, _, _, ok in falhas:
        print("FALHA-TESTE", "OK  " if ok else "ERRO", nome)
    print(f"Taxa de acerto: {acertos}/{n} = {acertos / n * 100:.1f}% | tempo médio {tempo:.3f} ms")
