
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
        return tr("Pipes from treatment to reservoir")

    def shortHelpString(self):
        return tr(
            "Create a new layer with the pipes between treatments and the nearest"
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
                self.SCHEMA,
                tr("Main schema"),
                connectionParameterName=self.CONNECTION_NAME
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
            msg = tr(
                f"Schema {schema} does not exist in database!"
            )
            return False, msg

        return super(PipesTreatmentToReservoir, self).checkParameterValues(parameters, context)

    def processAlgorithm(self, parameters, context, feedback):
        metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
        connection_name = self.parameterAsConnectionName(parameters, self.CONNECTION_NAME, context)
        connection = metadata.findConnection(connection_name)
        schema_global = self.parameterAsSchema(parameters, self.SCHEMA, context)
        schema_aep =  schema_global + "_aep"
        uri = QgsDataSourceUri(connection.uri())

        # get treatments fids
        traitement_fids = connection.execSql(
                f"SELECT fid FROM {schema_aep}.aep_traitement"
        )

        # get canalisations fids between each treatment and the nearest reservoir
        canalisation_fids = []

        for fid in traitement_fids:
            records = connection.execSql(
                f"SELECT fid FROM {schema_global}.aep_pgr_path_to_nearest_target("
                f"{fid[0]}, '{schema_aep}'::text, 'aep_reservoir'::text)"
            )
            fids = [record[0] for record in records]
            canalisation_fids.append(fids)

        # Select canalisations
        sql = f"""
            fid IN ({','.join([str(fid) for fids in canalisation_fids for fid in fids])})
        """
        uri.setDataSource(
            f"{schema_aep}",
            "aep_canalisation",
            "geom",
            sql,
            "fid"
        )
        uri.setWkbType(QgsWkbTypes.LineString)
        source = QgsVectorLayer(uri.uri(), "pipes_function", "postgres")

        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context,
                                           source.fields(), QgsWkbTypes.LineString, source.sourceCrs())
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
                categories = QgsMapLayer.Symbology,
            )
            layer.triggerRepaint()
        return {}
