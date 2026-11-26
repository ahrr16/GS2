"""Normalização, validação da consulta e busca por palavras-chave."""
import re
import unicodedata

STOPWORDS = {
    "a", "o", "as", "os", "um", "uma", "de", "do", "da", "dos", "das", "em",
    "no", "na", "nos", "nas", "para", "pra", "por", "pelo", "pela", "com",
    "sem", "que", "qual", "quais", "quanto", "quantos", "como", "e", "ou",
    "se", "me", "meu", "minha", "meus", "minhas", "eu", "ao", "aos", "esta",
    "est", "tem", "preciso", "posso", "faco", "quero", "onde", "quando",
    "ser", "sao", "e", "ha",
}
# Padrões que sugerem dado pessoal digitado (CPF, e-mail, telefone longo).
PADRAO_DADO_PESSOAL = re.compile(
    r"(\d[\d.\-\s]{9,}\d)|([\w.+-]+@[\w-]+\.[\w.]+)")
TAMANHO_MAXIMO = 200


def remover_acentos(texto):
    nfkd = unicodedata.normalize("NFD", texto)
    return "".join(c for c in nfkd if unicodedata.category(c) != "Mn")


def _radical(token):
    """Singular simples: remove 's' final de palavras longas."""
    if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


def tokenizar(texto):
    """Minúsculas, sem acentos, sem pontuação, sem stopwords, no singular."""
    texto = remover_acentos(texto.lower())
    tokens = re.findall(r"[a-z0-9]+", texto)
    return [_radical(t) for t in tokens if t not in STOPWORDS]


def validar_consulta(texto):
    """Retorna (ok, motivo). Usa condições booleanas encadeadas."""
    if texto is None or not texto.strip():
        return False, "consulta vazia"
    if len(texto) > TAMANHO_MAXIMO:
        return False, f"consulta muito longa (máximo {TAMANHO_MAXIMO} caracteres)"
    if PADRAO_DADO_PESSOAL.search(texto):
        return False, ("a consulta parece conter dado pessoal (número longo ou "
                       "e-mail); não digite dados pessoais")
    if not tokenizar(texto):
        return False, "a consulta não contém palavras de busca reconhecíveis"
    return True, ""


def indexar(registros):
    """Pré-processa as palavras-chave: lista de (registro, [(kw, tokens)])."""
    indice = []
    for reg in registros:
        kws = []
        for kw in reg["palavras_chave"]:
            toks = frozenset(tokenizar(kw))
            if toks:
                kws.append((kw, toks))
        indice.append((reg, kws))
    return indice


def buscar(consulta, indice, tema=None, limite=3):
    """Busca por palavras-chave.

    Critério: uma palavra-chave "casa" se TODOS os seus termos aparecem na
    consulta (após normalização). A pontuação é o número de palavras-chave
    distintas que casaram. Ordenação: maior pontuação; empate -> mais termos
    casados; novo empate -> código. Devolve até `limite` itens
    (registro, pontuacao, [palavras-chave encontradas]).
    """
    termos = set(tokenizar(consulta))
    resultados = []
    for reg, kws in indice:
        if tema is not None and reg["tema"] != tema:
            continue
        casadas = [(kw, t) for kw, t in kws if t <= termos]
        if casadas:
            pontos = len(casadas)
            cobertura = len(set().union(*(t for _, t in casadas)))
            resultados.append((reg, pontos, cobertura, [kw for kw, _ in casadas]))
    resultados.sort(key=lambda r: (-r[1], -r[2], r[0]["codigo"]))
    return [(reg, p, kws) for reg, p, _, kws in resultados[:limite]]
