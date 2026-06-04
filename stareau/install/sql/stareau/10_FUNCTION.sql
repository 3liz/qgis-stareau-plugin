--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;


SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

CREATE FUNCTION stareau.get_current_setting(setting_name text, default_value text, value_type text DEFAULT 'text') RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
    setting_value text;
BEGIN
    -- Get the setting value, if not set default_value
    setting_value = coalesce(current_setting(setting_name, true), default_value);
    -- Try to cast the setting value to the expected type, if it fails return the default_value
    BEGIN
        IF value_type = 'integer' THEN
           RETURN setting_value::integer;
        ELSIF value_type = 'boolean' THEN
           RETURN setting_value::boolean;
        ELSIF value_type = 'real' THEN
           RETURN setting_value::boolean;
        END IF;
    EXCEPTION WHEN OTHERS THEN
        IF value_type = 'integer' THEN
           RETURN default_value::integer;
        ELSIF value_type = 'boolean' THEN
           RETURN default_value::boolean;
        ELSIF value_type = 'real' THEN
           RETURN default_value::boolean;
        END IF;
    END;

    RETURN setting_value;
END;
$$;

COMMENT ON FUNCTION stareau.get_current_setting(text, text, text) IS
'Get a PostgreSQL current setting, with a default value if the setting is not set or is invalid.
The function is used to avoid repeating the coalesce(current_setting(...))::TYPE, 0) = 1 and to
have a single point of maintenace for getting settings.
';

-- aa_before_geometry_insert_or_update_reduce_precision()
CREATE FUNCTION stareau.aa_before_geometry_insert_or_update_reduce_precision() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Trigger disabled by session variable
    IF stareau.get_current_setting('stareau.graph.disable.trigger', '0', 'boolean')
    THEN
        RETURN NEW;
    END IF;

    -- Do not modify the geometry if geom field has not been changed
    IF TG_OP = 'UPDATE' AND (
            ST_Equals(OLD.geom, NEW.geom)
            OR
            ST_Equals(NEW.geom, ST_ReducePrecision(NEW.geom, 0.05))
        )
    THEN
        RETURN NEW;
    END IF;

    -- Reduce geometry precision
    NEW.geom = ST_ReducePrecision(NEW.geom, 0.05);

    RETURN NEW;
END;
$$;


-- FUNCTION aa_before_geometry_insert_or_update()
COMMENT ON FUNCTION stareau.aa_before_geometry_insert_or_update_reduce_precision() IS
'Fonction qui arrondit la précision des coordonnées à 0.05 soit (cm si ce n''est pas déjà fait
lors d''une création ou d''une modification de géométrie.
Elle est préfixée par aa_ pour être lancée avant les autres trigger,
car l''ordre alphabétique compte.
';

-- before_canalisation_insert_or_update()
CREATE FUNCTION stareau.before_canalisation_insert_or_update() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    start_point geometry(point);
    end_point geometry(point);
    is_aep boolean;
    upstream_node record;
    downstream_node record;
    raise_notice text;
