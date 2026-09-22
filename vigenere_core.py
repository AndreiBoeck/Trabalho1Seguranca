"""Funcoes centrais da cifra e da criptoanalise de Vigenere.

Todas as funcoes trabalham sobre texto higienizado: somente letras de a a z,
cada uma representada pelo numero de 0 (a) a 25 (z).

Desempenho: o texto pode ter milhoes de letras, entao evitamos lacos em Python
letra a letra. As contagens usam str.count e as trocas de letra usam
str.translate, ambos implementados em C. Os lacos que sobram percorrem apenas
as 26 letras do alfabeto ou as posicoes da chave.
"""

from __future__ import annotations

import math
import re
import unicodedata

ALFABETO = "abcdefghijklmnopqrstuvwxyz"

# Frequencia (%) de cada letra em textos tipicos do portugues, ja sem acentos.
FREQUENCIAS_PT = {
    "a": 14.63, "b": 1.04, "c": 3.88, "d": 4.99, "e": 12.57,
    "f": 1.02, "g": 1.30, "h": 1.28, "i": 6.18, "j": 0.40,
    "k": 0.02, "l": 2.78, "m": 4.74, "n": 5.05, "o": 10.73,
    "p": 2.52, "q": 1.20, "r": 6.53, "s": 7.81, "t": 4.34,
    "u": 4.63, "v": 1.67, "w": 0.01, "x": 0.21, "y": 0.01,
    "z": 0.47,
}
# Mesmas frequencias como proporcoes, na ordem do alfabeto (indice 0 = a).
_PROPORCOES_PT = [FREQUENCIAS_PT[letra] / 100 for letra in ALFABETO]

_FORA_DO_ALFABETO = re.compile("[^a-z]+")


def higienizar(texto: str) -> str:
    """Converte para minusculas, remove acentos e mantem somente a-z."""
    # NFD separa a letra do acento ("a" vira "a" + acento combinante), e o
    # acento, por nao estar em a-z, e removido junto com espacos, pontuacao
    # e numeros.
    normalizado = unicodedata.normalize("NFD", texto.lower())
    return _FORA_DO_ALFABETO.sub("", normalizado)


def validar_chave(chave: str) -> str:
    chave_limpa = higienizar(chave)
    if not chave_limpa:
        raise ValueError("A chave deve conter pelo menos uma letra de a a z.")
    return chave_limpa


def _tabela_deslocamento(deslocamento: int) -> dict[int, int]:
    """Tabela para str.translate que soma `deslocamento` a cada letra, mod 26."""
    deslocado = ALFABETO[deslocamento % 26:] + ALFABETO[:deslocamento % 26]
    return str.maketrans(ALFABETO, deslocado)


def transformar_vigenere(texto: str, chave: str, decifrar: bool = False) -> str:
    """Cifra ou decifra texto higienizado com operacoes modulo 26.

    Cifrar:   C[i] = (P[i] + K[i mod n]) mod 26
    Decifrar: P[i] = (C[i] - K[i mod n]) mod 26

    As letras nas posicoes i, i+n, i+2n... usam a mesma letra da chave, ou
    seja, sao uma cifra de Cesar. Por isso cada uma dessas colunas e deslocada
    de uma vez e depois as colunas sao intercaladas de volta.
    """
    chave = validar_chave(chave)
    sinal = -1 if decifrar else 1
    n = len(chave)
    resultado = [""] * len(texto)
    for posicao, letra_chave in enumerate(chave):
        tabela = _tabela_deslocamento(sinal * (ord(letra_chave) - ord("a")))
        resultado[posicao::n] = texto[posicao::n].translate(tabela)
    return "".join(resultado)


def criptografar(texto: str, chave: str) -> str:
    return transformar_vigenere(higienizar(texto), chave)


def decifrar_com_chave(texto_cifrado: str, chave: str) -> str:
    return transformar_vigenere(higienizar(texto_cifrado), chave, decifrar=True)


def contar_letras(texto: str) -> list[int]:
    """Quantidade de cada letra, na ordem do alfabeto."""
    return [texto.count(letra) for letra in ALFABETO]


def indice_coincidencia(texto: str) -> float:
    """Probabilidade de duas letras sorteadas do texto serem iguais.

    IC = soma(f * (f - 1)) / (N * (N - 1))

    No portugues fica perto de 0,072, porque algumas letras (a, e, o) sao muito
    mais comuns. Em letras uniformemente aleatorias fica perto de 1/26 = 0,038.
    """
    tamanho = len(texto)
    if tamanho < 2:
        return 0.0
    return sum(f * (f - 1) for f in contar_letras(texto)) / (tamanho * (tamanho - 1))


