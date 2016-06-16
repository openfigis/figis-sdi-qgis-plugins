# -*- coding: utf-8 -*-
"""
/***************************************************************************
 VmeHelper
                                 A QGIS plugin
 VME-db GIS helper
                              -------------------
        begin                : 2016-06-06
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Emmanuel Blondel
        email                : emmanuel.blondel@fao.org
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
#imports
from PyQt4.QtCore import Qt, QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog, QPixmap
from qgis.gui import QgsMessageBar

#other imports
import time

# Initialize Qt resources from file resources.pys
import resources
# Import the code for the dialog
from vme_helper_dialog import VmeHelperDialog
import os.path


class VmeHelper:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'VmeHelper_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
      
        # Create the dialog (after translation) and keep reference
        self.dlg = VmeHelperDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&VME-db GIS helper')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'VmeHelper')
        self.toolbar.setObjectName(u'VmeHelper')
        
        #init UI
        #-------
        self.layers = []
        
        #input layer
        self.dlg.sourceComboBox.clear()
        self.dlg.sourceComboBox.currentIndexChanged.connect(self.state_changed_layer)
        self.dlg.sourceCheckBox.setCheckState(Qt.Checked)

        #VME type
        self.dlg.attrComboBox.clear()
        self.dlg.attrComboBox.setEnabled(False)
        self.dlg.attrCheckBox.setCheckState(Qt.Unchecked)
        self.dlg.attrCheckBox.stateChanged.connect(self.state_changed_attrs)
        self.dlg.vmeType1.toggled.connect(self.state_changed_vmetype)
        self.dlg.vmeType2.toggled.connect(self.state_changed_vmetype)
        self.dlg.vmeType2.toggled.connect(self.state_changed_vmetype)
        
        #output
        self.dlg.outLineEdit.clear()
        self.dlg.outPushButton.clicked.connect(self.select_output_file)
        

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('VmeHelper', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToDatabaseMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/VmeHelper/images/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'VME-db helper'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginDatabaseMenu(
                self.tr(u'&VME-db GIS helper'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def fetch_layer_attrs(self):
        self.dlg.attrComboBox.clear()
        layerIndex = self.dlg.sourceComboBox.currentIndex()
        if layerIndex != -1:
            layer = self.layers[layerIndex]
            fields = layer.pendingFields()   
            field_names = [field.name() for field in fields]
            self.dlg.attrComboBox.addItems(field_names)

    def get_vme_type(self):
        vmeType = ""
        if self.dlg.vmeType1.isChecked():
            vmeType = "VME"
        elif self.dlg.vmeType2.isChecked():
            vmeType = "BTM_FISH"
        elif self.dlg.vmeType3.isChecked():
            vmeType = "OTHER"
        return vmeType
       
    def get_sql_type(self):
        sqlType = ""
        if self.dlg.sqlType1.isChecked():
            sqlType = "UPDATE"
        elif self.dlg.sqlType2.isChecked():
            sqlType = "INSERT"
        return sqlType
      
    def get_chunks(self, string, length):
        return (string[0+i:length+i] for i in range(0, len(string), length))
      
    def prepare_sql_statement(self, dataType, sqlType, f):
    
        sql = ""
    
        #define sql approach according to geom wkt size
        chunkSize = 4000
        geom = f.geometry()
        geomWkt = geom.exportToWkt()
        geomSize = len(geomWkt)
        chunkNote = "-- Note: Given the size of the geometry WKT ("+str(geomSize)+" characters), the SQL generated is a PL/SQL procedure based on WKT chunks.\n"
        chunks = []
        byChunks = False
        if geomSize > chunkSize:
            byChunks = True
            chunks = self.get_chunks(geomWkt, chunkSize)
            
        if dataType == "VME":
            #case of VME closures
            vmeTable = "VME.GEOREF"
            vmeFilterField = "GEOGRAPHICFEATUREID"
            
            #sql comment/statement
            if sqlType == "UPDATE":
                sql = "-- VME.GEOREF SQL UPDATE statement - "+vmeFilterField+" = '"+f['VME_AREA_T']+"'\n"
                if byChunks:
                    sql += chunkNote
                    sql += "DECLARE\n"
                    sql += "   the_clob CLOB;\n"
                    sql += "BEGIN\n"
                    sql += "   the_clob := empty_clob();\n"
                    for chunk in chunks:   
                        sql += "   the_clob := CONCAT(the_clob,'"+chunk+"');\n"    
                    sql += "   UPDATE "+vmeTable+" SET WKT_GEOM = the_clob WHERE "+vmeFilterField+" = '"+f['VME_AREA_T']+"';" + "\n\n"
                    sql += "END;"
                else:   
                    sql += "UPDATE "+vmeTable+" SET WKT_GEOM = "+geomWkt+" WHERE "+vmeFilterField+" = '"+f['VME_AREA_T']+"';" + "\n\n"
                
            elif sqlType == "INSERT":
                sql = "-- No SQL statement generated for "+vmeFilterField+" = '"+f['VME_AREA_T']+"'. "
                sql += "INSERT statements are not supported for 'VME closures' type.\n\n"
                    
        else :
            #case of BFAs and OARAs
            dbFields = ["VME_ID","LOCAL_NAME","YEAR","END_YEAR","OWNER","VME_AREA_T","GLOB_TYPE","GLOB_NAME","REG_TYPE","REG_NAME","SURFACE"]
            vmeTable = ""
            if dataType == "BTM_FISH":
                vmeTable = "FIGIS_GIS.VME_GIS_BFA"
            elif dataType == "OTHER":
                vmeTable = "FIGIS_GIS.VME_GIS_OARA"
            vmeFilterField = "VME_AREA_TIME"
            
            if vmeTable != "":
                #sql comment
                sql = "-- "+vmeTable+" SQL "+sqlType+" statement - "+vmeFilterField+" = '"+f['VME_AREA_T']+"'\n"
                thegeomField = "'"+ geomWkt +"'"
                if byChunks:
                    thegeomField = "the_clob"
                    sql += chunkNote
                    sql += "DECLARE\n"
                    sql += "   the_clob CLOB;\n"
                    sql += "BEGIN\n"
                    sql += "   the_clob := empty_clob();\n"
                    for chunk in chunks:   
                        sql += "   the_clob := CONCAT(the_clob,'"+chunk+"');\n"    
                                
                #sql statement (UPDATE or INSERT)
                if sqlType == "UPDATE":
                    sql += "UPDATE "+vmeTable+" "
                    sql += "SET"
                    sql += " THE_GEOM = SDO_GEOMETRY("+thegeomField+",4326)"
                    for dbField in dbFields:
                        if dbField == "VME_AREA_T": continue                 
                        fieldValue = f[dbField]
                        if dbField != "SURFACE" and dbField != "YEAR" and dbField != "END_YEAR":
                            fieldValue = "'"+fieldValue+"'"
                        sql += ","+dbField+" = "+str(fieldValue)
                    sql += " WHERE "+vmeFilterField+" = '"+f['VME_AREA_T']+"';" + "\n\n"
                    
                elif sqlType == "INSERT":
                    sqlFields = ", ".join(dbFields)
                    sqlFieldValues = []
                    for dbField in dbFields:
                        fieldValue = f[dbField]
                        if dbField != "SURFACE" and dbField != "YEAR" and dbField != "END_YEAR":
                           fieldValue = "'"+fieldValue+"'"
                           sqlFieldValues.append(str(fieldValue))
                    sqlFieldValues = ", ".join(sqlFieldValues)    
                    sql += "INSERT INTO "+vmeTable+" (THE_GEOM, "+sqlFields+")"
                    sql += " VALUES(SDO_GEOMETRY("+thegeomField+",4326), "+ sqlFieldValues +");\n\n"
                
                if byChunks:
                    sql += "END;"
                    
            else:
               sql = "-- No SQL statement generated for "+vmeFilterField+" = '"+f['VME_AREA_T']+"'. "
               sql += "Please check the field selected to inherit VME type is correct, and/or its values are correct and match the VME type classification ('VME','BTM_FISH','OTHER').\n\n"
     
        return sql
     
     
    def state_changed_layer(self, int):
        if self.dlg.attrCheckBox.checkState() == Qt.Checked:
            self.fetch_layer_attrs()
        
    def state_changed_vmetype(self, enabled):
        if self.dlg.vmeType1.isChecked():   
            if self.dlg.attrCheckBox.checkState() == Qt.Unchecked:
                self.dlg.sqlType2.setEnabled(False)
                self.dlg.sqlType1.setChecked(True)  
            else:
                self.dlg.sqlType2.setEnabled(True)
            return
        elif (self.dlg.vmeType2.isChecked() or self.dlg.vmeType3.isChecked()):
            self.dlg.sqlType2.setEnabled(True)
            return
    
    def state_changed_attrs(self, int):
        if self.dlg.attrCheckBox.checkState() == Qt.Checked:
            self.dlg.attrComboBox.setEnabled(True)
            self.fetch_layer_attrs()
            if self.dlg.vmeType1.isChecked():
                self.dlg.sqlType2.setEnabled(True)
        else:
            self.dlg.attrComboBox.clear()
            self.dlg.attrComboBox.setEnabled(False)
            if self.dlg.vmeType1.isChecked():
                self.dlg.sqlType2.setEnabled(False)
                self.dlg.sqlType1.setChecked(True) 
        
    def write_sql_file(self, filename, layer, vmeType, sqlType):
        output_file = open(filename, 'w')
        fields = layer.pendingFields()
        fieldnames = [field.name() for field in fields]
        targetFeatures = layer.getFeatures()
        if self.dlg.sourceCheckBox.checkState() == Qt.Checked:
            targetFeatures = layer.selectedFeatures()

        #write header for sql file    
        headerline = "-- QGIS VmeHelper plugin - https://github.com/openfigis/figis-sdi-qgis-plugins/tree/master/VmeHelper \n"
        headerline += "-- SQL automatically generated on "+time.strftime("%c")+"\n"
        headerline += "-- User parameters:\n"
        headerline += "--   * input layer source: "+layer.source()+"\n"
        headerline += "--   * input layer name: "+layer.name()+"\n"
        headerline += "--   * selected features only: "
        if self.dlg.sourceCheckBox.checkState() == Qt.Checked:
            headerline += "YES"
            headerline += " ("+str(len(targetFeatures))+" features)\n"
        else:
            headerline += "NO\n"
        headerline += "--   * VME type: "
        if self.dlg.attrCheckBox.checkState() == Qt.Checked:
            headerline += "Inherited from field '"+fieldnames[self.dlg.attrComboBox.currentIndex()]+"'\n"
        else:
            headerline += vmeType+"\n"
        headerline += "--   * SQL Statement type: "+sqlType+"\n"
        headerline += "--   * Output file name: "+filename+"\n"
        headerline += "\n\n"
        unicode_headerline = headerline.encode('utf-8')
        output_file.write(unicode_headerline)
        
        #write SQL statements
        dataType = vmeType
        for f in targetFeatures:

            """ Define dataType """
            if vmeType == "":
                attrIndex = self.dlg.attrComboBox.currentIndex()
                dataType = f.attributes()[attrIndex]
            
            """ Prepare SQL statements according to dataType """
            line = self.prepare_sql_statement(dataType, sqlType, f)
                
            """ Write line to SQL file"""
            if line != "":
                unicode_line = line.encode('utf-8')
                output_file.write(unicode_line)
        output_file.close()
        return filename
		
    def select_output_file(self):
        filename = QFileDialog.getSaveFileName(self.dlg, "Select output file ","", '*.sql')
        self.dlg.outLineEdit.setText(filename)
		
    def run(self):
        """Run method that performs all the real work"""
        self.dlg.sourceComboBox.clear()
        self.dlg.sourceCheckBox.setCheckState(Qt.Checked)
        self.layers = self.iface.legendInterface().layers()
        layer_list = []
        for layer in self.layers:
			layer_list.append(layer.name())
	
        self.dlg.sourceComboBox.addItems(layer_list)
		
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
        
            #input layer
            selectedLayerIndex = self.dlg.sourceComboBox.currentIndex()
            if selectedLayerIndex == -1:
                self.iface.messageBar().pushMessage("Error", "No input layer selected", level=QgsMessageBar.CRITICAL)
                return
            selectedLayer = self.layers[selectedLayerIndex]
            
            #input features selection
            if (self.dlg.sourceCheckBox.checkState() == Qt.Checked) and (len(selectedLayer.selectedFeatures()) == 0):
                self.iface.messageBar().pushMessage("Error", "No features selected in input layer", level=QgsMessageBar.CRITICAL)
                return
            
            #get vme type
            vmeType = self.get_vme_type()
            if vmeType == "":
                if self.dlg.attrCheckBox.checkState() == Qt.Unchecked:
                    self.iface.messageBar().pushMessage("Error", "Please select a VME type or check VME type selection by attribute", level=QgsMessageBar.CRITICAL)
                    return
            else :
                if self.dlg.attrCheckBox.checkState() == Qt.Checked:
                    vmeType = ""
            
            sqlType = self.get_sql_type()
            if sqlType == "":
                self.iface.messageBar().pushMessage("Error", "No SQL statement type selected", level=QgsMessageBar.CRITICAL)
                return
            
            #output file
            outfile = self.dlg.outLineEdit.text()
            if outfile == "":
                self.iface.messageBar().pushMessage("Error", "No output SQL file specified", level=QgsMessageBar.CRITICAL)
                return    
            out = self.write_sql_file(outfile, selectedLayer, vmeType, sqlType)
            if out:
                self.iface.messageBar().pushMessage("Info", "The SQL file '"+out+"' has been successfully created!", level=QgsMessageBar.INFO)
                return 