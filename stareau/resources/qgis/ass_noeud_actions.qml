<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.34.15-Prizren" styleCategories="Actions">
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
    <actionsetting name="Downstream" capture="0" type="1" isEnabledOnlyWhenEditable="0" action="from qgis.utils import plugins&#xa;&#xa;plugins['stareau'].run_action(&#xa;    'ass_downstream',&#xa;    id_noeud = '[% id_noeud_reseau %]',&#xa;    id_layer = '[% @layer_id %]',&#xa;)" icon="" id="{88331b1a-50f6-458d-a43b-746f915985f4}" shortTitle="Downstream" notificationMessage="">
      <actionScope id="Canvas"/>
      <actionScope id="Feature"/>
    </actionsetting>
    <actionsetting name="Upstream" capture="0" type="1" isEnabledOnlyWhenEditable="0" action="from qgis.utils import plugins&#xa;&#xa;plugins['stareau'].run_action(&#xa;    'ass_upstream',&#xa;    id_noeud = '[% id_noeud_reseau %]',&#xa;    id_layer = '[% @layer_id %]',&#xa;)" icon="" id="{888cf3a2-bc92-42a9-9869-7d5eb8228ab8}" shortTitle="Upstream" notificationMessage="">
      <actionScope id="Canvas"/>
      <actionScope id="Feature"/>
    </actionsetting>
  </attributeactions>
  <layerGeometryType>0</layerGeometryType>
</qgis>
