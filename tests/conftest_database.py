"""Base class for tests using a database."""
import os

from pathlib import Path
from typing import Generator, Optional, Sequence

import psycopg
import pytest

from qgis import processing
from qgis.core import QgsApplication

from stareau.plugin_tools import resources
from stareau.plugin_tools.feedback import LoggerProcessingFeedBack
from stareau.plugin_tools.resources import schema_version
from stareau.processing.provider import Provider


# Return the latest upgrade version
@pytest.fixture(scope="session")
def db_install_version() -> Optional[int]:
    version = os.getenv("DB_INSTALL_VERSION")
    if version is not None:
        return int(version)

    latest = resources.latest_upgrade()
    return latest[0] if latest else None


# Return the schema defined in environment
@pytest.fixture(scope="session")
def db_schema() -> str:
    return os.getenv("SCHEMA", resources.schema_name())


# Register the processing provider once
@pytest.fixture(scope="session")
def processing_provider() -> Provider:
    """Initialize processing"""
    provider = Provider()

    registry = QgsApplication.processingRegistry()
    registry.addProvider(provider)

    provider_id = provider.id()

    assert registry.algorithmById(f"{provider_id}:create_database_structure") is not None
    assert registry.algorithmById(f"{provider_id}:upgrade_database_structure") is not None

    return provider


@pytest.fixture(scope="session")
def db_test_sql(data: Path) -> Sequence[Path]:
    """Return the list of sql scripts to run
    when initializing database for tests
    """
    return (data.joinpath("99_test_data.sql"),)


@pytest.fixture()
def initialized_database(
    db_connection: psycopg.Connection,
    processing_provider: Provider,
    db_test_sql: Sequence[Path],
) -> psycopg.Connection:
    """Create a fresh database structure and load test data"""
    params = {
        "CONNECTION_NAME": "test",
        "OVERRIDE": True,
    }
    feedback = LoggerProcessingFeedBack()

    alg = f"{processing_provider.id()}:create_database_structure"
    processing_output = processing.run(alg, params, feedback=feedback)

    assert processing_output["OUTPUT_STATUS"] == 1
    assert processing_output["OUTPUT_VERSION"] == schema_version()

    cursor = db_connection.cursor()
    for sql_file in db_test_sql:
        with Path.open(sql_file, "r") as f:
            cursor.execute(f.read())
    cursor.close()

    return db_connection


def open_db_connection() -> psycopg.Connection:
    if os.getenv("TEST_RUNTYPE") == "docker":
        connection =  psycopg.connect(
            user="docker",
            password="docker",  # noqa S106
            host="db",
            port="5432",
            dbname="gis"
        )
    else:
        connection = psycopg.connect(
            user="docker",
            password="docker",  # noqa S106
            host="localhost",
            port="35432",
            dbname="gis"
        )

    return connection


# The following is executed  in each test
#
# Initialize (Override existing) and return a db
# connection
@pytest.fixture()
def db_connection() -> Generator[psycopg.Connection, None, None]:
    """Initialize (Override existing) and return a db connection"""
    connection = open_db_connection()
    with connection:
        yield connection

