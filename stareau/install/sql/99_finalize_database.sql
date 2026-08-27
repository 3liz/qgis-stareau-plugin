SET statement_timeout = 0;
SET lock_timeout = 0;


SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

-- APPLY TRIGGERS from "stareau" functions to "StaR-Eau" tables

-- noeud_reseau trg_aa_before_geometry_insert_or_update_reduce_precision
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON "stareau_principale".noeud_reseau
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON "stareau_ass".ass_traitement
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON "stareau_ass".ass_pretraitement
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON "stareau_ass".ass_equipement
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON "stareau_ass".ass_pompage
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON "stareau_ass".ass_chambre_depollution
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON "stareau_ass".ass_piece
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON "stareau_ass".ass_regard
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON stareau_ass.ass_exutoire
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON stareau_ass.ass_bassin
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON "stareau_ass".ass_ouvrage_special_point
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON "stareau_ass_brcht".ass_point_collecte
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON "stareau_ass_brcht".ass_raccord
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON stareau_ass_brcht.ass_engouffrement_point
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON "stareau_aep".aep_captage
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON "stareau_aep".aep_reservoir
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON "stareau_aep".aep_traitement
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON "stareau_aep".aep_vanne
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON "stareau_aep".aep_regulation
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON "stareau_aep".aep_pompage
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON "stareau_aep".aep_appareillage
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON "stareau_aep".aep_piece
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON "stareau_aep_brcht".aep_point_livraison
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();

-- canalisation trg_aa_before_geometry_insert_or_update_reduce_precision
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON "stareau_principale".canalisation
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON "stareau_ass".ass_canalisation
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON "stareau_ass".ass_ouvrage_special_ligne
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON "stareau_ass_brcht".ass_canalisation_branchement
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON stareau_ass_brcht.ass_engouffrement_ligne
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON "stareau_aep".aep_canalisation
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON "stareau_aep_brcht".aep_canalisation_branchement
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();

-- emprise trg_aa_before_geometry_insert_or_update_reduce_precision
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON "stareau_principale".emprise
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON stareau_aep.aep_genie_civil
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON stareau_ass.ass_genie_civil
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON stareau_aep.aep_perimetre_gestion
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON stareau_ass.ass_perimetre_gestion
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON "stareau_ass".ass_ouvrage_special_surface
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();
CREATE TRIGGER trg_aa_before_geometry_insert_or_update_reduce_precision
    BEFORE INSERT OR UPDATE OF geom ON stareau_ass_brcht.ass_engouffrement_surface
    FOR EACH ROW EXECUTE PROCEDURE stareau.aa_before_geometry_insert_or_update_reduce_precision();


-- canalisation trg_before_canalisation_insert_or_update
CREATE TRIGGER trg_before_canalisation_insert_or_update
    BEFORE INSERT OR UPDATE OF geom ON "stareau_principale".canalisation
    FOR EACH ROW EXECUTE PROCEDURE stareau.before_canalisation_insert_or_update();
CREATE TRIGGER trg_before_canalisation_insert_or_update
    BEFORE INSERT OR UPDATE OF geom ON "stareau_ass".ass_canalisation
    FOR EACH ROW EXECUTE PROCEDURE stareau.before_canalisation_insert_or_update();
CREATE TRIGGER trg_before_canalisation_insert_or_update
    BEFORE INSERT OR UPDATE OF geom ON "stareau_ass".ass_ouvrage_special_ligne
    FOR EACH ROW EXECUTE PROCEDURE stareau.before_canalisation_insert_or_update();
CREATE TRIGGER trg_before_canalisation_insert_or_update
    BEFORE INSERT OR UPDATE OF geom ON "stareau_ass_brcht".ass_canalisation_branchement
    FOR EACH ROW EXECUTE PROCEDURE stareau.before_canalisation_insert_or_update();
CREATE TRIGGER trg_before_canalisation_insert_or_update
    BEFORE INSERT OR UPDATE OF geom ON stareau_ass_brcht.ass_engouffrement_ligne
    FOR EACH ROW EXECUTE PROCEDURE stareau.before_canalisation_insert_or_update();
