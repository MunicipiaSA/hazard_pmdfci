# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Perigosidade Incêndios Florestais (PMDFCI)
                                 A QGIS plugin
 Calcula a perigosidade de incêndios florestais
                              -------------------
        begin                : 2018-04-24
        git sha              : $Format:%H$
        copyright            : (C) 2018 by BernardoSargento&NelsonMileu
        email                : _@_
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
import os, sys, processing, math
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QFileInfo
from PyQt4.QtGui import QAction, QIcon, QFileDialog, QTableWidgetItem
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry
from qgis.PyQt.QtCore import *
from qgis.core import *
import qgis.utils

# Importar para barra de mensagens
from qgis.gui import QgsMessageBar
from operator import itemgetter

# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from Perigosidade_PMDFCI_dialog import Perigosidade_PMDFCIDialog

import aboutdialog

class Perigosidade_PMDFCI:
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
			'Perigosidade_PMDFCI_{}.qm'.format(locale))

		if os.path.exists(locale_path):
			self.translator = QTranslator()
			self.translator.load(locale_path)

			if qVersion() > '4.3.3':
				QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
		
		self.dlg = Perigosidade_PMDFCIDialog()
		
		# Declare instance attributes
		self.actions = []
		self.menu = self.tr(u'&Perigosidade (PMDFCI)')
		# TODO: We are going to let the user set this up in a future iteration
		self.toolbar = self.iface.addToolBar(u'Perigosidade_PMDFCI')
		self.toolbar.setObjectName(u'Perigosidade_PMDFCI')
		
		self.dlg.toolButton_1.clicked.connect(self.AddLimite)
		
		self.dlg.lineEdit_2.clear()
		self.dlg.toolButton_2.clicked.connect(self.SelecionarOutputPath)
		
		self.dlg.toolButton_3.clicked.connect(self.AddAreasArdidas)
		self.dlg.toolButton_4.clicked.connect(self.RemoveAreasArdidas)		
		
		self.dlg.toolButton_5.clicked.connect(self.AddCLC)		

		self.dlg.toolButton_6.clicked.connect(self.AddMDT)
	# noinspection PyMethodMayBeStatic

	def tr(self, message):
		# noinspection PyTypeChecker,PyArgumentList,PyCallByClass
		return QCoreApplication.translate('Perigosidade_PMDFCI', message)

	def add_action(self, icon_path, text, callback, enabled_flag=True, add_to_menu=True, add_to_toolbar=True, status_tip=None, whats_this=None, parent=None):
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
			self.iface.addPluginToVectorMenu(self.menu,action)
			
		self.actions.append(action)

		return action

	def initGui(self):
		icon_path = ':/plugins/Perigosidade_PMDFCI//icons/pmdfci.png'
		self.add_action(icon_path,text=self.tr(u' Calcula a perigosidade de incêndios florestais'),callback=self.run,parent=self.iface.mainWindow())
		self.add_action(":/icons/about.png",text=self.tr(u' About'),callback=self.about, parent=self.iface.mainWindow())
	
	def unload(self):
		for action in self.actions:
			self.iface.removePluginVectorMenu(self.tr(u'&Perigosidade_PMDFCI'),action)
			self.iface.removeToolBarIcon(action)
		# remove the toolbar
		del self.toolbar
		
	def about(self):
		d = aboutdialog.AboutDialog()
		d.exec_()
		
# PARAMETRO 1 - "LIMITE"
	def AddLimite(self):
		try:
			layer_list = []
			for layer in self.iface.legendInterface().layers():
				if layer.type() == QgsMapLayer.VectorLayer:
					layer_list.append(layer.source())
			Path = str(QFileDialog.getOpenFileNames(self.dlg, "Selecionar um ficheiro", "/home/", "ESRI Shapefiles (*.shp *.SHP);;Todos os ficheiros (*)(*.*)")[0])
			InFileObject = processing.getObject(Path)
			layer_list.insert(0, Path)
			if InFileObject.type() == QgsMapLayer.VectorLayer:
				self.dlg.comboBox.clear()
				self.dlg.comboBox.addItems(layer_list)
		except:
			pass
	
# PARAMETRO 3 - "OUTPUT FOLDER"		
	def SelecionarOutputPath(self):
		OutputPath = QFileDialog.getExistingDirectory(self.dlg, "Guardar em","/home/")
		self.dlg.lineEdit_2.setText(OutputPath)

