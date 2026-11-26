"""Citizen Assist AI - interface de terminal.

Uso: python src/sistema.py [caminho_da_base.json]
"""
import os
import sys

from apresentacao import AVISO, MSG_SEM_RESPOSTA, NOMES_FORMATO, formatar
from base import BaseErro, carregar_base, construir_hierarquia
from busca import buscar, indexar, validar_consulta

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_PADRAO = os.path.join(RAIZ, "data", "base_orientacoes.json")


class Encerrar(Exception):
    """Sinaliza que o usuário quer encerrar a aplicação."""


class Sessao:
    def __init__(self, registros, entrada=input, saida=print):
        self.registros = registros
        self.indice = indexar(registros)
        self.hierarquia = construir_hierarquia(registros)
        self.temas = sorted(self.hierarquia)
        self.formato = "resumido"
        self._entrada, self._saida = entrada, saida

    def dizer(self, texto=""):
        self._saida(texto)

    def ler(self, prompt):
        """Lê uma linha; 'sair' (ou fim da entrada) encerra a qualquer momento."""
        try:
            texto = self._entrada(prompt)
        except (EOFError, KeyboardInterrupt):
            raise Encerrar()
        if texto.strip().lower() == "sair":
            raise Encerrar()
        return texto.strip()

    # ---- apresentação ----
    def mostrar(self, reg):
        self.dizer("\n" + "=" * 60)
        self.dizer(formatar(reg, self.formato))
        self.dizer("-" * 60)
        self.dizer(AVISO)
        self.dizer("=" * 60)

    def menu_principal(self):
        self.dizer("\n=== CITIZEN ASSIST AI ===")
        self.dizer("Guia de orientações sobre documentos (protótipo, não oficial).")
        for i, tema in enumerate(self.temas, start=1):
            self.dizer(f"  {i} - Tema: {tema}")
        n = len(self.temas)
        self.dizer(f"  {n + 1} - Pesquisar por palavras-chave")
        self.dizer(f"  {n + 2} - Alternar formato (atual: {NOMES_FORMATO[self.formato]})")
        self.dizer("  0 - Sair   (digite 'sair' a qualquer momento para encerrar)")

    # ---- fluxos ----
    def escolher_numero(self, prompt, maximo, tentativas=3):
        """Pede um número entre 0 e maximo; trata entrada vazia/inválida."""
        for _ in range(tentativas):
            texto = self.ler(prompt)
            if texto == "":
                self.dizer("Entrada vazia. Digite uma das opções.")
            elif not texto.isdigit() or not 0 <= int(texto) <= maximo:
                self.dizer(f"Opção inválida: '{texto}'. Use números de 0 a {maximo}.")
            else:
                return int(texto)
        self.dizer("Muitas tentativas inválidas; voltando ao menu.")
        return 0

    def fluxo_tema(self, tema):
        itens = []
        self.dizer(f"\nTema: {tema}")
        for sub, codigos in self.hierarquia[tema].items():
            self.dizer(f" [{sub}]")
            for cod in codigos:
                reg = next(r for r in self.registros if r["codigo"] == cod)
                itens.append(reg)
                self.dizer(f"  {len(itens)} - {reg['pergunta']}")
        self.dizer("  0 - Voltar ao menu")
        escolha = self.escolher_numero("Escolha uma pergunta: ", len(itens))
        if escolha:
            self.mostrar(itens[escolha - 1])

    def fluxo_busca(self):
        consulta = self.ler("\nDigite sua dúvida (sem dados pessoais): ")
        ok, motivo = validar_consulta(consulta)
        if not ok:
            self.dizer(f"Consulta não aceita: {motivo}.")
            return
        resultados = buscar(consulta, self.indice)
        if not resultados:  # sem correspondência confiável
            self.dizer("\n" + MSG_SEM_RESPOSTA)
            return
        if len(resultados) == 1:
            self.mostrar(resultados[0][0])
            return
        self.dizer("\nEncontrei mais de uma orientação possível:")
        for i, (reg, pontos, kws) in enumerate(resultados, start=1):
            self.dizer(f"  {i} - {reg['pergunta']}  "
                       f"[{reg['tema']}; {pontos} palavra(s)-chave: {', '.join(kws)}]")
        self.dizer("  0 - Voltar ao menu")
        escolha = self.escolher_numero("Escolha uma opção: ", len(resultados))
        if escolha:
            self.mostrar(resultados[escolha - 1][0])

    def executar(self):
        self.dizer(AVISO)
        try:
            while True:
                self.menu_principal()
                n = len(self.temas)
                op = self.escolher_numero("Opção: ", n + 2)
                if op == 0:
                    break
                if op <= n:
                    self.fluxo_tema(self.temas[op - 1])
                elif op == n + 1:
                    self.fluxo_busca()
                else:
                    self.formato = "passos" if self.formato == "resumido" else "resumido"
                    self.dizer(f"Formato alterado para: {NOMES_FORMATO[self.formato]}.")
        except Encerrar:
            pass
        self.dizer("\nEncerrando. Obrigado por usar o Citizen Assist AI!")


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    caminho = argv[0] if argv else BASE_PADRAO
    try:
        registros, avisos = carregar_base(caminho)
    except BaseErro as e:
        print(f"Erro ao carregar a base: {e}")
        return 1
    for a in avisos:
        print("Aviso:", a)
    Sessao(registros).executar()
    return 0


if __name__ == "__main__":
    sys.exit(main())