def ics_por_tamanho(texto: str, maximo: int = 10) -> dict[int, float]:
    """IC medio das colunas para cada tamanho de chave de 1 ate `maximo`.

    Com o tamanho certo, cada coluna foi cifrada por uma so letra da chave
    (um Cesar), que preserva o IC do portugues. Com o tamanho errado, a coluna
    mistura deslocamentos diferentes e o IC cai para perto do aleatorio.
    Multiplos do tamanho certo tambem dao IC alto; isso e tratado em
    criptoanalisar.
    """
    limite = max(1, min(maximo, max(1, len(texto) // 2)))
    resultados = {}
    for tamanho in range(1, limite + 1):
        colunas = [texto[posicao::tamanho] for posicao in range(tamanho)]
        resultados[tamanho] = sum(map(indice_coincidencia, colunas)) / tamanho
    return resultados


def qui_quadrado(contagens: list[int], deslocamento: int) -> float:
    """Distancia entre a coluna decifrada com `deslocamento` e o portugues.

    qui2 = soma((observado - esperado)^2 / esperado)

    Decifrar com o deslocamento d transforma a letra cifrada (L + d) mod 26 na
    letra L. Entao a contagem observada de L e so a contagem de (L + d) mod 26
    na coluna cifrada: basta rotacionar as contagens, sem decifrar o texto.
    Quanto menor o valor, mais a coluna se parece com portugues.
    """
    n = sum(contagens)
    if not n:
        return math.inf
    total = 0.0
    for letra, proporcao in enumerate(_PROPORCOES_PT):
        esperado = n * proporcao
        observado = contagens[(letra + deslocamento) % 26]
        total += (observado - esperado) ** 2 / esperado
    return total


def qui_quadrado_para_deslocamento(coluna: str, deslocamento: int) -> float:
    """Qui-quadrado de uma coluna em texto; conta as letras e usa qui_quadrado."""
    return qui_quadrado(contar_letras(coluna), deslocamento)


def inferir_chave(texto: str, tamanho: int) -> tuple[str, list[float]]:
    """Escolhe, para cada posicao da chave, o deslocamento de menor qui-quadrado.

    Devolve a chave e o qui-quadrado vencedor de cada posicao.
    """
    letras, pontuacoes = [], []
    for posicao in range(tamanho):
        # As letras da coluna sao contadas uma vez so; os 26 deslocamentos
        # candidatos reaproveitam as mesmas contagens.
        contagens = contar_letras(texto[posicao::tamanho])
        candidatos = [qui_quadrado(contagens, d) for d in range(26)]
        melhor = min(range(26), key=candidatos.__getitem__)
        letras.append(ALFABETO[melhor])
        pontuacoes.append(candidatos[melhor])
    return "".join(letras), pontuacoes


def reduzir_chave_repetida(chave: str) -> str:
    """Reduz uma chave periodica ao menor periodo ("abcabc" -> "abc").

    Necessario porque o IC de um multiplo do tamanho real (14 para uma chave
    de 7 letras) pode ficar ligeiramente acima do IC do tamanho real.
    """
    for tamanho in range(1, len(chave) + 1):
        if len(chave) % tamanho == 0 and chave == chave[:tamanho] * (len(chave) // tamanho):
            return chave[:tamanho]
    return chave


def criptoanalisar(texto_cifrado: str, maximo: int = 10) -> dict:
    """Estima o tamanho, a chave e o texto original sem receber a senha."""
    texto = higienizar(texto_cifrado)
    if len(texto) < 40:
        raise ValueError("Use ao menos 40 letras para uma analise minimamente confiavel.")
    # Etapa 1: o maior IC medio indica o tamanho candidato da chave.
    ics = ics_por_tamanho(texto, maximo)
    tamanho_estimado = max(ics, key=ics.get)
    # Etapa 2: analise de frequencia em cada coluna.
    chave, pontuacoes = inferir_chave(texto, tamanho_estimado)
    chave_reduzida = reduzir_chave_repetida(chave)
    if chave_reduzida != chave:
        # Refaz a analise no periodo real para que cada pontuacao corresponda
        # a uma coluna da chave final.
        chave, pontuacoes = inferir_chave(texto, len(chave_reduzida))
    return {
        "texto_limpo": texto,
        "ics": ics,
        "tamanho": len(chave),
        "tamanho_candidato": tamanho_estimado,
        "chave": chave,
        "pontuacoes": pontuacoes,
        "texto_decifrado": transformar_vigenere(texto, chave, decifrar=True),
    }
