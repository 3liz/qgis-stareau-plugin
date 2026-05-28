<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.34.15-Prizren" styleCategories="Actions">
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
    <actionsetting name="Affiche les canalisations depuis le point de captage jusqu'à l'usine de traitement des eaux la plus proche" action="from qgis.utils import plugins&#xa;&#xa;plugins['stareau'].run_action(&#xa;    'aep_pgr_path_to_nearest_target',&#xa;    fid_noeud = [% fid %],&#xa;    id_layer = '[% @layer_id %]',&#xa;    target_table = 'aep_traitement',&#xa;)" notificationMessage="" capture="0" icon="" shortTitle="Chercher traitement" isEnabledOnlyWhenEditable="0" id="{824c8850-3484-4408-9408-6248dbd17655}" type="1">
      <actionScope id="Feature"/>
      <actionScope id="Canvas"/>
    </actionsetting>
  <layerGeometryType>0</layerGeometryType>
</qgis>
