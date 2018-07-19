# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Perigosidade_PMDFCI
                                 A QGIS plugin
 Perigosidade_PMDFCI
                             -------------------
        begin                : 2018-04-24
        copyright            : (C) 2018 by BernardoSargento&NelsonMileu
        email                : a
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
    """Load Perigosidade_PMDFCI class from file Perigosidade_PMDFCI.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .Perigosidade_PMDFCI import Perigosidade_PMDFCI
    return Perigosidade_PMDFCI(iface)
