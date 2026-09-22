"""Testes do vigenere_core. Execute na pasta do projeto:

    python -m unittest discover -s tests -v
"""

import random
import sys
import time
import unittest
import unicodedata
from collections import Counter
from pathlib import Path

PASTA = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PASTA))

import vigenere_core as v  # noqa: E402

TEXTO_ORIGINAL = (PASTA / "exemplo_original.txt").read_text(encoding="utf-8")
TEXTO_CIFRADO = (PASTA / "exemplo_criptografado.txt").read_text(encoding="utf-8")


# Implementacoes diretas das formulas, letra a letra, usadas como referencia
# para conferir as versoes otimizadas do modulo.

def higienizar_referencia(texto):
    normalizado = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in normalizado if c in v.ALFABETO)


def vigenere_referencia(texto, chave, decifrar=False):
    sinal = -1 if decifrar else 1
    return "".join(
        chr((ord(c) - 97 + sinal * (ord(chave[i % len(chave)]) - 97)) % 26 + 97)
        for i, c in enumerate(texto)
    )


def qui_quadrado_referencia(coluna, deslocamento):
    n = len(coluna)
    observadas = Counter(chr((ord(c) - 97 - deslocamento) % 26 + 97) for c in coluna)
    return sum(
        (observadas.get(letra, 0) - n * v.FREQUENCIAS_PT[letra] / 100) ** 2
        / (n * v.FREQUENCIAS_PT[letra] / 100)
        for letra in v.ALFABETO
    )


def letras_aleatorias(tamanho, semente):
    gerador = random.Random(semente)
    return "".join(gerador.choice(v.ALFABETO) for _ in range(tamanho))


class TestHigienizacao(unittest.TestCase):
    def test_remove_acentos_pontuacao_numeros_e_espacos(self):
        self.assertEqual(v.higienizar("Ação, Ç 123 É!"), "acaoce")
        self.assertEqual(v.higienizar("Pão-de-Açúcar, não é?"), "paodeacucarnaoe")

    def test_mantem_somente_a_a_z(self):
        self.assertEqual(v.higienizar("ÀÉÎÕÜ ñ ç ß ø æ € @ \n\t"), "aeiounc")

    def test_texto_sem_letras_fica_vazio(self):
        self.assertEqual(v.higienizar("123 !?. \n"), "")

    def test_igual_a_referencia_no_dom_casmurro(self):
        self.assertEqual(v.higienizar(TEXTO_ORIGINAL), higienizar_referencia(TEXTO_ORIGINAL))


class TestCifra(unittest.TestCase):
    def test_vetor_conhecido(self):
        # Exemplo classico: ATTACKATDAWN com a chave LEMON.
        self.assertEqual(v.criptografar("ATTACK AT DAWN", "LEMON"), "lxfopvefrnhr")

    def test_chave_a_nao_altera_o_texto(self):
        self.assertEqual(v.criptografar("Olá mundo", "a"), "olamundo")

    def test_chave_e_higienizada(self):
        self.assertEqual(v.criptografar("texto", "Ségr edo!"), v.criptografar("texto", "segredo"))

    def test_chave_invalida(self):
        for chave in ("", "123", " !?"):
            with self.assertRaises(ValueError):
                v.criptografar("texto", chave)

    def test_ida_e_volta(self):
        limpo = v.higienizar(TEXTO_ORIGINAL)
        for chave in ("a", "z", "abc", "segredo", "umachavebemmaislonga"):
            cifrado = v.criptografar(TEXTO_ORIGINAL, chave)
            self.assertEqual(v.decifrar_com_chave(cifrado, chave), limpo)

    def test_igual_a_referencia(self):
        for semente, chave in enumerate(("b", "segredo", "xyz", "chavecomtrezes")):
            texto = letras_aleatorias(1001, semente)
            for decifrar in (False, True):
                self.assertEqual(
                    v.transformar_vigenere(texto, chave, decifrar),
                    vigenere_referencia(texto, chave, decifrar),
                )

    def test_reproduz_o_exemplo_do_repositorio(self):
        self.assertEqual(v.criptografar(TEXTO_ORIGINAL, "segredo"), TEXTO_CIFRADO.strip())


