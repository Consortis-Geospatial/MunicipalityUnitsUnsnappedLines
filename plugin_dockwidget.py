from qgis.PyQt.QtWidgets import QDockWidget, QListWidgetItem, QComboBox, QDoubleSpinBox, QPushButton, QVBoxLayout, QLabel, QWidget, QListWidget, QCheckBox, QProgressBar
from qgis.PyQt.QtCore import Qt, QTimer
from qgis.PyQt.QtGui import QColor
from qgis.core import (
    QgsProject,
    QgsSpatialIndex,
    QgsPointXY,
    QgsGeometry,
    QgsFeature,
    QgsVectorLayer,
    QgsWkbTypes,
    Qgis,
    QgsRectangle
)
from qgis.gui import QgsRubberBand

class PluginDockWidget(QDockWidget):
    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Road Network Anchor Check at Municipal Boundaries")
        self.resize(300, 400)

        # Main widget and layout
        self.main_widget = QWidget()
        self.layout = QVBoxLayout(self.main_widget)

        # Polygon Layer ComboBox
        self.polygonLayerLabel = QLabel("Municipality Polygon Layer:")
        self.layout.addWidget(self.polygonLayerLabel)
        self.polygonLayerCombo = QComboBox()
        self.layout.addWidget(self.polygonLayerCombo)

        # Multiline Layer ComboBox
        self.mlineLayerLabel = QLabel("Road Network Line Layer:")
        self.layout.addWidget(self.mlineLayerLabel)
        self.mlineLayerCombo = QComboBox()
        self.layout.addWidget(self.mlineLayerCombo)

        # Checkbox for selected features
        self.check_selected = QCheckBox("Check only selected features")
        self.layout.addWidget(self.check_selected)

        # Buffer Distance SpinBox
        self.bufferLabel = QLabel("Max distance from municipality boundary (meters):")
        self.layout.addWidget(self.bufferLabel)
        self.bufferSpinBox = QDoubleSpinBox()
        self.bufferSpinBox.setMinimum(0.0)
        self.bufferSpinBox.setMaximum(1000.0)
        self.bufferSpinBox.setValue(0.1)
        self.layout.addWidget(self.bufferSpinBox)

        # Run Button
        self.runButton = QPushButton("Run Check")
        self.layout.addWidget(self.runButton)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setVisible(False)
        self.layout.addWidget(self.progress_bar)

        # Result List
        self.resultLabel = QLabel("Results:")
        self.layout.addWidget(self.resultLabel)
        self.resultList = QListWidget()
        self.layout.addWidget(self.resultList)

        # Shapefile Export Button
        self.download_button = QPushButton("Download Shapefile")
        self.download_button.clicked.connect(self.export_to_shapefile)
        self.download_button.setVisible(False)
        self.layout.addWidget(self.download_button)

        self.setWidget(self.main_widget)

        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.flagged_points = []

        self.populate_layers()

        self.runButton.clicked.connect(self.run_analysis)
        self.resultList.itemClicked.connect(self.zoom_to_vertex)

    def populate_layers(self):
        self.polygonLayerCombo.clear()
        self.mlineLayerCombo.clear()
        for layer in QgsProject.instance().mapLayers().values():
            if isinstance(layer, QgsVectorLayer):
                if layer.geometryType() == QgsWkbTypes.PolygonGeometry:
                    self.polygonLayerCombo.addItem(layer.name(), layer.id())
                elif layer.geometryType() == QgsWkbTypes.LineGeometry:
                    self.mlineLayerCombo.addItem(layer.name(), layer.id())

    def start_progress(self, total_features):
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def end_progress(self):
        self.progress_bar.setVisible(False)
        self.progress_bar.reset()

    def run_analysis(self):
        self.download_button.setVisible(False)
        self.resultList.clear()

        buffer_dist = self.bufferSpinBox.value()
        poly_layer = QgsProject.instance().mapLayer(self.polygonLayerCombo.currentData())
        mline_layer = QgsProject.instance().mapLayer(self.mlineLayerCombo.currentData())

        if not poly_layer or not mline_layer:
            self.iface.messageBar().pushMessage("Error", "Missing or invalid input layers", level=Qgis.Critical)
            return

        if self.check_selected.isChecked():
            if poly_layer.selectedFeatureCount() == 0 or mline_layer.selectedFeatureCount() == 0:
                self.iface.messageBar().pushMessage("Error", "Please select features to check", level=Qgis.Critical)
                return
            poly_features = poly_layer.selectedFeatures()
            mline_features = mline_layer.selectedFeatures()
            total_features = max(len(poly_features), len(mline_features))
        else:
            poly_features = poly_layer.getFeatures()
            mline_features = mline_layer.getFeatures()
            total_features = max(poly_layer.featureCount(), mline_layer.featureCount())

        self.start_progress(total_features)

        tolerance = 1e-6
        line_index = QgsSpatialIndex()
        line_features = {}
        progress_idx = 0

        for m_feat in mline_features:
            line_index.addFeature(m_feat)
            progress_idx += 1
            self.update_progress((progress_idx * 100) // total_features)

        self.flagged_points = []
        progress_idx = 0

        for poly_feat in poly_features:
            geom = poly_feat.geometry()
            if not geom.isGeosValid():
                self.iface.messageBar().pushMessage("Warning", f"Invalid geometry in polygon FID {poly_feat.id()}", level=Qgis.Warning)
                continue

            outer_buffer = geom.buffer(buffer_dist, 8)
            inner_buffer = geom.buffer(-buffer_dist, 8)
            virtual_buffer = outer_buffer.difference(inner_buffer)
            boundary_geom = geom.constGet().boundary()
            boundary = QgsGeometry(boundary_geom)
            if boundary.isEmpty():
                self.iface.messageBar().pushMessage("Warning", f"Empty boundary for polygon FID {poly_feat.id()}", level=Qgis.Warning)
                continue

            candidate_ids = line_index.intersects(virtual_buffer.boundingBox())
            for fid in candidate_ids:
                m_feat = mline_layer.getFeature(fid)
                geom = m_feat.geometry()
                if geom.isMultipart():
                    parts = geom.asMultiPolyline()
                    if not parts:
                        continue
                    points = parts[0]
                else:
                    points = geom.asPolyline()

                if not points:
                    continue

                for idx in [0, -1]:
                    if abs(idx) >= len(points):
                        continue
                    point = points[idx]
                    pt_geom = QgsGeometry.fromPointXY(point)
                    distance_to_boundary = pt_geom.distance(boundary)
                    if distance_to_boundary < tolerance:
                        continue

                    if virtual_buffer.contains(pt_geom):
                        label = f"FID {m_feat.id()} | {'Start' if idx == 0 else 'End'}"
                        item = QListWidgetItem(label)
                        item.setData(Qt.UserRole, point)
                        self.resultList.addItem(item)
                        self.flagged_points.append(point)
            progress_idx += 1
            self.update_progress((progress_idx * 100) // total_features)

        self.end_progress()

        if self.resultList.count() > 0:
            self.download_button.setVisible(True)
        else:
            self.iface.messageBar().pushMessage("Road Network Anchor Check", "Total: 0", level=Qgis.Info)

    def export_to_shapefile(self):
        if not self.flagged_points:
            return

        vl = QgsVectorLayer("Point?crs=epsg:2100", "unsnapped_line_endpoints", "memory")
        pr = vl.dataProvider()
        vl.startEditing()

        for point in self.flagged_points:
            fet = QgsFeature()
            fet.setGeometry(QgsGeometry.fromPointXY(point))
            pr.addFeature(fet)

        vl.commitChanges()
        vl.updateExtents()

        from qgis.PyQt.QtWidgets import QFileDialog
        save_path, _ = QFileDialog.getSaveFileName(None, "Save Shapefile", "", "Shapefile (*.shp)")
        if save_path:
            from qgis.core import QgsVectorFileWriter
            error = QgsVectorFileWriter.writeAsVectorFormat(vl, save_path, "UTF-8", vl.crs(), "ESRI Shapefile")
            if error[0] == QgsVectorFileWriter.NoError:
                self.iface.messageBar().pushSuccess("Export", "Shapefile saved successfully.")
            else:
                self.iface.messageBar().pushCritical("Error", "Failed to save shapefile.")

    def zoom_to_vertex(self, item):
        pt = item.data(Qt.UserRole)
        center = QgsPointXY(pt)
        rect = QgsRectangle(center.x() - 1, center.y() - 1, center.x() + 1, center.y() + 1)
        self.canvas.setExtent(rect)
        self.canvas.zoomScale(50)
        self.canvas.refresh()

        rubber = QgsRubberBand(self.canvas, QgsWkbTypes.PointGeometry)
        rubber.setColor(QColor(255, 0, 0))
        rubber.setWidth(5)
        rubber.addPoint(center)
        rubber.show()
        QTimer.singleShot(800, rubber.reset)
