"""Tests SQL functions"""

import unittest

import psycopg

from qgis import processing

from stareau.plugin_tools.feedback import LoggerProcessingFeedBack
from stareau.plugin_tools.resources import (
    schema_name,
    schema_version,
)
from stareau.processing.provider import Provider


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
        if record[2] == "ass_rega_0034073":
            case.assertEqual(record[3], 770192.9)
            case.assertEqual(record[4], 6280461.4)
        elif record[2] == "ass_rega_0030456":
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
        if record[2] == "ass_cana_0001774":
            case.assertEqual(record[3], nodes["ass_rega_0034073"][1])
            case.assertEqual(record[5], nodes["ass_rega_0034073"][3])
            case.assertEqual(record[6], nodes["ass_rega_0034073"][4])
            case.assertEqual(record[4], nodes["ass_rega_0030456"][1])
            case.assertEqual(record[7], nodes["ass_rega_0030456"][3])
            case.assertEqual(record[8], nodes["ass_rega_0030456"][4])
        if record[2] == "ass_cana_0001775_v":
            case.assertEqual(record[3], nodes["ass_rega_0030456"][1])
            case.assertEqual(record[5], nodes["ass_rega_0030456"][3])
            case.assertEqual(record[6], nodes["ass_rega_0030456"][4])
            case.assertEqual(record[4], "non_renseigne")
            case.assertAlmostEqual(record[7], 770223.95, places=2)
            case.assertAlmostEqual(record[8], 6280429.05, places=2)

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
        if record[2] == "ass_rega_0034073":
            case.assertEqual(record[3], 770192.9)
            case.assertEqual(record[4], 6280461.4)
        elif record[2] == "ass_rega_0030456":
            case.assertEqual(record[3], 770200.0)
            case.assertEqual(record[4], 6280431.9)
        elif record[2] == "ass_rega_0077750":
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
        if record[2] == "ass_cana_0001774":
            case.assertEqual(record[3], nodes["ass_rega_0034073"][1])
            case.assertEqual(record[5], nodes["ass_rega_0034073"][3])
            case.assertEqual(record[6], nodes["ass_rega_0034073"][4])
            case.assertEqual(record[4], nodes["ass_rega_0030456"][1])
            case.assertEqual(record[7], nodes["ass_rega_0030456"][3])
            case.assertEqual(record[8], nodes["ass_rega_0030456"][4])
        if record[2] == "ass_cana_0001775_v":
            case.assertEqual(record[3], nodes["ass_rega_0030456"][1])
            case.assertEqual(record[5], nodes["ass_rega_0030456"][3])
            case.assertEqual(record[6], nodes["ass_rega_0030456"][4])
            case.assertNotEqual(record[4], "non_renseigne")
            case.assertNotEqual(record[7], 770223.95)
            case.assertNotEqual(record[8], 6280429.05)
            case.assertEqual(record[4], nodes["ass_rega_0077750"][1])
            case.assertEqual(record[7], nodes["ass_rega_0077750"][3])
            case.assertEqual(record[8], nodes["ass_rega_0077750"][4])

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
        if record[2] == "ass_cana_0001774":
            case.assertEqual(record[3], nodes["ass_rega_0034073"][1])
            case.assertEqual(record[5], nodes["ass_rega_0034073"][3])
            case.assertEqual(record[6], nodes["ass_rega_0034073"][4])
            case.assertNotEqual(record[4], nodes["ass_rega_0030456"][1])
            case.assertEqual(record[4], "non_renseigne")
            case.assertEqual(record[7], nodes["ass_rega_0030456"][3])
            case.assertEqual(record[8], nodes["ass_rega_0030456"][4])
        if record[2] == "ass_cana_0001775_v":
            case.assertNotEqual(record[3], nodes["ass_rega_0030456"][1])
            case.assertEqual(record[3], "non_renseigne")
            case.assertEqual(record[5], nodes["ass_rega_0030456"][3])
            case.assertEqual(record[6], nodes["ass_rega_0030456"][4])
            case.assertNotEqual(record[4], "non_renseigne")
            case.assertNotEqual(record[7], 770223.95)
            case.assertNotEqual(record[8], 6280429.05)
            case.assertEqual(record[4], nodes["ass_rega_0077750"][1])
            case.assertEqual(record[7], nodes["ass_rega_0077750"][3])
            case.assertEqual(record[8], nodes["ass_rega_0077750"][4])

    # Close connection
    db_connection.close()


