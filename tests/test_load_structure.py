"""Tests for Processing algorithms."""

import unittest

from pathlib import Path

import psycopg

from qgis import processing

from stareau.plugin_tools.feedback import LoggerProcessingFeedBack
from stareau.plugin_tools.resources import (
    available_migrations,
    schema_name,
    schema_version,
)
from stareau.processing.database import CreateDatabaseStructure
from stareau.processing.provider import Provider


SCHEMAS = [
    "stareau",
    "stareau_commun",
    "stareau_principale",
    "stareau_ass",
    "stareau_ass_brcht",
    "stareau_aep",
    "stareau_aep_brcht",
    "stareau_valeur",
    "stareau_defense_incendie",
]
# This list must not be changed
# as it correspond to the list of tables
# created for the first version
TABLES_FOR_FIRST_VERSION = {}
TABLES_FOR_FIRST_VERSION["stareau"] = [
    "glossary_test_category",
    "metadata",
    "test",
]
TABLES_FOR_FIRST_VERSION["stareau_commun"] = [
    "piezometre",
    "pluviometre",
    "point_geolocalisation",
]
TABLES_FOR_FIRST_VERSION["stareau_principale"] = [
    "canalisation",
    "champ_commun",
    "dimension",
    "emprise",
    "mm_emprise_ponctuel",
    "noeud_reseau",
]
TABLES_FOR_FIRST_VERSION["stareau_ass"] = [
    "ass_affleurant",
    "ass_bassin",
    "ass_canalisation",
    "ass_chambre_depollution",
    "ass_equipement",
    "ass_exutoire",
    "ass_genie_civil",
    "ass_gestion_epl_ligne",
    "ass_gestion_epl_point",
    "ass_gestion_epl_surface",
    "ass_ouvrage_special_ligne",
    "ass_ouvrage_special_point",
    "ass_ouvrage_special_surface",
    "ass_perimetre_gestion",
    "ass_piece",
    "ass_piece_hors_topo",
    "ass_pompage",
    "ass_point_mesure",
    "ass_point_prelevement",
    "ass_pretraitement",
    "ass_protection_mecanique",
    "ass_traitement",
    "ass_regard",
    "mm_ass_cana_protection",
]
TABLES_FOR_FIRST_VERSION["stareau_ass_brcht"] = [
    "ass_canalisation_branchement",
    "ass_engouffrement_ligne",
    "ass_engouffrement_point",
    "ass_engouffrement_surface",
    "ass_point_collecte",
    "ass_raccord",
]
TABLES_FOR_FIRST_VERSION["stareau_aep"] = [
    "aep_affleurant",
    "aep_appareillage",
    "aep_canalisation",
    "aep_captage",
    "aep_genie_civil",
    "aep_perimetre_gestion",
    "aep_piece",
    "aep_piece_hors_topo",
    "aep_pompage",
    "aep_point_mesure",
    "aep_protection_mecanique",
    "aep_traitement",
    "aep_regulation",
    "aep_reservoir",
    "aep_station_alerte",
    "aep_vanne",
    "mm_aep_cana_protection",
]
TABLES_FOR_FIRST_VERSION["stareau_aep_brcht"] = [
    "aep_canalisation_branchement",
    "aep_piece_branchement",
    "aep_point_livraison",
    "aep_raccord",
    "aep_vanne_branchement",
]
TABLES_FOR_FIRST_VERSION["stareau_valeur"] = [
    "aep_contenu_canalisation",
    "aep_etat_ouverture",
    "aep_fonction_branchement",
    "aep_fonction_canalisation",
    "aep_fonction_point_mesure",
    "aep_fonction_pompage",
    "aep_fonction_traitement",
    "aep_fonction_vanne",
    "aep_installation_pompage",
    "aep_sens_fermeture",
    "aep_type_appareillage",
    "aep_type_captage",
    "aep_type_consigne",
    "aep_type_desinfection",
    "aep_type_piece",
    "aep_type_point_livraison",
    "aep_type_point_mesure",
    "aep_type_pression",
    "aep_type_regulation",
    "aep_type_reservoir",
    "aep_type_ressource",
    "aep_type_vanne",
    "ass_code_sandre",
    "ass_contenu_canalisation",
    "ass_destination",
    "ass_fonction_bassin",
    "ass_fonction_branchement",
    "ass_fonction_canalisation",
    "ass_fonction_equipement",
    "ass_fonction_gestion_epl",
    "ass_fonction_pompage",
    "ass_position",
    "ass_structure_bassin",
    "ass_techno_traitement",
    "ass_type_bassin",
    "ass_type_chambre",
    "ass_type_descente",
    "ass_type_engouffrement",
    "ass_type_equipement",
    "ass_type_gestion_epl",
    "ass_type_ouvrage_special",
    "ass_type_piece",
    "ass_type_point_collecte",
    "ass_type_point_mesure",
    "ass_type_point_prelevement",
    "ass_type_pompage",
    "ass_type_pretraitement",
    "ass_type_raccord",
    "ass_type_regard",
    "com_etat_service",
    "com_forme",
    "com_materiau",
    "com_mode_circulation",
    "com_mode_lever",
    "com_origine",
    "com_oui_non",
    "com_precision",
    "com_raison_pose",
    "com_reference_z",
    "com_revetement_interieur",
    "com_type_acces",
    "com_type_affleurant",
    "com_type_perimetre",
    "com_type_pluviometre",
    "com_type_pose",
    "com_type_protection",
    "com_type_reseau",
    "com_type_usager"
]
TABLES_FOR_FIRST_VERSION["stareau_defense_incendie"] = [
    "pei",
    "pei_diam",
    "pei_precision",
    "pei_source",
    "pei_statut",
    "pei_type",
]

