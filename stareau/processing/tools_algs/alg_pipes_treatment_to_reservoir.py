from psycopg2 import connect, sql
from qgis.core import (
    QgsDataSourceUri,
    QgsFeatureRequest,
    QgsFeatureSink,
    QgsMapLayer,
    QgsProcessing,
    QgsProcessingParameterDatabaseSchema,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterProviderConnection,
    QgsProcessingUtils,
    QgsProject,
    QgsProviderRegistry,
    QgsVectorLayer,
    QgsWkbTypes,
)

from stareau.plugin_tools.resources import plugin_path

from ..database.base import BaseDatabaseAlgorithm, i18n
from ..tools import get_connection_name

# Shorcut
tr = i18n.tr


class PipesTreatmentToReservoir(BaseDatabaseAlgorithm):
    """
    Create a new layer with the pipes between treatments and the nearest
    reservoir in order to check the pipes function.
    """

    CONNECTION_NAME = "CONNECTION_NAME"
    SCHEMA = "SCHEMA"

    OUTPUT = "OUTPUT"

    def name(self):
        return "pipes_treatment_to_reservoir"

    def displayName(self):
        return tr("Treatments to nearest reservoir")

    def shortHelpString(self):
        return tr(
            "Create a new layer with the pipes between treatments and the nearest "
            "reservoir in order to check the pipes function."
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
                self.SCHEMA, tr("Main schema"), connectionParameterName=self.CONNECTION_NAME
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                tr("Pipes between treatments and the nearest reservoir"),
                QgsProcessing.TypeVectorLine,
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

        return super(PipesTreatmentToReservoir, self).checkParameterValues(parameters, context)

    def processAlgorithm(self, parameters, context, feedback):
        metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
        connection_name = self.parameterAsConnectionName(parameters, self.CONNECTION_NAME, context)
        connection = metadata.findConnection(connection_name)
        schema_global = self.parameterAsSchema(parameters, self.SCHEMA, context)
        schema_aep = schema_global + "_aep"
        uri = QgsDataSourceUri(connection.uri())

        # get treatments fids
        # psycopg2 composed request
        query_traitements = sql.SQL("""
            SELECT fid FROM {schemaname}.aep_traitement
        """).format(schemaname=sql.Identifier(schema_aep))

        # psycopg2 connection
        conn = connect(uri.connectionInfo())
        traitement_fids = connection.executeSql(query_traitements.as_string(conn))

        # get canalisations fids between each treatment and the nearest reservoir
        canalisation_fids = []

        for fid in traitement_fids:
            query_canal = sql.SQL("""
                SELECT fid FROM {sg}.aep_pgr_path_to_nearest_target(
                {f}, {saep}::text, 'aep_reservoir'::text)
            """).format(
                sg=sql.Identifier(schema_global),
                f=sql.Literal(fid[0]),
                saep=sql.Literal(schema_aep),
            )
            records = connection.execSql(query_canal.as_string(conn))
            fids = [record[0] for record in records]
            canalisation_fids.append(fids)

        # psycopg2 connection close
        conn.close()

        # Select canalisations
        canalisations_sql = f"""
            fid IN ({",".join([str(fid) for fids in canalisation_fids for fid in fids])})
        """
        uri.setDataSource(f"{schema_aep}", "aep_canalisation", "geom", canalisations_sql, "fid")
        uri.setWkbType(QgsWkbTypes.LineString)
        source = QgsVectorLayer(uri.uri(), "pipes_function", "postgres")

        (sink, dest_id) = self.parameterAsSink(
            parameters, self.OUTPUT, context, source.fields(), QgsWkbTypes.LineString, source.sourceCrs()
        )
        sink.addFeatures(source.getFeatures(QgsFeatureRequest()), QgsFeatureSink.FastInsert)
        self.dest_id = dest_id

        return {self.OUTPUT: dest_id}

    def postProcessAlgorithm(self, context, feedback):
        # Rename layer
        details = context.layerToLoadOnCompletionDetails(self.dest_id)
        if details:
            details.name = tr("Pipes layer")
            details.forceName = True

        # Apply style
        layer = QgsProcessingUtils.mapLayerFromString(self.dest_id, context)
        if layer:
            layer.loadNamedStyle(
                str(plugin_path("resources", "styles", "pipes_function_symbology.qml")),
                categories=QgsMapLayer.Symbology,
            )
            layer.triggerRepaint()
        return {}
