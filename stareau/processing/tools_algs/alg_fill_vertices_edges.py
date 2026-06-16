
from psycopg2 import connect, sql
from qgis.core import (
    QgsDataSourceUri,
    QgsProcessingParameterDatabaseSchema,
    QgsProcessingParameterProviderConnection,
    QgsProject,
    QgsProviderConnectionException,
    QgsProviderRegistry,
)

from ..database.base import BaseDatabaseAlgorithm, i18n, resources
from ..tools import get_connection_name

# Shorcut
tr = i18n.tr


class FillVerticesEdgesAEP(BaseDatabaseAlgorithm):
    """
    Fill the "graph schema" with the AEP vertices and edges from the main schema
    """

    CONNECTION_NAME = "CONNECTION_NAME"
    SCHEMA = "SCHEMA"

    def name(self):
        return "fill_vertices_edges_aep"

    def displayName(self):
        return tr("Fill AEP vertices and edges")

    def shortHelpString(self):
        return tr(
            "Fill the graph schema with the AEP edges and vertices from the main schema "
        )

    def initAlgorithm(self, config):
        project = QgsProject.instance()
        connection_name = get_connection_name(project)
        self.addParameter(
            QgsProcessingParameterProviderConnection(
                self.CONNECTION_NAME,
                tr("Connection to the PostgreSQL database"),
                "postgres",
                defaultValue=connection_name,
                optional=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterDatabaseSchema(
                self.SCHEMA,
                tr("Schema"),
                connectionParameterName=self.CONNECTION_NAME,
                defaultValue=resources.schema_name(),
            )
        )

    def checkParameterValues(self, parameters, context):
        metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
        connection_name = self.parameterAsConnectionName(
            parameters,
            self.CONNECTION_NAME,
            context,
        )
        connection = metadata.findConnection(connection_name)
        schema = self.parameterAsString(parameters, self.SCHEMA, context)

        if schema not in connection.schemas():
            msg = tr(
                f"Schema {schema} does not exist in database!"
            )
            return False, msg

        return super(FillVerticesEdgesAEP, self).checkParameterValues(parameters, context)

    def processAlgorithm(self, parameters, context, feedback):
        metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
        connection_name = self.parameterAsConnectionName(parameters, self.CONNECTION_NAME, context)
        connection = metadata.findConnection(connection_name)

        graph_schema = self.parameterAsSchema(parameters, self.SCHEMA, context)
        main_schema = f'{graph_schema}_principale'

        pg_conn = connect(QgsDataSourceUri(connection.uri()).connectionInfo())

        query = sql.SQL("""
        -- purge des tables
        TRUNCATE {graph_schema}.aep_edge RESTART IDENTITY;
        TRUNCATE {graph_schema}.aep_vertex RESTART IDENTITY;

        -- Ajout des noeuds réseaux aep
        INSERT INTO {graph_schema}.aep_vertex (id, fictif, geom)
            SELECT fid as id, False as fictif, geom FROM {main_schema}.noeud_reseau WHERE type_reseau = 'aep';
        -- Déplacement de la séquence à la valeur max
        SELECT setval({seq}::regclass,
            (SELECT MAX(id) FROM {graph_schema}.aep_vertex));
        -- Ajout des noeuds réseaux aep manquants
        INSERT INTO {graph_schema}.aep_vertex (fictif, geom)
            SELECT True as fictif, geom FROM {graph_schema}.aep_noeud_manquant();

        -- Ajout des canalisations AEP ayant des noeuds en débuts et fin
        INSERT INTO {graph_schema}.aep_edge (id, source, target, cost, reverse_cost, geom)
            SELECT c.fid as id, ni.fid as source, nt.fid as target, ST_Length(c.geom) as cost,
            ST_Length(c.geom) as reverse_cost, c.geom
                FROM {main_schema}.canalisation c
                JOIN {main_schema}.noeud_reseau ni ON c.noeudinitial = ni.id_noeud_reseau
                JOIN {main_schema}.noeud_reseau nt ON c.noeudterminal = nt.id_noeud_reseau
                WHERE c.type_reseau = 'aep' AND NOT ST_IsEmpty(c.geom);

        -- Ajout des canalisations AEP  ayant un noeud terminal manquant
        INSERT INTO {graph_schema}.aep_edge (id, source, target, cost, reverse_cost, geom)
            SELECT c.fid as id, ni.fid as source, vt.id as target, ST_Length(c.geom) as cost,
            ST_Length(c.geom) as reverse_cost, c.geom
                FROM {main_schema}.canalisation c
                JOIN {main_schema}.noeud_reseau ni ON c.noeudinitial = ni.id_noeud_reseau
                JOIN {graph_schema}.aep_vertex vt ON St_EndPoint(c.geom) && vt.geom
                    AND St_EndPoint(c.geom) = vt.geom
                WHERE c.type_reseau = 'aep' AND NOT ST_IsEmpty(c.geom) AND c.noeudterminal = 'non_renseigne';

        -- Ajout des canalisations AEP  ayant un noeud initial manquant
        INSERT INTO {graph_schema}.aep_edge (id, source, target, cost, reverse_cost, geom)
            SELECT c.fid as id, vi.id as source, nt.fid as target, ST_Length(c.geom) as cost,
            ST_Length(c.geom) as reverse_cost, c.geom
                FROM {main_schema}.canalisation c
                JOIN {graph_schema}.aep_vertex vi ON St_StartPoint(c.geom) && vi.geom
                    AND St_StartPoint(c.geom) = vi.geom
                JOIN {main_schema}.noeud_reseau nt ON c.noeudterminal = nt.id_noeud_reseau
                WHERE c.type_reseau = 'aep' AND NOT ST_IsEmpty(c.geom) AND c.noeudinitial = 'non_renseigne';

        -- Ajout des canalisations AEP  ayant le noeud terminal et initial manquant
        INSERT INTO {graph_schema}.aep_edge (id, source, target, cost, reverse_cost, geom)
            SELECT c.fid as id, vi.id as source, vt.id as target, ST_Length(c.geom) as cost,
                ST_Length(c.geom) as reverse_cost, c.geom
                FROM {main_schema}.canalisation c
                JOIN {graph_schema}.aep_vertex vi ON St_StartPoint(c.geom) && vi.geom
                    AND St_StartPoint(c.geom) = vi.geom
                JOIN {graph_schema}.aep_vertex vt ON St_EndPoint(c.geom) && vt.geom
                    AND St_EndPoint(c.geom) = vt.geom
                WHERE c.type_reseau = 'aep' AND NOT ST_IsEmpty(c.geom)
                    AND c.noeudinitial = 'non_renseigne' AND c.noeudterminal = 'non_renseigne';
        """).format(
            graph_schema=sql.Identifier(graph_schema),
            main_schema=sql.Identifier(main_schema),
            seq=sql.Literal(f"{graph_schema}.aep_vertex_id_seq"),
        )

        query_index = sql.SQL("""
        -- Mise à jour des index
        REINDEX TABLE {graph_schema}.aep_vertex;
        REINDEX TABLE {graph_schema}.aep_edge;
        """).format(graph_schema=sql.Identifier(graph_schema))

        try:
            connection.execSql(query.as_string(pg_conn))
            connection.vacuum(graph_schema, "aep_vertex")
            connection.vacuum(graph_schema, "aep_edge")
            connection.execSql(query_index.as_string(pg_conn))
            feedback.pushInfo(tr("Edges and vertex are correctly generated"))

        except QgsProviderConnectionException as e:
            feedback.reportError(tr(
                f"An error occured while filling edges and vertex : \n {e}"),
                fatalError=True
            )
        finally:
            pg_conn.close()

        return {}
