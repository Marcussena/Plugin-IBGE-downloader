# -*- coding: utf-8 -*-
import os
import io
import zipfile

from .Downloader import Downloader
from .LayerLoader import LayerLoader
from .IBGEBrowser import IBGEBrowser

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'IBGEdownloader_dialog_base.ui'))

# Prefixos usados para distinguir tipo de item na lista
_DIR_PREFIX  = "__DIR__"
_FILE_PREFIX = "__FILE__"


class IBGEdownloaderDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self._browser    = IBGEBrowser()
        self._history    = []          # pilha de URLs visitadas
        self._current_url = ""
        self._selected_file_url  = ""
        self._selected_file_name = ""

        # Conexões
        self.btnNavegar.clicked.connect(self._on_navegar)
        self.btnVoltar.clicked.connect(self._on_voltar)
        self.listWidget.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.listWidget.itemClicked.connect(self._on_item_clicked)
        self.pushButton.clicked.connect(self._on_baixar)

    # ------------------------------------------------------------------
    # Navegação
    # ------------------------------------------------------------------

    def _navegar_para(self, url, push_history=True):
        """Carrega o conteúdo de uma URL de diretório na listWidget."""
        self.textEdit.append(f"Listando: {url}")
        QtWidgets.QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            entries = self._browser.list_entries(url)
        except RuntimeError as e:
            self.textEdit.append(f"Erro: {e}")
            return
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

        if push_history and self._current_url:
            self._history.append(self._current_url)

        self._current_url = url if url.endswith("/") else url + "/"
        self._selected_file_url  = ""
        self._selected_file_name = ""
        self.pushButton.setEnabled(False)
        self.labelSelecionado.setText("Nenhum arquivo selecionado.")
        self.labelCaminho.setText(f"Caminho atual: {self._current_url}")
        self.btnVoltar.setEnabled(bool(self._history))

        self.listWidget.clear()

        # Diretórios primeiro
        for nome, full_url in entries["dirs"]:
            item = QtWidgets.QListWidgetItem(f"📁  {nome}")
            item.setData(Qt.UserRole, _DIR_PREFIX + full_url)
            self.listWidget.addItem(item)

        # Arquivos ZIP
        for nome, full_url in entries["files"]:
            item = QtWidgets.QListWidgetItem(f"🗜  {nome}")
            item.setData(Qt.UserRole, _FILE_PREFIX + full_url)
            self.listWidget.addItem(item)

        if self.listWidget.count() == 0:
            self.textEdit.append("Nenhum subdiretório ou arquivo .zip encontrado nesta pasta.")

    def _on_navegar(self):
        url = self.lineEdit.text().strip()
        if not url:
            self.textEdit.append("Insira uma URL antes de navegar.")
            return
        self._history.clear()
        self._navegar_para(url, push_history=False)

    def _on_voltar(self):
        if self._history:
            url = self._history.pop()
            self._navegar_para(url, push_history=False)
            self.btnVoltar.setEnabled(bool(self._history))

    def _on_item_double_clicked(self, item):
        data = item.data(Qt.UserRole) or ""
        if data.startswith(_DIR_PREFIX):
            self._navegar_para(data[len(_DIR_PREFIX):])

    def _on_item_clicked(self, item):
        data = item.data(Qt.UserRole) or ""
        if data.startswith(_FILE_PREFIX):
            url  = data[len(_FILE_PREFIX):]
            nome = url.rstrip("/").split("/")[-1]
            self._selected_file_url  = url
            self._selected_file_name = nome
            self.labelSelecionado.setText(f"✔ {nome}")
            self.pushButton.setEnabled(True)
        else:
            # clicou num diretório — deseleciona arquivo
            self._selected_file_url  = ""
            self._selected_file_name = ""
            self.labelSelecionado.setText("Nenhum arquivo selecionado.")
            self.pushButton.setEnabled(False)

    # ------------------------------------------------------------------
    # Download + carregamento
    # ------------------------------------------------------------------

    def _on_baixar(self):
        if not self._selected_file_url:
            self.textEdit.append("Selecione um arquivo .zip primeiro.")
            return

        destination = self.mQgsFileWidget.filePath()
        if not destination:
            self.textEdit.append("Selecione uma pasta de destino.")
            return

        file_name_no_ext = os.path.splitext(self._selected_file_name)[0]
        # A URL completa já inclui o arquivo; precisamos separar base e nome
        base_url = self._selected_file_url[: self._selected_file_url.rfind("/") + 1]

        downloader = Downloader(base_url, destination)

        self.textEdit.append(
            f"Baixando {self._selected_file_name} para {destination} ..."
        )
        QtWidgets.QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            file_path = downloader.download_file(file_name_no_ext)
        except RuntimeError as e:
            self.textEdit.append(f"Erro no download: {e}")
            return
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

        self.textEdit.append(downloader.messages)

        loader = LayerLoader()
        try:
            loader.load(file_path)
        except (FileNotFoundError, ValueError, RuntimeError) as e:
            self.textEdit.append(f"Erro ao carregar: {e}")
            return
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

        self.textEdit.append(loader.messages)