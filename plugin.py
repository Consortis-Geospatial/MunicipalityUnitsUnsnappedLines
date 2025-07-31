from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import Qt
import os
from .plugin_dockwidget import PluginDockWidget

class PolygonMlineBufferPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.dockwidget = None
        self.plugin_dir = os.path.dirname(__file__)

    def initGui(self):
        icon = QIcon(os.path.join(self.plugin_dir, 'icon.png'))
        self.action = QAction(icon, "Έλεγχος αγκύρωσης οδικού δικτύου στα όρια της Δημοτικής Ενότητας", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&Έλεγχος αγκύρωσης οδικού δικτύου στα όρια της Δημοτικής Ενότητας", self.action)

    def unload(self):
        self.iface.removePluginMenu("&Έλεγχος αγκύρωσης οδικού δικτύου στα όρια της Δημοτικής Ενότητας", self.action)
        self.iface.removeToolBarIcon(self.action)
        if self.dockwidget:
            self.iface.removeDockWidget(self.dockwidget)
            self.dockwidget = None

    def run(self):
        # Create or show the dock widget
        if not self.dockwidget:
            self.dockwidget = PluginDockWidget(self.iface)
            self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockwidget)
        self.dockwidget.show()