BEGIN
    -- Trigger disabled by session variable
    IF stareau.get_current_setting('stareau.graph.disable.trigger', '0', 'boolean')
    THEN
        RETURN NEW;
    END IF;

    -- Check if we must log
    raise_notice = stareau.get_current_setting('stareau.graph.raise.notice', '0', 'boolean');

    -- Do nothing if geometry has not changed
    IF TG_OP = 'UPDATE' AND ST_OrderingEquals(NEW.geom, OLD.geom) THEN
        IF raise_notice IN ('info', 'debug') THEN
            RAISE NOTICE '% BEFORE canalisation % n° %, NEW and OLD geom are equal',
                repeat('    ', pg_trigger_depth()::integer), TG_OP, NEW.fid
            ;
        END IF;

        RETURN NEW;
    END IF;

    -- start & end point
    start_point = ST_StartPoint(NEW.geom);
    end_point = ST_EndPoint(NEW.geom);
    -- is reseau AEP ?
    is_aep = (NEW.type_reseau = 'aep');

    -- Get first nodes < 0.1 m - If found, edit NEW geom
    -- upstream
    IF is_aep THEN
        SELECT INTO upstream_node
            n.fid, n.id_noeud_reseau, n.geom
        FROM "stareau_principale".noeud_reseau AS n
        WHERE ST_DWithin(n.geom, start_point, 0.1)
          AND n.type_reseau = 'aep'
        ORDER BY n.geom <-> start_point, n.fid
        LIMIT 1
        ;
    ELSE
        SELECT INTO upstream_node
            n.fid, n.id_noeud_reseau, n.geom
        FROM "stareau_principale".noeud_reseau AS n
        WHERE ST_DWithin(n.geom, start_point, 0.1)
          AND n.type_reseau <> 'aep'
        ORDER BY n.geom <-> start_point, n.fid
        LIMIT 1
        ;
    END IF;

    -- upstream - update value
    IF upstream_node IS NOT NULL THEN
        IF raise_notice IN ('info', 'debug') THEN
            RAISE NOTICE '% BEFORE canalisation % n° %, upstream_node NOT NULL : % % -> use it',
                repeat('    ', pg_trigger_depth()::integer), TG_OP, NEW.fid, upstream_node.fid, upstream_node.id_noeud_reseau
            ;
        END IF;

        -- Update the geometry
        NEW.geom = ST_SetPoint(NEW.geom, 0, upstream_node.geom);
        -- Update the node ID in upstream attribute
        NEW.noeudinitial = upstream_node.id_noeud_reseau;
    ELSE
        IF raise_notice IN ('info', 'debug') THEN
            RAISE NOTICE '% BEFORE canalisation % n° %, upstream_node IS NULL',
                repeat('    ', pg_trigger_depth()::integer), TG_OP, NEW.fid
            ;
        END IF;

        -- Update the node ID in upstream attribute
        NEW.noeudinitial = 'non_renseigne';
    END IF;

    -- Get last nodes < 0.1 m - If found, edit NEW geom
    -- downstream
    IF is_aep THEN
        SELECT INTO downstream_node
            n.fid, n.id_noeud_reseau, n.geom
        FROM "stareau_principale".noeud_reseau AS n
        WHERE ST_DWithin(n.geom, end_point, 0.1)
          AND n.type_reseau = 'aep'
        ORDER BY n.geom <-> end_point, n.fid
        LIMIT 1
        ;
    ELSE
        SELECT INTO downstream_node
            n.fid, n.id_noeud_reseau, n.geom
        FROM "stareau_principale".noeud_reseau AS n
        WHERE ST_DWithin(n.geom, end_point, 0.1)
          AND n.type_reseau <> 'aep'
        ORDER BY n.geom <-> end_point, n.fid
        LIMIT 1
        ;
    END IF;

    -- downstream - update value
    IF downstream_node IS NOT NULL THEN
        IF raise_notice IN ('info', 'debug') THEN
            RAISE NOTICE '% BEFORE canalisation % n° %, downstream_node NOT NULL : % % -> use it',
                repeat('    ', pg_trigger_depth()::integer), TG_OP, NEW.fid, downstream_node.fid, downstream_node.id_noeud_reseau
            ;
        END IF;

        -- Update the geometry
        NEW.geom = ST_SetPoint(NEW.geom,  ST_NPoints(NEW.geom) - 1, downstream_node.geom);
        -- Update the node ID in upstream attribute
        NEW.noeudterminal = downstream_node.id_noeud_reseau;
    ELSE
        IF raise_notice IN ('info', 'debug') THEN
            RAISE NOTICE '% BEFORE canalisation % n° %, downstream_node IS NULL',
                repeat('    ', pg_trigger_depth()::integer), TG_OP, NEW.fid
            ;
        END IF;

        -- Update the node ID in upstream attribute
        NEW.noeudterminal = 'non_renseigne';
    END IF;

    RETURN NEW;
END;
$$;


-- FUNCTION before_canalisation_insert_or_update()
COMMENT ON FUNCTION stareau.before_canalisation_insert_or_update() IS
'Fonction qui lie les canalisations aux noeuds de réseau en amont et en aval
Si le point initial de la géometrie de la canalisation est à moins de 10cm d''un noeud de réseau,
alors on lie la canalisation à ce noeud en modifiant la géométrie et le champ noeudinitial
sinon la valeur ''non_renseigne'' est précisée dans le champs noeudinitial
Si le point final de la géometrie de la canalisation est à moins de 10m d''un noeud de réseau,
alors on lie la canalisation à ce noeud en modifiant la géométrie et le champ noeudterminal
sinon la valeur ''non_renseigne'' est précisée dans le champs noeudterminal
';

-- after_noeud_reseau_insert_or_update()
CREATE FUNCTION stareau.after_noeud_reseau_insert_or_update() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    is_aep boolean;
    _set_config text;
    raise_notice text;
