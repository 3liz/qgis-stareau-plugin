<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="Actions" version="3.34.15-Prizren">
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
    <actionsetting isEnabledOnlyWhenEditable="0" action="from qgis.utils import plugins&#xa;&#xa;plugins['stareau'].run_action(&#xa;    'fermer_vanne',&#xa;    '[% fid %]',&#xa;    '[% @layer_id %]',&#xa;)" id="{c3173b4b-da76-4939-a966-e3ea927f3af2}" shortTitle="Fermer la vanne" type="1" icon="" name="Fermer la vanne" notificationMessage="" capture="0">
      <actionScope id="Field"/>
      <actionScope id="Feature"/>
      <actionScope id="Canvas"/>
    </actionsetting>
    <actionsetting isEnabledOnlyWhenEditable="0" action="from qgis.utils import plugins&#xa;&#xa;plugins['stareau'].run_action(&#xa;    'ouvrir_vanne',&#xa;    '[% fid %]',&#xa;    '[% @layer_id %]',&#xa;)" id="{3fe74685-34f2-4fe2-b691-7c775a77dcfb}" shortTitle="Ouvrir la vanne" type="1" icon="" name="Ouvrir la vanne" notificationMessage="" capture="0">
      <actionScope id="Field"/>
      <actionScope id="Feature"/>
      <actionScope id="Canvas"/>
    </actionsetting>
  </attributeactions>
  <layerGeometryType>0</layerGeometryType>
</qgis>
