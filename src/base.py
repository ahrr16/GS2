"""Leitura, validação e atualização da base de orientações (JSON)."""
import json
import os
import re

CAMPOS_OBRIGATORIOS = ["codigo", "tema", "pergunta", "palavras_chave",
                       "orientacao", "fonte", "data_verificacao"]
PADRAO_DATA = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class BaseErro(Exception):
    """Erro ao carregar a base (arquivo ausente, vazio ou inválido)."""


def validar_registro(reg):
    """Retorna lista de problemas do registro (lista vazia = válido)."""
    if not isinstance(reg, dict):
        return ["registro não é um dicionário"]
    problemas = []
    for campo in CAMPOS_OBRIGATORIOS:
        valor = reg.get(campo)
        if valor is None or (isinstance(valor, (str, list)) and len(valor) == 0):
            problemas.append(f"campo obrigatório ausente ou vazio: {campo}")
    kws = reg.get("palavras_chave")
    if isinstance(kws, list):
        validas = [k for k in kws if isinstance(k, str) and k.strip()]
        if len(validas) < 2:
            problemas.append("é preciso ao menos 2 palavras-chave")
    elif kws is not None:
        problemas.append("palavras_chave deve ser uma lista")
    data = reg.get("data_verificacao")
    if isinstance(data, str) and data and not PADRAO_DATA.match(data):
        problemas.append("data_verificacao deve estar no formato AAAA-MM-DD")
    if "passos" in reg and not isinstance(reg["passos"], list):
        problemas.append("passos deve ser uma lista")
    return problemas


def carregar_base(caminho):
    """Lê o JSON e devolve (registros_validos, avisos).

    Levanta BaseErro se o arquivo não existir, estiver vazio ou inválido.
    Registros com problemas são ignorados e descritos em 'avisos'.
    """
    if not os.path.isfile(caminho):
        raise BaseErro(f"Arquivo da base não encontrado: {caminho}")
    try:
        with open(caminho, encoding="utf-8") as f:
            texto = f.read()
    except OSError as e:
        raise BaseErro(f"Não foi possível ler a base: {e}")
    if not texto.strip():
        raise BaseErro("O arquivo da base está vazio.")
    try:
        dados = json.loads(texto)
    except json.JSONDecodeError as e:
        raise BaseErro(f"JSON inválido na base (linha {e.lineno}): {e.msg}")
    lista = dados.get("orientacoes") if isinstance(dados, dict) else dados
    if not isinstance(lista, list) or not lista:
        raise BaseErro("A base não contém nenhuma orientação.")

    validos, avisos, codigos = [], [], set()
    for i, reg in enumerate(lista, start=1):
        problemas = validar_registro(reg)
        if not problemas and reg["codigo"] in codigos:
            problemas = [f"código duplicado: {reg['codigo']}"]
        if problemas:
            rotulo = reg.get("codigo", f"#{i}") if isinstance(reg, dict) else f"#{i}"
            avisos.append(f"Registro {rotulo} ignorado: " + "; ".join(problemas))
            continue
        codigos.add(reg["codigo"])
        validos.append(reg)
    if not validos:
        raise BaseErro("Nenhum registro válido na base.")
    return validos, avisos


def construir_hierarquia(registros):
    """Árvore tema -> subassunto -> [códigos]. Montada a partir dos dados."""
    arvore = {}
    for reg in registros:
        sub = reg.get("subassunto") or "Geral"
        arvore.setdefault(reg["tema"], {}).setdefault(sub, []).append(reg["codigo"])
    return arvore


def incluir_ou_corrigir(caminho, registro):
    """Insere um registro novo ou substitui o de mesmo código, no arquivo.

    Não altera nenhuma função de busca: a base é só dados.
    """
    problemas = validar_registro(registro)
    if problemas:
        raise BaseErro("Registro inválido: " + "; ".join(problemas))
    if os.path.isfile(caminho) and os.path.getsize(caminho) > 0:
        with open(caminho, encoding="utf-8") as f:
            dados = json.load(f)
    else:
        dados = {"versao": 1, "orientacoes": []}
    if isinstance(dados, list):
        dados = {"versao": 1, "orientacoes": dados}
    lista = dados.setdefault("orientacoes", [])
    for i, existente in enumerate(lista):
        if existente.get("codigo") == registro["codigo"]:
            lista[i] = registro
            acao = "corrigido"
            break
    else:
        lista.append(registro)
        acao = "incluído"
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    return acao