BEGIN
    -- Trigger disabled by session variable
    IF stareau.get_current_setting('stareau.graph.disable.trigger', '0', 'boolean')
    THEN
        RETURN NEW;
    END IF;

    -- Check if we must log
    raise_notice = stareau.get_current_setting('stareau.graph.raise.notice', '0', 'boolean');

    -- Do nothing if geometry has not changed
    IF TG_OP = 'UPDATE' AND ST_Equals(NEW.geom, OLD.geom) THEN
        IF raise_notice IN ('info', 'debug') THEN
            RAISE NOTICE '% AFTER noeud_reseau % n° % UPDATE, NEW and OLD geom are equal',
                repeat('    ', pg_trigger_depth()::integer), TG_OP, NEW.fid
            ;
        END IF;

        RETURN NEW;
    END IF;

    -- is reseau AEP ?
    is_aep = (NEW.type_reseau = 'aep');

    -- Disable triggers
    SELECT set_config('stareau.graph.disable.trigger', '1'::text, true)
    INTO _set_config;

    IF TG_OP = 'UPDATE' THEN
        IF raise_notice IN ('info', 'debug') THEN
            RAISE NOTICE '% AFTER noeud_reseau % n° % UPDATE, UPDATE linked canalisations',
                repeat('    ', pg_trigger_depth()::integer), TG_OP, NEW.fid
            ;
        END IF;

        IF is_aep THEN
            UPDATE "stareau_principale".canalisation SET geom = ST_SetPoint(geom, 0, NEW.geom)
            WHERE noeudinitial = NEW.id_noeud_reseau
              AND type_reseau = 'aep';
            UPDATE "stareau_principale".canalisation SET geom = ST_SetPoint(geom, ST_NPoints(geom) - 1, NEW.geom)
            WHERE noeudterminal = NEW.id_noeud_reseau
              AND type_reseau = 'aep';
        ELSE
            UPDATE "stareau_principale".canalisation SET geom = ST_SetPoint(geom, 0, NEW.geom)
            WHERE noeudinitial = NEW.id_noeud_reseau
              AND type_reseau <> 'aep';
            UPDATE "stareau_principale".canalisation SET geom = ST_SetPoint(geom, ST_NPoints(geom) - 1, NEW.geom)
            WHERE noeudterminal = NEW.id_noeud_reseau
              AND type_reseau <> 'aep';
        END IF;
    END IF;

    IF TG_OP = 'INSERT' THEN
        IF raise_notice IN ('info', 'debug') THEN
            RAISE NOTICE '% AFTER noeud_reseau % n° % INSERT, UPDATE canalisations links',
                repeat('    ', pg_trigger_depth()::integer), TG_OP, NEW.fid
            ;
        END IF;

        IF is_aep THEN
            UPDATE "stareau_principale".canalisation
               SET geom = ST_SetPoint(geom, 0, NEW.geom), noeudinitial = NEW.id_noeud_reseau
            WHERE noeudinitial = 'non_renseigne'
              AND ST_DWITHIN(geom, NEW.geom, 0.1)
              AND ST_DWITHIN(ST_StartPoint(geom), NEW.geom, 0.1)
              AND type_reseau = 'aep';
            UPDATE "stareau_principale".canalisation
               SET geom = ST_SetPoint(geom, ST_NPoints(geom) - 1, NEW.geom), noeudterminal = NEW.id_noeud_reseau
            WHERE noeudterminal = 'non_renseigne'
              AND ST_DWITHIN(geom, NEW.geom, 0.1)
              AND ST_DWITHIN(ST_EndPoint(geom), NEW.geom, 0.1)
              AND type_reseau = 'aep';
        ELSE
            UPDATE "stareau_principale".canalisation
               SET geom = ST_SetPoint(geom, 0, NEW.geom), noeudinitial = NEW.id_noeud_reseau
            WHERE noeudinitial = 'non_renseigne'
              AND ST_DWITHIN(geom, NEW.geom, 0.1)
              AND ST_DWITHIN(ST_StartPoint(geom), NEW.geom, 0.1)
              AND type_reseau <> 'aep';
            UPDATE "stareau_principale".canalisation
               SET geom = ST_SetPoint(geom, ST_NPoints(geom) - 1, NEW.geom), noeudterminal = NEW.id_noeud_reseau
            WHERE noeudterminal = 'non_renseigne'
              AND ST_DWITHIN(geom, NEW.geom, 0.1)
              AND ST_DWITHIN(ST_EndPoint(geom), NEW.geom, 0.1)
              AND type_reseau <> 'aep';
        END IF;
    END IF;

    -- Re-enable triggers
    SELECT set_config('stareau.graph.disable.trigger', '0'::text, true)
    INTO _set_config;

    RETURN NEW;
