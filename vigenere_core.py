"""Funcoes centrais da cifra e da criptoanalise de Vigenere."""

from __future__ import annotations

import math
import unicodedata
from collections import Counter

ALFABETO = "abcdefghijklmnopqrstuvwxyz"
FREQUENCIAS_PT = {
    "a": 14.63, "b": 1.04, "c": 3.88, "d": 4.99, "e": 12.57,
    "f": 1.02, "g": 1.30, "h": 1.28, "i": 6.18, "j": 0.40,
    "k": 0.02, "l": 2.78, "m": 4.74, "n": 5.05, "o": 10.73,
    "p": 2.52, "q": 1.20, "r": 6.53, "s": 7.81, "t": 4.34,
    "u": 4.63, "v": 1.67, "w": 0.01, "x": 0.21, "y": 0.01,
    "z": 0.47,
}


def higienizar(texto: str) -> str:
    """Converte para minusculas, remove acentos e mantem somente a-z."""
    normalizado = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in normalizado if c in ALFABETO)


def validar_chave(chave: str) -> str:
    chave_limpa = higienizar(chave)
    if not chave_limpa:
        raise ValueError("A chave deve conter pelo menos uma letra de a a z.")
    return chave_limpa


def transformar_vigenere(texto: str, chave: str, decifrar: bool = False) -> str:
    """Cifra ou decifra texto higienizado com operacoes modulo 26."""
    chave = validar_chave(chave)
    sinal = -1 if decifrar else 1
    resultado = []
    for indice, caractere in enumerate(texto):
        valor_texto = ord(caractere) - ord("a")
        valor_chave = ord(chave[indice % len(chave)]) - ord("a")
        resultado.append(chr((valor_texto + sinal * valor_chave) % 26 + ord("a")))
    return "".join(resultado)


def criptografar(texto: str, chave: str) -> str:
    return transformar_vigenere(higienizar(texto), chave)


def decifrar_com_chave(texto_cifrado: str, chave: str) -> str:
    return transformar_vigenere(higienizar(texto_cifrado), chave, decifrar=True)


def indice_coincidencia(texto: str) -> float:
    tamanho = len(texto)
    if tamanho < 2:
        return 0.0
    contagens = Counter(texto)
    return sum(f * (f - 1) for f in contagens.values()) / (tamanho * (tamanho - 1))


def ics_por_tamanho(texto: str, maximo: int = 10) -> dict[int, float]:
    limite = max(1, min(maximo, max(1, len(texto) // 2)))
    resultados = {}
    for tamanho in range(1, limite + 1):
        colunas = [texto[posicao::tamanho] for posicao in range(tamanho)]
        resultados[tamanho] = sum(map(indice_coincidencia, colunas)) / tamanho
    return resultados


def qui_quadrado_para_deslocamento(coluna: str, deslocamento: int) -> float:
    n = len(coluna)
    if not n:
        return math.inf
    observadas = Counter(chr((ord(c) - 97 - deslocamento) % 26 + 97) for c in coluna)
    total = 0.0
    for letra in ALFABETO:
        esperado = n * FREQUENCIAS_PT[letra] / 100
        total += (observadas.get(letra, 0) - esperado) ** 2 / esperado
    return total


def inferir_chave(texto: str, tamanho: int) -> tuple[str, list[float]]:
    letras, pontuacoes = [], []
    for posicao in range(tamanho):
        coluna = texto[posicao::tamanho]
        candidatos = [qui_quadrado_para_deslocamento(coluna, d) for d in range(26)]
        melhor = min(range(26), key=candidatos.__getitem__)
        letras.append(ALFABETO[melhor])
        pontuacoes.append(candidatos[melhor])
    return "".join(letras), pontuacoes


def reduzir_chave_repetida(chave: str) -> str:
    for tamanho in range(1, len(chave) + 1):
        if len(chave) % tamanho == 0 and chave == chave[:tamanho] * (len(chave) // tamanho):
            return chave[:tamanho]
    return chave


def criptoanalisar(texto_cifrado: str, maximo: int = 10) -> dict:
    """Estima o tamanho, a chave e o texto original sem receber a senha."""
    texto = higienizar(texto_cifrado)
    if len(texto) < 40:
        raise ValueError("Use ao menos 40 letras para uma analise minimamente confiavel.")
    ics = ics_por_tamanho(texto, maximo)
    tamanho_estimado = max(ics, key=ics.get)
    chave, pontuacoes = inferir_chave(texto, tamanho_estimado)
    chave = reduzir_chave_repetida(chave)
    return {
        "texto_limpo": texto,
        "ics": ics,
        "tamanho": len(chave),
        "tamanho_candidato": tamanho_estimado,
        "chave": chave,
        "pontuacoes": pontuacoes,
        "texto_decifrado": transformar_vigenere(texto, chave, decifrar=True),
    }
