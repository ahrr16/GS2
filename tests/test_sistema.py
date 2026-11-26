"""Testes automatizados. Execute: python -m unittest discover -s tests -v"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from base import BaseErro, carregar_base, incluir_ou_corrigir  # noqa: E402
from busca import buscar, indexar, tokenizar, validar_consulta  # noqa: E402
from sistema import BASE_PADRAO, Sessao  # noqa: E402

REG = {"codigo": "X01", "tema": "Teste", "pergunta": "Pergunta?",
       "palavras_chave": ["alfa beta", "gama delta"], "orientacao": "Texto.",
       "fonte": "https://exemplo.gov.br", "data_verificacao": "2026-11-25"}


def teclado(respostas):
    it = iter(respostas)

    def entrada(_=""):
        try:
            return next(it)
        except StopIteration:
            raise EOFError
    return entrada


class TestBase(unittest.TestCase):
    def test_base_padrao_tem_12_registros_e_2_temas(self):
        regs, avisos = carregar_base(BASE_PADRAO)
        self.assertGreaterEqual(len(regs), 10)
        self.assertEqual(len({r["tema"] for r in regs}), 2)
        self.assertEqual(avisos, [])

    def test_arquivo_ausente(self):
        with self.assertRaises(BaseErro):
            carregar_base("/nao/existe.json")

    def test_arquivo_vazio(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            caminho = f.name
        with self.assertRaises(BaseErro):
            carregar_base(caminho)
        os.remove(caminho)

    def test_registro_com_campo_faltando_e_ignorado(self):
        ruim = dict(REG, codigo="X02")
        del ruim["fonte"]
        with tempfile.TemporaryDirectory() as d:
            c = os.path.join(d, "b.json")
            with open(c, "w") as f:
                json.dump({"orientacoes": [REG, ruim]}, f)
            regs, avisos = carregar_base(c)
        self.assertEqual([r["codigo"] for r in regs], ["X01"])
        self.assertEqual(len(avisos), 1)

    def test_incluir_e_corrigir_sem_mexer_na_logica(self):
        with tempfile.TemporaryDirectory() as d:
            c = os.path.join(d, "b.json")
            self.assertEqual(incluir_ou_corrigir(c, REG), "incluído")
            self.assertEqual(incluir_ou_corrigir(c, dict(REG, orientacao="Novo.")), "corrigido")
            regs, _ = carregar_base(c)
            self.assertEqual(regs[0]["orientacao"], "Novo.")
            self.assertEqual(len(regs), 1)


class TestBusca(unittest.TestCase):
    def setUp(self):
        self.regs, _ = carregar_base(BASE_PADRAO)
        self.indice = indexar(self.regs)

    def test_tokenizar_remove_acentos_stopwords_e_plural(self):
        self.assertEqual(tokenizar("Quais DOCUMENTOS são necessários?"),
                         ["documento", "necessario"])

    def test_consulta_vazia_e_invalida(self):
        self.assertFalse(validar_consulta("")[0])
        self.assertFalse(validar_consulta("   ")[0])
        self.assertFalse(validar_consulta("???")[0])
        self.assertFalse(validar_consulta("meu cpf 123.456.789-09")[0])
        self.assertTrue(validar_consulta("taxa do passaporte")[0])

    def test_busca_direta(self):
        self.assertEqual(buscar("valor da taxa do passaporte", self.indice)[0][0]["codigo"], "PAS04")

    def test_sem_correspondencia(self):
        self.assertEqual(buscar("como renovar a CNH", self.indice), [])

    def test_maximo_tres_sugestoes_ordenadas(self):
        res = buscar("cpf passaporte taxa custo valor documento prazo tirar", self.indice)
        self.assertLessEqual(len(res), 3)
        pontos = [p for _, p, _ in res]
        self.assertEqual(pontos, sorted(pontos, reverse=True))


class TestInterface(unittest.TestCase):
    def setUp(self):
        self.regs, _ = carregar_base(BASE_PADRAO)

    def rodar(self, respostas):
        saida = []
        Sessao(self.regs, entrada=teclado(respostas), saida=saida.append).executar()
        return "\n".join(saida)

    def test_opcao_invalida_nao_quebra(self):
        t = self.rodar(["99", "abc", "", "0"])
        self.assertIn("Opção inválida", t)
        self.assertIn("Entrada vazia", t)
        self.assertIn("Encerrando", t)

    def test_consulta_vazia_volta_ao_menu(self):
        t = self.rodar(["3", "", "0"])
        self.assertIn("Consulta não aceita: consulta vazia", t)
        self.assertIn("Encerrando", t)

    def test_pergunta_sem_resposta(self):
        t = self.rodar(["3", "como renovar a CNH", "0"])
        self.assertIn("Não encontrei na base", t)

    def test_resposta_mostra_fonte_e_data(self):
        t = self.rodar(["3", "valor da taxa do passaporte", "0"])
        self.assertIn("Fonte: https://www.gov.br", t)
        self.assertIn("Verificado em: 2026-11-25", t)

    def test_sair_a_qualquer_momento(self):
        self.assertIn("Encerrando", self.rodar(["3", "sair"]))

    def test_fim_da_entrada_encerra(self):
        self.assertIn("Encerrando", self.rodar([]))

    def test_alternar_formato(self):
        t = self.rodar(["4", "3", "tirar passaporte passo", "0"])
        self.assertIn("passo a passo", t)
        self.assertIn("1. Preencha o formulário online", t)

    def test_sugestoes_e_escolha(self):
        t = self.rodar(["3", "tirar cpf e passaporte", "1", "0"])
        self.assertIn("mais de uma orientação", t)


if __name__ == "__main__":
    unittest.main()