END;
$$;

-- FUNCTION after_noeud_reseau_insert_or_update()
COMMENT ON FUNCTION stareau.after_noeud_reseau_insert_or_update() IS
'Fonction qui modifie les canalisations afin de les lier aux noeuds de réseau ajoutés ou modifiés
Si le noeud modifié est référencé dans le champ noeudinitial ou noeudterminal d''une canalisation,
alors la géométrie de la canalisation est modifiée pour maintenir le lien géographique avec le noeud de réseau
Si le noeud ajouté se trouve à moins de 10 cm du point initial ou final de la géométrie d''une canalisation,
et que le champ noeudinitial ou noeudterminal de la canalisation est renseigné avec la valeur ''non_renseigne'',
alors la géométrie de la canalisation est modifiée pour créer le lien géographique avec le noeud de réseau
et le champ noeudinitial ou noeudterminal est renseigné avec l''identifiant du noeud de réseau.
';

-- after_noeud_reseau_delete()
CREATE FUNCTION stareau.after_noeud_reseau_delete() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    is_aep boolean;
    _set_config text;
    raise_notice text;
BEGIN
    -- Trigger disabled by session variable
    IF stareau.get_current_setting('stareau.graph.disable.trigger', '0', 'boolean')
    THEN
        RETURN OLD;
    END IF;

    -- Check if we must log
    raise_notice = stareau.get_current_setting('stareau.graph.raise.notice', '0', 'boolean');

    IF raise_notice IN ('info', 'debug') THEN
        RAISE NOTICE '% AFTER noeud_reseau % n° % DELETE, UPDATE canalisations links',
            repeat('    ', pg_trigger_depth()::integer), TG_OP, OLD.fid
        ;
    END IF;

    UPDATE "stareau_principale".canalisation
        SET noeudinitial = 'non_renseigne'
    WHERE noeudinitial = OLD.id_noeud_reseau;

    UPDATE "stareau_principale".canalisation
        SET noeudterminal = 'non_renseigne'
    WHERE noeudterminal = OLD.id_noeud_reseau;

    RETURN OLD;
END;
$$;

-- FUNCTION after_noeud_reseau_insert_or_update()
COMMENT ON FUNCTION stareau.after_noeud_reseau_insert_or_update() IS
'Fonction qui modifie les canalisations afin de modifier les champs noeudinitial et noeudterminal
en assignant la valeur ''non_renseigne'' pour le noeud supprimé.
';

-- ass_downstream(text)
CREATE FUNCTION stareau.ass_downstream(id_noeud_reseau text)
    RETURNS TABLE (
        idx integer,
        fid_canalisation integer,
        fid_noeudinitial integer,
        id_noeudinitial text,
        fid_noeudterminal integer,
        id_noeudterminal text
    )
    LANGUAGE plpgsql AS
    $func$
    BEGIN
        RETURN QUERY EXECUTE
        format(
        $$
            WITH RECURSIVE walk_network(
                idx, fid_canalisation,
                id_noeudinitial,
                id_noeudterminal,
                all_parents
            ) AS (
                SELECT 1 AS idx, c.fid as fid_canalisation,
                    c.noeudinitial as id_noeudinitial,
                    c.noeudterminal as id_noeudterminal,
                    array[c.fid] as all_parents
                FROM stareau_principale.canalisation AS c
                WHERE c.type_reseau <> 'aep'
                AND c.noeudinitial = '%1$s'
                UNION
                SELECT w.idx+1 AS idx, c.fid as fid_canalisation,
                    c.noeudinitial as id_noeudinitial,
                    c.noeudterminal as id_noeudterminal,
                    w.all_parents || c.fid
                FROM walk_network AS w
                INNER JOIN stareau_principale.canalisation AS c ON c.noeudinitial = w.id_noeudterminal
                WHERE c.noeudinitial <> 'non_renseigne' AND NOT c.fid = ANY(w.all_parents)
            )
            SELECT w.idx, w.fid_canalisation,
                ni.fid AS fid_noeudinitial, w.id_noeudinitial,
                nt.fid AS fid_noeudterminal, w.id_noeudterminal
            FROM walk_network AS w
            JOIN stareau_principale.noeud_reseau AS ni ON w.id_noeudinitial = ni.id_noeud_reseau
            LEFT JOIN stareau_principale.noeud_reseau AS nt ON w.id_noeudterminal = nt.id_noeud_reseau
            ORDER BY idx
        $$,
        id_noeud_reseau
        );
    END
    $func$;

