
from qgis.core import (
    QgsDataSourceUri,
    QgsMapLayer,
    QgsProject,
    QgsProviderRegistry,
    QgsVectorLayer,
    QgsWkbTypes,
)

from ..plugin_tools.resources import plugin_path
from .tools import display_error_message, get_postgres_layers

# NOTE: Supported parameter types are (str, int, bool, float)

def inverser_canalisation(fid_canalisation: int, id_layer: str):
    """
    Inverser la canalisation sélectionnée.

    These lines are included in the QGIS project.

        from qgis.utils import plugins
        plugins['raepa'].run_action(
            'inverser_canalisation',
            fid_canalisation = [% fid %],
            id_layer = '[% @layer_id %]',
        )
    """
    action_name = "Inverser la canalisation"

    layer = get_postgres_layers(id_layer, action_name)
    if layer is None:
        # Message d'erreur déjà affiché dans get_postgres_layers
        return
    if layer.wkbType() != QgsWkbTypes.LineString:
        display_error_message(
            f"Erreur dans l'action \"{action_name}\", "
            f"la couche {id_layer} n'est pas une couche de type ligne !"
        )
        return

    uri = layer.dataProvider().uri()

    metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
    connection = metadata.createConnection(uri.uri(), {})
    connection.executeSql(
        f"UPDATE \"{uri.schema()}\".\"{uri.table()}\" "
        f"SET geom = ST_Reverse(geom) WHERE fid = {fid_canalisation};"
    )
    layer.triggerRepaint()


def fermer_vanne(fid_vanne: int, id_layer: str):
    """
    Fermer la vanne sélectionnée.

    These lines are included in the QGIS project.

        from qgis.utils import plugins
        plugins['raepa'].run_action(
            'fermer_vanne',
            fid_vanne = [% fid %],
            id_layer='[% @layer_id %]',
        )
    """
    action_name = "Fermer la vanne"

    layer = get_postgres_layers(id_layer, action_name)
    if layer is None:
        # Message d'erreur déjà affiché dans get_postgres_layers
        return
    if layer.wkbType() != QgsWkbTypes.Point:
        display_error_message(
            f"Erreur dans l'action \"{action_name}\", "
            f"la couche {id_layer} n'est pas une couche de type point !"
        )
        return
    if layer.fields().indexOf('etat_ouverture') == -1:
        display_error_message(
            f"Erreur dans l'action \"{action_name}\", "
            f"la couche {id_layer} n'a pas de champ 'etat_ouverture' !"
        )
        return

    uri = layer.dataProvider().uri()

    metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
    connection = metadata.createConnection(uri.uri(), {})
    connection.executeSql(
        f"UPDATE \"{uri.schema()}\".\"{uri.table()}\" "
        f"SET etat_ouverture = 'fermee' WHERE fid = {fid_vanne};"
    )
    layer.triggerRepaint()


def ouvrir_vanne(fid_vanne: int, id_layer: str):
    """
    Ouvrir la vanne sélectionnée.

    These lines are included in the QGIS project.

        from qgis.utils import plugins
        plugins['raepa'].run_action(
            'ouvrir_vanne',
            fid_vanne = [% fid %],
            id_layer='[% @layer_id %]',
        )
    """
    action_name = "Ouvrir la vanne"

    layer = get_postgres_layers(id_layer, action_name)
    if layer is None:
        # Message d'erreur déjà affiché dans get_postgres_layers
        return
    if layer.wkbType() != QgsWkbTypes.Point:
        display_error_message(
            f"Erreur dans l'action \"{action_name}\", "
            f"la couche {id_layer} n'est pas une couche de type point !"
        )
        return
    if layer.fields().indexOf('etat_ouverture') == -1:
        display_error_message(
            f"Erreur dans l'action \"{action_name}\", "
            f"la couche {id_layer} n'a pas de champ 'etat_ouverture' !"
        )
        return

    uri = layer.dataProvider().uri()

    metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
    connection = metadata.createConnection(uri.uri(), {})
    connection.executeSql(
        f"UPDATE \"{uri.schema()}\".\"{uri.table()}\" "
        f"SET etat_ouverture = 'ouverte' WHERE fid = {fid_vanne};"
    )
    layer.triggerRepaint()


