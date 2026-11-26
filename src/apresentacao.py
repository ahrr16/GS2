"""Modelos de resposta (dois formatos) e textos fixos da interface."""

AVISO = ("Protótipo acadêmico: NÃO é um canal oficial. Confirme sempre a "
         "informação na fonte indicada.")

# Instruções (modelos) de cada formato, documentadas também no README.
MODELOS_INSTRUCAO = {
    "resumido": (
        "Responda em um parágrafo curto e direto, usando apenas o texto da "
        "orientação da base. Termine com a fonte e a data de verificação. "
        "Não acrescente informações que não estejam na base."
    ),
    "passos": (
        "Apresente a orientação como lista numerada de etapas, usando apenas "
        "as etapas da base. Termine com a fonte e a data de verificação. "
        "Não acrescente informações que não estejam na base."
    ),
}
NOMES_FORMATO = {"resumido": "resumido", "passos": "passo a passo"}


def formatar_resumido(reg):
    return (f"{reg['pergunta']}\n\n{reg['orientacao']}\n\n"
            f"Fonte: {reg['fonte']}\nVerificado em: {reg['data_verificacao']}")


def formatar_passos(reg):
    etapas = reg.get("passos")
    if not etapas:  # sem passos na base: usa as frases da orientação
        etapas = [s.strip() for s in reg["orientacao"].split(". ") if s.strip()]
    linhas = [f"{i}. {e}" for i, e in enumerate(etapas, start=1)]
    return (f"{reg['pergunta']}\n\n" + "\n".join(linhas) +
            f"\n\nFonte: {reg['fonte']}\nVerificado em: {reg['data_verificacao']}")


FORMATADORES = {"resumido": formatar_resumido, "passos": formatar_passos}


def formatar(reg, formato="resumido"):
    return FORMATADORES.get(formato, formatar_resumido)(reg)


MSG_SEM_RESPOSTA = (
    "Não encontrei na base orientação suficiente para essa pergunta. "
    "Prefiro não inventar uma resposta. Tente outras palavras-chave, navegue "
    "pelos temas do menu ou consulte diretamente os canais oficiais.")