-- FUNCTION ass_downstream(text)
COMMENT ON FUNCTION stareau.ass_downstream(text) IS
'Fonction de parcours du réseau en aval d''un noeud de réseau ASS.
Retourne les canalisations et les noeuds de réseau en aval du noeud de réseau passé en paramètre.
';

-- ass_upstream(text)
CREATE FUNCTION stareau.ass_upstream(id_noeud_reseau text)
    RETURNS TABLE (
        idx integer,
        fid_canalisation integer,
        fid_noeudinitial integer,
        id_noeudinitial text,
        fid_noeudterminal integer,
        id_noeudterminal text
    )
    LANGUAGE plpgsql AS
    $func$
    BEGIN
        RETURN QUERY EXECUTE
        format(
        $$
            WITH RECURSIVE walk_network(
                idx, fid_canalisation,
                id_noeudinitial,
                id_noeudterminal,
                all_parents
            ) AS (
                SELECT 1 AS idx, c.fid as fid_canalisation,
                    c.noeudinitial as id_noeudinitial,
                    c.noeudterminal as id_noeudterminal,
                    array[c.fid] as all_parents
                FROM stareau_principale.canalisation AS c
                WHERE c.type_reseau <> 'aep'
                AND c.noeudterminal = '%1$s'
                UNION
                SELECT w.idx+1 AS idx, c.fid as fid_canalisation,
                    c.noeudinitial as id_noeudinitial,
                    c.noeudterminal as id_noeudterminal,
                    w.all_parents || c.fid
                FROM walk_network AS w
                INNER JOIN stareau_principale.canalisation AS c ON c.noeudterminal = w.id_noeudinitial
                WHERE c.noeudterminal <> 'non_renseigne' AND NOT c.fid = ANY(w.all_parents)
            )
            SELECT w.idx, w.fid_canalisation,
                ni.fid AS fid_noeudinitial, w.id_noeudinitial,
                nt.fid AS fid_noeudterminal, w.id_noeudterminal
            FROM walk_network AS w
            LEFT JOIN stareau_principale.noeud_reseau AS ni ON w.id_noeudinitial = ni.id_noeud_reseau
            JOIN stareau_principale.noeud_reseau AS nt ON w.id_noeudterminal = nt.id_noeud_reseau
            ORDER BY idx
        $$,
        id_noeud_reseau
        );
    END
    $func$;

-- FUNCTION ass_upstream(text)
COMMENT ON FUNCTION stareau.ass_upstream(text) IS
'Fonction de parcours du réseau en amnt d''un noeud de réseau ASS.
Retourne les canalisations et les noeuds de réseau en amont du noeud de réseau passé en paramètre.
';

-- ass_noeud_manquant()
CREATE FUNCTION stareau.ass_noeud_manquant()
    RETURNS TABLE (
        fid integer,
        geom public.geometry(point, 2154),
        id_canalisation_upstream text,
        id_canalisation_downstream text
    )
    LANGUAGE plpgsql AS
    $func$
    BEGIN
        RETURN QUERY
            SELECT min(b.fid) as fid, b.geom, max(b.upstream_cana) AS id_canalisation_upstream, max(b.downstream_cana) AS id_canalisation_downstream
            FROM (
                SELECT dc.fid * 10 as fid, st_startpoint(dc.geom) AS geom, null as upstream_cana, dc.id_canalisation as downstream_cana
                FROM stareau_principale.canalisation dc
                WHERE dc.type_reseau <> 'aep' AND dc.noeudinitial = 'non_renseigne' AND NOT ST_IsEmpty(dc.geom)
                UNION ALL
                SELECT uc.fid * 10 + 1 as fid, st_endpoint(uc.geom) AS geom, uc.id_canalisation as upstream_cana, null as downstream_cana
                FROM stareau_principale.canalisation uc
                WHERE uc.type_reseau <> 'aep' AND uc.noeudterminal = 'non_renseigne' AND NOT ST_IsEmpty(uc.geom)
            ) b
            GROUP BY b.geom;
    END
    $func$;

