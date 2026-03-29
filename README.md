# IBGEdownloader — Plugin QGIS

Plugin para o QGIS que permite navegar no servidor FTP do IBGE, baixar arquivos geoespaciais e carregá-los automaticamente como camadas no projeto atual.

---

## Funcionalidades

- **Navegação interativa** pelo servidor do IBGE diretamente na interface do QGIS
- **Listagem automática** de subdiretórios e arquivos `.zip` disponíveis
- **Download** com validação de integridade do arquivo recebido
- **Carregamento automático** de camadas vetoriais e matriciais no projeto QGIS
- **Suporte a arquivos compactados** — extrai e carrega camadas diretamente de ZIPs via GDAL (`/vsizip/`)
- **Definição automática de projeção** — arquivos sem CRS recebem EPSG:4674 (SIRGAS 2000) por padrão

### Formatos suportados

| Tipo | Extensões |
|------|-----------|
| Vetorial | `.shp`, `.gpkg`, `.geojson`, `.kml`, `.kmz`, `.gml` |
| Matricial | `.tif`, `.tiff`, `.img`, `.asc` |

---

## Requisitos

- QGIS 3.0 ou superior
- Python 3.6+
- PyQt5 (incluído no QGIS)

---

## Instalação

1. Clone ou baixe este repositório:
   ```bash
   git clone https://github.com/seu-usuario/ibgedownloader.git
   ```

2. Copie a pasta do plugin para o diretório de plugins do QGIS:

   | Sistema | Caminho |
   |---------|---------|
   | Linux | `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/` |
   | macOS | `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/` |
   | Windows | `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\` |

3. Compile o arquivo de recursos (caso `resources.py` não esteja presente):
   ```bash
   pyrcc5 resources.qrc -o resources.py
   ```

4. No QGIS, abra **Plugins → Gerenciar e Instalar Plugins**, localize **IBGEdownloader** e ative-o.

---

## Como usar

1. Clique no ícone do plugin na barra de ferramentas ou acesse **Plugins → IBGEdownloader**

2. No campo **URL do servidor**, insira o endereço de um diretório do servidor do IBGE. Exemplo:
   ```
   https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/
   ```

3. Clique em **Navegar** — a lista será populada com 📁 subdiretórios e 🗜 arquivos ZIP

4. Navegue pelos diretórios com **duplo clique** e use **← Voltar** para subir um nível

5. **Clique uma vez** sobre o arquivo ZIP desejado para selecioná-lo

6. Escolha a **pasta de destino** onde o arquivo será salvo localmente

7. Clique em **Baixar e Carregar** — o plugin fará o download, validará o arquivo e carregará as camadas automaticamente no QGIS

---

## Estrutura do projeto

```
ibgedownloader/
├── IBGEdownloader.py               # Classe principal do plugin
├── IBGEdownloader_dialog.py        # Lógica da interface e navegação
├── IBGEdownloader_dialog_base.ui   # Layout da interface (Qt Designer)
├── IBGEBrowser.py                  # Navegação e listagem do servidor IBGE
├── Downloader.py                   # Download e validação de arquivos
├── LayerLoader.py                  # Carregamento de camadas no QGIS
├── resources.py                    # Recursos compilados (ícone)
├── resources.qrc                   # Definição dos recursos Qt
├── metadata.txt                    # Metadados do plugin para o QGIS
├── icon.png                        # Ícone do plugin
└── __init__.py                     # Ponto de entrada do plugin
```

---

## Arquitetura

O plugin é dividido em três módulos independentes com responsabilidades bem definidas:

- **`IBGEBrowser`** — faz parse do HTML de listagem de diretório do servidor, separando subdiretórios de arquivos ZIP
- **`Downloader`** — gerencia o download via HTTP e valida a integridade do ZIP recebido antes de salvar
- **`LayerLoader`** — detecta o tipo de arquivo (vetorial/matricial), abre ZIPs via GDAL e registra as camadas no `QgsProject`

---

## Servidor IBGE

Os dados estão disponíveis publicamente em:

```
https://geoftp.ibge.gov.br/
```

Algumas URLs de interesse:

| Dado | URL |
|------|-----|
| Malhas municipais | `https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/` |
| Malhas estaduais | `https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_de_setores_censitarios/` |
| Bases cartográficas | `https://geoftp.ibge.gov.br/cartas_e_mapas/bases_cartograficas_continuas/` |

---

## Autor

**Marcus Sena**
Instituto Militar de Engenharia (IME)
✉ marcus.sena@ime.eb.br

---

## Licença

Distribuído sob a licença **GNU General Public License v2** ou superior. Consulte o cabeçalho de cada arquivo para detalhes.