CREATE TRIGGER trg_before_canalisation_insert_or_update
    BEFORE INSERT OR UPDATE OF geom ON "stareau_aep".aep_canalisation
    FOR EACH ROW EXECUTE PROCEDURE stareau.before_canalisation_insert_or_update();
CREATE TRIGGER trg_before_canalisation_insert_or_update
    BEFORE INSERT OR UPDATE OF geom ON "stareau_aep_brcht".aep_canalisation_branchement
    FOR EACH ROW EXECUTE PROCEDURE stareau.before_canalisation_insert_or_update();


-- noeud_reseau trg_after_noeud_reseau_insert_or_update
CREATE TRIGGER trg_after_noeud_reseau_insert_or_update
    AFTER INSERT OR UPDATE OF geom ON "stareau_principale".noeud_reseau
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_insert_or_update();
CREATE TRIGGER trg_after_noeud_reseau_insert_or_update
    AFTER INSERT OR UPDATE OF geom ON "stareau_ass".ass_traitement
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_insert_or_update();
CREATE TRIGGER trg_after_noeud_reseau_insert_or_update
    AFTER INSERT OR UPDATE OF geom ON "stareau_ass".ass_pretraitement
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_insert_or_update();
CREATE TRIGGER trg_after_noeud_reseau_insert_or_update
    AFTER INSERT OR UPDATE OF geom ON "stareau_ass".ass_equipement
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_insert_or_update();
CREATE TRIGGER trg_after_noeud_reseau_insert_or_update
    AFTER INSERT OR UPDATE OF geom ON "stareau_ass".ass_pompage
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_insert_or_update();
CREATE TRIGGER trg_after_noeud_reseau_insert_or_update
    AFTER INSERT OR UPDATE OF geom ON "stareau_ass".ass_chambre_depollution
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_insert_or_update();
CREATE TRIGGER trg_after_noeud_reseau_insert_or_update
    AFTER INSERT OR UPDATE OF geom ON "stareau_ass".ass_piece
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_insert_or_update();
CREATE TRIGGER trg_after_noeud_reseau_insert_or_update
    AFTER INSERT OR UPDATE OF geom ON "stareau_ass".ass_regard
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_insert_or_update();
CREATE TRIGGER trg_after_noeud_reseau_insert_or_update
    AFTER INSERT OR UPDATE OF geom ON stareau_ass.ass_exutoire
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_insert_or_update();
CREATE TRIGGER trg_after_noeud_reseau_insert_or_update
    AFTER INSERT OR UPDATE OF geom ON stareau_ass.ass_bassin
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_insert_or_update();
CREATE TRIGGER trg_after_noeud_reseau_insert_or_update
    AFTER INSERT OR UPDATE OF geom ON "stareau_ass".ass_ouvrage_special_point
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_insert_or_update();
CREATE TRIGGER trg_after_noeud_reseau_insert_or_update
    AFTER INSERT OR UPDATE OF geom ON "stareau_ass_brcht".ass_point_collecte
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_insert_or_update();
CREATE TRIGGER trg_after_noeud_reseau_insert_or_update
    AFTER INSERT OR UPDATE OF geom ON "stareau_ass_brcht".ass_raccord
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_insert_or_update();
CREATE TRIGGER trg_after_noeud_reseau_insert_or_update
    AFTER INSERT OR UPDATE OF geom ON stareau_ass_brcht.ass_engouffrement_point
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_insert_or_update();
CREATE TRIGGER trg_after_noeud_reseau_insert_or_update
    AFTER INSERT OR UPDATE OF geom ON "stareau_aep".aep_captage
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_insert_or_update();
CREATE TRIGGER trg_after_noeud_reseau_insert_or_update
    AFTER INSERT OR UPDATE OF geom ON "stareau_aep".aep_reservoir
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_insert_or_update();
CREATE TRIGGER trg_after_noeud_reseau_insert_or_update
    AFTER INSERT OR UPDATE OF geom ON "stareau_aep".aep_traitement
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_insert_or_update();
CREATE TRIGGER trg_after_noeud_reseau_insert_or_update
    AFTER INSERT OR UPDATE OF geom ON "stareau_aep".aep_vanne
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_insert_or_update();
CREATE TRIGGER trg_after_noeud_reseau_insert_or_update
    AFTER INSERT OR UPDATE OF geom ON "stareau_aep".aep_regulation
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_insert_or_update();
CREATE TRIGGER trg_after_noeud_reseau_insert_or_update
    AFTER INSERT OR UPDATE OF geom ON "stareau_aep".aep_pompage
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_insert_or_update();
CREATE TRIGGER trg_after_noeud_reseau_insert_or_update
    AFTER INSERT OR UPDATE OF geom ON "stareau_aep".aep_appareillage
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_insert_or_update();
CREATE TRIGGER trg_after_noeud_reseau_insert_or_update
    AFTER INSERT OR UPDATE OF geom ON "stareau_aep".aep_piece
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_insert_or_update();
CREATE TRIGGER trg_after_noeud_reseau_insert_or_update
    AFTER INSERT OR UPDATE OF geom ON "stareau_aep_brcht".aep_point_livraison
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_insert_or_update();

