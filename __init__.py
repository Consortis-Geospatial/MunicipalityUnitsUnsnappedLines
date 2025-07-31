def classFactory(iface):
    from .plugin import PolygonMlineBufferPlugin
    return PolygonMlineBufferPlugin(iface)