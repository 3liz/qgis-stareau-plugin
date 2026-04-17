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
                fid_noeudinitial, id_noeudinitial,
                fid_noeudterminal, id_noeudterminal,
                all_parents
            ) AS (
                SELECT 1 AS idx, c.fid,
                    ni.fid, c.noeudinitial,
                    nt.fid, c.noeudterminal,
                    array[c.fid] as all_parents
                FROM stareau_principale.canalisation AS c
                JOIN stareau_principale.noeud_reseau AS ni ON c.noeudinitial = ni.id_noeud_reseau
                LEFT JOIN stareau_principale.noeud_reseau AS nt ON c.noeudterminal = nt.id_noeud_reseau
                WHERE c.type_reseau <> 'aep'
                AND c.noeudinitial = '%1$s'
                AND ni.type_reseau <> 'aep'
                AND (nt.type_reseau IS NULL OR nt.type_reseau <> 'aep')
                UNION
                SELECT w.idx+1 AS idx, c.fid,
                    ni.fid, c.noeudinitial,
                    nt.fid, c.noeudterminal,
                    w.all_parents || c.fid
                FROM walk_network AS w
                INNER JOIN stareau_principale.canalisation AS c ON c.noeudinitial = w.id_noeudterminal
                JOIN stareau_principale.noeud_reseau AS ni ON c.noeudinitial = ni.id_noeud_reseau
                JOIN stareau_principale.noeud_reseau AS nt ON c.noeudterminal = nt.id_noeud_reseau
                WHERE NOT c.fid = ANY(w.all_parents)
            )
            SELECT idx, fid_canalisation, fid_noeudinitial, id_noeudinitial, fid_noeudterminal, id_noeudterminal
            FROM walk_network
            ORDER BY idx
        $$,
        id_noeud_reseau
        );
    END
    $func$;

-- FUNCTION ass_downstream(text)
COMMENT ON FUNCTION stareau.ass_downstream(id_noeud_reseau text) IS
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
                fid_noeudinitial, id_noeudinitial,
                fid_noeudterminal, id_noeudterminal,
                all_parents
            ) AS (
                SELECT 1 AS idx, c.fid,
                    ni.fid, c.noeudinitial,
                    nt.fid, c.noeudterminal,
                    array[c.fid] as all_parents
                FROM stareau_principale.canalisation AS c
                JOIN stareau_principale.noeud_reseau AS nt ON c.noeudterminal = nt.id_noeud_reseau
                LEFT JOIN stareau_principale.noeud_reseau AS ni ON c.noeudinitial = ni.id_noeud_reseau
                WHERE c.type_reseau <> 'aep'
                AND c.noeudterminal = '%1$s'
                AND nt.type_reseau <> 'aep'
                AND (ni.type_reseau IS NULL OR ni.type_reseau <> 'aep')
                UNION
                SELECT w.idx+1 AS idx, c.fid,
                    ni.fid, c.noeudinitial,
                    nt.fid, c.noeudterminal,
                    w.all_parents || c.fid
                FROM walk_network AS w
                INNER JOIN stareau_principale.canalisation AS c ON c.noeudterminal = w.id_noeudinitial
                JOIN stareau_principale.noeud_reseau AS ni ON c.noeudinitial = ni.id_noeud_reseau
                JOIN stareau_principale.noeud_reseau AS nt ON c.noeudterminal = nt.id_noeud_reseau
                WHERE NOT c.fid = ANY(w.all_parents)
            )
            SELECT idx, fid_canalisation, fid_noeudinitial, id_noeudinitial, fid_noeudterminal, id_noeudterminal
            FROM walk_network
            ORDER BY idx
        $$,
        id_noeud_reseau
        );
    END
    $func$;

-- FUNCTION ass_upstream(text)
COMMENT ON FUNCTION stareau.ass_upstream(id_noeud_reseau text) IS
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
--
-- PostgreSQL database dump complete
--