# PARAMETRO 4 - "AREAS ARDIDAS"
	def AddAreasArdidas(self):
		PathList = QFileDialog.getOpenFileNames(self.dlg, "Selecionar um ou mais ficheiros", "/home/", "ESRI Shapefiles (*.shp *.SHP);;Todos os ficheiros (*)(*.*)")
		if PathList is not None:
			for Path in PathList:
				LayerName = os.path.basename(Path).rsplit(".")[0]
				InFileObject = processing.getObject(Path)
				if InFileObject.type() == QgsMapLayer.VectorLayer:
					rowPosition = self.dlg.tableWidget.rowCount()
					self.dlg.tableWidget.insertRow(rowPosition)
					NrColunas = self.dlg.tableWidget.columnCount()
					NrLinhas = self.dlg.tableWidget.rowCount()           
					self.dlg.tableWidget.setRowCount(NrLinhas)
					self.dlg.tableWidget.setColumnCount(NrColunas)           
					self.dlg.tableWidget.setItem(NrLinhas -1,0,QTableWidgetItem(Path))
					self.dlg.tableWidget.setItem(NrLinhas -1,1,QTableWidgetItem(LayerName))		
	def RemoveAreasArdidas(self):
		self.dlg.tableWidget.currentRow()
		self.dlg.tableWidget.removeRow(self.dlg.tableWidget.currentRow())

# PARAMETRO 5 - "CLC"		
	def AddCLC(self):
		try:
			layer_list = []
			for layer in self.iface.legendInterface().layers():
				if layer.type() == QgsMapLayer.VectorLayer:
					layer_list.append(layer.source())
			Path = str(QFileDialog.getOpenFileNames(self.dlg, "Selecionar um ficheiro", "/home/", "ESRI Shapefiles (*.shp *.SHP);;Todos os ficheiros (*)(*.*)")[0])	
			InFileObject = processing.getObject(Path)
			layer_list.insert(0, Path)
			if InFileObject.type() == QgsMapLayer.VectorLayer:
				self.dlg.comboBox_2.clear()
				self.dlg.comboBox_2.addItems(layer_list)
		except:
			pass
			
# PARAMETRO 6 - "MDT"					
	def AddMDT(self):
		try:
			layer_list = []
			for layer in self.iface.legendInterface().layers():
				if layer.type() == QgsMapLayer.RasterLayer:
					layer_list.append(layer.source())
				
			Path = str(QFileDialog.getOpenFileNames(self.dlg, "Selecionar um ficheiro", "/home/", "TIFF / BigTIFF / GeoTIFF (*.tif);;Arc/Info Binary Grid (*.adf)")[0])
			InFileObject = processing.getObject(Path)
			layer_list.insert(0, Path)
			if InFileObject.type() == QgsMapLayer.RasterLayer:
				self.dlg.comboBox_3.clear()
				self.dlg.comboBox_3.addItems(layer_list)
		except:
			pass
			
	def run(self):
		VectorList = []
		for layer in self.iface.legendInterface().layers():
			if layer.type() == QgsMapLayer.VectorLayer:
				VectorList.append(layer.source())
		RasterList = []
		for layer in self.iface.legendInterface().layers():
			if layer.type() == QgsMapLayer.RasterLayer:
				RasterList.append(layer.source())
				
		self.dlg.comboBox.clear()
		self.dlg.comboBox.addItems(VectorList)
		self.dlg.comboBox_2.clear()
		self.dlg.comboBox_2.addItems(VectorList)
		self.dlg.comboBox_3.clear()
		self.dlg.comboBox_3.addItems(RasterList)		

		# show the dialog
		self.dlg.show()
		# Run the dialog event loop
		result = self.dlg.exec_()
		# See if OK was pressed
		if result:
			