-- FUNCTION ass_noeud_manquant()
COMMENT ON FUNCTION stareau.ass_noeud_manquant() IS
'Fonction de création d''une table des noeuds manquants du réseau ASS.
';


-- aep_noeud_manquant()
CREATE FUNCTION stareau.aep_noeud_manquant()
    RETURNS TABLE (
        fid integer,
        geom public.geometry(point, 2154),
        id_canalisation_upstream text,
        id_canalisation_downstream text
    )
    LANGUAGE plpgsql AS
    $func$
    BEGIN
        RETURN QUERY
            SELECT min(b.fid) as fid, b.geom, max(b.upstream_cana) AS id_canalisation_upstream, max(b.downstream_cana) AS id_canalisation_downstream
            FROM (
                SELECT dc.fid * 10 as fid, st_startpoint(dc.geom) AS geom, null as upstream_cana, dc.id_canalisation as downstream_cana
                FROM stareau_principale.canalisation dc
                WHERE dc.type_reseau = 'aep' AND dc.noeudinitial = 'non_renseigne' AND NOT ST_IsEmpty(dc.geom)
                UNION ALL
                SELECT uc.fid * 10 + 1 as fid, st_endpoint(uc.geom) AS geom, uc.id_canalisation as upstream_cana, null as downstream_cana
                FROM stareau_principale.canalisation uc
                WHERE uc.type_reseau = 'aep' AND uc.noeudterminal = 'non_renseigne' AND NOT ST_IsEmpty(uc.geom)
            ) b
            GROUP BY b.geom;
    END
    $func$;

-- FUNCTION aep_noeud_manquant()
COMMENT ON FUNCTION stareau.aep_noeud_manquant() IS
'Fonction de création d''une table des noeuds manquants du réseau AEP.
';


-- ass_noeud_orphelin()
CREATE FUNCTION stareau.ass_noeud_orphelin()
    RETURNS SETOF stareau_principale.noeud_reseau AS $$
        SELECT nr.*
        FROM stareau_principale.noeud_reseau nr
            LEFT JOIN stareau_principale.canalisation downstream_cana ON nr.id_noeud_reseau = downstream_cana.noeudinitial
            LEFT JOIN stareau_principale.canalisation upstream_cana ON nr.id_noeud_reseau = upstream_cana.noeudterminal
        WHERE nr.type_reseau <> 'aep' AND upstream_cana.noeudterminal IS NULL AND downstream_cana.noeudterminal IS NULL;
    $$ LANGUAGE SQL;

-- FUNCTION ass_noeud_orphelin()
COMMENT ON FUNCTION stareau.ass_noeud_orphelin() IS
'Fonction de récupération des noeuds orphelins (sans lien avec une canalisation) du réseau ASS.
';


-- aep_noeud_orphelin()
CREATE FUNCTION stareau.aep_noeud_orphelin()
    RETURNS SETOF stareau_principale.noeud_reseau AS $$
        SELECT nr.*
        FROM stareau_principale.noeud_reseau nr
            LEFT JOIN stareau_principale.canalisation downstream_cana ON nr.id_noeud_reseau = downstream_cana.noeudinitial
            LEFT JOIN stareau_principale.canalisation upstream_cana ON nr.id_noeud_reseau = upstream_cana.noeudterminal
        WHERE nr.type_reseau = 'aep' AND upstream_cana.noeudterminal IS NULL AND downstream_cana.noeudterminal IS NULL;
    $$ LANGUAGE SQL;

-- FUNCTION aep_noeud_orphelin()
COMMENT ON FUNCTION stareau.aep_noeud_orphelin() IS
'Fonction de récupération des noeuds orphelins (sans lien avec une canalisation) du réseau AEP.
';

-- ass_noeud_doublon()
CREATE FUNCTION stareau.ass_noeud_doublon()
    RETURNS SETOF stareau_principale.noeud_reseau AS $$
        SELECT nro.*
        FROM stareau.ass_noeud_orphelin() nro
            JOIN stareau_principale.noeud_reseau nr ON ST_DWithin(nro.geom, nr.geom, 0.05) AND ST_Equals(nro.geom, nr.geom) AND nro.fid <> nr.fid
        WHERE nro.type_reseau <> 'aep' AND nr.fid IS NOT NULL;
    $$ LANGUAGE SQL;

