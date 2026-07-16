-- Path to nearest target avoiding closed valves
CREATE OR REPLACE FUNCTION stareau.aep_pgr_path_to_nearest_target_avoiding_closed_valves(
    vertex_id integer,
    target_schema text,
    target_table text)
    RETURNS SETOF stareau_aep.aep_canalisation
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
    BEGIN
        RETURN QUERY EXECUTE
        format(
        $format$

        WITH target_search_path AS (
            SELECT start_vid, end_vid, max(agg_cost) as agg_cost,
                array_agg(edge) FILTER (WHERE edge != -1) as edges
            FROM pgr_bdDijkstra(
                -- The Edge SQL, exluding edges connected to closed valves
                $e$
                SELECT id, source, target, cost, reverse_cost
                FROM stareau.aep_edge
                WHERE source NOT IN (
                    SELECT vertex.id
                    FROM stareau_aep.aep_vanne vanne
                    JOIN stareau.aep_vertex vertex ON vertex.id = vanne.fid
                    WHERE vanne.etat_ouverture = 'fermee'
                )
                AND target NOT IN (
                    SELECT vertex.id
                    FROM stareau_aep.aep_vanne vanne
                    JOIN stareau.aep_vertex vertex ON vertex.id = vanne.fid
                    WHERE vanne.etat_ouverture = 'fermee'
                )
                $e$,
                -- The started vertex
                %1$s,
                -- The ended vertexes
                ARRAY(
                    -- The 10 nearest target vertex from the provided vertex id
                    SELECT vertex.id
                    FROM %2$I.%3$I AS target
                    JOIN stareau.aep_vertex vertex ON vertex.id = target.fid
                    WHERE NOT (vertex.id = %1$s)
                    ORDER BY (SELECT geom FROM stareau.aep_vertex WHERE id=%1$s) <-> vertex.geom
                    LIMIT 10
                )
            )
            GROUP BY start_vid, end_vid
            ORDER BY agg_cost
            LIMIT 1
        )
        SELECT canalisation.*
        FROM target_search_path
        JOIN UNNEST(target_search_path.edges) AS edge_id ON true
        JOIN stareau_aep.aep_canalisation AS canalisation ON canalisation.fid = edge_id;

        $format$,
        vertex_id,
        target_schema,
        target_table
        );
    END
$BODY$;

COMMENT ON FUNCTION stareau.aep_pgr_path_to_nearest_target_avoiding_closed_valves(integer, text, text) IS
'Fonction de recherche de la cible la plus proche d''un noeud réseau AEP.
Les vannes fermées ne sont pas traversables.
⚠ Nécessite PGRouting.';


-- Get nearest vannes from a point, update to use pgr_withPoints instead of pgr_trsp
CREATE OR REPLACE FUNCTION stareau.aep_pgr_nearest_vannes(the_point geometry)
    RETURNS SETOF stareau_aep.aep_vanne
    LANGUAGE plpgsql AS
    $func$
    BEGIN
        RETURN QUERY EXECUTE
        format(
        $format$

        WITH shortest_path_to_vannes AS (
            SELECT start_vid, end_vid, max(agg_cost) as agg_cost
            FROM pgr_withPoints(
                -- Edge SQL: valves are dead ends (you can reach them, but not leave them), EXCEPT on the "starting edge"
                $e$
                WITH closest AS (
                    SELECT edge_id
                    FROM pgr_findCloseEdges(
                        $pe$ SELECT id, geom FROM stareau.aep_edge $pe$,
                        '%1$s'::geometry,
                        5, cap => 1
                    )
                )
                SELECT e.id, e.source, e.target,
                    -- Avoid leaving a valve forward by attributing a negative cost (source -> target)
                    -- Except on the starting edge, where we want to use the real cost
                    CASE
                        WHEN e.id = (SELECT edge_id FROM closest) THEN e.cost
                        WHEN vanne_source.fid IS NOT NULL THEN -1
                        ELSE e.cost
                    END AS cost,
                    -- Avoid leaving a valve backward by attributing a negative reverse_cost (target -> source)
                    -- Except on the starting edge, where we want to use the real cost
                    CASE
                        WHEN e.id = (SELECT edge_id FROM closest) THEN e.reverse_cost
                        WHEN vanne_target.fid IS NOT NULL THEN -1
                        ELSE e.reverse_cost
                    END AS reverse_cost
                FROM stareau.aep_edge e
                LEFT JOIN stareau_aep.aep_vanne vanne_source ON vanne_source.fid = e.source
                LEFT JOIN stareau_aep.aep_vanne vanne_target ON vanne_target.fid = e.target
                $e$,

                -- The points SQL, the edge closest to the point
                $p$
                SELECT edge_id, round(fraction::numeric, 2) AS fraction, side
                FROM pgr_findCloseEdges(
                -- The Edge SQL
                $pe$ SELECT id, geom FROM stareau.aep_edge $pe$,
                -- The provided point as geometry
                '%1$s'::geometry,
                -- The minimum distance and the number of edges to find
                5, cap => 1
                )
                $p$,

                -- Starting vertex
                -1,

                -- 100 nearest valves as targets
                ARRAY(
                    SELECT vertex.id
                    FROM stareau_aep.aep_vanne vanne
                    JOIN stareau.aep_vertex vertex ON vertex.id = vanne.fid
                    ORDER BY '%1$s'::geometry <-> vertex.geom
                    LIMIT 100
                )
            )
            GROUP BY start_vid, end_vid
        )
        SELECT aep_vanne.*
        FROM shortest_path_to_vannes
        JOIN stareau_aep.aep_vanne aep_vanne ON aep_vanne.fid = shortest_path_to_vannes.end_vid;

        $format$,
        the_point
        );
    END
    $func$;