def test_processing_trigger_with_reverse(
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
        if record[2] == "ass_cana_0001774":
            case.assertEqual(record[3], nodes["ass_rega_0034073"][1])
            case.assertEqual(record[5], nodes["ass_rega_0034073"][3])
            case.assertEqual(record[6], nodes["ass_rega_0034073"][4])
            case.assertEqual(record[4], nodes["ass_rega_0030456"][1])
            case.assertEqual(record[7], nodes["ass_rega_0030456"][3])
            case.assertEqual(record[8], nodes["ass_rega_0030456"][4])

    # Reverse canalisation
    cursor.execute(
        f"""
        UPDATE "{plugin_schema_name}_ass".ass_canalisation SET geom = ST_Reverse(geom)
        WHERE id_ass_canalisation = 'ass_cana_0001774';
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
        if record[2] == "ass_cana_0001774":
            # Start is not the same
            case.assertNotEqual(record[3], nodes["ass_rega_0034073"][1])
            case.assertNotEqual(record[5], nodes["ass_rega_0034073"][3])
            case.assertNotEqual(record[6], nodes["ass_rega_0034073"][4])
            # Start is the old end
            case.assertEqual(record[3], nodes["ass_rega_0030456"][1])
            case.assertEqual(record[5], nodes["ass_rega_0030456"][3])
            case.assertEqual(record[6], nodes["ass_rega_0030456"][4])
            # End is not the same
            case.assertNotEqual(record[4], nodes["ass_rega_0030456"][1])
            case.assertNotEqual(record[7], nodes["ass_rega_0030456"][3])
            case.assertNotEqual(record[8], nodes["ass_rega_0030456"][4])
            # End is the old start
            case.assertEqual(record[4], nodes["ass_rega_0034073"][1])
            case.assertEqual(record[7], nodes["ass_rega_0034073"][3])
            case.assertEqual(record[8], nodes["ass_rega_0034073"][4])

    # Close connection
    db_connection.close()


def test_processing_noeud_manquant(
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

    # check canas without nodes
    cursor.execute(
        f"""
        SELECT fid, id_canalisation, id_ass_canalisation, noeudinitial, noeudterminal,
            ST_X(ST_StartPoint(geom)) AS start_x, ST_Y(ST_StartPoint(geom)) AS start_y,
            ST_X(ST_EndPoint(geom)) AS end_x, ST_Y(ST_EndPoint(geom)) AS end_y
        FROM "{plugin_schema_name}_ass".ass_canalisation;
        """
    )
    records = cursor.fetchall()
    canas = {}
    count_records = 0
    count_checking = 0
    for record in records:
        if record[2] == "ass_cana_0001774":
            case.assertEqual(record[3], "non_renseigne")
            case.assertEqual(record[5], 770192.9)
            case.assertEqual(record[6], 6280461.4)
            case.assertEqual(record[4], "non_renseigne")
            case.assertEqual(record[7], 770200.0)
            case.assertEqual(record[8], 6280431.9)
            canas[record[2]] = record
            count_checking += 1
        if record[2] == "ass_cana_0001775_v":
            case.assertEqual(record[3], "non_renseigne")
            case.assertEqual(record[5], 770200.0)
            case.assertEqual(record[6], 6280431.9)
            case.assertEqual(record[4], "non_renseigne")
            case.assertAlmostEqual(record[7], 770223.95, places=2)
            case.assertAlmostEqual(record[8], 6280429.05, places=2)
            canas[record[2]] = record
            count_checking += 1
        count_records += 1
    case.assertEqual(count_checking, 2)
    case.assertEqual(count_records, 2)

    # check noeud_manquant
    cursor.execute(
        f"""
        SELECT fid, id_canalisation_upstream, id_canalisation_downstream
        FROM "{plugin_schema_name}".ass_noeud_manquant();
        """
    )
    records = cursor.fetchall()
    count_records = 0
    count_checking = 0
    for record in records:
        if record[0] == 10:
            case.assertEqual(record[1], None)
            case.assertEqual(record[2], canas["ass_cana_0001774"][1])
            count_checking += 1
        if record[0] == 11:
            case.assertEqual(record[1], canas["ass_cana_0001774"][1])
            case.assertEqual(record[2], canas["ass_cana_0001775_v"][1])
            count_checking += 1
        if record[0] == 21:
            case.assertEqual(record[1], canas["ass_cana_0001775_v"][1])
            case.assertEqual(record[2], None)
            count_checking += 1
        count_records += 1
    case.assertEqual(count_checking, 3)
    case.assertEqual(count_records, 3)

    # Close connection
    db_connection.close()


def test_processing_noeud_orphelin(
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
    count_records = 0
    for record in records:
        nodes[record[2]] = record
        count_records += 1
    case.assertEqual(count_records, 3)

    # Get orphelins
    cursor.execute(
        f"""
        SELECT fid, id_noeud_reseau, ST_X(geom) AS x, ST_Y(geom) AS y
        FROM "{plugin_schema_name}".ass_noeud_orphelin();
        """
    )
    records = cursor.fetchall()
    count_records = 0
    count_checking = 0
    for record in records:
        if record[1] == nodes["ass_rega_0034073"][1]:
            case.assertEqual(record[0], nodes["ass_rega_0034073"][0])
            case.assertEqual(record[2], nodes["ass_rega_0034073"][3])
            case.assertEqual(record[3], nodes["ass_rega_0034073"][4])
            count_checking += 1
        if record[1] == nodes["ass_rega_0030456"][1]:
            case.assertEqual(record[0], nodes["ass_rega_0030456"][0])
            case.assertEqual(record[2], nodes["ass_rega_0030456"][3])
            case.assertEqual(record[3], nodes["ass_rega_0030456"][4])
            count_checking += 1
        if record[1] == nodes["ass_rega_0077750"][1]:
            case.assertEqual(record[0], nodes["ass_rega_0077750"][0])
            case.assertEqual(record[2], nodes["ass_rega_0077750"][3])
            case.assertEqual(record[3], nodes["ass_rega_0077750"][4])
            count_checking += 1
        count_records += 1
    case.assertEqual(count_records, 3)
    case.assertEqual(count_checking, 3)

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
        );
        """
    )

    # check canas without nodes
    cursor.execute(
        f"""
        SELECT fid, id_canalisation, id_ass_canalisation, noeudinitial, noeudterminal,
            ST_X(ST_StartPoint(geom)) AS start_x, ST_Y(ST_StartPoint(geom)) AS start_y,
            ST_X(ST_EndPoint(geom)) AS end_x, ST_Y(ST_EndPoint(geom)) AS end_y
        FROM "{plugin_schema_name}_ass".ass_canalisation;
        """
    )
    records = cursor.fetchall()
    canas = {}
    count_records = 0
    count_checking = 0
    for record in records:
        if record[2] == "ass_cana_0001774":
            case.assertEqual(record[3], nodes["ass_rega_0034073"][1])
            case.assertEqual(record[5], nodes["ass_rega_0034073"][3])
            case.assertEqual(record[6], nodes["ass_rega_0034073"][4])
            case.assertEqual(record[4], nodes["ass_rega_0030456"][1])
            case.assertEqual(record[7], nodes["ass_rega_0030456"][3])
            case.assertEqual(record[8], nodes["ass_rega_0030456"][4])
            canas[record[2]] = record
            count_checking += 1
        count_records += 1
    case.assertEqual(count_records, 1)
    case.assertEqual(count_checking, 1)

    # Get orphelins
    cursor.execute(
        f"""
        SELECT fid, id_noeud_reseau, ST_X(geom) AS x, ST_Y(geom) AS y
        FROM "{plugin_schema_name}".ass_noeud_orphelin();
        """
    )
    records = cursor.fetchall()
    count_records = 0
    count_checking = 0
    for record in records:
        if record[1] == nodes["ass_rega_0077750"][1]:
            case.assertEqual(record[0], nodes["ass_rega_0077750"][0])
            case.assertEqual(record[2], nodes["ass_rega_0077750"][3])
            case.assertEqual(record[3], nodes["ass_rega_0077750"][4])
            count_checking += 1
        count_records += 1
    case.assertEqual(count_records, 1)
    case.assertEqual(count_checking, 1)

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
        if record[2] == "ass_cana_0001774":
            case.assertEqual(record[3], nodes["ass_rega_0034073"][1])
            case.assertEqual(record[4], nodes["ass_rega_0030456"][1])
            count_checking += 1
        if record[2] == "ass_cana_0001775_v":
            case.assertEqual(record[3], nodes["ass_rega_0030456"][1])
            case.assertEqual(record[4], nodes["ass_rega_0077750"][1])
            count_checking += 1
        if record[2] == "ass_cana_0001776_v":
            case.assertEqual(record[3], nodes["ass_rega_0077750"][1])
            case.assertEqual(record[4], nodes["ass_rega_0029618"][1])
            count_checking += 1
        count_records += 1
    case.assertEqual(count_checking, 3)
    case.assertEqual(count_records, 3)

    # Downstream
    cursor.execute(
        f"""
        SELECT d.idx, c.id_ass_canalisation, d.id_noeudinitial, d.id_noeudterminal
        FROM "{plugin_schema_name}".ass_downstream('{nodes["ass_rega_0034073"][1]}') d
        JOIN "{plugin_schema_name}_ass".ass_canalisation c ON d.fid_canalisation = c.fid;
        """
    )
    records = cursor.fetchall()
    count_records = 0
    count_checking = 0
    for record in records:
        if record[0] == 1:
            case.assertEqual(record[2], nodes["ass_rega_0034073"][1])
            case.assertEqual(record[3], nodes["ass_rega_0030456"][1])
            case.assertEqual(record[1], "ass_cana_0001774")
            count_checking += 1
        elif record[0] == 2:
            case.assertEqual(record[2], nodes["ass_rega_0030456"][1])
            case.assertEqual(record[3], nodes["ass_rega_0077750"][1])
            case.assertEqual(record[1], "ass_cana_0001775_v")
            count_checking += 1
        elif record[0] == 3:
            case.assertEqual(record[2], nodes["ass_rega_0077750"][1])
            case.assertEqual(record[3], nodes["ass_rega_0029618"][1])
            case.assertEqual(record[1], "ass_cana_0001776_v")
            count_checking += 1
        count_records += 1
    case.assertEqual(count_checking, 3)
    case.assertEqual(count_records, 3)

    # Downstream
    cursor.execute(
        f"""
        SELECT d.idx, c.id_ass_canalisation, d.id_noeudinitial, d.id_noeudterminal
        FROM "{plugin_schema_name}".ass_downstream('{nodes["ass_rega_0030456"][1]}') d
        JOIN "{plugin_schema_name}_ass".ass_canalisation c ON d.fid_canalisation = c.fid;
        """
    )
    records = cursor.fetchall()
    count_records = 0
    count_checking = 0
    for record in records:
        if record[0] == 1:
            case.assertEqual(record[2], nodes["ass_rega_0030456"][1])
            case.assertEqual(record[3], nodes["ass_rega_0077750"][1])
            case.assertEqual(record[1], "ass_cana_0001775_v")
            count_checking += 1
        elif record[0] == 2:
            case.assertEqual(record[2], nodes["ass_rega_0077750"][1])
            case.assertEqual(record[3], nodes["ass_rega_0029618"][1])
            case.assertEqual(record[1], "ass_cana_0001776_v")
            count_checking += 1
        count_records += 1
    case.assertEqual(count_checking, 2)
    case.assertEqual(count_records, 2)

    # Remove ass_rega_0077750
    cursor.execute(
        f"""
        DELETE FROM "{plugin_schema_name}_ass".ass_regard
        WHERE id_ass_regard = 'ass_rega_0077750';
        """
    )

    # Downstream
    cursor.execute(
        f"""
        SELECT d.idx, c.id_ass_canalisation, d.id_noeudinitial, d.id_noeudterminal
        FROM "{plugin_schema_name}".ass_downstream('{nodes["ass_rega_0030456"][1]}') d
        JOIN "{plugin_schema_name}_ass".ass_canalisation c ON d.fid_canalisation = c.fid;
        """
    )
    records = cursor.fetchall()
    count_records = 0
    count_checking = 0
    for record in records:
        if record[0] == 1:
            case.assertEqual(record[2], nodes["ass_rega_0030456"][1])
            case.assertEqual(record[3], "non_renseigne")
            case.assertEqual(record[1], "ass_cana_0001775_v")
            count_checking += 1
        count_records += 1
    case.assertEqual(count_checking, 1)
    case.assertEqual(count_records, 1)

    # Close connection
    db_connection.close()


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
        if record[2] == "ass_cana_0001774":
            case.assertEqual(record[3], nodes["ass_rega_0034073"][1])
            case.assertEqual(record[4], nodes["ass_rega_0030456"][1])
            count_checking += 1
        if record[2] == "ass_cana_0001775_v":
            case.assertEqual(record[3], nodes["ass_rega_0030456"][1])
            case.assertEqual(record[4], nodes["ass_rega_0077750"][1])
            count_checking += 1
        if record[2] == "ass_cana_0001776_v":
            case.assertEqual(record[3], nodes["ass_rega_0077750"][1])
            case.assertEqual(record[4], nodes["ass_rega_0029618"][1])
            count_checking += 1
        count_records += 1
    case.assertEqual(count_checking, 3)
    case.assertEqual(count_records, 3)

    # Downstream
    cursor.execute(
        f"""
        SELECT d.idx, c.id_ass_canalisation, d.id_noeudinitial, d.id_noeudterminal
        FROM "{plugin_schema_name}".ass_upstream('{nodes["ass_rega_0029618"][1]}') d
        JOIN "{plugin_schema_name}_ass".ass_canalisation c ON d.fid_canalisation = c.fid;
        """
    )
    records = cursor.fetchall()
    count_records = 0
    count_checking = 0
    for record in records:
        if record[0] == 1:
            case.assertEqual(record[2], nodes["ass_rega_0077750"][1])
            case.assertEqual(record[3], nodes["ass_rega_0029618"][1])
            case.assertEqual(record[1], "ass_cana_0001776_v")
            count_checking += 1
        elif record[0] == 2:
            case.assertEqual(record[2], nodes["ass_rega_0030456"][1])
            case.assertEqual(record[3], nodes["ass_rega_0077750"][1])
            case.assertEqual(record[1], "ass_cana_0001775_v")
            count_checking += 1
        elif record[0] == 3:
            case.assertEqual(record[2], nodes["ass_rega_0034073"][1])
            case.assertEqual(record[3], nodes["ass_rega_0030456"][1])
            case.assertEqual(record[1], "ass_cana_0001774")
            count_checking += 1
        count_records += 1
    case.assertEqual(count_checking, 3)
    case.assertEqual(count_records, 3)

    # Downstream
    cursor.execute(
        f"""
        SELECT d.idx, c.id_ass_canalisation, d.id_noeudinitial, d.id_noeudterminal
        FROM "{plugin_schema_name}".ass_upstream('{nodes["ass_rega_0077750"][1]}') d
        JOIN "{plugin_schema_name}_ass".ass_canalisation c ON d.fid_canalisation = c.fid;
        """
    )
    records = cursor.fetchall()
    count_records = 0
    count_checking = 0
    for record in records:
        if record[0] == 1:
            case.assertEqual(record[2], nodes["ass_rega_0030456"][1])
            case.assertEqual(record[3], nodes["ass_rega_0077750"][1])
            case.assertEqual(record[1], "ass_cana_0001775_v")
            count_checking += 1
        elif record[0] == 2:
            case.assertEqual(record[2], nodes["ass_rega_0034073"][1])
            case.assertEqual(record[3], nodes["ass_rega_0030456"][1])
            case.assertEqual(record[1], "ass_cana_0001774")
            count_checking += 1
        count_records += 1
    case.assertEqual(count_checking, 2)
    case.assertEqual(count_records, 2)

    # Remove ass_rega_0030456
    cursor.execute(
        f"""
        DELETE FROM "{plugin_schema_name}_ass".ass_regard
        WHERE id_ass_regard = 'ass_rega_0030456';
        """
    )

    # Downstream
    cursor.execute(
        f"""
        SELECT d.idx, c.id_ass_canalisation, d.id_noeudinitial, d.id_noeudterminal
        FROM "{plugin_schema_name}".ass_upstream('{nodes["ass_rega_0077750"][1]}') d
        JOIN "{plugin_schema_name}_ass".ass_canalisation c ON d.fid_canalisation = c.fid;
        """
    )
    records = cursor.fetchall()
    count_records = 0
    count_checking = 0
    for record in records:
        if record[0] == 1:
            case.assertEqual(record[2], "non_renseigne")
            case.assertEqual(record[3], nodes["ass_rega_0077750"][1])
            case.assertEqual(record[1], "ass_cana_0001775_v")
            count_checking += 1
        count_records += 1
    case.assertEqual(count_checking, 1)
    case.assertEqual(count_records, 1)

    # Close connection
    db_connection.close()
