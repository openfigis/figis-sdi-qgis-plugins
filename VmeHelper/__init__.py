# -*- coding: utf-8 -*-
"""
/***************************************************************************
 VmeHelper
                                 A QGIS plugin
 VME-db GIS helper
                             -------------------
        begin                : 2016-06-06
        copyright            : (C) 2016 by Emmanuel Blondel
        email                : emmanuel.blondel@fao.org
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load VmeHelper class from file VmeHelper.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .vme_helper import VmeHelper
    return VmeHelper(iface)
