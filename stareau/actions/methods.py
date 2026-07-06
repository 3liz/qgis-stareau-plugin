
from psycopg2 import connect, sql
from qgis.core import (
    QgsDataSourceUri,
    QgsMapLayer,
    QgsPointXY,
    QgsProject,
    QgsProviderRegistry,
    QgsVectorLayer,
    QgsWkbTypes,
)

from ..plugin_tools.resources import plugin_path
from .tools import display_error_message, display_info_message, get_postgres_layers

# NOTE: Supported parameter types are (str, int, bool, float)

def inverser_canalisation(fid_canalisation: int, id_layer: str):
    """
    Inverser la canalisation sélectionnée.

    These lines are included in the QGIS project.

        from qgis.utils import plugins
        plugins['stareau'].run_action(
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
    pg_conn = connect(uri.connectionInfo())
    query = sql.SQL(
        "UPDATE {schema}.{table} SET geom = ST_Reverse(geom) WHERE fid = {fid};"
    ).format(
        schema=sql.Identifier(uri.schema()),
        table=sql.Identifier(uri.table()),
        fid=sql.Literal(fid_canalisation),
    )
    connection.executeSql(query.as_string(pg_conn))
    pg_conn.close()
    layer.triggerRepaint()


def fermer_vanne(fid_vanne: int, id_layer: str):
    """
    Fermer la vanne sélectionnée.

    These lines are included in the QGIS project.

        from qgis.utils import plugins
        plugins['stareau'].run_action(
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
    pg_conn = connect(uri.connectionInfo())
    query = sql.SQL(
        "UPDATE {schema}.{table} SET etat_ouverture = 'fermee' WHERE fid = {fid};"
    ).format(
        schema=sql.Identifier(uri.schema()),
        table=sql.Identifier(uri.table()),
        fid=sql.Literal(fid_vanne),
    )
    connection.executeSql(query.as_string(pg_conn))
    pg_conn.close()
    layer.triggerRepaint()


def ouvrir_vanne(fid_vanne: int, id_layer: str):
    """
    Ouvrir la vanne sélectionnée.

    These lines are included in the QGIS project.

        from qgis.utils import plugins
        plugins['stareau'].run_action(
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
    pg_conn = connect(uri.connectionInfo())
    query = sql.SQL(
        "UPDATE {schema}.{table} SET etat_ouverture = 'ouverte' WHERE fid = {fid};"
    ).format(
        schema=sql.Identifier(uri.schema()),
        table=sql.Identifier(uri.table()),
        fid=sql.Literal(fid_vanne),
    )
    connection.executeSql(query.as_string(pg_conn))
    pg_conn.close()
    layer.triggerRepaint()


def ass_downstream(id_noeud: str, id_layer: str):
    """
    Descendre le réseau de canalisations ASS à partir du noeud sélectionné
    et afficher les canalisations en aval du noeud sélectionnné.

    These lines are included in the QGIS project.

        from qgis.utils import plugins
        plugins['stareau'].run_action(
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

    pg_conn = connect(uri.connectionInfo())
    query = sql.SQL(
        "SELECT d.idx, d.fid_canalisation FROM {schema}.ass_downstream({id_noeud}) d"
    ).format(
        schema=sql.Identifier(schema),
        id_noeud=sql.Literal(id_noeud),
    )
    records = connection.execSql(query.as_string(pg_conn))
    pg_conn.close()
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
        str(plugin_path("actions", "styles", "downstream_symbology.qml")),
        categories = QgsMapLayer.Symbology,
    )


def ass_upstream(id_noeud: str, id_layer: str):
    """
    Remonter le réseau de canalisations ASS à partir du noeud sélectionné
    et afficher les canalisations en amont du noeud sélectionnné.

    These lines are included in the QGIS project.

        from qgis.utils import plugins
        plugins['stareau'].run_action(
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

    pg_conn = connect(uri.connectionInfo())
    query = sql.SQL(
        "SELECT d.idx, d.fid_canalisation FROM {schema}.ass_upstream({id_noeud}) d"
    ).format(
        schema=sql.Identifier(schema),
        id_noeud=sql.Literal(id_noeud),
    )
    records = connection.execSql(query.as_string(pg_conn))
    pg_conn.close()
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
        str(plugin_path("actions", "styles", "upstream_symbology.qml")),
        categories = QgsMapLayer.Symbology,
    )


def aep_pgr_path_to_nearest_target(fid_noeud: str, id_layer: str, target_table: str):
    """
    Parcourir le réseau de canalisations AEP à partir du noeud sélectionné
    et afficher les canalisations entre le noeud sélectionné et cible la plus proche.

    These lines are included in the QGIS project.

        from qgis.utils import plugins
        plugins['stareau'].run_action(
            'aep_pgr_path_to_nearest_target',
            fid_noeud = [% fid %],
            id_layer = '[% @layer_id %]',
            target_table = 'target_table',
        )
    """
    action_name = "aep_pgr_path_to_nearest_target"

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
    if layer.fields().indexOf('fid') == -1:
        display_error_message(
            f"Erreur dans l'action \"{action_name}\", "
            f"la couche {id_layer} n'a pas de champ 'fid' !"
        )
        return

    if not target_table.startswith('aep_'):
        display_error_message(
            f"Erreur dans l'action \"{action_name}\", "
            f"le nom de la table '{target_table}' est invalide, il doit commencer par 'aep_'"
        )
        return

    layer_uri = layer.dataProvider().uri()
    layer_schema = '_'.join(layer_uri.schema().split('_')[:-1])

    metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
    connection = metadata.createConnection(layer_uri.uri(), {})

    target_schema = layer_uri.schema()
    pg_conn = connect(layer_uri.connectionInfo())
    query = sql.SQL(
        "SELECT fid FROM {layer_schema}.aep_pgr_path_to_nearest_target_avoiding_closed_valves(" \
        "{fid_noeud}, {target_schema}, {target_table})"
    ).format(
        layer_schema=sql.Identifier(layer_schema),
        fid_noeud=sql.Literal(fid_noeud),
        target_schema=sql.Literal(target_schema),
        target_table=sql.Literal(target_table),
    )
    records = connection.execSql(query.as_string(pg_conn))
    pg_conn.close()

    fids = [record[0] for record in records]
    if not fids:
        display_info_message("Aucun chemin n'a été trouvé pour atteindre la cible")
        return

    uri = QgsDataSourceUri(layer.dataProvider().uri())
    uri.setWkbType(QgsWkbTypes.LineString)
    uri.setDataSource(
        f"{layer_schema}_principale",
        "canalisation",
        "geom",
        f"fid IN ({','.join([str(fid) for fid in fids])})",
        "fid",
    )

    source = QgsVectorLayer(uri.uri(), f"path_to_{target_table}", "postgres")
    QgsProject.instance().addMapLayer(source)
    source.loadNamedStyle(
        str(plugin_path("actions", "styles", "path_to_target_symbology.qml")),
        categories = QgsMapLayer.Symbology,
    )


def aep_pgr_nearest_vannes(id_layer: str, point_x: float, point_y: float, closed_valves_only: bool = False):
    """
    Parcourir le réseau de canalisations AEP à partir d'un point sur une canalisation
    et afficher les vannes les plus proches.

    These lines are included in the QGIS project.

        from qgis.utils import plugins
        plugins['stareau'].run_action(
            'aep_pgr_nearest_vannes',
            id_layer = '[% @layer_id %]',
            point_x = [% point_x %],
            point_y = [% point_y %],
            closed_valves_only = [% closed_valves_only %]
        )
    """
    action_name = "aep_pgr_nearest_vannes"

    function_name = "aep_pgr_nearest_closed_vannes" if closed_valves_only else "aep_pgr_nearest_vannes"

    point_wkt = QgsPointXY(point_x, point_y).asWkt()

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
    if layer.fields().indexOf('fid') == -1:
        display_error_message(
            f"Erreur dans l'action \"{action_name}\", "
            f"la couche {id_layer} n'a pas de champ 'fid' !"
        )
        return

    layer_uri = layer.dataProvider().uri()
    layer_schema = '_'.join(layer_uri.schema().split('_')[:-1])

    metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
    connection = metadata.createConnection(layer_uri.uri(), {})

    pg_conn = connect(layer_uri.connectionInfo())
    query = sql.SQL(
        'SELECT fid FROM {layer_schema}.{function_name}(' \
        'ST_GeomFromText({point_wkt}, 2154))'
    ).format(
        layer_schema=sql.Identifier(layer_schema),
        function_name=sql.Identifier(function_name),
        point_wkt=sql.Literal(point_wkt)
    )

    records = connection.execSql(query.as_string(pg_conn))
    pg_conn.close()

    fids = [record[0] for record in records]
    if not fids:
        display_info_message("Aucune vanne n'a été trouvée")
        return

    # Selected valves
    uri = QgsDataSourceUri(layer.dataProvider().uri())
    uri.setWkbType(QgsWkbTypes.Point)
    uri.setDataSource(
        f"{layer_schema}_aep",
        "aep_vanne",
        "geom",
        f"fid IN ({','.join([str(fid) for fid in fids])})",
        "fid",
    )

    source = QgsVectorLayer(uri.uri(), "vannes_trouvées", "postgres")
    QgsProject.instance().addMapLayer(source)
    source.loadNamedStyle(
        str(plugin_path("actions", "styles", "selected_vannes_symbology.qml")),
        categories = QgsMapLayer.Symbology,
    )

def noop_action(a: str, b: int, c: bool):
    """Test action

    Permet de vérifier le passage de paramètre
    """
    assert isinstance(a, str)   # noqa S101
    assert isinstance(b, int)   # noqa S101
    assert isinstance(c, bool)  # noqa S101
    pass