-- FUNCTION ass_noeud_doublon()
COMMENT ON FUNCTION stareau.ass_noeud_doublon() IS
'Fonction de récupération des noeuds en doublon (sans lien avec une canalisation et situé au même endroit qu''un autre noeud) du réseau ASS.
';

-- aep_noeud_doublon()
CREATE FUNCTION stareau.aep_noeud_doublon()
    RETURNS SETOF stareau_principale.noeud_reseau AS $$
        SELECT nro.*
        FROM stareau.ass_noeud_orphelin() nro
            JOIN stareau_principale.noeud_reseau nr ON ST_DWithin(nro.geom, nr.geom, 0.05) AND ST_Equals(nro.geom, nr.geom) AND nro.fid <> nr.fid
        WHERE nro.type_reseau = 'aep' AND nr.fid IS NOT NULL;
    $$ LANGUAGE SQL;

-- FUNCTION aep_noeud_doublon()
COMMENT ON FUNCTION stareau.aep_noeud_doublon() IS
'Fonction de récupération des noeuds en doublon (sans lien avec une canalisation et situé au même endroit qu''un autre noeud) du réseau AEP.
';


-- aep_pgr_nearest_vannes()
CREATE FUNCTION stareau.aep_pgr_nearest_vannes(vertex_id integer)
    RETURNS SETOF stareau_aep.aep_vanne
    LANGUAGE plpgsql AS
    $func$
    BEGIN
        RETURN QUERY EXECUTE
        format(
        $format$

WITH shortest_path_to_vannes AS (
  -- The shortest path from the provided vertex id to the 100 nearest vanne vertex
  -- start_vid: the provided vertex id
  -- end_vid: a vanne vertex
  -- steps: the number of steps to go from start_vid to end_vid
  -- max_step_cost: the cost of the most expensive step
  -- agg_cost: the total cost of the path
  SELECT start_vid, end_vid, MAX(path_seq) steps,
         max("cost") as max_step_cost,
         max(agg_cost) as agg_cost
    FROM pgr_trsp(
      -- The Edge SQL
      $e$ SELECT id, source, target, cost, reverse_cost from stareau.aep_edge $e$,
      -- The Restriction SQL, the cost the pass through a vanne vertex
      $r$

      WITH vanne_vertex AS (
        -- The 100 nearest vanne vertex from the provided vertex id
        SELECT vertex.id
        FROM stareau_aep.aep_vanne vanne
        JOIN stareau.aep_vertex vertex ON vertex.id = vanne.fid
        ORDER BY (SELECT geom FROM stareau.aep_vertex WHERE id=%1$s) <-> vertex.geom
        LIMIT 100
      ),
      vanne_vertex_edge AS (
        -- The edges connected to the vanne vertex (source or target)
        SELECT vertex.id as v_id, edge.id as e_id
        FROM stareau_aep.aep_vanne vanne
        JOIN vanne_vertex vertex ON vertex.id = vanne.fid
        JOIN stareau.aep_edge edge ON (vertex.id = edge.source OR vertex.id = edge.target)
      )
      -- For each edges connected by a vanne vertex (the path), the cost to pass through is 10000
      SELECT ARRAY[ve1.e_id, ve2.e_id] AS "path", 10000 as "cost"
        FROM vanne_vertex_edge ve1 JOIN vanne_vertex_edge ve2 ON ve1.v_id = ve2.v_id
        WHERE ve1.e_id <> ve2.e_id

      $r$,
      %1$s, ARRAY(
        -- The 100 nearest vanne vertex from the provided vertex id
        SELECT vertex.id
        FROM stareau_aep.aep_vanne vanne
        JOIN stareau.aep_vertex vertex ON vertex.id = vanne.fid
        ORDER BY (SELECT geom FROM stareau.aep_vertex WHERE id=%1$s) <-> vertex.geom
        LIMIT 100
      )
    )
    GROUP BY start_vid, end_vid
),
nearest_path_to_vannes AS (
    -- The nearest vannes are those with the path without a step through a vanne vertex
    SELECT *
      FROM shortest_path_to_vannes
     WHERE max_step_cost < 10000
    ORDER BY agg_cost
)
-- Return the nearest vanne data
SELECT aep_vanne.*
  FROM nearest_path_to_vannes
  JOIN stareau_aep.aep_vanne aep_vanne ON aep_vanne.fid = nearest_path_to_vannes.end_vid

        $format$,
        vertex_id
        );
    END
    $func$;

