import urllib.request
import urllib.error
import zipfile
import io
import os


class Downloader:
    def __init__(self, server_url_format, destination_folder):
        self.server_url_format = server_url_format
        self.destination_folder = destination_folder
        os.makedirs(self.destination_folder, exist_ok=True)
        self.messages = ""

    def download_file(self, name):
        file_url = self.server_url_format + name + ".zip"
        file_path = os.path.join(self.destination_folder, f"{name}.zip")

        try:
            with urllib.request.urlopen(file_url) as response:
                if response.status != 200:
                    raise RuntimeError(f"Servidor retornou status {response.status} para '{file_url}'.\n")
                
                content = response.read()

            # Valida se o conteúdo é realmente um ZIP antes de salvar
            if not zipfile.is_zipfile(io.BytesIO(content)):
                preview = content[:300].decode("utf-8", errors="replace")
                raise RuntimeError(
                    f"O servidor não retornou um arquivo ZIP válido.\n"
                    f"Verifique a URL: {file_url}\n"
                    f"Resposta do servidor:\n{preview}\n"
                )

            with open(file_path, 'wb') as f:
                f.write(content)

            self.messages += "Arquivo baixado com sucesso.\n"
            return file_path

        except urllib.error.HTTPError as e:
            raise RuntimeError(f"Erro HTTP {e.code} ao acessar '{file_url}'.\n") from e
        except urllib.error.URLError as e:
            raise RuntimeError(f"Falha de conexão: {e.reason}\n") from e