class TestEstatisticas(unittest.TestCase):
    def test_indice_coincidencia(self):
        self.assertEqual(v.indice_coincidencia(""), 0.0)
        self.assertEqual(v.indice_coincidencia("a"), 0.0)
        self.assertEqual(v.indice_coincidencia("aaaa"), 1.0)
        self.assertEqual(v.indice_coincidencia("ab"), 0.0)
        # aab: pares iguais = 2*1 / (3*2)
        self.assertAlmostEqual(v.indice_coincidencia("aab"), 1 / 3)

    def test_ic_do_portugues_e_do_aleatorio(self):
        self.assertAlmostEqual(v.indice_coincidencia(v.higienizar(TEXTO_ORIGINAL)), 0.072, delta=0.008)
        self.assertAlmostEqual(v.indice_coincidencia(letras_aleatorias(50000, 1)), 1 / 26, delta=0.002)

    def test_qui_quadrado_igual_a_referencia(self):
        for semente in range(5):
            coluna = letras_aleatorias(500, semente)
            for deslocamento in range(26):
                self.assertAlmostEqual(
                    v.qui_quadrado_para_deslocamento(coluna, deslocamento),
                    qui_quadrado_referencia(coluna, deslocamento),
                    places=6,
                )

    def test_qui_quadrado_de_coluna_vazia(self):
        self.assertEqual(v.qui_quadrado_para_deslocamento("", 3), float("inf"))

    def test_ic_destaca_o_tamanho_da_chave(self):
        ics = v.ics_por_tamanho(TEXTO_CIFRADO.strip(), 10)
        self.assertEqual(list(ics), list(range(1, 11)))
        self.assertEqual(max(ics, key=ics.get), 7)
        self.assertGreater(ics[7], 0.07)
        self.assertLess(max(ic for tamanho, ic in ics.items() if tamanho != 7), 0.05)

    def test_limite_de_tamanhos_em_texto_curto(self):
        self.assertEqual(list(v.ics_por_tamanho("abcdef", 10)), [1, 2, 3])

    def test_reduzir_chave_repetida(self):
        self.assertEqual(v.reduzir_chave_repetida("abcabc"), "abc")
        self.assertEqual(v.reduzir_chave_repetida("zzzz"), "z")
        self.assertEqual(v.reduzir_chave_repetida("segredo"), "segredo")
        self.assertEqual(v.reduzir_chave_repetida("abcab"), "abcab")


class TestCriptoanalise(unittest.TestCase):
    def test_quebra_o_exemplo_sem_a_senha(self):
        resultado = v.criptoanalisar(TEXTO_CIFRADO, 10)
        self.assertEqual(resultado["chave"], "segredo")
        self.assertEqual(resultado["tamanho"], 7)
        self.assertEqual(resultado["texto_decifrado"], v.higienizar(TEXTO_ORIGINAL))
        self.assertEqual(len(resultado["pontuacoes"]), 7)

    def test_varias_chaves(self):
        trecho = TEXTO_ORIGINAL[20000:80000]
        for chave in ("a", "z", "ok", "abc", "casa", "livro", "brasil", "segredo", "criptogr", "seguranca", "vigenerepm"):
            with self.subTest(chave=chave):
                resultado = v.criptoanalisar(v.criptografar(trecho, chave), 10)
                self.assertEqual(resultado["chave"], chave)
                self.assertEqual(resultado["tamanho"], len(chave))

    def test_chave_repetida_e_reduzida(self):
        resultado = v.criptoanalisar(v.criptografar(TEXTO_ORIGINAL, "abcabcabc"), 10)
        self.assertEqual(resultado["chave"], "abc")
        self.assertEqual(len(resultado["pontuacoes"]), 3)

    def test_chaves_maiores_que_o_limite_padrao(self):
        for chave in ("chaveonzeok", "chavedozeabc", "chavedequinze"):
            with self.subTest(chave=chave):
                cifrado = v.criptografar(TEXTO_ORIGINAL, chave)
                self.assertEqual(v.criptoanalisar(cifrado, 15)["chave"], chave)

    def test_texto_curto_demais(self):
        with self.assertRaises(ValueError):
            v.criptoanalisar("abc" * 13, 10)

    def test_arquivo_grande(self):
        # Cerca de 6,2 milhoes de letras: o Dom Casmurro repetido 20 vezes.
        grande = TEXTO_ORIGINAL * 20
        cifrado = v.criptografar(grande, "segredo")
        inicio = time.perf_counter()
        resultado = v.criptoanalisar(cifrado, 10)
        duracao = time.perf_counter() - inicio
        self.assertEqual(resultado["chave"], "segredo")
        self.assertEqual(resultado["texto_decifrado"], v.higienizar(grande))
        # Folga ampla para maquinas lentas; a versao anterior levava cerca de 50 s.
        self.assertLess(duracao, 20)


if __name__ == "__main__":
    unittest.main()
