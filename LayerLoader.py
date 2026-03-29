import os
import zipfile
from qgis.core import QgsProject, QgsVectorLayer, QgsRasterLayer, QgsCoordinateReferenceSystem

VECTOR_EXTENSIONS = {".shp", ".gpkg", ".geojson", ".kml", ".kmz", ".gml"}
RASTER_EXTENSIONS = {".tif", ".tiff", ".img", ".asc"}


class LayerLoader:
    def __init__(self):
        self.messages = ""

    def define_projection(self, layer):
        if not layer.crs().isValid():
            # CRS padrão: SIRGAS 2000 geográfico, comum em dados do IBGE
            crs = QgsCoordinateReferenceSystem("EPSG:4674")
            layer.setCrs(crs)
            self.messages += f"Projeção não encontrada. Definida como EPSG:4674 (SIRGAS 2000).\n"
        else:
            self.messages += f"Projeção identificada: {layer.crs().authid()} — {layer.crs().description()}\n"

    def load(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".zip":
            self._load_from_zip(file_path)
        elif ext in VECTOR_EXTENSIONS:
            self._load_vector(file_path)
        elif ext in RASTER_EXTENSIONS:
            self._load_raster(file_path)
        else:
            raise ValueError(f"Extensão '{ext}' não suportada.")

    def _load_vector(self, file_path):
        name = os.path.splitext(os.path.basename(file_path))[0]
        layer = QgsVectorLayer(file_path, name, "ogr")
        if not layer.isValid():
            raise ValueError(f"Camada vetorial inválida: {file_path}")
        self.define_projection(layer)
        QgsProject.instance().addMapLayer(layer)
        self.messages += f"[Vetorial] '{name}' carregada com sucesso.\n"

    def _load_raster(self, file_path):
        name = os.path.splitext(os.path.basename(file_path))[0]
        layer = QgsRasterLayer(file_path, name)
        if not layer.isValid():
            raise ValueError(f"Camada matricial inválida: {file_path}")
        self.define_projection(layer)
        QgsProject.instance().addMapLayer(layer)
        self.messages += f"[Matricial] '{name}' carregada com sucesso.\n"

    def _load_from_zip(self, zip_path):
        with zipfile.ZipFile(zip_path, 'r') as z:
            files = [f for f in z.namelist()
                     if os.path.splitext(f)[1].lower() in VECTOR_EXTENSIONS | RASTER_EXTENSIONS]

        if not files:
            raise ValueError(f"Nenhuma camada reconhecida em: {zip_path}")

        for file in files:
            ext = os.path.splitext(file)[1].lower()
            vsi_path = f"/vsizip/{zip_path}/{file}"
            name = os.path.splitext(os.path.basename(file))[0]

            if ext in VECTOR_EXTENSIONS:
                layer = QgsVectorLayer(vsi_path, name, "ogr")
                tipo = "Vetorial"
            else:
                layer = QgsRasterLayer(vsi_path, name)
                tipo = "Matricial"

            if layer.isValid():
                self.define_projection(layer)
                QgsProject.instance().addMapLayer(layer)
                self.messages += f"[{tipo}] '{name}' carregada.\n"
            else:
                self.messages += f"Aviso: '{name}' inválida, pulada.\n"