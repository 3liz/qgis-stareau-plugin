-- Duplicate nodes of the AEP network: use the orphan nodes of the AEP network
CREATE OR REPLACE FUNCTION stareau.aep_noeud_doublon() RETURNS SETOF stareau_principale.noeud_reseau
    LANGUAGE sql
    AS $$
        SELECT nro.*
        FROM stareau.aep_noeud_orphelin() nro
            JOIN stareau_principale.noeud_reseau nr ON ST_DWithin(nro.geom, nr.geom, 0.05) AND ST_Equals(nro.geom, nr.geom) AND nro.fid <> nr.fid
        WHERE nro.type_reseau = 'aep' AND nr.fid IS NOT NULL;
    $$;


-- Fix the distance to the terminal node in the comment
COMMENT ON FUNCTION stareau.before_canalisation_insert_or_update() IS 'Fonction qui lie les canalisations aux noeuds de réseau en amont et en aval
Si le point initial de la géometrie de la canalisation est à moins de 10cm d''un noeud de réseau,
alors on lie la canalisation à ce noeud en modifiant la géométrie et le champ noeudinitial
sinon la valeur ''non_renseigne'' est précisée dans le champs noeudinitial
Si le point final de la géometrie de la canalisation est à moins de 10cm d''un noeud de réseau,
alors on lie la canalisation à ce noeud en modifiant la géométrie et le champ noeudterminal
sinon la valeur ''non_renseigne'' est précisée dans le champs noeudterminal
';
