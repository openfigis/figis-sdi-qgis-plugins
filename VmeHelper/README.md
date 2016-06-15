# VmeHelper
Simple plugin intented to help maintaining the GIS data of the Vulnerable Marine Ecosystem database

## Overview

![https://raw.githubusercontent.com/openfigis/figis-sdi-qgis-plugins/master/VmeHelper/images/screenshot.jpg](https://raw.githubusercontent.com/openfigis/figis-sdi-qgis-plugins/master/VmeHelper/images/screenshot.jpg)

## Description

The plugin allows to:

* **select an input layer** (available through the QGIS workspace) or its selected features: typically a GDB layer
* **select the VME type** (VME closures, BFAs, OARAs) or inherit such VME type from an attribute.
* **select the SQL statement type** (UPDATE or INSERT)
* **set the output SQL file** where SQL statements will be written and from where they can be copied and executed to maintain the database(s)

**Notes:**

* In case a VME type is selected, the plugin considers all the layer features set as input are targeting this VME type, and consequently applies the SQL statement defined for this VME type.
* In case a VME type is selected, byt the "Inherit VME type from attribute" box is checked, the latter prevails.
* In case the "VME closures" type is selected, only the UPDATE SQL statement type is allowed.

**Target data scopes:**

* _**VME closures**_: SQL statements for WKT_GEOM field updates in VME database
* _**Bottom Fishing Areas (BFA)**_: SQL statements for multi-field updates or inserts in FIGIS_GIS database
* _**Other areas (OARA)**_: SQL statements for multi-field updates or inserts in FIGIS_GIS database
