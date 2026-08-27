from psycopg2 import connect, sql
from qgis.core import (
    QgsDataSourceUri,
    QgsFeatureRequest,
    QgsFeatureSink,
    QgsProcessing,
    QgsProcessingException,
    QgsProcessingParameterDatabaseSchema,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterProviderConnection,
    QgsProject,
    QgsProviderRegistry,
    QgsVectorLayer,
    QgsWkbTypes,
)

from ..database.base import BaseDatabaseAlgorithm, i18n, resources
from ..tools import get_connection_name
from .base import NETWORK_TYPES

# Shorcut
tr = i18n.tr


class OrphanNodes(BaseDatabaseAlgorithm):
    """
    Get orphan nodes
    """

    CONNECTION_NAME = "CONNECTION_NAME"
    SCHEMA = "SCHEMA"

    NETWORK_TYPE = "NETWORK_TYPE"
    DESTINATION = "DESTINATION"

    def name(self):
        return "orphan_nodes"

    def displayName(self):
        return tr("Get orphan nodes")

    def shortHelpString(self):
        return tr("Get orphan nodes in the water network")

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
                tr("Schema name"),
                connectionParameterName=self.CONNECTION_NAME,
                defaultValue=resources.schema_name(),
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.NETWORK_TYPE,
                tr("Network type"),
                options=NETWORK_TYPES,
                defaultValue="",
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.DESTINATION,
                tr("Destination"),
                QgsProcessing.TypeVectorPoint,
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
            msg = tr(f"Schema {schema} does not exist in database!")
            return False, msg

        return super(OrphanNodes, self).checkParameterValues(parameters, context)

    def processAlgorithm(self, parameters, context, feedback):
        metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
        connection_name = self.parameterAsConnectionName(parameters, self.CONNECTION_NAME, context)
        connection = metadata.findConnection(connection_name)
        schema = self.parameterAsString(parameters, self.SCHEMA, context)
        n_type = self.parameterAsEnum(parameters, self.NETWORK_TYPE, context)

        uri = QgsDataSourceUri(connection.uri())
        pg_conn = connect(uri.connectionInfo())
        if NETWORK_TYPES[n_type] == "ASS":
            subquery = (
                sql.SQL("( SELECT * FROM {schema}.ass_noeud_orphelin() )")
                .format(
                    schema=sql.Identifier(schema),
                )
                .as_string(pg_conn)
            )
            uri.setDataSource("", subquery, "geom", "", "fid")
        elif NETWORK_TYPES[n_type] == "AEP":
            subquery = (
                sql.SQL("( SELECT * FROM {schema}.aep_noeud_orphelin() )")
                .format(
                    schema=sql.Identifier(schema),
                )
                .as_string(pg_conn)
            )
            uri.setDataSource("", subquery, "geom", "", "fid")
        else:
            pg_conn.close()
            raise QgsProcessingException(tr("Network type not supported!"))
        pg_conn.close()

        source = QgsVectorLayer(uri.uri(), "layername", "postgres")

        (sink, dest_id) = self.parameterAsSink(
            parameters, self.DESTINATION, context, source.fields(), QgsWkbTypes.Point, source.sourceCrs()
        )

        sink.addFeatures(source.getFeatures(QgsFeatureRequest()), QgsFeatureSink.FastInsert)

        return {self.DESTINATION: dest_id}

    def postProcessAlgorithm(self, context, feedback):
        for key, details in context.layersToLoadOnCompletion().items():
            if details.outputName != self.DESTINATION:
                continue
            details.name = tr("Orphan nodes")
            details.forceName = True
            context.addLayerToLoadOnCompletion(key, details)

        return {}