COMMENT ON FUNCTION stareau.aep_pgr_nearest_vannes(integer) IS
'Fonction de recherche des vannes les plus proches d''un vertex AEP (un noeud réseau AEP).
⚠ Nécessite PGRouting.';


CREATE FUNCTION stareau."aep_pgr_nearest_vannes_withPoint"(the_point geometry)
    RETURNS SETOF stareau_aep.aep_vanne
    LANGUAGE plpgsql AS
    $func$
    BEGIN
        RETURN QUERY EXECUTE
        format(
        $format$

WITH shortest_path_to_vannes AS (
  -- The shortest path from the provided vertex id to the 100 nearest vanne vertex
  -- start_vid: the provided vertex id
  -- end_vid: a vanne vertex
  -- steps: the number of steps to go from start_vid to end_vid
  -- max_step_cost: the cost of the most expensive step
  -- agg_cost: the total cost of the path
  SELECT start_vid, end_vid, MAX(path_seq) steps,
         max("cost") as max_step_cost,
         max(agg_cost) as agg_cost
    FROM pgr_trsp_withPoints(
      -- The Edge SQL
      $e$ SELECT id, source, target, cost, reverse_cost from stareau.aep_edge $e$,
      -- The Restriction SQL, the cost the pass through a vanne vertex
      $r$

      WITH vanne_vertex AS (
        -- The 100 nearest vanne vertex from the provided point
        SELECT vertex.id
        FROM stareau_aep.aep_vanne vanne
        JOIN stareau.aep_vertex vertex ON vertex.id = vanne.fid
        ORDER BY '%1$s'::geometry <-> vertex.geom
        LIMIT 100
      ),
      vanne_vertex_edge AS (
        -- The edges connected to the vanne vertex (source or target)
        SELECT vertex.id as v_id, edge.id as e_id
        FROM stareau_aep.aep_vanne vanne
        JOIN vanne_vertex vertex ON vertex.id = vanne.fid
        JOIN stareau.aep_edge edge ON (vertex.id = edge.source OR vertex.id = edge.target)
      )
      -- For each edges connected by a vanne vertex (the path), the cost to pass through is 10000
      SELECT ARRAY[ve1.e_id, ve2.e_id] AS "path", 10000 as "cost"
        FROM vanne_vertex_edge ve1 JOIN vanne_vertex_edge ve2 ON ve1.v_id = ve2.v_id
        WHERE ve1.e_id <> ve2.e_id

      $r$,
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

      -1, ARRAY(
        -- The 100 nearest vanne vertex from the provided point
        SELECT vertex.id
        FROM stareau_aep.aep_vanne vanne
        JOIN stareau.aep_vertex vertex ON vertex.id = vanne.fid
        ORDER BY '%1$s'::geometry <-> vertex.geom
        LIMIT 100
      )
    )
    GROUP BY start_vid, end_vid
),
nearest_path_to_vannes AS (
    -- The nearest vannes are those with the path without a step through a vanne vertex
    SELECT *
      FROM shortest_path_to_vannes
     WHERE max_step_cost < 10000
    ORDER BY agg_cost
)
-- Return the nearest vanne data
SELECT aep_vanne.*
  FROM nearest_path_to_vannes
  JOIN stareau_aep.aep_vanne aep_vanne ON aep_vanne.fid = nearest_path_to_vannes.end_vid

        $format$,
        the_point
        );
    END
    $func$;


COMMENT ON FUNCTION stareau."aep_pgr_nearest_vannes_withPoint"(geometry) IS
'Fonction de recherche des vannes les plus proches d''un point proche du réseau AEP.
⚠ Nécessite PGRouting.';


CREATE FUNCTION stareau.aep_pgr_path_to_nearest_target(
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
                    -- The Edge SQL
                    'SELECT id, source, target, cost, reverse_cost from stareau.aep_edge',
                    -- The started vretex
                    %1$s,
                    -- The ended vertexes
                    ARRAY(
                        -- The 10 nearest target vertex from the provided vertex id
                        SELECT vertex.id
                        FROM "%2$I"."%3$I" AS target
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
    $func$;


COMMENT ON FUNCTION stareau.aep_pgr_path_to_nearest_target(integer, text, text) IS
'Fonction de recherche de la cible la plus proche d''un vertex AEP (un noeud réseau AEP).
⚠ Nécessite PGRouting.';



--
-- PostgreSQL database dump complete
--
