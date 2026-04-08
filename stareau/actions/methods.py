from os import path

from qgis.core import (
    QgsDataSourceUri,
    QgsMapLayer,
    QgsProject,
    QgsProviderRegistry,
    QgsVectorLayer,
    QgsWkbTypes,
)

from .tools import display_error_message, get_postgres_layers


def inverser_canalisation(*args):
    """
    Inverser la canalisation sélectionnée.

    :param *args: [fid_canalisation: int, id_layer: str]

    These lines are included in the QGIS project.

        from qgis.utils import plugins
        plugins['raepa'].run_action('inverser_canalisation', '[% fid %]', '[% @layer_id %]')
    """
    action_name = "Inverser la canalisation"
    if len(args) != 2:
        display_error_message(
            f"Erreur dans l'action \"{action_name}\", "
            "Mauvais nombre d'arguments ! "
            f"2 attendus et {len(args)} fournis."
        )
        return

    fid_canalisation = int(args[0])
    id_layer = args[1]

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


def fermer_vanne(*args):
    """
    Fermer la vanne sélectionnée.

    :param *args: [fid_vanne: int, id_layer: str]

    These lines are included in the QGIS project.

        from qgis.utils import plugins
        plugins['raepa'].run_action('fermer_vanne', '[% fid %]', '[% @layer_id %]')
    """
    action_name = "Fermer la vanne"
    if len(args) != 2:
        display_error_message(
            f"Erreur dans l'action \"{action_name}\", "
            "Mauvais nombre d'arguments ! "
            f"2 attendus et {len(args)} fournis."
        )
        return

    fid_vanne = int(args[0])
    id_layer = args[1]

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


def ouvrir_vanne(*args):
    """
    Ouvrir la vanne sélectionnée.

    :param *args: [fid_vanne: int, id_layer: str]

    These lines are included in the QGIS project.

        from qgis.utils import plugins
        plugins['raepa'].run_action('ouvrir_vanne', '[% fid %]', '[% @layer_id %]')
    """
    action_name = "Ouvrir la vanne"
    if len(args) != 2:
        display_error_message(
            f"Erreur dans l'action \"{action_name}\", "
            "Mauvais nombre d'arguments ! "
            f"2 attendus et {len(args)} fournis."
        )
        return

    fid_vanne = int(args[0])
    id_layer = args[1]

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


def ass_downstream(*args):
    """
    Descendre le réseau de canalisations ASS à partir du noeud sélectionné
    et afficher les canalisations en aval du noeud sélectionnné.

    :param *args: [id_noeud: str, id_layer: str]

    These lines are included in the QGIS project.

        from qgis.utils import plugins
        plugins['raepa'].run_action('ass_downstream', '[% id_noeud_reseau %]', '[% @layer_id %]')
    """
    action_name = "Downstream"
    if len(args) != 2:
        display_error_message(
            f"Erreur dans l'action \"{action_name}\", "
            "Mauvais nombre d'arguments ! "
            f"2 attendus et {len(args)} fournis."
        )
        return

    id_noeud = args[0]
    id_layer = args[1]

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
    fids = []
    for record in records:
        fids.append(record[1])

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
        path.join(path.dirname(__file__), "styles", "downstream_symbology.qml"),
        categories = QgsMapLayer.Symbology,
    )


def ass_upstream(*args):
    """
    Remonter le réseau de canalisations ASS à partir du noeud sélectionné
    et afficher les canalisations en amont du noeud sélectionnné.

    :param *args: [id_noeud: str, id_layer: str]

    These lines are included in the QGIS project.

        from qgis.utils import plugins
        plugins['raepa'].run_action('ass_upstream', '[% id_noeud_reseau %]', '[% @layer_id %]')
    """
    action_name = "Upstream"
    if len(args) != 2:
        display_error_message(
            f"Erreur dans l'action \"{action_name}\", "
            "Mauvais nombre d'arguments ! "
            f"2 attendus et {len(args)} fournis."
        )
        return

    id_noeud = args[0]
    id_layer = args[1]

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
    fids = []
    for record in records:
        fids.append(record[1])

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
        path.join(path.dirname(__file__), "styles", "upstream_symbology.qml"),
        categories = QgsMapLayer.Symbology,
    )