# Expected list of tables for current version
# Must be changed any time the SQL structure is changed
TABLES_FOR_CURRENT_VERSION = [
    "glossary_test_category",
    "metadata",
    "test",
]


def test_processing_create(
    db_connection: psycopg.Connection,
    processing_provider: Provider,
):
    params = {
        "CONNECTION_NAME": "test",
        "OVERRIDE": True,
    }

    feedback = LoggerProcessingFeedBack()

    # Run create database structure alg
    alg = f"{processing_provider.id()}:create_database_structure"
    processing_output = processing.run(alg, params, feedback=feedback)

    assert processing_output["OUTPUT_STATUS"] == 1
    assert processing_output["OUTPUT_VERSION"] == schema_version()

    cursor = db_connection.cursor()
    case = unittest.TestCase()

    for db_schema in SCHEMAS:
        # Check the number of tables
        cursor.execute(
            f"""
            SELECT count(table_name)
            FROM information_schema.tables
            WHERE table_schema = '{db_schema}'
            """
        )
        records = cursor.fetchall()
        case.assertEqual(
            len(TABLES_FOR_FIRST_VERSION[db_schema]),
            records[0][0],
            f"Le nombre de table du schéma `{db_schema}` n'est pas celui attendu"
        )
        # Check the list of tables
        cursor.execute(
            f"""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = '{db_schema}'
            ORDER BY table_name
            """
        )
        records = cursor.fetchall()
        result = [r[0] for r in records]
        case.assertCountEqual(
            TABLES_FOR_FIRST_VERSION[db_schema],
            result,
            f"La liste des tables du schéma `{db_schema}` n'est pas celle attendue"
        )

    for table in TABLES_FOR_FIRST_VERSION["stareau_valeur"]:
        # Check the number of rows in each table
        cursor.execute(
            f"""
            SELECT count(*)
            FROM stareau_valeur.{table}
            """
        )
        records = cursor.fetchall()
        case.assertGreaterEqual(
            records[0][0],
            4,
            f"Le nombre de lignes de la table `stareau_valeur.{table}` n'est pas au moins égal à 4."
        )


def test_processing_create_with_schema_name(
    db_connection: psycopg.Connection,
    processing_provider: Provider,
):
    plugin_schema_name = schema_name()
    schema = "cnm_eau"
    params = {
        "CONNECTION_NAME": "test",
        "OVERRIDE": True,
        "SCHEMA": schema,
    }

    feedback = LoggerProcessingFeedBack()

    # Run create database structure alg
    alg = f"{processing_provider.id()}:create_database_structure"
    processing_output = processing.run(alg, params, feedback=feedback)

    assert processing_output["OUTPUT_STATUS"] == 1
    assert processing_output["OUTPUT_VERSION"] == schema_version()

    cursor = db_connection.cursor()
    case = unittest.TestCase()

    for db_schema in SCHEMAS:
        db_new_schema = db_schema.replace(f"{plugin_schema_name}", f"{schema}")
        # Check the number of tables
        cursor.execute(
            f"""
            SELECT count(table_name)
            FROM information_schema.tables
            WHERE table_schema = '{db_new_schema}'
            """
        )
        records = cursor.fetchall()
        case.assertEqual(
            len(TABLES_FOR_FIRST_VERSION[db_schema]),
            records[0][0],
            f"Le nombre de table du schéma `{db_new_schema}` n'est pas celui attendu"
        )
        # Check the list of tables
        cursor.execute(
            f"""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = '{db_new_schema}'
            ORDER BY table_name
            """
        )
        records = cursor.fetchall()
        result = [r[0] for r in records]
        case.assertCountEqual(
            TABLES_FOR_FIRST_VERSION[db_schema],
            result,
            f"La liste des tables du schéma `{db_new_schema}` n'est pas celle attendue"
        )

    for table in TABLES_FOR_FIRST_VERSION["stareau_valeur"]:
        # Check the number of rows in each table
        cursor.execute(
            f"""
            SELECT count(*)
            FROM {schema}_valeur.{table}
            """
        )
        records = cursor.fetchall()
        case.assertGreaterEqual(
            records[0][0],
            4,
            f"Le nombre de lignes de la table `{schema}_valeur.{table}` n'est pas au moins égal à 4."
        )


