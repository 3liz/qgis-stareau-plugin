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
  </attributeactions>
  <layerGeometryType>0</layerGeometryType>
</qgis>
