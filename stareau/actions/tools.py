from qgis.core import (
    Qgis,
    QgsMessageLog,
    QgsProject,
    QgsVectorLayer,
)
from qgis.utils import iface


def display_error_message(message: str):
    """
    Display error message in QGIS message bar and log.
    """
    QgsMessageLog.logMessage(message, 'StarEau', Qgis.Critical)
    iface.messageBar().pushMessage(message, level=Qgis.Critical, duration=2)

def get_postgres_layers(id_layer: str, action_name: str) -> None|QgsVectorLayer:
    """
    Get a postgres layer from its id and check if it is valid.
    """
    layer = QgsProject.instance().mapLayer(id_layer)

    if layer is None:
        display_error_message(
            f"Erreur dans l'action \"{action_name}\", "
            f"la couche {id_layer} n'existe pas dans le projet !"
        )
        return None
    if not layer.isValid():
        display_error_message(
            f"Erreur dans l'action \"{action_name}\", "
            f"la couche {id_layer} est invalide !"
        )
        return None
    if layer.dataProvider().name() != 'postgres':
        display_error_message(
            f"Erreur dans l'action \"{action_name}\", "
            f"la couche {id_layer} n'est pas une couche Postgres !"
        )
        return None

    return layer