@unittest.skip("not yet ready")
def test_upgrade_from(
    db_schema: str,
    db_install_version: int,
    db_connection: psycopg.Connection,
    processing_provider: Provider,
    data: Path,
):
    """Test the algorithms for creating and updating the database structure."""

    current_version = schema_version()

    assert db_install_version is not None, "This test require at least one availabl upgrade"
    assert current_version >= db_install_version, (
        "Current schema version cannot be lower than install version"
    )

    # Get the installation dir
    install_dir = data.joinpath(f"install-version-{current_version}", "sql")
    assert install_dir.exists()

    feedback = LoggerProcessingFeedBack()

    # Create the database from the latest update
    CreateDatabaseStructure.create_database(
        "test",
        db_schema,
        version=db_install_version,
        override=True,
        install_dir=install_dir,
        feedback=feedback,
    )

    case = unittest.TestCase()

    provider_id = processing_provider.id()

    cursor = db_connection.cursor()

    # Check the list of tables and views from the database
    cursor.execute(
        f"""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = '{db_schema}'
        ORDER BY table_name
        """
    )
    records = cursor.fetchall()
    result = [r[0] for r in records]

    # Expected tables in the specific version written above at the beginning of the test.
    # DO NOT CHANGE HERE, change below at the end of the test.
    case.assertCountEqual(TABLES_FOR_FIRST_VERSION, result)

    assert result == TABLES_FOR_CURRENT_VERSION

    # Check if the version has been written in the metadata table
    sql = f"""
        SELECT me_version
        FROM {db_schema}.metadata
        WHERE me_status = 1
        ORDER BY me_version_date DESC
        LIMIT 1;
    """
    cursor.execute(sql)
    record = cursor.fetchone()
    assert record is not None
    assert int(record[0]) == db_install_version

    # Run the update database structure alg
    # Since the structure has been created with db_install_version above
    # The expected list of tables
    feedback.pushDebugInfo("Update the database")
    params = {
        "CONNECTION_NAME": "test",
        "RUN_MIGRATIONS": True
    }
    alg = f"{provider_id}:upgrade_database_structure"
    results = processing.run(alg, params, feedback=feedback)

    assert results["OUTPUT_STATUS"] == 1
    assert results["OUTPUT_STRING"] == "*** THE DATABASE STRUCTURE HAS BEEN UPDATED ***"

    # Check the version has been updated
    sql = f"""
        SELECT me_version
        FROM {db_schema}.metadata
        WHERE me_status = 1
        ORDER BY me_version_date DESC
        LIMIT 1;
    """
    cursor.execute(sql)
    record = cursor.fetchone()

    migrations = available_migrations()
    if migrations:
        version, _ = migrations[-1]
        assert record is not None
        assert int(record[0]) == version

    # Check the list of tables
    cursor.execute(
        f"""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = '{db_schema}'
        ORDER BY table_name
        """
    )
    records = cursor.fetchall()
    result = [r[0] for r in records]
    case.assertCountEqual(TABLES_FOR_CURRENT_VERSION, result)

    # Create the database structure with override
    # This will delete and recreate the structure for the last version
    feedback.pushDebugInfo("Relaunch the algorithm without override")
    params = {
        'CONNECTION_NAME': 'test',
        "OVERRIDE": True,
    }

    # Check we need to run upgrade or not
    feedback.pushDebugInfo("Update the database")
    params = {
        "CONNECTION_NAME": "test",
        "RUN_MIGRATIONS": True
    }
    alg = f"{provider_id}:upgrade_database_structure"
    results = processing.run(alg, params, feedback=feedback)
    assert results["OUTPUT_STATUS"] == 1
    assert results["OUTPUT_STRING"] == (
        " The database version already matches the plugin version. No upgrade needed."
    )

    # Check the list of tables
    cursor.execute(
        f"""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = '{db_schema}'
        ORDER BY table_name
        """
    )
    records = cursor.fetchall()
    result = [r[0] for r in records]

    case.assertCountEqual(TABLES_FOR_CURRENT_VERSION, result)

    assert result == TABLES_FOR_CURRENT_VERSION