-- Get nearest closed vannes from a point
CREATE OR REPLACE FUNCTION stareau.aep_pgr_nearest_closed_vannes(the_point geometry)
    RETURNS SETOF stareau_aep.aep_vanne
    LANGUAGE plpgsql AS
    $func$
    BEGIN
        RETURN QUERY EXECUTE
        format(
        $format$

        WITH shortest_path_to_vannes AS (
            SELECT start_vid, end_vid, max(agg_cost) as agg_cost
            FROM pgr_withPoints(
                -- Edge SQL: valves are dead ends (you can reach them, but not leave them), EXCEPT on the "starting edge"
                $e$
                WITH closest AS (
                    SELECT edge_id
                    FROM pgr_findCloseEdges(
                        $pe$ SELECT id, geom FROM stareau.aep_edge $pe$,
                        '%1$s'::geometry,
                        5, cap => 1
                    )
                )
                SELECT e.id, e.source, e.target,
                    -- Avoid leaving a valve forward by attributing a negative cost (source -> target)
                    -- Except on the starting edge, where we want to use the real cost
                    CASE
                        WHEN e.id = (SELECT edge_id FROM closest) THEN e.cost
                        WHEN (vanne_source.fid IS NOT NULL AND vanne_source.etat_ouverture = 'fermee') THEN -1
                        ELSE e.cost
                    END AS cost,
                    -- Avoid leaving a valve backward by attributing a negative reverse_cost (target -> source)
                    -- Except on the starting edge, where we want to use the real cost
                    CASE
                        WHEN e.id = (SELECT edge_id FROM closest) THEN e.reverse_cost
                        WHEN (vanne_target.fid IS NOT NULL AND vanne_target.etat_ouverture = 'fermee') THEN -1
                        ELSE e.reverse_cost
                    END AS reverse_cost
                FROM stareau.aep_edge e
                LEFT JOIN stareau_aep.aep_vanne vanne_source ON vanne_source.fid = e.source
                LEFT JOIN stareau_aep.aep_vanne vanne_target ON vanne_target.fid = e.target
                $e$,

                -- The points SQL, the edge closest to the point
                $p$
                SELECT edge_id, round(fraction::numeric, 2) AS fraction, side
                FROM pgr_findCloseEdges(
                -- The Edge SQL
                $pe$ SELECT id, geom FROM stareau.aep_edge $pe$,
                -- The provided point as geometry
                '%1$s'::geometry,
                -- The minimum distance and the number of edges to find
                5, cap => 1
                )
                $p$,

                -- Starting vertex
                -1,

                -- 100 nearest valves as targets
                ARRAY(
                    SELECT vertex.id
                    FROM stareau_aep.aep_vanne vanne
                    JOIN stareau.aep_vertex vertex ON vertex.id = vanne.fid
                    WHERE vanne.etat_ouverture = 'fermee'
                    ORDER BY '%1$s'::geometry <-> vertex.geom
                    LIMIT 100
                )
            )
            GROUP BY start_vid, end_vid
        )
        SELECT aep_vanne.*
        FROM shortest_path_to_vannes
        JOIN stareau_aep.aep_vanne aep_vanne ON aep_vanne.fid = shortest_path_to_vannes.end_vid;

        $format$,
        the_point
        );
    END
    $func$;

COMMENT ON FUNCTION stareau.aep_pgr_nearest_closed_vannes(geometry) IS
'Fonction de recherche des vannes fermées les plus proches d''un point donné.
⚠ Nécessite PGRouting.';


-- Path to nearest targets (multiple targets)
CREATE OR REPLACE FUNCTION stareau.aep_pgr_find_captages_from_traitement(
    vertex_id integer,
	target_schema text,
	target_table text)
    RETURNS SETOF stareau_aep.aep_canalisation
    LANGUAGE plpgsql AS
    $func$
    BEGIN
        RETURN QUERY EXECUTE
        format(
        $format$

        WITH target_search_path AS (
            SELECT start_vid, end_vid, max(agg_cost) as agg_cost,
                    array_agg(edge) FILTER (WHERE edge != -1) as edges
                FROM pgr_bdDijkstra(
                    -- The Edge SQL : keep only canalisation whith "adduction" type.
                    $e$
                    SELECT id, source, target, cost, reverse_cost
                    FROM stareau.aep_edge
                    JOIN stareau_aep.aep_canalisation canalisation ON canalisation.fid = id
                    WHERE canalisation.fonction_canalisation = 'adduction'
                    $e$,
                    -- The started vertex
                    %1$s,
                    -- The ended vertexes
                    ARRAY(
                        -- The 10 nearest target vertex from the provided vertex id
                        SELECT vertex.id
                        FROM %2$I.%3$I AS target
                        JOIN stareau.aep_vertex vertex ON vertex.id = target.fid
                        WHERE NOT (vertex.id = %1$s)
                        ORDER BY (SELECT geom FROM stareau.aep_vertex WHERE id=%1$s) <-> vertex.geom
                        LIMIT 10
                    )
                )
            GROUP BY start_vid, end_vid
            ORDER BY agg_cost
        )
        SELECT canalisation.*
        FROM target_search_path
        JOIN UNNEST(target_search_path.edges) AS edge_id ON true
        JOIN stareau_aep.aep_canalisation AS canalisation ON canalisation.fid = edge_id;

        $format$,
        vertex_id,
		target_schema,
		target_table
        );
    END
    $func$;


COMMENT ON FUNCTION stareau.aep_pgr_find_captages_from_traitement(integer, text, text) IS
'Fonction de recherche des points de captages alimentant un point de traitement.
⚠ Nécessite PGRouting.';
