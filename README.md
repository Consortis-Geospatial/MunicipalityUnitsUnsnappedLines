# MunicipalityUnitsUnsnappedLines
**MunicipalityUnitsUnsnappedLines** is a QGIS plugin that identifies road network line features (multiline geometries) whose start or end points are not properly snapped to municipal boundary polygons within a user-defined distance threshold. This helps reveal topological issues or missing connections in road networks near administrative borders, especially useful when integrating datasets from different sources. Users can specify a maximum snapping distance (in meters), choose to analyze full layers or only selected features, and inspect flagged line endpoints in an interactive dock. Results can be exported to a point shapefile for further correction or review.

---

## Features

- Detect road network line endpoints not properly snapped to municipality polygon boundaries.
- User-defined maximum snapping distance (in meters) for checking connectivity.
- Option to analyze full layers or restrict to selected features in both polygon and line layers.
- Visual feedback with temporary red rubber bands highlighting flagged endpoints on the map canvas.
- Interactive dock widget to list and zoom to flagged endpoints.
- Export flagged endpoints as a point Shapefile (EPSG:2100) for further analysis.
- Progress bar to monitor analysis progress.

---

## How It Works

1. Activate the plugin via the toolbar icon or the "Check Road Network Connectivity at Municipal Boundaries" menu.
2. In the dockable panel, select a municipality polygon layer and a road network line layer.
3. Optionally, enable the "Check only selected features" checkbox to limit analysis to selected features.
4. Set the maximum snapping distance (in meters) for detecting unsnapped endpoints.
5. Click "Run Check" to start the analysis.
6. View flagged endpoints in the results list; click an item to zoom to the point with a temporary red rubber band highlight.
7. Export flagged points to a Shapefile using the "Download Shapefile" button.

---

## Installation

1. Clone or download this repository:
   ```bash
   git clone https://github.com/Consortis-Geospatial/MunicipalityUnitsUnsnappedLines.git
   ```
2. Copy the folder to your QGIS plugin directory:
   - Linux: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
   - Windows: `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\`
   - macOS: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
3. Open QGIS and enable the plugin via Plugins > Manage and Install Plugins.

---

## Screenshot
Coming Soon...

---

## Developer Notes

- Developed in Python using PyQt and PyQGIS APIs.
- Uses a custom `QDockWidget` to provide an interactive interface for layer selection, parameter input, and result display.
- Employs `QgsSpatialIndex` for efficient spatial queries to identify line endpoints within the buffer zone of polygon boundaries.
- Temporary red rubber band visualization with an 800ms display for flagged endpoints.
- Exports results as a point Shapefile in EPSG:2100, optimized for Greek road network datasets.
- Handles invalid geometries and empty boundaries with user-friendly warning messages.
- Compatible with QGIS 3.0 and later.

---

## Dependencies

- **QGIS 3.x**: Compatible with QGIS version 3.0 and later (tested with 3.38.3), providing the core GIS functionality and PyQGIS API.
- **Python 3**: QGIS 3.x includes an embedded Python 3 interpreter (typically version 3.7 or higher).
- **PyQt5**: Required for GUI components like `QAction`, `QDockWidget`, `QComboBox`, `QDoubleSpinBox`, `QPushButton`, `QListWidget`, `QCheckBox`, and `QProgressBar`. Bundled with QGIS 3.x installations (version 5.15.10 or similar).
- **PyQGIS**: Provides core QGIS functionality, including `QgsProject`, `QgsSpatialIndex`, `QgsGeometry`, `QgsVectorLayer`, `QgsRubberBand`, and `QgsVectorFileWriter`. Included with QGIS.
- **PyQt5-sip**: A dependency for PyQt5, typically included with QGIS (version 12.13.0 or higher).

---

## Support and Contributions

- **Homepage**: [https://github.com/Consortis-Geospatial](https://github.com/Consortis-Geospatial)
- **Issue Tracker**: [https://github.com/Consortis-Geospatial/MunicipalityUnitsUnsnappedLines/issues](https://github.com/Consortis-Geospatial/MunicipalityUnitsUnsnappedLines/issues)
- **Author**: Gkaravelis Andreas - Consortis Geospatial
- **Email**: gkaravelis@consortis.gr
- **Repository**: [https://github.com/Consortis-Geospatial/MunicipalityUnitsUnsnappedLines](https://github.com/Consortis-Geospatial/MunicipalityUnitsUnsnappedLines)

---

## License
This plugin is released under the GPL-3.0 license.
