# Useful functions

The `stareau` schema provides SQL functions which can be used directly in your queries,
for example in the QGIS **Browser** panel (right-click on the PostgreSQL connection or schema, then `Execute SQL…`),
in the QGIS **DB Manager**, in `psql` or in a **virtual layer** built on a PostgreSQL query.

The examples below use the default schema name `stareau` and the coordinate reference system `EPSG:2154`.

## Network check functions

| Function | Usage |
|----------|-------|
| `stareau.aep_noeud_manquant()`, `stareau.ass_noeud_manquant()` | Missing nodes of the AEP or ASS network |
| `stareau.aep_noeud_orphelin()`, `stareau.ass_noeud_orphelin()` | Orphan nodes of the AEP or ASS network |
| `stareau.aep_noeud_doublon()`, `stareau.ass_noeud_doublon()` | Duplicate nodes of the AEP or ASS network |

These functions are used by the [network check algorithms](../user-guide/processing.md#network-checks).

### Missing nodes

`stareau.ass_noeud_manquant()` and `stareau.aep_noeud_manquant()` return the start and end points of the pipes
whose initial or terminal node is `non_renseigne`, with the fields
`fid`, `geom`, `id_canalisation_upstream` and `id_canalisation_downstream`.

```sql
-- Number of missing nodes of the sanitation network
SELECT count(*) FROM stareau.ass_noeud_manquant();
```

### Orphan nodes

`stareau.ass_noeud_orphelin()` and `stareau.aep_noeud_orphelin()` return the network nodes
(all the fields of `stareau_principale.noeud_reseau`) which are not the initial or terminal node of any pipe.

```sql
-- Orphan nodes of the drinking water network, with the name of their table
SELECT n.tableoid::regclass AS table_name, n.fid, n.id_noeud_reseau
FROM stareau.aep_noeud_orphelin() AS n;
```

### Duplicate nodes

`stareau.ass_noeud_doublon()` and `stareau.aep_noeud_doublon()` return the orphan nodes
located at the same place as another network node.

## Sanitation network functions

| Function | Usage |
|----------|-------|
| `stareau.ass_downstream(id_noeud_reseau)` | Pipes downstream of a node |
| `stareau.ass_upstream(id_noeud_reseau)` | Pipes upstream of a node |

These functions walk the **sanitation network** recursively, following the direction of the pipes,
from the node with the given `id_noeud_reseau`. They do not need pgRouting.
They are used by the actions [Downstream and Upstream](../user-guide/qgis-project.md#upstream-and-downstream-of-a-sanitation-node).

They return one line per pipe, with the fields:

| Field | Description |
|-------|-------------|
| `idx` | Step of the walk, from `1` for the pipes connected to the node |
| `fid_canalisation` | `fid` of the pipe |
| `fid_noeudinitial`, `id_noeudinitial` | `fid` and `id_noeud_reseau` of the initial node of the pipe |
| `fid_noeudterminal`, `id_noeudterminal` | `fid` and `id_noeud_reseau` of the terminal node of the pipe |

Example: total length of the pipes downstream of a manhole:

```sql
SELECT sum(ST_Length(c.geom)) AS length
FROM stareau.ass_downstream('ac05c1e8-2c1f-4a8e-9bf7-3a2a7bd7dc0b') AS d
JOIN stareau_principale.canalisation AS c ON c.fid = d.fid_canalisation;
```

## Network analysis functions (pgRouting)

| Function | Usage |
|----------|-------|
| [aep_pgr_path_to_nearest_target](#path-to-the-nearest-target) | Pipes between a node and the nearest target |
| [aep_pgr_path_to_nearest_target_avoiding_closed_valves](#path-to-the-nearest-target) | Same, without crossing the closed valves |
| [aep_pgr_find_captages_from_traitement](#water-intakes-of-a-treatment-plant) | Adduction pipes between a treatment plant and its water intakes |
| [aep_pgr_nearest_vannes](#nearest-valves) | Valves to close to isolate a point or a node |
| [aep_pgr_nearest_closed_vannes](#nearest-valves) | Closed valves isolating a point |

These functions need the **pgRouting** extension and an up to date **routing graph**
(tables `stareau.aep_vertex` and `stareau.aep_edge`):
run the algorithm [Fill AEP vertices and edges](../user-guide/processing.md#fill-aep-vertices-and-edges) beforehand.
See [Network analysis](../user-guide/network-analysis.md).

The identifier of a vertex of the graph is the `fid` of the network node.

### Path to the nearest target

`stareau.aep_pgr_path_to_nearest_target(vertex_id, target_schema, target_table)` returns the pipes
(all the fields of `stareau_aep.aep_canalisation`) of the shortest path between a node
and the nearest object of the target table:

* `vertex_id`: the `fid` of the start node,
* `target_schema`: the schema of the target table, e.g. `stareau_aep`,
* `target_table`: the target table, e.g. `aep_captage`, `aep_traitement` or `aep_reservoir`.

Only the **10 targets closest** to the node (as the crow flies) are tested.

```sql
-- Pipes between the water intake 12 and the nearest treatment plant
SELECT fid, fonction_canalisation, ST_Length(geom) AS length
FROM stareau.aep_pgr_path_to_nearest_target(12, 'stareau_aep', 'aep_traitement');
```

`stareau.aep_pgr_path_to_nearest_target_avoiding_closed_valves(vertex_id, target_schema, target_table)`
has the same parameters, but the pipes connected to a **closed valve** (`etat_ouverture = 'fermee'`) are not used.

### Water intakes of a treatment plant

`stareau.aep_pgr_find_captages_from_traitement(vertex_id, target_schema, target_table)` returns the pipes
of the paths between a treatment plant and the water intakes which supply it, using only the
**adduction** pipes (`fonction_canalisation = 'adduction'`):

```sql
SELECT DISTINCT fid
FROM stareau.aep_pgr_find_captages_from_traitement(25, 'stareau_aep', 'aep_captage');
```

Unlike `aep_pgr_path_to_nearest_target`, the paths to all the reachable water intakes are returned
(among the 10 closest ones).

### Nearest valves

`stareau.aep_pgr_nearest_vannes(the_point)` returns the **valves** (all the fields of `stareau_aep.aep_vanne`)
to close to isolate a point of the drinking water network:

* `the_point`: a point geometry, located **less than 5 m** from a pipe of the graph.

The walk starts from the pipe closest to the point, in both directions, and stops at the first valve met
on each branch. Only the **100 valves closest** to the point are tested.

```sql
SELECT fid, id_noeud_reseau, etat_ouverture
FROM stareau.aep_pgr_nearest_vannes(
    ST_GeomFromText('POINT(785691.35 6272226.25)', 2154)
);
```

`stareau.aep_pgr_nearest_closed_vannes(the_point)` does the same with the **closed valves** only:
the open valves are crossed.

`stareau.aep_pgr_nearest_vannes(vertex_id)` is a variant starting from a network node, given by its `fid`.

## Trigger functions

| Function | Usage |
|----------|-------|
| `stareau.aa_before_geometry_insert_or_update_reduce_precision()` | Round the coordinates to 5 cm |
| `stareau.before_canalisation_insert_or_update()` | Link a pipe to its initial and terminal nodes |
| `stareau.after_noeud_reseau_insert_or_update()` | Link the pipes to a new node, move the pipes with a node |
| `stareau.after_noeud_reseau_delete()` | Unlink the pipes of a deleted node |

See [Network topology](../user-guide/topology.md) for the rules applied by these functions.

## Other functions

`stareau.get_current_setting(setting_name, default_value, value_type)` returns the value of a PostgreSQL setting,
or the default value if the setting is not set or invalid. It is used by the trigger functions to read the setting
[`stareau.graph.disable.trigger`](../user-guide/topology.md#disable-the-triggers).
