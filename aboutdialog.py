# -*- coding: utf-8 -*-

#******************************************************************************
#
# MergeShapes
# ---------------------------------------------------------
# Merge multiple shapefiles to a single shapefile
#
# Copyright (C) 2010-2013 Alexander Bruy (alexander.bruy@gmail.com)
#
# This source is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# A copy of the GNU General Public License is available on the World Wide Web
# at <http://www.gnu.org/copyleft/gpl.html>. You can also obtain it by writing
# to the Free Software Foundation, Inc., 59 Temple Place - Suite 330, Boston,
# MA 02111-1307, USA.
#
#******************************************************************************


import os
import ConfigParser

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui.ui_aboutdialogbase import Ui_Dialog

import resources


class AboutDialog(QDialog, Ui_Dialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)

        self.btnHelp = self.buttonBox.button(QDialogButtonBox.Help)

        cfg = ConfigParser.SafeConfigParser()
        cfg.read(os.path.join(os.path.dirname(__file__), "metadata.txt"))
        version = cfg.get("general", "version")

        self.lblLogo.setPixmap(QPixmap(":/plugins/Perigosidade_PMDFCI//icons/pmdfci.png"))
        self.lblVersion.setText(self.tr("Version: %s") % (version))
        doc = QTextDocument()
        doc.setHtml(self.getAboutText())
        self.textBrowser.setDocument(doc)
        self.textBrowser.setOpenExternalLinks(True)

        self.buttonBox.helpRequested.connect(self.openHelp)

    def reject(self):
        QDialog.reject(self)

    def openHelp(self):
        overrideLocale = QSettings().value("locale/overrideFlag", False)
        if not overrideLocale:
            localeFullName = QLocale.system().name()
        else:
            localeFullName = QSettings().value("locale/userLocale", "")

        localeShortName = localeFullName[0:2]
        if localeShortName in ["ru", "uk"]:
            QDesktopServices.openUrl(QUrl("http://hub.qgis.org/projects/mergeshapes/wiki"))
        else:
            QDesktopServices.openUrl(QUrl("http://hub.qgis.org/projects/mergeshapes/wiki"))

    def getAboutText(self):
        return self.tr("""<p>Calcula a perigosidade de incendio florestal segundo a metodologia  constante no Guia Tecnico do Plano Municipal de Defesa da Floresta contra Incendios (PMDFCI) publicado pelo Instituto da Conservacao da Natureza e das Florestas (ICNF).<br>
		A metodologia consiste no calculo da probabilidade e da suscetibilidade de ocorrencia de incendios florestais, com base no historico de areas ardidas, ocupacao do solo e declives. O mapa de perigosidade produzido, resulta da combinacao dos mapas de probabilidade e de suscetibilidade. <br></p>
		
		<p><strong>INPUTS</strong>:<br></p>
		<strong> - Limite:</strong>  Limite da area de estudo (shapefile)<br>
		<strong> - Tamanho do pixel:</strong>  Unidade de terreno em metros<br>
		<strong> - Pasta de destino:</strong>  Destino dos ouputs do modelo<br>
		<strong> - Areas Ardidas:</strong>  Poligonos das areas ardidas, separadas por ano (shapefile)<br>
		<strong> - Ocupacao do Solo:</strong> Poligonos de ocupacao do solo  - Corine Land Cover (shapefile)<br>
		<strong> - Modelo Digital do Terreno:</strong> Modelo digital do terreno (raster)<br>
		
		<p>
		<a href="https://www.google.pt/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&ved=0ahUKEwin0aao4L7bAhVH8RQKHQINC9QQFggoMAA&url=http%3A%2F%2Fwww2.icnf.pt%2Fportal%2Fflorestas%2Fdfci%2FResource%2Fdoc%2Fguia-tec-pmdfci-abril12&usg=AOvVaw2O-D-JrUKVuJ7ljsvi4AtF"><strong> Download Guia Tecnico PMDFCI </strong></a></p>

		<p><strong>Desenvolvimento</strong>: Bernardo Sargento & Nelson Mileu</p>
		<p><strong>Homepage</strong>: <a href="https://www.municipia.pt">www.municipia.pt</a></p>
		<p>Please report bugs at nmileu@municipia.pt</p>""")
