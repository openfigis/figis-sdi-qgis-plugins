# VmeHelper
Simple plugin intented to help maintaining the GIS data of the Vulnerable Marine Ecosystem database

The plugin allows to

* select a layer (available through the QGIS workspace) or its selected features: typically a GDB layer
* select the output SQL file where SQL statements will be written and from where they can be copied and executed to maintain the database

Target data scopes:

* WKT geometry for VME closures (SQL UPDATE statements)