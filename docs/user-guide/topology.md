# Network topology

The links between the **pipes** and the **network nodes** are maintained by **trigger functions**
of the schema `stareau`, each time a pipe or a node is created, moved or deleted.
They work the same way in QGIS, in Lizmap or with SQL queries.

The triggers are installed on the parent tables `stareau_principale.noeud_reseau` and `stareau_principale.canalisation`
and on **each child table** (PostgreSQL does not apply the triggers of a parent table to its child tables).

A pipe is only linked to a node of the **same network family**:
a drinking water pipe (`type_reseau = 'aep'`) to a drinking water node,
a sanitation pipe (any other network type) to a sanitation node.

## Coordinates precision

The coordinates of the geometries of the nodes and of the pipes are **rounded to 5 cm**
(`ST_ReducePrecision(geom, 0.05)`) when they are created or modified.

This trigger function, `aa_before_geometry_insert_or_update_reduce_precision`, is prefixed by `aa_`
to be run **before the other triggers**, which are run in alphabetical order.

## Create or move a pipe

When a pipe is **created**, or when its **geometry is modified**:

* if a network node is located **less than 10 cm** from the **start point** of the line,
  the start point is **moved on the node** and the field `noeudinitial` gets the `id_noeud_reseau` of this node,
* otherwise, `noeudinitial` gets the value `non_renseigne`,
* the same rules apply to the **end point** of the line and the field `noeudterminal`.

If several nodes are closer than 10 cm, the closest one is used.

The direction of the line defines the initial and terminal nodes:
use the action [Inverser la canalisation](qgis-project.md#reverse-a-pipe) to reverse a pipe
drawn in the wrong direction. Its initial and terminal nodes are then swapped automatically.

## Create a node

When a network node is **created**, the pipes of the same network family:

* whose `noeudinitial` is `non_renseigne` and whose **start point** is less than **10 cm** from the node,
* whose `noeudterminal` is `non_renseigne` and whose **end point** is less than **10 cm** from the node,

are **linked to the new node**: their start or end point is moved on the node,
and their field `noeudinitial` or `noeudterminal` gets the `id_noeud_reseau` of the node.

This allows to correct the [missing nodes](processing.md#get-missing-nodes) by creating the nodes after the pipes.

## Move a node

When the geometry of a network node is **modified**, the **start point** of the pipes starting at this node
and the **end point** of the pipes ending at this node are **moved** with the node.

## Delete a node

When a network node is **deleted**, the fields `noeudinitial` and `noeudterminal` of the pipes linked to this node
get the value `non_renseigne`. The geometries of the pipes are not modified.

## Disable the triggers

For a bulk import or a batch update, the trigger functions can be **disabled** for the current
transaction or session with the setting `stareau.graph.disable.trigger`:

```sql
BEGIN;
-- Disable the StarEau triggers for this transaction
SET LOCAL stareau.graph.disable.trigger = '1';

-- Import or update the data here

COMMIT;
```

The precision of the coordinates and the links between the pipes and the nodes are then **not** computed:
use the [network checks](processing.md#network-checks) algorithms afterwards.
