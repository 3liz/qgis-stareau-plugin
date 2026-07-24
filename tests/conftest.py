import sys

from pathlib import Path
from typing import Any

import pytest

from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QT_VERSION_STR

# NOTE Remove if not using database
from .conftest_database import (  # noqa F401
    db_connection,
    db_install_version,
    db_schema,
    db_test_sql,
    initialized_database,
    open_db_connection,
    processing_provider,
)
from .qgis_testing import QGIS_VERSION_INT, install_logger_hook, load_plugin

# with warnings.catch_warnings():
#    warnings.filterwarnings("ignore", category=DeprecationWarning)
#    from osgeo import gdal

PLUGIN_SOURCE = "stareau"


def pytest_addoption(parser):
    parser.addoption("--with-pgrouting", action="store_true", help="Enable pg_routing tests")


def pytest_collection_modifyitems(config, items):
    enable_pgrouting = config.getoption("--with-pgrouting")

    skip_pg_routing = pytest.mark.skip(reason="pgRouting not activated")

    for item in items:
        if not enable_pgrouting and "pgrouting" in item.keywords:
            item.add_marker(skip_pg_routing)


def pytest_report_header(config):
    from osgeo import gdal

    with open_db_connection() as conn:
        extensions = "\n".join(f"* {name:<20} {version}"
            for (name, version) in conn.execute("SELECT extname, extversion FROM pg_extension"))

    return (
        f"QGIS : {QGIS_VERSION_INT}\n"
        f"Python GDAL : {gdal.VersionInfo('VERSION_NUM')}\n"
        f"Python : {sys.version}\n"
        f"QT : {QT_VERSION_STR}\n"
        f"PostgreSQL: Installed extensions:\n{extensions}"
    )

#
# Fixtures
#


def pytest_sessionstart(session: pytest.Session):
    """Start qgis application"""

    # Enable PgRouting
    with open_db_connection() as conn:
        if session.config.getoption("--with-pgrouting"):
            row = conn.execute("CREATE EXTENSION IF NOT EXISTS pgRouting CASCADE;")
            print("Activating pgRouting extension", row.statusmessage)
        else:
            row = conn.execute("DROP EXTENSION IF EXISTS pgRouting CASCADE;")
            print("Disabling pgRouting extension: ", row.statusmessage)

    install_logger_hook()


@pytest.fixture(scope="session")
def rootdir(request: pytest.FixtureRequest) -> Path:
    return request.config.rootpath


@pytest.fixture(scope="session")
def data(rootdir: Path) -> Path:
    return rootdir.joinpath("data")


@pytest.fixture(autouse=True, scope="session")
def plugin(rootdir: Path, qgis_iface: QgisInterface, qgis_processing: Any) -> Any:
    plugin_path = rootdir.parent.joinpath(PLUGIN_SOURCE)
    plugin = load_plugin(plugin_path, qgis_iface, processing=True)

    yield plugin
