# Changelog

## 0.6.0 - 2026-08-27

* Fix: remove hardcoded schema name in path_to_nearest_target function
* Feature: Add new functions for AEP to get nearest target with PgRouting - database version 2
* Fix: apply provided SRID
* Fix: migration database tests

## 0.5.1 - 2026-06-17

* Fix: Possible SQL injections detect by Bandit at medium severity level

## 0.5.0 - 2026-06-15

* Feature: Create the plugin structure in Database (Create schema, tables and others)
* Feature: Create database local interface (QGIS project to manage data)
* Feature: Create a new layer with the missing nodes (Undefined nodes at the beginning or end of water pipes)
* Feature: Create a new layer with the orphan nodes (Nodes that do not represent the beginning or end of a water pipe)
* Feature: Create a new layer with the duplicate nodes (Overlapping nodes on the water network)
* Feature: Fill the "graph schema" with the AEP vertices and edges from the main schema
* Feature: Create a new layer with the pipes between water intake points and the nearest treatment in order to check the pipes function.
* Feature: Create a new layer with the pipes between treatments and the nearest reservoir in order to check the pipes function.
* Feature: QGIS action to reverse the pipe geometry
* Feature: QGIS action to close the valve
* Feature: QGIS action to open the valve
* Feature: QGIS action to downstream the ASS network from the node
* Feature: QGIS action to upstream the ASS network from the node
* Feature: QGIS action to find the shortest path on AEP network from the node to the target table (water intake to treatment, treatment to water intake, treatment to tank, tank to tank, valve to tank, etc)


## 0.1.0 - 2025-07-22

### Changed

First version of the plugin
