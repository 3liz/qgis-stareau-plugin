<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.34.15-Prizren" styleCategories="Actions">
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
    <actionsetting name="Fermer la vanne" capture="0" type="1" isEnabledOnlyWhenEditable="0" action="from qgis.utils import plugins&#xa;&#xa;plugins['stareau'].run_action(&#xa;    'fermer_vanne',&#xa;    fid_vanne = [% fid %],&#xa;    id_layer = '[% @layer_id %]',&#xa;)" icon="" id="{c3173b4b-da76-4939-a966-e3ea927f3af2}" shortTitle="Fermer la vanne" notificationMessage="">
      <actionScope id="Canvas"/>
      <actionScope id="Field"/>
      <actionScope id="Feature"/>
    </actionsetting>
    <actionsetting name="Ouvrir la vanne" capture="0" type="1" isEnabledOnlyWhenEditable="0" action="from qgis.utils import plugins&#xa;&#xa;plugins['stareau'].run_action(&#xa;    'ouvrir_vanne',&#xa;    fid_vanne = [% fid %],&#xa;    id_layer = '[% @layer_id %]',&#xa;)" icon="" id="{3fe74685-34f2-4fe2-b691-7c775a77dcfb}" shortTitle="Ouvrir la vanne" notificationMessage="">
      <actionScope id="Canvas"/>
      <actionScope id="Field"/>
      <actionScope id="Feature"/>
    </actionsetting>
    <actionsetting name="Affiche les canalisations depuis la vanne jusqu'à l'usine de traitement des eaux la plus proche" icon="" shortTitle="Chercher traitement" capture="0" notificationMessage="" type="1" id="{824c8850-3484-4408-9408-6248dbd17655}" action="from qgis.utils import plugins&#xa;&#xa;plugins['stareau'].run_action(&#xa;    'aep_pgr_path_to_nearest_target',&#xa;    fid_noeud = [% fid %],&#xa;    id_layer = '[% @layer_id %]',&#xa;    target_table = 'aep_traitement',&#xa;)" isEnabledOnlyWhenEditable="0">
      <actionScope id="Canvas"/>
      <actionScope id="Feature"/>
    </actionsetting>
    <actionsetting name="Affiche les canalisations depuis la vanne jusqu'au réservoir le plus proche" icon="" shortTitle="Chercher reservoir" capture="0" notificationMessage="" type="1" id="{7e2b2fc1-db77-4f75-b7e3-f9af25decb9b}" action="from qgis.utils import plugins&#xa;&#xa;plugins['stareau'].run_action(&#xa;    'aep_pgr_path_to_nearest_target',&#xa;    fid_noeud = [% fid %],&#xa;    id_layer = '[% @layer_id %]',&#xa;    target_table = 'aep_reservoir',&#xa;)" isEnabledOnlyWhenEditable="0">
      <actionScope id="Canvas"/>
      <actionScope id="Feature"/>
    </actionsetting>
    <actionsetting name="Affiche les canalisations depuis la vanne jusqu'au point de captage le plus proche" icon="" shortTitle="Chercher captage" capture="0" notificationMessage="" type="1" id="{c5571599-204b-4fab-83f2-021962400418}" action="from qgis.utils import plugins&#xa;&#xa;plugins['stareau'].run_action(&#xa;    'aep_pgr_path_to_nearest_target',&#xa;    fid_noeud = [% fid %],&#xa;    id_layer = '[% @layer_id %]',&#xa;    target_table = 'aep_captage',&#xa;)" isEnabledOnlyWhenEditable="0">
      <actionScope id="Canvas"/>
      <actionScope id="Feature"/>
    </actionsetting>
  </attributeactions>
  <layerGeometryType>0</layerGeometryType>
</qgis>