def ass_downstream(id_noeud: str, id_layer: str):
    """
    Descendre le réseau de canalisations ASS à partir du noeud sélectionné
    et afficher les canalisations en aval du noeud sélectionnné.

    These lines are included in the QGIS project.

        from qgis.utils import plugins
        plugins['raepa'].run_action(
            'ass_downstream',
            id_noeud = '[% id_noeud_reseau %]',
            id_layer = '[% @layer_id %]',
        )
    """
    action_name = "Downstream"

    layer = get_postgres_layers(id_layer, action_name)
    if layer is None:
        # Message d'erreur déjà affiché dans get_postgres_layers
        return
    if layer.wkbType() != QgsWkbTypes.Point:
        display_error_message(
            f"Erreur dans l'action \"{action_name}\", "
            f"la couche {id_layer} n'est pas une couche de type point !"
        )
        return
    if layer.fields().indexOf('id_noeud_reseau') == -1:
        display_error_message(
            f"Erreur dans l'action \"{action_name}\", "
            f"la couche {id_layer} n'a pas de champ 'id_noeud_reseau' !"
        )
        return

    uri = layer.dataProvider().uri()
    schema = '_'.join(uri.schema().split('_')[:-1])
    metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
    connection = metadata.createConnection(uri.uri(), {})

    # 63906 'BC2AD790347B4ACEA7D15FA12473AFEB'
    records = connection.execSql(
        f"SELECT d.idx, d.fid_canalisation FROM \"{schema}\".ass_downstream('{id_noeud}') d "
    )
    fids = [record[1] for record in records]

    uri = QgsDataSourceUri(layer.dataProvider().uri())
    uri.setWkbType(QgsWkbTypes.LineString)
    uri.setDataSource(
        f"{schema}_principale",
        "canalisation",
        "geom",
        f"fid IN ({','.join([str(fid) for fid in fids])})",
        "fid",
    )

    source = QgsVectorLayer(uri.uri(), "Downstream", "postgres")
    QgsProject.instance().addMapLayer(source)
    source.loadNamedStyle(
        plugin_path("actions", "styles", "downstream_symbology.qml"),
        categories = QgsMapLayer.Symbology,
    )


def ass_upstream(id_noeud: str, id_layer: str):
    """
    Remonter le réseau de canalisations ASS à partir du noeud sélectionné
    et afficher les canalisations en amont du noeud sélectionnné.

    These lines are included in the QGIS project.

        from qgis.utils import plugins
        plugins['raepa'].run_action(
            'ass_upstream',
            id_noeud = '[% id_noeud_reseau %]',
            id_layer = '[% @layer_id %]',
        )
    """
    action_name = "Upstream"

    layer = get_postgres_layers(id_layer, action_name)
    if layer is None:
        # Message d'erreur déjà affiché dans get_postgres_layers
        return
    if layer.wkbType() != QgsWkbTypes.Point:
        display_error_message(
            f"Erreur dans l'action \"{action_name}\", "
            f"la couche {id_layer} n'est pas une couche de type point !"
        )
        return
    if layer.fields().indexOf('id_noeud_reseau') == -1:
        display_error_message(
            f"Erreur dans l'action \"{action_name}\", "
            f"la couche {id_layer} n'a pas de champ 'id_noeud_reseau' !"
        )
        return

    uri = layer.dataProvider().uri()
    schema = '_'.join(uri.schema().split('_')[:-1])
    metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
    connection = metadata.createConnection(uri.uri(), {})

    # 63906 'BC2AD790347B4ACEA7D15FA12473AFEB'
    records = connection.execSql(
        f"SELECT d.idx, d.fid_canalisation FROM \"{schema}\".ass_upstream('{id_noeud}') d "
    )
    fids = [record[1] for record in records]

    uri = QgsDataSourceUri(layer.dataProvider().uri())
    uri.setWkbType(QgsWkbTypes.LineString)
    uri.setDataSource(
        f"{schema}_principale",
        "canalisation",
        "geom",
        f"fid IN ({','.join([str(fid) for fid in fids])})",
        "fid",
    )

    source = QgsVectorLayer(uri.uri(), "Upstream", "postgres")
    QgsProject.instance().addMapLayer(source)
    source.loadNamedStyle(
        plugin_path("actions", "styles", "upstream_symbology.qml"),
        categories = QgsMapLayer.Symbology,
    )
