# Presentation of the plugin concepts

The StarEau plugin helps to manage the data of **underground water networks** with **QGIS** and **PostGIS**:

* **drinking water** networks (AEP, *alimentation en eau potable*),
* **sanitation** networks (ASS, *assainissement*): wastewater, stormwater and combined sewers.

The data model is the **StaR'Eau geostandard**, published by the CNIG
(*Conseil national de l'information géolocalisée*) and the ASTEE.
The SQL files of the geostandard are available in the
[StaR-Eau repository](https://github.com/cnigfr/StaR-Eau): the plugin installs them
and adds its own functions and triggers to keep the network **topology** consistent
and to **analyse** the network.

## Network types

Each object of the network has a **network type**, stored in the field `type_reseau`
(value list `com_type_reseau`):

| Code | Network |
|------|---------|
| `aep` | Drinking water |
| `assaeu` | Wastewater |
| `assaep` | Stormwater |
| `assaru` | Combined sewer (*réseau unitaire*) |
| `ince` | Fire fighting |

The plugin tools work either on the **AEP** network (`type_reseau = 'aep'`)
or on the **ASS** network (all the other network types).
A pipe is never linked to a node of the other network family.

## Nodes and pipes

The network is a **graph** made of **network nodes** and **pipes**:

* a **network node** (*nœud réseau*) is a point: a valve, a manhole, a reservoir, a pumping station, etc.,
* a **pipe** (*canalisation*) is a line linking two nodes:
    * its **initial node** (`noeudinitial`), at the start point of the line,
    * its **terminal node** (`noeudterminal`), at the end point of the line.

The **direction of the line** is meaningful: from the initial node to the terminal node.
For a sanitation network, it is the **flow direction**, used to walk the network
[upstream and downstream](../user-guide/qgis-project.md#layer-actions).

When there is no node at the start or end point of a pipe, the field `noeudinitial` or `noeudterminal`
contains the value `non_renseigne`: it is a **missing node**,
which can be found with the algorithm [Get missing nodes](../user-guide/processing.md#get-missing-nodes).

The links between pipes and nodes are **maintained automatically** by the database,
see [Network topology](../user-guide/topology.md).

## Table inheritance

The StaR'Eau data model uses the **PostgreSQL table inheritance**:

* the table `stareau_principale.noeud_reseau` is the parent of all the node tables:
  `aep_vanne`, `aep_reservoir`, `ass_regard`, `ass_pompage`, etc.,
* the table `stareau_principale.canalisation` is the parent of all the pipe tables:
  `aep_canalisation`, `ass_canalisation`, `aep_canalisation_branchement`, etc.,
* all these tables also inherit the **common fields** of `stareau_principale.champ_commun`:
  network type, service status, INSEE code of the municipality, owner, operator, XY and Z precisions, dates, etc.

The data is **stored in the child tables**, e.g. a valve in `stareau_aep.aep_vanne`.
A query on a parent table returns the objects of **all its child tables**:
`stareau_principale.noeud_reseau` contains all the nodes of all the networks.
The identifiers `fid`, `id_noeud_reseau` and `id_canalisation` are therefore unique across all the child tables.

## Value lists

Most fields contain a **code** from a value list, stored in the schema `stareau_valeur`
(one table per list, with the fields `code`, `valeur` and `description`).
For example, the field `etat_ouverture` of a valve uses the list `aep_etat_ouverture`:
`ouverte`, `fermee`, `partiel_ouverte`, `partiel_fermee`.

Besides the values of the geostandard, every list contains the values
`non_renseigne`, `non_concerne`, `non_valide`, `non_determine` and `autre`.

## Network analysis

Some tools use the extension **pgRouting** to find paths in the **drinking water** network:

* the pipes between a node and the **nearest target**: water intake, treatment plant, reservoir,
* the pipes between the **water intakes and the treatment plants**, or between the
  **treatment plants and the reservoirs**, to check the **function of the pipes**,
* the **valves** to close to isolate a part of the network.

These tools use a **routing graph** computed from the AEP nodes and pipes, see
[Network analysis](../user-guide/network-analysis.md).

## Glossary

| Concept | French | Definition |
|---------|--------|------------|
| AEP | Alimentation en eau potable | Drinking water network |
| ASS | Assainissement | Sanitation network: wastewater, stormwater, combined sewer |
| Network node | Nœud réseau | Point object of the network linked to the pipes: valve, manhole, reservoir, etc. |
| Pipe | Canalisation | Line between an initial node and a terminal node |
| Service connection | Branchement | Part of the network between the main pipe and the user (schemas `*_brcht`) |
| Missing node | Nœud manquant | Start or end point of a pipe without any network node |
| Orphan node | Nœud orphelin | Network node which is not the initial or terminal node of any pipe |
| Duplicate node | Nœud en doublon | Orphan node located at the same place as another node |
| Water intake | Captage | Point where the raw water is taken from the resource |
| Treatment plant | Traitement | Drinking water treatment plant |
| Reservoir | Réservoir | Water tank or water tower |
| Valve | Vanne | Device used to open or close a pipe |
| Manhole | Regard | Access point to a sanitation pipe |
| PEI | Point d'eau incendie | Fire hydrant or fire water point (schema `stareau_defense_incendie`) |
| Vertex / Edge | | Node / pipe of the pgRouting graph, see [Network analysis](../user-guide/network-analysis.md) |
