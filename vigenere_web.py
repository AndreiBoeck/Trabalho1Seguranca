"""Interface grafica local no navegador, servida apenas em 127.0.0.1."""

from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import json
import os
from collections import Counter
from pathlib import Path
import subprocess
import sys
import webbrowser

from vigenere_core import criptoanalisar, criptografar, higienizar, validar_chave

PASTA = Path(__file__).parent.resolve()


class ServidorVigenere(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PASTA), **kwargs)

    def do_GET(self):
        if self.path in ("/", "/interface.html"):
            corpo = (PASTA / "interface.html").read_text(encoding="utf-8")
            corpo = corpo.replace("{{PASTA}}", str(PASTA)).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)
            return
        super().do_GET()

    def do_POST(self):
        try:
            tamanho = int(self.headers.get("Content-Length", "0"))
            dados = json.loads(self.rfile.read(tamanho).decode("utf-8"))
            if self.path == "/api/cifrar":
                origem = self._caminho(dados["entrada"])
                destino = self._caminho(dados["saida"])
                chave = validar_chave(dados["chave"])
                original = dados.get("conteudo")
                if original is None:
                    original = origem.read_text(encoding="utf-8")
                limpo = higienizar(original)
                cifrado = criptografar(original, chave)
                destino.parent.mkdir(parents=True, exist_ok=True)
                destino.write_text(cifrado, encoding="utf-8")
                resposta = {"ok": True, "original": limpo, "cifrado": cifrado,
                            "chave": chave, "total": len(cifrado), "saida": str(destino.resolve())}
            elif self.path == "/api/quebrar":
                origem = self._caminho(dados["entrada"])
                destino = self._caminho(dados["saida"])
                conteudo = dados.get("conteudo")
                if conteudo is None:
                    conteudo = origem.read_text(encoding="utf-8")
                resultado = criptoanalisar(conteudo, int(dados["maximo"]))
                destino.parent.mkdir(parents=True, exist_ok=True)
                destino.write_text(resultado["texto_decifrado"], encoding="utf-8")
                colunas = []
                for posicao in range(resultado["tamanho"]):
                    subtexto = resultado["texto_limpo"][posicao::resultado["tamanho"]]
                    contagens = Counter(subtexto)
                    principais = [
                        {"letra": letra, "percentual": quantidade * 100 / len(subtexto)}
                        for letra, quantidade in contagens.most_common(3)
                    ]
                    colunas.append({
                        "posicao": posicao + 1,
                        "amostra": subtexto[:28],
                        "principais": principais,
                        "deslocamento": ord(resultado["chave"][posicao]) - ord("a"),
                        "letra_chave": resultado["chave"][posicao],
                        "qui_quadrado": resultado["pontuacoes"][posicao],
                    })
                resposta = {"ok": True, "ics": resultado["ics"], "chave": resultado["chave"],
                            "tamanho": resultado["tamanho"], "trecho": resultado["texto_decifrado"][:180],
                            "tamanho_candidato": resultado["tamanho_candidato"],
                            "colunas": colunas,
                            "cifrado": resultado["texto_limpo"],
                            "decifrado": resultado["texto_decifrado"],
                            "total": len(resultado["texto_decifrado"]),
                            "saida": str(destino.resolve())}
            elif self.path == "/api/abrir":
                arquivo = self._caminho(dados["arquivo"]).resolve()
                if not arquivo.is_file():
                    raise FileNotFoundError(f"Arquivo nao encontrado: {arquivo}")
                if sys.platform == "darwin":
                    subprocess.Popen(["open", str(arquivo)], stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
                elif os.name == "nt":
                    os.startfile(str(arquivo))
                else:
                    subprocess.Popen(["xdg-open", str(arquivo)], stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
                resposta = {"ok": True, "arquivo": str(arquivo)}
            else:
                raise ValueError("Operacao desconhecida.")
            self._json(200, resposta)
        except Exception as erro:
            self._json(400, {"ok": False, "erro": str(erro)})

    def _caminho(self, valor):
        caminho = Path(valor).expanduser()
        return caminho if caminho.is_absolute() else PASTA / caminho

    def _json(self, codigo, dados):
        corpo = json.dumps(dados, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def log_message(self, formato, *args):
        pass


if __name__ == "__main__":
    endereco = ("127.0.0.1", 8765)
    try:
        servidor = ThreadingHTTPServer(endereco, ServidorVigenere)
    except OSError:
        servidor = ThreadingHTTPServer(("127.0.0.1", 0), ServidorVigenere)
    url = f"http://127.0.0.1:{servidor.server_port}/interface.html"
    print(f"Vigenere Lab aberto em {url}", flush=True)
    webbrowser.open(url)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        servidor.server_close()
