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
    srid_value,
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

    # Close connection
    db_connection.close()


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

    # clear
    cursor.execute(
        f"""
        DROP SCHEMA IF EXISTS {schema}_defense_incendie CASCADE;
        DROP SCHEMA IF EXISTS {schema}_aep_brcht CASCADE;
        DROP SCHEMA IF EXISTS {schema}_aep CASCADE;
        DROP SCHEMA IF EXISTS {schema}_ass_brcht CASCADE;
        DROP SCHEMA IF EXISTS {schema}_ass CASCADE;
        DROP SCHEMA IF EXISTS {schema}_principale CASCADE;
        DROP SCHEMA IF EXISTS {schema}_commun CASCADE;
        DROP SCHEMA IF EXISTS {schema}_valeur CASCADE;
        DROP SCHEMA IF EXISTS {schema} CASCADE;
        DROP DOMAIN IF EXISTS {schema}.c_insee;
        DROP DOMAIN IF EXISTS {schema}.c_annee;
        """
    )

    # Close connection
    db_connection.close()


def test_processing_create_with_crs(
    db_connection: psycopg.Connection,
    processing_provider: Provider,
):
    plugin_schema_name = schema_name()
    plugin_srid = srid_value()
    srid = 3943
    params = {
        "CONNECTION_NAME": "test",
        "OVERRIDE": True,
        "CRS": f"EPSG:{srid}",
    }

    feedback = LoggerProcessingFeedBack()

    # Run create database structure alg
    alg = f"{processing_provider.id()}:create_database_structure"
    processing_output = processing.run(alg, params, feedback=feedback)

    assert processing_output["OUTPUT_STATUS"] == 1
    assert processing_output["OUTPUT_VERSION"] == schema_version()

    cursor = db_connection.cursor()
    case = unittest.TestCase()
    # Check the list of geometries
    cursor.execute(
        f"""
        SELECT *
        FROM geometry_columns
        WHERE f_table_schema LIKE '{plugin_schema_name}%'
        ORDER BY f_table_schema,f_table_name
        """
    )
    records = cursor.fetchall()
    for record in records:
        case.assertNotEqual(
            record[5],
            plugin_srid,
            f"Le SRID de {record[1]}.{record[2]} de la colonne {record[3]} ne devrait pas être {plugin_srid}",
        )
        case.assertEqual(
            record[5],
            srid,
            f"Le SRID de {record[1]}.{record[2]} de la colonne {record[3]} devrait être {srid} au lieu de {record[5]}",
        )

    # Close connection
    db_connection.close()


