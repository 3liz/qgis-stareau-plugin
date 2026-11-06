# Tables and fields

The plugin installs the tables of the **StaR'Eau geostandard**, split in several schemas,
and its own schema `stareau`. The names below use the default schema name `stareau`:
all the schemas are prefixed by the schema name chosen when
[creating the database structure](../installation/index.md#create-the-database-structure).

For the complete description of the StaR'Eau tables and fields, see the documentation of the geostandard
in the [StaR-Eau repository](https://github.com/cnigfr/StaR-Eau). The tables and fields of the database
also have **comments**, visible in the QGIS **Browser** panel or with SchemaSpy.

For the technical details of the schemas (types, constraints, relationships, indexes, functions, etc.),
see the [Database structure](structure.md).

## Schemas

| Schema | Content |
|--------|---------|
| `stareau` | Functions and triggers of the plugin, [routing graph](#aep_vertex-and-aep_edge), [metadata](#metadata) |
| `stareau_principale` | Parent tables: [`champ_commun`](#champ_commun), [`noeud_reseau`](#noeud_reseau), [`canalisation`](#canalisation), `dimension`, `emprise` |
| `stareau_commun` | Tables shared by the AEP and ASS networks: `pluviometre`, `piezometre`, `point_geolocalisation` |
| `stareau_aep` | Drinking water network: `aep_canalisation`, `aep_captage`, `aep_traitement`, `aep_reservoir`, `aep_vanne`, `aep_pompage`, `aep_regulation`, `aep_appareillage`, `aep_point_mesure`, `aep_piece`, etc. |
| `stareau_aep_brcht` | Drinking water service connections: `aep_canalisation_branchement`, `aep_point_livraison`, `aep_raccord`, `aep_vanne_branchement`, `aep_piece_branchement` |
| `stareau_ass` | Sanitation network: `ass_canalisation`, `ass_regard`, `ass_pompage`, `ass_traitement`, `ass_bassin`, `ass_exutoire`, `ass_equipement`, `ass_ouvrage_special_*`, `ass_gestion_epl_*`, etc. |
| `stareau_ass_brcht` | Sanitation service connections: `ass_canalisation_branchement`, `ass_point_collecte`, `ass_raccord`, `ass_engouffrement_*` |
| `stareau_defense_incendie` | Fire water points: `pei` and its value lists |
| `stareau_valeur` | [Value lists](#value-lists) |

The tables `*_affleurant`, `*_genie_civil`, `*_perimetre_gestion` and `*_protection_mecanique`
are created in both schemas `stareau_aep` and `stareau_ass`.

## Main tables

The tables of the network objects **inherit** from the parent tables of the schema `stareau_principale`
(see [Table inheritance](../concepts/index.md#table-inheritance)): they have all the fields described below,
and their own specific fields.

### champ_commun

The **common fields** of all the network objects. This table contains no data.

| Field | Type | Description |
|-------|------|-------------|
| `type_reseau` | text | **Network type**: `aep`, `assaeu`, `assaep`, `assaru`, `ince` (list `com_type_reseau`) |
| `fictif` | boolean | If the object is **fictitious**, e.g. a node added to link two pipes. Default: `False`. |
| `etat_service` | text | Service status (list `com_etat_service`) |
| `insee_commune` | text | INSEE code of the municipality |
| `localisation` | text | Address, name of the main street, or relative location of the object |
| `maitre_ouvrage` | text | Owner |
| `exploitant` | text | Current operator |
| `entreprise_pose` | text | Company which installed the object |
| `precision_xy`, `precision_z` | text | Precision class of the XY and Z coordinates (list `com_precision`) |
| `an_pose_inf`, `an_pose_sup` | integer | Start and end years of the installation period. `an_pose_sup` is `-9999` if unknown. |
| `an_service_inf`, `an_service_sup` | integer | Start and end years of the commissioning period |
| `an_abandon_inf`, `an_abandon_sup` | integer | Start and end years of the decommissioning period |
| `an_rehab_inf`, `an_rehab_sup` | integer | Start and end years of the rehabilitation period |
| `date_creation`, `origine_creation` | timestamp, text | Date and origin of the creation of the object |
| `date_maj`, `origine_maj` | timestamp, text | Date and origin of the last update of the object |
| `lien_doc1`, `lien_doc2` | text | Links to documents |
| `commentaire` | text | Comment |

### noeud_reseau

The **network nodes**: parent table of all the point objects of the networks
(`aep_vanne`, `aep_reservoir`, `ass_regard`, etc.).

| Field | Type | Description |
|-------|------|-------------|
| `fid` | integer | Unique identifier (automatic), unique across all the node tables |
| `id_noeud_reseau` | text | **Identifier of the node** used by the pipes. Unique. A UUID by default. |
| `geom` | Point | Geometry of the node. Its coordinates are [rounded to 5 cm](../user-guide/topology.md#coordinates-precision). |

### canalisation

The **pipes**: parent table of all the pipe tables
(`aep_canalisation`, `ass_canalisation`, `aep_canalisation_branchement`, `ass_canalisation_branchement`).

| Field | Type | Description |
|-------|------|-------------|
| `fid` | integer | Unique identifier (automatic), unique across all the pipe tables |
| `id_canalisation` | text | Identifier of the pipe. Unique. A UUID by default. |
| `geom` | LineString | Geometry of the pipe, from the initial node to the terminal node |
| `noeudinitial` | text | `id_noeud_reseau` of the **initial node**, or `non_renseigne`. [Filled automatically](../user-guide/topology.md#create-or-move-a-pipe). |
| `noeudterminal` | text | `id_noeud_reseau` of the **terminal node**, or `non_renseigne`. Filled automatically. |
| `mode_circulation` | text | Flow mode (list `com_mode_circulation`) |
| `type_pose` | text | Laying type (list `com_type_pose`) |
| `raison_pose` | text | Reason for laying (list `com_raison_pose`) |
| `materiau` | text | Material (list `com_materiau`) |
| `revetement_interieur` | text | Inner lining (list `com_revetement_interieur`) |
| `diametre_equivalent` | integer | Nominal diameter |
| `longueur_terrain` | real | Length measured on the ground |
| `sensible` | boolean | If the pipe is sensitive |

The drinking water pipes `aep_canalisation` also have the field `fonction_canalisation`
(list `aep_fonction_canalisation`: `adduction`, `transport`, `transport_distri`, `distribution`),
used by the [network analysis algorithms](../user-guide/processing.md#network-analysis).

### aep_vanne

The **valves** of the drinking water network. Among their specific fields, the field `etat_ouverture`
(list `aep_etat_ouverture`: `ouverte`, `fermee`, `partiel_ouverte`, `partiel_fermee`) is the
**opening state** of the valve in normal operation. It is modified by the actions
[Fermer la vanne and Ouvrir la vanne](../user-guide/qgis-project.md#close-or-open-a-valve),
and used by the [network analysis](../user-guide/network-analysis.md) functions.

## Value lists

The schema `stareau_valeur` contains one table per **value list** of the geostandard,
prefixed by `aep_`, `ass_` or `com_` (common to both networks), e.g. `aep_type_vanne`,
`ass_type_regard`, `com_materiau`.

| Field | Type | Description |
|-------|------|-------------|
| `code` | text | **Code** stored in the fields of the network tables. Unique. |
| `valeur` | text | Label of the value |
| `description` | text | Description of the value |

The lists are filled when [creating the database structure](../installation/index.md#create-the-database-structure),
from the CSV files of the geostandard. The following values are added to every list:

| Code | Label | Description |
|------|-------|-------------|
| `non_renseigne` | Non renseigné(e) | Information being searched, or available but not entered |
| `non_concerne` | Non concerné(e) | Information not possible or not relevant for the object |
| `non_valide` | Non validé(e) | Information exists but is not officially validated |
| `non_determine` | Non déterminé(e) | Information unknown or not available, and cannot be |
| `autre` | Autre | Not in the list, see the comment |

The list `com_precision` only gets the additional value `N` (*Non renseigné(e)*).

## Plugin tables

The schema `stareau` contains the tables of the plugin.

### aep_vertex and aep_edge

The **routing graph** of the drinking water network, used by the pgRouting functions,
and filled by the algorithm [Fill AEP vertices and edges](../user-guide/processing.md#fill-aep-vertices-and-edges).

`aep_vertex`:

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Identifier of the vertex: the `fid` of the AEP network node, or an automatic identifier for a missing node |
| `fictif` | boolean | `True` for a vertex created at the location of a [missing node](../user-guide/processing.md#get-missing-nodes) |
| `geom` | Point | Geometry of the vertex |

`aep_edge`:

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Identifier of the edge: the `fid` of the AEP pipe |
| `source` | integer | Identifier of the vertex of the initial node |
| `target` | integer | Identifier of the vertex of the terminal node |
| `cost` | real | Cost from `source` to `target`: the length of the pipe |
| `reverse_cost` | real | Cost from `target` to `source`: the length of the pipe |
| `geom` | LineString | Geometry of the pipe |

### metadata

The **version** of the database structure, used by the plugin to know which
[upgrades](../installation/index.md#upgrade-database-structure) must be run.

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Identifier |
| `me_version` | text | Version of the database structure |
| `me_version_date` | date | Date of the version |
| `me_status` | integer | Status of the version: `1` for the active version |

The tables `test` and `glossary_test_category` are examples, not used by the plugin.
