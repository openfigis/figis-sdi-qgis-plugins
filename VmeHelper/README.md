# VmeHelper
Simple plugin intented to help maintaining the GIS data of the Vulnerable Marine Ecosystem database

The plugin allows to

* select a layer (available through the QGIS workspace) or its selected features: typically a GDB layer
* select the VME type (VME closures, BFAs, OARAs) or inherit such VME type from an attribute
* select the output SQL file where SQL statements will be written and from where they can be copied and executed to maintain the database(s)

Overview

![https://raw.githubusercontent.com/openfigis/figis-sdi-qgis-plugins/master/VmeHelper/images/screenshot.jpg](https://raw.githubusercontent.com/openfigis/figis-sdi-qgis-plugins/master/VmeHelper/images/screenshot.jpg)

Target data scopes:

* _**VME closures**_: SQL statements for WKT_GEOM field updates in VME database
* _**Bottom Fishing Areas (BFA)**_: SQL statements for multi-field updates in FIGIS_GIS database
* _**Other areas (OARA)**_: SQL statements for multi-field updates in FIGIS_GIS database
