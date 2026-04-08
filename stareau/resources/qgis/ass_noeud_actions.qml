<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.34.15-Prizren" styleCategories="Actions">
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
    <actionsetting action="from qgis.utils import plugins&#xa;&#xa;plugins['stareau'].run_action(&#xa;    'ass_downstream',&#xa;    '[% id_noeud_reseau %]',&#xa;    '[% @layer_id %]',&#xa;)" notificationMessage="" type="1" isEnabledOnlyWhenEditable="0" icon="" capture="0" shortTitle="Downstream" id="{88331b1a-50f6-458d-a43b-746f915985f4}" name="Downstream">
      <actionScope id="Canvas"/>
      <actionScope id="Feature"/>
    </actionsetting>
    <actionsetting action="from qgis.utils import plugins&#xa;&#xa;plugins['stareau'].run_action(&#xa;    'ass_upstream',&#xa;    '[% id_noeud_reseau %]',&#xa;    '[% @layer_id %]',&#xa;)" notificationMessage="" type="1" isEnabledOnlyWhenEditable="0" icon="" capture="0" shortTitle="Upstream" id="{888cf3a2-bc92-42a9-9869-7d5eb8228ab8}" name="Upstream">
      <actionScope id="Canvas"/>
      <actionScope id="Feature"/>
    </actionsetting>
  </attributeactions>
  <layerGeometryType>0</layerGeometryType>
</qgis>
