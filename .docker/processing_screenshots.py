#!/usr/bin/env python3
"""
Create screenshots of the plugin Processing algorithm dialogs for the documentation.

The dialogs are rendered by QGIS itself, without a display (Qt offscreen platform),
in a temporary QGIS profile containing a demo PostgreSQL connection.
The connection uses the PostgreSQL service 'test' of the docker database,
on which the database structure must be installed: the schema parameters
need a connection to the database.

Usage: run `make processing-screenshots`, or from the repository root, in the docker
image of QGIS, with the docker database:

    python3 .docker/processing_screenshots.py [OUTPUT_DIR]

OUTPUT_DIR defaults to docs/media, the output file names are relative to it.
"""

import os
import sys
import tempfile

from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
for path in ("/usr/share/qgis/python/plugins", "/usr/lib/qgis/python/plugins"):
    if Path(path).exists():
        sys.path.insert(0, path)

from qgis.core import QgsApplication, QgsProviderRegistry  # noqa: E402

DEMO_CONNECTION_NAME = "stareau_demo"
DEMO_CONNECTION_URI = "service='test'"
DEMO_SCHEMA = "stareau"

# Algorithm name: output file name, relative to the output directory
ALGORITHMS = {
    "configure_plugin": "installation/configure_plugin.png",
    "create_database_structure": "installation/create_database_structure.png",
    "upgrade_database_structure": "installation/upgrade_database_structure.png",
    "create_database_local_interface": "installation/create_database_local_interface.png",
    "missing_nodes": "user-guide/processing_missing_nodes.png",
    "orphan_nodes": "user-guide/processing_orphan_nodes.png",
    "duplicate_nodes": "user-guide/processing_duplicate_nodes.png",
    "fill_vertices_edges_aep": "user-guide/processing_fill_vertices_edges_aep.png",
    "pipes_water_intake_to_treatment": "user-guide/processing_pipes_water_intake_to_treatment.png",
    "pipes_treatment_to_reservoir": "user-guide/processing_pipes_treatment_to_reservoir.png",
}

DIALOG_WIDTH = 1200
DIALOG_HEIGHT = 600


def main() -> int:
    output_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs" / "media"

    # Use a temporary QGIS profile, to avoid using the user connections and settings
    profile_dir = tempfile.mkdtemp(prefix="qgis-profile-")
    app = QgsApplication([], True, profile_dir)
    app.initQgis()

    # Demo PostgreSQL connection
    metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
    connection = metadata.createConnection(DEMO_CONNECTION_URI, {})
    metadata.saveConnection(connection, DEMO_CONNECTION_NAME)

    from processing.core.Processing import Processing
    from processing.gui.AlgorithmDialog import AlgorithmDialog

    Processing.initialize()

    from stareau.processing.provider import Provider

    provider = Provider()
    QgsApplication.processingRegistry().addProvider(provider)

    for name, file_name in ALGORITHMS.items():
        algorithm = provider.algorithm(name)
        if algorithm is None:
            print(f"Algorithm '{name}' not found", file=sys.stderr)
            return 1

        dialog = AlgorithmDialog(algorithm.create())
        # Select the demo connection and schema in every connection and schema parameter
        values = {"providerconnection": DEMO_CONNECTION_NAME, "databaseschema": DEMO_SCHEMA}
        dialog.setParameters(
            {
                param.name(): values[param.type()]
                for param in algorithm.parameterDefinitions()
                if param.type() in values
            }
        )
        dialog.resize(DIALOG_WIDTH, DIALOG_HEIGHT)
        dialog.show()
        app.processEvents()

        output = output_dir / file_name
        output.parent.mkdir(parents=True, exist_ok=True)
        dialog.grab().save(str(output))
        dialog.close()
        print(f"{name} -> {output}")

    app.exitQgis()
    return 0


if __name__ == "__main__":
    sys.exit(main())