# CARREGAR VALORES DOS PARAMETROS:
		#PARAMETRO 1 - "LIMITE"
			InputLimite = self.dlg.comboBox.currentText()
		#PARAMETRO 2 - "CELL SIZE"
			CellSize = self.dlg.spinBox.text()
		#PARAMETRO 3 - "OUTPUT FOLDER"
			OutputPath = self.dlg.lineEdit_2.text()
		#PARAMETRO 4 - "AREAS ARDIDAS"		
			InputAA = []
			InputLayerNameAA = []
			NrLinhasTabela = self.dlg.tableWidget.rowCount()
			for Linhas in range(NrLinhasTabela):
				AAPath = self.dlg.tableWidget.item(Linhas, 0).text()
				AALayerName = self.dlg.tableWidget.item(Linhas, 1).text()
				InputAA.append(AAPath)
				InputLayerNameAA.append(AALayerName)
		#PARAMETRO 5 - "CLC"			
			InputCLC = self.dlg.comboBox_2.currentText()		
		#PARAMETRO 6 - "MDT"
			InputMDT = self.dlg.comboBox_3.currentText()
				
			def CreateOutputFolder(OutputPath):
				# CRIAR PASTAS
				OutputFolder = os.path.join(OutputPath, "Incendios")
				if not os.path.exists(OutputFolder):
					os.makedirs(OutputFolder)
				else:
					for NrPastas in range(1, 10):
						sufixo = "_" + str(NrPastas)
						OutputFolder = os.path.join(OutputPath, "Incendios" + sufixo)
						if not os.path.exists(OutputFolder):
							os.makedirs(OutputFolder)
							break
				return OutputFolder			

			def CreateTempFolder(OutputFolder):
				TempFolder = os.path.join(OutputFolder, "Temp")
				os.makedirs(TempFolder)
				return TempFolder				
				
			def Extent(InputLimite):
				ext = QgsVectorLayer(InputLimite, "limite", "ogr").extent()
				xmin = ext.xMinimum()
				xmax = ext.xMaximum()
				ymin = ext.yMinimum()
				ymax = ext.yMaximum()
				Extent = "%f,%f,%f,%f" %(xmin, xmax, ymin, ymax)
				return Extent				
				
			def Probabilidade(InputAA, InputLayerNameAA, InputLimite, CellSize, TempFolder, Extent):
				# CRIAR SHAPEFILE "Limite" TEMPORARIO
				LimiteOriginal = QgsVectorLayer(InputLimite, "LimiteOriginal", "ogr")
				LimiteCopy = os.path.join(TempFolder, "LimiteCopy.shp")
				processing.runalg("qgis:dissolve",LimiteOriginal,True,None,LimiteCopy)
				Limite = QgsVectorLayer(LimiteCopy, "Limite", "ogr")
				
				# CRIAR CAMPO "Limite"
				CampoLimite = Limite.dataProvider().addAttributes([QgsField("Limite", QVariant.Int)])
				Limite.updateFields()
				Limite.startEditing()	
				[Limite.changeAttributeValue(Valores.id(), Limite.fieldNameIndex("Limite"), int(0)) for Valores in processing.features(Limite)]
				Limite.commitChanges()
				Limite.updateFields()

				# APAGAR CAMPOS DESNECESSARIOS
				for field in range(len(Limite.dataProvider().attributeIndexes())-1):
					Limite.dataProvider().deleteAttributes([0])
				Limite.updateFields()
				
				AA = []
				inc = 0
				for AreasArdidas, LayerName in zip(InputAA,InputLayerNameAA):
					# CLIP POR "Limite"
					ClipOutput = os.path.join(TempFolder, LayerName + "_Clip.shp")
					processing.runalg("qgis:clip",AreasArdidas,Limite,ClipOutput)
					LoadAA = QgsVectorLayer(ClipOutput, LayerName, "ogr")
					FeatureList = []

					for f in LoadAA.getFeatures():
						FeatureList.append(f)
					if len(FeatureList) == 0:
						LimiteGeometryList = []
						for feature in Limite.getFeatures():
							LimiteGeometryList.append(feature)
						LoadAA.startEditing()
						DataProvider = LoadAA.dataProvider()
						DataProvider.addFeatures(LimiteGeometryList)
						LoadAA.commitChanges()
					
					# CRIAR CAMPOS "ANO"
					inc +=1
					CampoName = "A_" + str(inc)
					CampoAno = LoadAA.dataProvider().addAttributes([QgsField(CampoName, QVariant.Int)])
					LoadAA.updateFields()
					CampoAnoIndex = LoadAA.fieldNameIndex(CampoName)
					LoadAA.startEditing()
					if len(FeatureList) == 0:
						[LoadAA.changeAttributeValue(Valores.id(), CampoAnoIndex, int(0)) for Valores in processing.features(LoadAA)]
					else:
						[LoadAA.changeAttributeValue(Valores.id(), CampoAnoIndex, int(1)) for Valores in processing.features(LoadAA)]
					LoadAA.commitChanges()
					LoadAA.updateFields()

					# APAGAR CAMPOS DESNECESSARIOS
					for field in range(len(LoadAA.dataProvider().attributeIndexes())-1):
						LoadAA.dataProvider().deleteAttributes([0])
					LoadAA.updateFields()
					AA.append(LoadAA)
				
				# EXECUTAR UNION
				UnionAnos = []
				for incremento in range(0, len(AA)-1):
					if incremento == 0:
						processing.runalg("saga:union",AA[0],AA[1],True, os.path.join(TempFolder, "Union_" + str(incremento)+ ".shp"))
					else:
						UnionAnos = os.path.join(TempFolder, "Union_" + str(incremento)+ ".shp")
						processing.runalg("saga:union",os.path.join(TempFolder, "Union_" + str(incremento-1)+ ".shp"),AA[incremento + 1],True, UnionAnos)
						
				OutputUnion = os.path.join(TempFolder, "Probabilidade.shp")
				processing.runalg("saga:union",UnionAnos,Limite,True, OutputUnion)
				
				### CALCULAR PROBABILIDADE
				Probabilidade = QgsVectorLayer(OutputUnion, "Probabilidade", "ogr")
				
				ExpressaoAppend = []
				for field in Probabilidade.dataProvider().attributeIndexes():
					ExpressaoAppend.append("float(Valores["+str(field) + "]) ")
				ExpressaoProb = '+ '.join(ExpressaoAppend)
				NrCampos = int(len(ExpressaoAppend)-1)
				CampoProb = Probabilidade.dataProvider().addAttributes([QgsField("PROB", QVariant.Double)])
				Probabilidade.updateFields()
				CampoProbIndex = Probabilidade.fieldNameIndex("PROB")

				Probabilidade.startEditing()	
				for Valores in processing.features(Probabilidade):
					Probabilidade.changeAttributeValue(Valores.id(), CampoProbIndex, eval(ExpressaoProb)/float(NrCampos)*100)
				Probabilidade.commitChanges()
				Probabilidade.updateFields()

				Probabilidade.startEditing()	
				for Valores in processing.features(Probabilidade):
					if Valores[CampoProbIndex] == 0:
						Probabilidade.changeAttributeValue(Valores.id(), CampoProbIndex, float(1))
				Probabilidade.commitChanges()
				Probabilidade.updateFields()
				processing.runalg("grass7:v.to.rast.attribute",Probabilidade,0,"PROB",Extent,CellSize,-1,0.0001, os.path.join(OutputFolder, "probabilidade.tif"))

			def clc2raster(InputCLC, CellSize, Extent, TempFolder):
				processing.runalg("grass7:v.to.rast.attribute",InputCLC,0,"CLC2012",Extent,CellSize,-1,0.0001, os.path.join(TempFolder, "clc.tif"))
				processing.runalg("grass7:r.reclass",os.path.join(TempFolder, "clc.tif"),os.path.join(self.plugin_dir, "txt\clc_codes.txt"),"",Extent,CellSize,os.path.join(TempFolder, "clc_reclass.tif"))

			def mdt2slope(InputMDT, Extent, CellSize, TempFolder):
				processing.runalg("grass7:r.slope",InputMDT,0,False,1,0,Extent,CellSize,os.path.join(TempFolder, "slope.tif"))
				processing.runalg("gdalogr:rastercalculator",os.path.join(TempFolder, "slope.tif"),"1",None,"1",None,"1",None,"1",None,"1",None,"1","rint(A)","",4,"",os.path.join(TempFolder, "slope_int.tif"))
				processing.runalg("grass7:r.recode",os.path.join(TempFolder, "slope_int.tif"),os.path.join(self.plugin_dir, "txt\slope_recodes.txt"),False,Extent,CellSize,os.path.join(TempFolder, "slope_reclass.tif"))

			def suscetibilidade(input_clcraster,input_sloperaster, OutputFolder):
				try:
					processing.runalg("gdalogr:rastercalculator",input_clcraster,"1",input_sloperaster,"1",None,"1",None,"1",None,"1",None,"1","A*B","",5,"",os.path.join(OutputFolder, "suscetibilidade.tif"))
				except:
					pass

			def perigosidade(input_probabilidade,input_suscetibilidade, OutputFolder):
				try:
					processing.runalg("gdalogr:rastercalculator",input_probabilidade,"1",input_suscetibilidade,"1",None,"1",None,"1",None,"1",None,"1","A*B","",5,"",os.path.join(OutputFolder, "perigosidade.tif"))
				except:
					pass				
				
		# CREATE OUTPUT FOLDERS
			OutputFolder = CreateOutputFolder(OutputPath)
			TempFolder = CreateTempFolder(OutputFolder)

		# EXTENT
			Extent = Extent(InputLimite)

		# PROBABILIDADE
			if self.dlg.groupProbabilidade.isChecked():
				Probabilidade(InputAA, InputLayerNameAA, InputLimite, CellSize, TempFolder, Extent)
			else:
				pass
				
		# SUSCETIBILIDADE
			clc2raster(InputCLC, CellSize, Extent, TempFolder)
			mdt2slope(InputMDT, Extent, CellSize, TempFolder)
			input_clcraster = os.path.join(TempFolder, "clc_reclass.tif")
			input_sloperaster = os.path.join(TempFolder, "slope_reclass.tif")
			if self.dlg.groupSuscetilidade.isChecked():
				suscetibilidade(input_clcraster,input_sloperaster, OutputFolder)
			else:
				pass
				
		# PERIGOSIDADE
			input_probabilidade = os.path.join(OutputFolder, "probabilidade.tif")
			input_suscetibilidade = os.path.join(OutputFolder, "suscetibilidade.tif")
			if self.dlg.groupProbabilidade.isChecked() and self.dlg.groupSuscetilidade.isChecked():
				perigosidade(input_probabilidade,input_suscetibilidade, OutputFolder)
			else:
				pass