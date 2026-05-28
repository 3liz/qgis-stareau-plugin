<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.34.15-Prizren" styleCategories="Actions">
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
    <actionsetting name="Affiche les canalisations depuis le reservoir jusqu'au réservoir le plus proche" action="from qgis.utils import plugins&#xa;&#xa;plugins['stareau'].run_action(&#xa;    'aep_pgr_path_to_nearest_target',&#xa;    fid_noeud = [% fid %],&#xa;    id_layer = '[% @layer_id %]',&#xa;    target_table = 'aep_reservoir',&#xa;)" notificationMessage="" capture="0" icon="" shortTitle="Chercher reservoir" isEnabledOnlyWhenEditable="0" id="{7e2b2fc1-db77-4f75-b7e3-f9af25decb9b}" type="1">
      <actionScope id="Feature"/>
      <actionScope id="Canvas"/>
    </actionsetting>
  </attributeactions>
  <layerGeometryType>0</layerGeometryType>
</qgis>
