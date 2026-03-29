import urllib.request
import urllib.error
from html.parser import HTMLParser


class _LinkParser(HTMLParser):
    """Extrai links de uma listagem de diretório HTML."""

    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attr, value in attrs:
                if attr == "href" and value and not value.startswith("?") and value != "/":
                    self.links.append(value)


class IBGEBrowser:
    """Navega em diretórios HTTP do servidor FTP do IBGE e lista arquivos ZIP."""

    TIMEOUT = 10

    def __init__(self):
        self.messages = ""

    def list_entries(self, url):
        """
        Lista entradas (subdiretórios e arquivos .zip) em uma URL de diretório.

        Retorna um dicionário com duas listas:
            {
                "dirs":  [(nome_exibição, url_completa), ...],
                "files": [(nome_exibição, url_completa), ...],
            }
        """
        url = url if url.endswith("/") else url + "/"

        try:
            with urllib.request.urlopen(url, timeout=self.TIMEOUT) as response:
                if response.status != 200:
                    raise RuntimeError(f"Servidor retornou status {response.status}.")
                html = response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"Erro HTTP {e.code} ao acessar '{url}'.") from e
        except urllib.error.URLError as e:
            raise RuntimeError(f"Falha de conexão: {e.reason}") from e

        parser = _LinkParser()
        parser.feed(html)

        dirs = []
        files = []

        for link in parser.links:
            # ignora links de navegação para o pai
            if link.startswith("..") or link.startswith("/") and not link.startswith(url):
                continue

            # monta URL absoluta
            if link.startswith("http://") or link.startswith("https://"):
                full_url = link
            else:
                full_url = url + link

            display = link.rstrip("/")
            display = display.split("/")[-1]  # só o nome final

            if link.endswith("/"):
                dirs.append((display, full_url))
            elif link.lower().endswith(".zip"):
                files.append((display, full_url))

        return {"dirs": dirs, "files": files}