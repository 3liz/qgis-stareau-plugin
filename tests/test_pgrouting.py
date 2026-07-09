import unittest

import psycopg
import pytest

from stareau.plugin_tools.resources import schema_name

# Testing points
A = "'Point (785691.34999999997671694 6272226.25)'"
B = "'Point (783029.5 6270588.45000000018626451)'"
C = "'Point (783835.09999999997671694 6272302.65000000037252903)'"

@pytest.mark.pgrouting
def test_nearest_vannes(initialized_database: psycopg.Connection):
    db_connection = initialized_database
    cursor = db_connection.cursor()
    case = unittest.TestCase()

    plugin_schema_name = schema_name()

    # closed valves on the same canalisation
    cursor.execute(
        f"""
        SELECT fid FROM "{plugin_schema_name}".aep_pgr_nearest_vannes(
            ST_GeomFromText({A}, 2154)
        );
        """
    )
    expected_fids = [8, 12]
    actual_fids = [record[0] for record in cursor.fetchall()]
    case.assertCountEqual(actual_fids, expected_fids)

    # open valves on the same canalisation
    cursor.execute(
        f"""
        SELECT fid FROM "{plugin_schema_name}".aep_pgr_nearest_vannes(
            ST_GeomFromText({B}, 2154)
        );
        """
    )
    expected_fids = [3, 4]
    actual_fids = [record[0] for record in cursor.fetchall()]
    case.assertCountEqual(actual_fids, expected_fids)

    # multiple valves
    cursor.execute(
        f"""
        SELECT fid FROM "{plugin_schema_name}".aep_pgr_nearest_vannes(
            ST_GeomFromText({C}, 2154)
        );
        """
    )
    expected_fids = [1, 6, 7, 12]
    actual_fids = [record[0] for record in cursor.fetchall()]
    case.assertCountEqual(actual_fids, expected_fids)

    # Close connection
    db_connection.close()


@pytest.mark.pgrouting
def test_nearest_closed_vannes(initialized_database: psycopg.Connection):
    db_connection = initialized_database
    cursor = db_connection.cursor()
    case = unittest.TestCase()

    plugin_schema_name = schema_name()

    # closed valves on the same canalisation
    cursor.execute(
        f"""
        SELECT fid FROM "{plugin_schema_name}".aep_pgr_nearest_closed_vannes(
            ST_GeomFromText({A}, 2154)
        );
        """
    )
    expected_fids = [8, 12]
    actual_fids = [record[0] for record in cursor.fetchall()]
    case.assertCountEqual(actual_fids, expected_fids)

    # open valves on the same canalisation
    cursor.execute(
        f"""
        SELECT fid FROM "{plugin_schema_name}".aep_pgr_nearest_closed_vannes(
            ST_GeomFromText({B}, 2154)
        );
        """
    )
    expected_fids = [5, 13, 40]
    actual_fids = [record[0] for record in cursor.fetchall()]
    case.assertCountEqual(actual_fids, expected_fids)

    # multiple valves
    cursor.execute(
        f"""
        SELECT fid FROM "{plugin_schema_name}".aep_pgr_nearest_closed_vannes(
            ST_GeomFromText({C}, 2154)
        );
        """
    )
    expected_fids = [2, 12, 40]
    actual_fids = [record[0] for record in cursor.fetchall()]
    case.assertCountEqual(actual_fids, expected_fids)

    # Close connection
    db_connection.close()


@pytest.mark.pgrouting
def test_path_to_nearest_target_avoiding_closed_valves(initialized_database: psycopg.Connection):
    db_connection = initialized_database
    cursor = db_connection.cursor()
    case = unittest.TestCase()

    plugin_schema_name = schema_name()

    # Find no canalisation (closed valves on the path)
    cursor.execute(
        f"""
        SELECT fid FROM "{plugin_schema_name}".aep_pgr_path_to_nearest_target_avoiding_closed_valves(
            1,
            '{plugin_schema_name}_aep',
            'aep_traitement'
        );
        """
    )
    expected_fids = []
    actual_fids = [record[0] for record in cursor.fetchall()]
    case.assertCountEqual(actual_fids, expected_fids)

    # Find canalisation
    cursor.execute(
        f"""
        SELECT fid FROM "{plugin_schema_name}".aep_pgr_path_to_nearest_target_avoiding_closed_valves(
            3,
            '{plugin_schema_name}_aep',
            'aep_traitement'
        );
        """
    )
    expected_fids = [9, 11, 23, 24]
    actual_fids = [record[0] for record in cursor.fetchall()]
    case.assertCountEqual(actual_fids, expected_fids)

    # Close connection
    db_connection.close()