-- noeud_reseau trg_after_noeud_reseau_delete
CREATE TRIGGER trg_after_noeud_reseau_delete
    AFTER DELETE ON "stareau_principale".noeud_reseau
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_delete();
CREATE TRIGGER trg_after_noeud_reseau_delete
    AFTER DELETE ON "stareau_ass".ass_traitement
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_delete();
CREATE TRIGGER trg_after_noeud_reseau_delete
    AFTER DELETE ON "stareau_ass".ass_pretraitement
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_delete();
CREATE TRIGGER trg_after_noeud_reseau_delete
    AFTER DELETE ON "stareau_ass".ass_equipement
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_delete();
CREATE TRIGGER trg_after_noeud_reseau_delete
    AFTER DELETE ON "stareau_ass".ass_pompage
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_delete();
CREATE TRIGGER trg_after_noeud_reseau_delete
    AFTER DELETE ON "stareau_ass".ass_chambre_depollution
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_delete();
CREATE TRIGGER trg_after_noeud_reseau_delete
    AFTER DELETE ON "stareau_ass".ass_piece
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_delete();
CREATE TRIGGER trg_after_noeud_reseau_delete
    AFTER DELETE ON "stareau_ass".ass_regard
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_delete();
CREATE TRIGGER trg_after_noeud_reseau_delete
    AFTER DELETE ON stareau_ass.ass_exutoire
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_delete();
CREATE TRIGGER trg_after_noeud_reseau_delete
    AFTER DELETE ON stareau_ass.ass_bassin
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_delete();
CREATE TRIGGER trg_after_noeud_reseau_delete
    AFTER DELETE ON "stareau_ass".ass_ouvrage_special_point
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_delete();
CREATE TRIGGER trg_after_noeud_reseau_delete
    AFTER DELETE ON "stareau_ass_brcht".ass_point_collecte
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_delete();
CREATE TRIGGER trg_after_noeud_reseau_delete
    AFTER DELETE ON "stareau_ass_brcht".ass_raccord
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_delete();
CREATE TRIGGER trg_after_noeud_reseau_delete
    AFTER DELETE ON stareau_ass_brcht.ass_engouffrement_point
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_delete();
CREATE TRIGGER trg_after_noeud_reseau_delete
    AFTER DELETE ON "stareau_aep".aep_captage
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_delete();
CREATE TRIGGER trg_after_noeud_reseau_delete
    AFTER DELETE ON "stareau_aep".aep_reservoir
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_delete();
CREATE TRIGGER trg_after_noeud_reseau_delete
    AFTER DELETE ON "stareau_aep".aep_traitement
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_delete();
CREATE TRIGGER trg_after_noeud_reseau_delete
    AFTER DELETE ON "stareau_aep".aep_vanne
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_delete();
CREATE TRIGGER trg_after_noeud_reseau_delete
    AFTER DELETE ON "stareau_aep".aep_regulation
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_delete();
CREATE TRIGGER trg_after_noeud_reseau_delete
    AFTER DELETE ON "stareau_aep".aep_pompage
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_delete();
CREATE TRIGGER trg_after_noeud_reseau_delete
    AFTER DELETE ON "stareau_aep".aep_appareillage
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_delete();
CREATE TRIGGER trg_after_noeud_reseau_delete
    AFTER DELETE ON "stareau_aep".aep_piece
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_delete();
CREATE TRIGGER trg_after_noeud_reseau_delete
    AFTER DELETE ON "stareau_aep_brcht".aep_point_livraison
    FOR EACH ROW EXECUTE PROCEDURE stareau.after_noeud_reseau_delete();