def test_processing_trigger(
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

    plugin_schema_name = schema_name()

    # INSERT noeud_reseau / ass_regard
    cursor.execute(
        f"""
        INSERT INTO "{plugin_schema_name}_ass".ass_regard (
            type_reseau, etat_service, insee_commune, maitre_ouvrage, exploitant,
            precision_xy, precision_z, an_pose_sup, date_creation, origine_creation, date_maj,
            geom,
            forme, id_ass_regard, type_regard, materiau, position, type_descente
        ) VALUES (
            'assaru', 'non_renseigne', '34172', 'non_renseigne', 'non_renseigne',
            'N', 'N', -9999, NOW(), 'non_renseigne', NOW(),
            St_SetSRID(ST_MakePoint(770192.899, 6280461.411), 2154),
            'non_renseigne', 'ass_rega_0034073', 'non_renseigne', 'nr', 'non_renseigne', 'non_renseigne'
        ), (
            'assaru', 'non_renseigne', '34172', 'non_renseigne', 'non_renseigne',
            'N', 'N', -9999, NOW(), 'non_renseigne', NOW(),
            St_SetSRID(ST_MakePoint(770200.024, 6280431.888), 2154),
            'non_renseigne', 'ass_rega_0030456', 'non_renseigne', 'nr', 'non_renseigne', 'non_renseigne'
        );
        """
    )

    # Check precision of the geometry
    cursor.execute(
        f"""
        SELECT fid, id_noeud_reseau, id_ass_regard, ST_X(geom) AS x, ST_Y(geom) AS y
        FROM "{plugin_schema_name}_ass".ass_regard;
        """
    )
    nodes = {}
    records = cursor.fetchall()
    for record in records:
        if record[2] == 'ass_rega_0034073':
            case.assertEqual(record[3], 770192.9)
            case.assertEqual(record[4], 6280461.4)
        elif record[2] == 'ass_rega_0030456':
            case.assertEqual(record[3], 770200.0)
            case.assertEqual(record[4], 6280431.9)
        nodes[record[2]] = record

    # INSERT canalisation
    cursor.execute(
        f"""
        INSERT INTO "{plugin_schema_name}_ass".ass_canalisation (
            type_reseau, etat_service, insee_commune, maitre_ouvrage, exploitant,
            precision_xy, precision_z, an_pose_sup, date_creation, origine_creation, date_maj,
            geom,
            mode_circulation, type_pose, raison_pose, materiau, revetement_interieur, diametre_equivalent,
            forme, id_ass_canalisation, fonction_canalisation, contenu_canalisation, visitable
        ) VALUES (
            'assaru', 'non_renseigne', '34172', 'non_renseigne', 'non_renseigne',
            'N', 'N', -9999, NOW(), 'non_renseigne', NOW(),
            ST_GeomFromText('LINESTRING(770192.9 6280461.4, 770200.0 6280431.9)', 2154),
            'gravitaire', 'non_renseigne', 'non_renseigne', 'beton', 'non_renseigne', 1800,
            'non_renseigne', 'ass_cana_0001774', 'non_renseigne', 'non_renseigne', 'non_renseigne'
        ), (
            'assaru', 'non_renseigne', '34172', 'non_renseigne', 'non_renseigne',
            'N', 'N', -9999, NOW(), 'non_renseigne', NOW(),
            ST_GeomFromText('LINESTRING(770200.0 6280431.9, 770223.974 6280429.045)', 2154),
            'gravitaire', 'non_renseigne', 'non_renseigne', 'beton', 'non_renseigne', 1800,
            'non_renseigne', 'ass_cana_0001775_v', 'non_renseigne', 'non_renseigne', 'non_renseigne'
        );
        """
    )

    # check linked
    cursor.execute(
        f"""
        SELECT fid, id_canalisation, id_ass_canalisation, noeudinitial, noeudterminal,
            ST_X(ST_StartPoint(geom)) AS start_x, ST_Y(ST_StartPoint(geom)) AS start_y,
            ST_X(ST_EndPoint(geom)) AS end_x, ST_Y(ST_EndPoint(geom)) AS end_y
        FROM "{plugin_schema_name}_ass".ass_canalisation;
        """
    )
    records = cursor.fetchall()
    for record in records:
        if record[2] == 'ass_cana_0001774':
            case.assertEqual(record[3], nodes['ass_rega_0034073'][1])
            case.assertEqual(record[5], nodes['ass_rega_0034073'][3])
            case.assertEqual(record[6], nodes['ass_rega_0034073'][4])
            case.assertEqual(record[4], nodes['ass_rega_0030456'][1])
            case.assertEqual(record[7], nodes['ass_rega_0030456'][3])
            case.assertEqual(record[8], nodes['ass_rega_0030456'][4])
        if record[2] == 'ass_cana_0001775_v':
            case.assertEqual(record[3], nodes['ass_rega_0030456'][1])
            case.assertEqual(record[5], nodes['ass_rega_0030456'][3])
            case.assertEqual(record[6], nodes['ass_rega_0030456'][4])
            case.assertEqual(record[4], 'non_renseigne')
            case.assertEqual(record[7], 770223.95)
            case.assertEqual(record[8], 6280429.05)

    # INSERT noeud_reseau / ass_regard
    cursor.execute(
        f"""
        INSERT INTO "{plugin_schema_name}_ass".ass_regard (
            type_reseau, etat_service, insee_commune, maitre_ouvrage, exploitant,
            precision_xy, precision_z, an_pose_sup, date_creation, origine_creation, date_maj,
            geom,
            forme, id_ass_regard, type_regard, materiau, position, type_descente
        ) VALUES (
            'assaru', 'non_renseigne', '34172', 'non_renseigne', 'non_renseigne',
            'N', 'N', -9999, NOW(), 'non_renseigne', NOW(),
            St_SetSRID(ST_MakePoint(770223.9, 6280429.0), 2154),
            'non_renseigne', 'ass_rega_0077750', 'non_renseigne', 'nr', 'non_renseigne', 'non_renseigne'
        );
        """
    )

    # Check precision of the geometry
    cursor.execute(
        f"""
        SELECT fid, id_noeud_reseau, id_ass_regard, ST_X(geom) AS x, ST_Y(geom) AS y
        FROM "{plugin_schema_name}_ass".ass_regard;
        """
    )
    nodes = {}
    records = cursor.fetchall()
    for record in records:
        if record[2] == 'ass_rega_0034073':
            case.assertEqual(record[3], 770192.9)
            case.assertEqual(record[4], 6280461.4)
        elif record[2] == 'ass_rega_0030456':
            case.assertEqual(record[3], 770200.0)
            case.assertEqual(record[4], 6280431.9)
        elif record[2] == 'ass_rega_0077750':
            case.assertEqual(record[3], 770223.9)
            case.assertEqual(record[4], 6280429.0)
        nodes[record[2]] = record

    # check linked
    cursor.execute(
        f"""
        SELECT fid, id_canalisation, id_ass_canalisation, noeudinitial, noeudterminal,
            ST_X(ST_StartPoint(geom)) AS start_x, ST_Y(ST_StartPoint(geom)) AS start_y,
            ST_X(ST_EndPoint(geom)) AS end_x, ST_Y(ST_EndPoint(geom)) AS end_y
        FROM "{plugin_schema_name}_ass".ass_canalisation;
        """
    )
    records = cursor.fetchall()
    for record in records:
        if record[2] == 'ass_cana_0001774':
            case.assertEqual(record[3], nodes['ass_rega_0034073'][1])
            case.assertEqual(record[5], nodes['ass_rega_0034073'][3])
            case.assertEqual(record[6], nodes['ass_rega_0034073'][4])
            case.assertEqual(record[4], nodes['ass_rega_0030456'][1])
            case.assertEqual(record[7], nodes['ass_rega_0030456'][3])
            case.assertEqual(record[8], nodes['ass_rega_0030456'][4])
        if record[2] == 'ass_cana_0001775_v':
            case.assertEqual(record[3], nodes['ass_rega_0030456'][1])
            case.assertEqual(record[5], nodes['ass_rega_0030456'][3])
            case.assertEqual(record[6], nodes['ass_rega_0030456'][4])
            case.assertNotEqual(record[4], 'non_renseigne')
            case.assertNotEqual(record[7], 770223.95)
            case.assertNotEqual(record[8], 6280429.05)
            case.assertEqual(record[4], nodes['ass_rega_0077750'][1])
            case.assertEqual(record[7], nodes['ass_rega_0077750'][3])
            case.assertEqual(record[8], nodes['ass_rega_0077750'][4])

    # DELETE noeud_reseau ass_rega_0030456
    cursor.execute(
        f"""
        DELETE FROM "{plugin_schema_name}_ass".ass_regard
        WHERE id_ass_regard = 'ass_rega_0030456';
        """
    )

    # check linked
    cursor.execute(
        f"""
        SELECT fid, id_canalisation, id_ass_canalisation, noeudinitial, noeudterminal,
            ST_X(ST_StartPoint(geom)) AS start_x, ST_Y(ST_StartPoint(geom)) AS start_y,
            ST_X(ST_EndPoint(geom)) AS end_x, ST_Y(ST_EndPoint(geom)) AS end_y
        FROM "{plugin_schema_name}_ass".ass_canalisation;
        """
    )
    records = cursor.fetchall()
    for record in records:
        if record[2] == 'ass_cana_0001774':
            case.assertEqual(record[3], nodes['ass_rega_0034073'][1])
            case.assertEqual(record[5], nodes['ass_rega_0034073'][3])
            case.assertEqual(record[6], nodes['ass_rega_0034073'][4])
            case.assertNotEqual(record[4], nodes['ass_rega_0030456'][1])
            case.assertEqual(record[4], 'non_renseigne')
            case.assertEqual(record[7], nodes['ass_rega_0030456'][3])
            case.assertEqual(record[8], nodes['ass_rega_0030456'][4])
        if record[2] == 'ass_cana_0001775_v':
            case.assertNotEqual(record[3], nodes['ass_rega_0030456'][1])
            case.assertEqual(record[3], 'non_renseigne')
            case.assertEqual(record[5], nodes['ass_rega_0030456'][3])
            case.assertEqual(record[6], nodes['ass_rega_0030456'][4])
            case.assertNotEqual(record[4], 'non_renseigne')
            case.assertNotEqual(record[7], 770223.95)
            case.assertNotEqual(record[8], 6280429.05)
            case.assertEqual(record[4], nodes['ass_rega_0077750'][1])
            case.assertEqual(record[7], nodes['ass_rega_0077750'][3])
            case.assertEqual(record[8], nodes['ass_rega_0077750'][4])

    # Close connection
    db_connection.close()


def test_processing_downstream(
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

    plugin_schema_name = schema_name()

    # INSERT noeud_reseau / ass_regard
    cursor.execute(
        f"""
        INSERT INTO "{plugin_schema_name}_ass".ass_regard (
            type_reseau, etat_service, insee_commune, maitre_ouvrage, exploitant,
            precision_xy, precision_z, an_pose_sup, date_creation, origine_creation, date_maj,
            geom,
            forme, id_ass_regard, type_regard, materiau, position, type_descente
        ) VALUES (
            'assaru', 'non_renseigne', '34172', 'non_renseigne', 'non_renseigne',
            'N', 'N', -9999, NOW(), 'non_renseigne', NOW(),
            St_SetSRID(ST_MakePoint(770192.899, 6280461.411), 2154),
            'non_renseigne', 'ass_rega_0034073', 'non_renseigne', 'nr', 'non_renseigne', 'non_renseigne'
        ), (
            'assaru', 'non_renseigne', '34172', 'non_renseigne', 'non_renseigne',
            'N', 'N', -9999, NOW(), 'non_renseigne', NOW(),
            St_SetSRID(ST_MakePoint(770200.024, 6280431.888), 2154),
            'non_renseigne', 'ass_rega_0030456', 'non_renseigne', 'nr', 'non_renseigne', 'non_renseigne'
        ), (
            'assaru', 'non_renseigne', '34172', 'non_renseigne', 'non_renseigne',
            'N', 'N', -9999, NOW(), 'non_renseigne', NOW(),
            St_SetSRID(ST_MakePoint(770223.9, 6280429.0), 2154),
            'non_renseigne', 'ass_rega_0077750', 'non_renseigne', 'nr', 'non_renseigne', 'non_renseigne'
        ), (
            'assaru', 'non_renseigne', '34172', 'non_renseigne', 'non_renseigne',
            'N', 'N', -9999, NOW(), 'non_renseigne', NOW(),
            St_SetSRID(ST_MakePoint(770253.3, 6280403.8), 2154),
            'non_renseigne', 'ass_rega_0029618', 'non_renseigne', 'nr', 'non_renseigne', 'non_renseigne'
        );
        """
    )

    # Get nodes
    cursor.execute(
        f"""
        SELECT fid, id_noeud_reseau, id_ass_regard, ST_X(geom) AS x, ST_Y(geom) AS y
        FROM "{plugin_schema_name}_ass".ass_regard;
        """
    )
    nodes = {}
    records = cursor.fetchall()
    for record in records:
        nodes[record[2]] = record

    # INSERT canalisation
    cursor.execute(
        f"""
        INSERT INTO "{plugin_schema_name}_ass".ass_canalisation (
            type_reseau, etat_service, insee_commune, maitre_ouvrage, exploitant,
            precision_xy, precision_z, an_pose_sup, date_creation, origine_creation, date_maj,
            geom,
            mode_circulation, type_pose, raison_pose, materiau, revetement_interieur, diametre_equivalent,
            forme, id_ass_canalisation, fonction_canalisation, contenu_canalisation, visitable
        ) VALUES (
            'assaru', 'non_renseigne', '34172', 'non_renseigne', 'non_renseigne',
            'N', 'N', -9999, NOW(), 'non_renseigne', NOW(),
            ST_GeomFromText('LINESTRING(770192.9 6280461.4, 770200.0 6280431.9)', 2154),
            'gravitaire', 'non_renseigne', 'non_renseigne', 'beton', 'non_renseigne', 1800,
            'non_renseigne', 'ass_cana_0001774', 'non_renseigne', 'non_renseigne', 'non_renseigne'
        ), (
            'assaru', 'non_renseigne', '34172', 'non_renseigne', 'non_renseigne',
            'N', 'N', -9999, NOW(), 'non_renseigne', NOW(),
            ST_GeomFromText('LINESTRING(770200.0 6280431.9, 770223.974 6280429.045)', 2154),
            'gravitaire', 'non_renseigne', 'non_renseigne', 'beton', 'non_renseigne', 1800,
            'non_renseigne', 'ass_cana_0001775_v', 'non_renseigne', 'non_renseigne', 'non_renseigne'
        ), (
            'assaru', 'non_renseigne', '34172', 'non_renseigne', 'non_renseigne',
            'N', 'N', -9999, NOW(), 'non_renseigne', NOW(),
            ST_GeomFromText('LINESTRING(770223.974 6280429.045, 770253.3 6280403.8)', 2154),
            'gravitaire', 'non_renseigne', 'non_renseigne', 'beton', 'non_renseigne', 1800,
            'non_renseigne', 'ass_cana_0001776_v', 'non_renseigne', 'non_renseigne', 'non_renseigne'
        );
        """
    )

    # check linked
    cursor.execute(
        f"""
        SELECT fid, id_canalisation, id_ass_canalisation, noeudinitial, noeudterminal,
            ST_X(ST_StartPoint(geom)) AS start_x, ST_Y(ST_StartPoint(geom)) AS start_y,
            ST_X(ST_EndPoint(geom)) AS end_x, ST_Y(ST_EndPoint(geom)) AS end_y
        FROM "{plugin_schema_name}_ass".ass_canalisation;
        """
    )
    records = cursor.fetchall()
    count_records = 0
    count_checking = 0
    for record in records:
        if record[2] == 'ass_cana_0001774':
            case.assertEqual(record[3], nodes['ass_rega_0034073'][1])
            case.assertEqual(record[4], nodes['ass_rega_0030456'][1])
            count_checking += 1
        if record[2] == 'ass_cana_0001775_v':
            case.assertEqual(record[3], nodes['ass_rega_0030456'][1])
            case.assertEqual(record[4], nodes['ass_rega_0077750'][1])
            count_checking += 1
        if record[2] == 'ass_cana_0001776_v':
            case.assertEqual(record[3], nodes['ass_rega_0077750'][1])
            case.assertEqual(record[4], nodes['ass_rega_0029618'][1])
            count_checking += 1
        count_records += 1
    case.assertEqual(count_checking, 3)
    case.assertEqual(count_records, 3)

    # Downstream
    cursor.execute(
        f"""
        SELECT d.idx, c.id_ass_canalisation, d.id_noeudinitial, d.id_noeudterminal
        FROM "{plugin_schema_name}".ass_downstream('{nodes['ass_rega_0034073'][1]}') d
        JOIN "{plugin_schema_name}_ass".ass_canalisation c ON d.fid_canalisation = c.fid;
        """
    )
    records = cursor.fetchall()
    count_records = 0
    count_checking = 0
    for record in records:
        if record[0] == 1:
            case.assertEqual(record[2], nodes['ass_rega_0034073'][1])
            case.assertEqual(record[3], nodes['ass_rega_0030456'][1])
            case.assertEqual(record[1], 'ass_cana_0001774')
            count_checking += 1
        elif record[0] == 2:
            case.assertEqual(record[2], nodes['ass_rega_0030456'][1])
            case.assertEqual(record[3], nodes['ass_rega_0077750'][1])
            case.assertEqual(record[1], 'ass_cana_0001775_v')
            count_checking += 1
        elif record[0] == 3:
            case.assertEqual(record[2], nodes['ass_rega_0077750'][1])
            case.assertEqual(record[3], nodes['ass_rega_0029618'][1])
            case.assertEqual(record[1], 'ass_cana_0001776_v')
            count_checking += 1
        count_records += 1
    case.assertEqual(count_checking, 3)
    case.assertEqual(count_records, 3)

    # Downstream
    cursor.execute(
        f"""
        SELECT d.idx, c.id_ass_canalisation, d.id_noeudinitial, d.id_noeudterminal
        FROM "{plugin_schema_name}".ass_downstream('{nodes['ass_rega_0030456'][1]}') d
        JOIN "{plugin_schema_name}_ass".ass_canalisation c ON d.fid_canalisation = c.fid;
        """
    )
    records = cursor.fetchall()
    count_records = 0
    count_checking = 0
    for record in records:
        if record[0] == 1:
            case.assertEqual(record[2], nodes['ass_rega_0030456'][1])
            case.assertEqual(record[3], nodes['ass_rega_0077750'][1])
            case.assertEqual(record[1], 'ass_cana_0001775_v')
            count_checking += 1
        elif record[0] == 2:
            case.assertEqual(record[2], nodes['ass_rega_0077750'][1])
            case.assertEqual(record[3], nodes['ass_rega_0029618'][1])
            case.assertEqual(record[1], 'ass_cana_0001776_v')
            count_checking += 1
        count_records += 1
    case.assertEqual(count_checking, 2)
    case.assertEqual(count_records, 2)

    cursor.close()


def test_processing_upstream(
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

    plugin_schema_name = schema_name()

    # INSERT noeud_reseau / ass_regard
    cursor.execute(
        f"""
        INSERT INTO "{plugin_schema_name}_ass".ass_regard (
            type_reseau, etat_service, insee_commune, maitre_ouvrage, exploitant,
            precision_xy, precision_z, an_pose_sup, date_creation, origine_creation, date_maj,
            geom,
            forme, id_ass_regard, type_regard, materiau, position, type_descente
        ) VALUES (
            'assaru', 'non_renseigne', '34172', 'non_renseigne', 'non_renseigne',
            'N', 'N', -9999, NOW(), 'non_renseigne', NOW(),
            St_SetSRID(ST_MakePoint(770192.899, 6280461.411), 2154),
            'non_renseigne', 'ass_rega_0034073', 'non_renseigne', 'nr', 'non_renseigne', 'non_renseigne'
        ), (
            'assaru', 'non_renseigne', '34172', 'non_renseigne', 'non_renseigne',
            'N', 'N', -9999, NOW(), 'non_renseigne', NOW(),
            St_SetSRID(ST_MakePoint(770200.024, 6280431.888), 2154),
            'non_renseigne', 'ass_rega_0030456', 'non_renseigne', 'nr', 'non_renseigne', 'non_renseigne'
        ), (
            'assaru', 'non_renseigne', '34172', 'non_renseigne', 'non_renseigne',
            'N', 'N', -9999, NOW(), 'non_renseigne', NOW(),
            St_SetSRID(ST_MakePoint(770223.9, 6280429.0), 2154),
            'non_renseigne', 'ass_rega_0077750', 'non_renseigne', 'nr', 'non_renseigne', 'non_renseigne'
        ), (
            'assaru', 'non_renseigne', '34172', 'non_renseigne', 'non_renseigne',
            'N', 'N', -9999, NOW(), 'non_renseigne', NOW(),
            St_SetSRID(ST_MakePoint(770253.3, 6280403.8), 2154),
            'non_renseigne', 'ass_rega_0029618', 'non_renseigne', 'nr', 'non_renseigne', 'non_renseigne'
        );
        """
    )

    # Get nodes
    cursor.execute(
        f"""
        SELECT fid, id_noeud_reseau, id_ass_regard, ST_X(geom) AS x, ST_Y(geom) AS y
        FROM "{plugin_schema_name}_ass".ass_regard;
        """
    )
    nodes = {}
    records = cursor.fetchall()
    for record in records:
        nodes[record[2]] = record

    # INSERT canalisation
    cursor.execute(
        f"""
        INSERT INTO "{plugin_schema_name}_ass".ass_canalisation (
            type_reseau, etat_service, insee_commune, maitre_ouvrage, exploitant,
            precision_xy, precision_z, an_pose_sup, date_creation, origine_creation, date_maj,
            geom,
            mode_circulation, type_pose, raison_pose, materiau, revetement_interieur, diametre_equivalent,
            forme, id_ass_canalisation, fonction_canalisation, contenu_canalisation, visitable
        ) VALUES (
            'assaru', 'non_renseigne', '34172', 'non_renseigne', 'non_renseigne',
            'N', 'N', -9999, NOW(), 'non_renseigne', NOW(),
            ST_GeomFromText('LINESTRING(770192.9 6280461.4, 770200.0 6280431.9)', 2154),
            'gravitaire', 'non_renseigne', 'non_renseigne', 'beton', 'non_renseigne', 1800,
            'non_renseigne', 'ass_cana_0001774', 'non_renseigne', 'non_renseigne', 'non_renseigne'
        ), (
            'assaru', 'non_renseigne', '34172', 'non_renseigne', 'non_renseigne',
            'N', 'N', -9999, NOW(), 'non_renseigne', NOW(),
            ST_GeomFromText('LINESTRING(770200.0 6280431.9, 770223.974 6280429.045)', 2154),
            'gravitaire', 'non_renseigne', 'non_renseigne', 'beton', 'non_renseigne', 1800,
            'non_renseigne', 'ass_cana_0001775_v', 'non_renseigne', 'non_renseigne', 'non_renseigne'
        ), (
            'assaru', 'non_renseigne', '34172', 'non_renseigne', 'non_renseigne',
            'N', 'N', -9999, NOW(), 'non_renseigne', NOW(),
            ST_GeomFromText('LINESTRING(770223.974 6280429.045, 770253.3 6280403.8)', 2154),
            'gravitaire', 'non_renseigne', 'non_renseigne', 'beton', 'non_renseigne', 1800,
            'non_renseigne', 'ass_cana_0001776_v', 'non_renseigne', 'non_renseigne', 'non_renseigne'
        );
        """
    )

    # check linked
    cursor.execute(
        f"""
        SELECT fid, id_canalisation, id_ass_canalisation, noeudinitial, noeudterminal,
            ST_X(ST_StartPoint(geom)) AS start_x, ST_Y(ST_StartPoint(geom)) AS start_y,
            ST_X(ST_EndPoint(geom)) AS end_x, ST_Y(ST_EndPoint(geom)) AS end_y
        FROM "{plugin_schema_name}_ass".ass_canalisation;
        """
    )
    records = cursor.fetchall()
    count_records = 0
    count_checking = 0
    for record in records:
        if record[2] == 'ass_cana_0001774':
            case.assertEqual(record[3], nodes['ass_rega_0034073'][1])
            case.assertEqual(record[4], nodes['ass_rega_0030456'][1])
            count_checking += 1
        if record[2] == 'ass_cana_0001775_v':
            case.assertEqual(record[3], nodes['ass_rega_0030456'][1])
            case.assertEqual(record[4], nodes['ass_rega_0077750'][1])
            count_checking += 1
        if record[2] == 'ass_cana_0001776_v':
            case.assertEqual(record[3], nodes['ass_rega_0077750'][1])
            case.assertEqual(record[4], nodes['ass_rega_0029618'][1])
            count_checking += 1
        count_records += 1
    case.assertEqual(count_checking, 3)
    case.assertEqual(count_records, 3)

    # Downstream
    cursor.execute(
        f"""
        SELECT d.idx, c.id_ass_canalisation, d.id_noeudinitial, d.id_noeudterminal
        FROM "{plugin_schema_name}".ass_upstream('{nodes['ass_rega_0029618'][1]}') d
        JOIN "{plugin_schema_name}_ass".ass_canalisation c ON d.fid_canalisation = c.fid;
        """
    )
    records = cursor.fetchall()
    count_records = 0
    count_checking = 0
    for record in records:
        if record[0] == 1:
            case.assertEqual(record[2], nodes['ass_rega_0077750'][1])
            case.assertEqual(record[3], nodes['ass_rega_0029618'][1])
            case.assertEqual(record[1], 'ass_cana_0001776_v')
            count_checking += 1
        elif record[0] == 2:
            case.assertEqual(record[2], nodes['ass_rega_0030456'][1])
            case.assertEqual(record[3], nodes['ass_rega_0077750'][1])
            case.assertEqual(record[1], 'ass_cana_0001775_v')
            count_checking += 1
        elif record[0] == 3:
            case.assertEqual(record[2], nodes['ass_rega_0034073'][1])
            case.assertEqual(record[3], nodes['ass_rega_0030456'][1])
            case.assertEqual(record[1], 'ass_cana_0001774')
            count_checking += 1
        count_records += 1
    case.assertEqual(count_checking, 3)
    case.assertEqual(count_records, 3)

    # Downstream
    cursor.execute(
        f"""
        SELECT d.idx, c.id_ass_canalisation, d.id_noeudinitial, d.id_noeudterminal
        FROM "{plugin_schema_name}".ass_upstream('{nodes['ass_rega_0077750'][1]}') d
        JOIN "{plugin_schema_name}_ass".ass_canalisation c ON d.fid_canalisation = c.fid;
        """
    )
    records = cursor.fetchall()
    count_records = 0
    count_checking = 0
    for record in records:
        if record[0] == 1:
            case.assertEqual(record[2], nodes['ass_rega_0030456'][1])
            case.assertEqual(record[3], nodes['ass_rega_0077750'][1])
            case.assertEqual(record[1], 'ass_cana_0001775_v')
            count_checking += 1
        elif record[0] == 2:
            case.assertEqual(record[2], nodes['ass_rega_0034073'][1])
            case.assertEqual(record[3], nodes['ass_rega_0030456'][1])
            case.assertEqual(record[1], 'ass_cana_0001774')
            count_checking += 1
        count_records += 1
    case.assertEqual(count_checking, 2)
    case.assertEqual(count_records, 2)


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
