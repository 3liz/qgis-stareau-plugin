<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.34.15-Prizren" styleCategories="Actions">
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
    <actionsetting action="from qgis.utils import plugins&#xa;&#xa;plugins['stareau'].run_action(&#xa;    'inverser_canalisation',&#xa;    '[% fid %]',&#xa;    '[% @layer_id %]',&#xa;)" notificationMessage="" type="1" isEnabledOnlyWhenEditable="0" icon="" capture="0" shortTitle="Inverser la canalisation" id="{a1de2e8e-24c9-4e10-bc3a-cb40fa5c2f94}" name="Inverser la canalisation">
      <actionScope id="Canvas"/>
      <actionScope id="Field"/>
      <actionScope id="Feature"/>
    </actionsetting>
  </attributeactions>
  <layerGeometryType>1</layerGeometryType>
</qgis>
