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

-- FUNCTION aa_before_geometry_insert_or_update_reduce_precision()
COMMENT ON FUNCTION stareau.aa_before_geometry_insert_or_update_reduce_precision() IS 'Fonction qui arrondit la précision des coordonnées à 0.05 soit (cm si ce n''est pas déjà fait
lors d''une création ou d''une modification de géométrie.
Elle est préfixée par aa_ pour être lancée avant les autres trigger,
car l''ordre alphabétique compte.
';


-- FUNCTION aep_noeud_doublon()
COMMENT ON FUNCTION stareau.aep_noeud_doublon() IS 'Fonction de récupération des noeuds en doublon (sans lien avec une canalisation et situé au même endroit qu''un autre noeud) du réseau AEP.
';


-- FUNCTION aep_noeud_manquant()
COMMENT ON FUNCTION stareau.aep_noeud_manquant() IS 'Fonction de création d''une table des noeuds manquants du réseau AEP.
';


-- FUNCTION aep_noeud_orphelin()
COMMENT ON FUNCTION stareau.aep_noeud_orphelin() IS 'Fonction de récupération des noeuds orphelins (sans lien avec une canalisation) du réseau AEP.
';


-- FUNCTION aep_pgr_find_captages_from_traitement(vertex_id integer, target_schema text, target_table text)
COMMENT ON FUNCTION stareau.aep_pgr_find_captages_from_traitement(vertex_id integer, target_schema text, target_table text) IS 'Fonction de recherche des points de captages alimentant un point de traitement.
⚠ Nécessite PGRouting.';


-- FUNCTION aep_pgr_nearest_closed_vannes(the_point geometry)
COMMENT ON FUNCTION stareau.aep_pgr_nearest_closed_vannes(the_point geometry) IS 'Fonction de recherche des vannes fermées les plus proches d''un point donné.
⚠ Nécessite PGRouting.';


-- FUNCTION aep_pgr_nearest_vannes(vertex_id integer)
COMMENT ON FUNCTION stareau.aep_pgr_nearest_vannes(vertex_id integer) IS 'Fonction de recherche des vannes les plus proches d''un vertex AEP (un noeud réseau AEP).
⚠ Nécessite PGRouting.';


-- FUNCTION "aep_pgr_nearest_vannes_withPoint"(the_point geometry)
COMMENT ON FUNCTION stareau."aep_pgr_nearest_vannes_withPoint"(the_point geometry) IS 'Fonction de recherche des vannes les plus proches d''un point proche du réseau AEP.
⚠ Nécessite PGRouting.';


-- FUNCTION aep_pgr_path_to_nearest_target(vertex_id integer, target_schema text, target_table text)
COMMENT ON FUNCTION stareau.aep_pgr_path_to_nearest_target(vertex_id integer, target_schema text, target_table text) IS 'Fonction de recherche de la cible la plus proche d''un vertex AEP (un noeud réseau AEP).
⚠ Nécessite PGRouting.';


-- FUNCTION aep_pgr_path_to_nearest_target_avoiding_closed_valves(vertex_id integer, target_schema text, target_table text)
COMMENT ON FUNCTION stareau.aep_pgr_path_to_nearest_target_avoiding_closed_valves(vertex_id integer, target_schema text, target_table text) IS 'Fonction de recherche de la cible la plus proche d''un noeud réseau AEP.
Les vannes fermées ne sont pas traversables.
⚠ Nécessite PGRouting.';


-- FUNCTION after_noeud_reseau_insert_or_update()
COMMENT ON FUNCTION stareau.after_noeud_reseau_insert_or_update() IS 'Fonction qui modifie les canalisations afin de modifier les champs noeudinitial et noeudterminal
en assignant la valeur ''non_renseigne'' pour le noeud supprimé.
';


-- FUNCTION ass_downstream(id_noeud_reseau text)
COMMENT ON FUNCTION stareau.ass_downstream(id_noeud_reseau text) IS 'Fonction de parcours du réseau en aval d''un noeud de réseau ASS.
Retourne les canalisations et les noeuds de réseau en aval du noeud de réseau passé en paramètre.
';


-- FUNCTION ass_noeud_doublon()
COMMENT ON FUNCTION stareau.ass_noeud_doublon() IS 'Fonction de récupération des noeuds en doublon (sans lien avec une canalisation et situé au même endroit qu''un autre noeud) du réseau ASS.
';


-- FUNCTION ass_noeud_manquant()
COMMENT ON FUNCTION stareau.ass_noeud_manquant() IS 'Fonction de création d''une table des noeuds manquants du réseau ASS.
';


-- FUNCTION ass_noeud_orphelin()
COMMENT ON FUNCTION stareau.ass_noeud_orphelin() IS 'Fonction de récupération des noeuds orphelins (sans lien avec une canalisation) du réseau ASS.
';


-- FUNCTION ass_upstream(id_noeud_reseau text)
COMMENT ON FUNCTION stareau.ass_upstream(id_noeud_reseau text) IS 'Fonction de parcours du réseau en amnt d''un noeud de réseau ASS.
Retourne les canalisations et les noeuds de réseau en amont du noeud de réseau passé en paramètre.
';


-- FUNCTION before_canalisation_insert_or_update()
COMMENT ON FUNCTION stareau.before_canalisation_insert_or_update() IS 'Fonction qui lie les canalisations aux noeuds de réseau en amont et en aval
Si le point initial de la géometrie de la canalisation est à moins de 10cm d''un noeud de réseau,
alors on lie la canalisation à ce noeud en modifiant la géométrie et le champ noeudinitial
sinon la valeur ''non_renseigne'' est précisée dans le champs noeudinitial
Si le point final de la géometrie de la canalisation est à moins de 10m d''un noeud de réseau,
alors on lie la canalisation à ce noeud en modifiant la géométrie et le champ noeudterminal
sinon la valeur ''non_renseigne'' est précisée dans le champs noeudterminal
';


-- FUNCTION get_current_setting(setting_name text, default_value text, value_type text)
COMMENT ON FUNCTION stareau.get_current_setting(setting_name text, default_value text, value_type text) IS 'Get a PostgreSQL current setting, with a default value if the setting is not set or is invalid.
The function is used to avoid repeating the coalesce(current_setting(...))::TYPE, 0) = 1 and to
have a single point of maintenace for getting settings.
';


-- aep_edge
COMMENT ON TABLE stareau.aep_edge IS 'AEP Edge for routing';


-- aep_vertex
COMMENT ON TABLE stareau.aep_vertex IS 'AEP Vertex for routing';


-- glossary_test_category
COMMENT ON TABLE stareau.glossary_test_category IS 'Glossary for the column category of the table test';


-- metadata
COMMENT ON TABLE stareau.metadata IS 'Metadata of the structure : version and date. Useful for database structure and glossary data migrations between versions';


-- test
COMMENT ON TABLE stareau.test IS 'Test table';


--
-- PostgreSQL database dump complete
--



