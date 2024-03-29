# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AsBuiltMeNowDialog
                                 A QGIS plugin
 Update design features according to specified constructed features list
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2024-01-11
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Ian McHugh
        email                : imchugh00@gmail.com
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

import os
import re
import sys
import processing, os,glob

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.core import *
from qgis.utils import iface
from qgis.core import QgsFeature, QgsGeometry
from pathlib import Path
from shapely.geometry import Point
from shapely.ops import nearest_points
from qgis.core.additions.edit import edit

from qgis.PyQt.QtGui import (
    QColor,
)
from processing.core.Processing import Processing
Processing.initialize()
from processing.tools import *


# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'AsBuiltMeNow_dialog_base.ui'))


class AsBuiltMeNowDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(AsBuiltMeNowDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.pushButton.clicked.connect(self.asBuilt)
        self.comboBox.addItem('')
        self.comboBox.addItem('Distribution')
        self.comboBox.addItem('Feeder')

    def asBuilt(self):
        if QgsProject.instance().mapLayersByName('GC_layer'):
            QgsProject.instance().removeMapLayer(QgsProject.instance().mapLayersByName('GC_layer')[0])
        if QgsProject.instance().mapLayersByName('output'):
            QgsProject.instance().removeMapLayer(QgsProject.instance().mapLayersByName('output')[0])
     
        filepathe = self.mQgsFileWidget.filePath()
        gcFeatArr = []
        featArr = []
        lyrCheck = ''
        paLayer = QgsProject.instance().mapLayersByName('Postal address')[0]
        value = self.comboBox.currentText()
            
        layer = iface.addVectorLayer(filepathe,'GC_layer',"ogr")
        if not layer or not layer.isValid():
            print("Layer failed to load!")
            self.textBrowser.append('Layer failed to load!')

        
        for feature in QgsProject.instance().mapLayersByName('GC_layer')[0].getFeatures():
            gcFeatArr.append(feature)
 
#find geometry type
        if layer.wkbType() == 1 or layer.wkbType() == 1001:
            lyrCheck = 'Point'
        else:
            lyrCheck = 'Line'

        if lyrCheck == 'Point':
            for gc in gcFeatArr:
                for feat in QgsProject.instance().mapLayersByName('Chamber')[0].getFeatures():
                    if gc['ID'] == feat['ID']:
                        #lyrCheck = 'Ch'
                        featArr.append(feat['ID'])
                        g = gc.geometry()
                        with edit(QgsProject.instance().mapLayersByName('Chamber')[0]):
                            feat.setGeometry(QgsGeometry.fromPointXY(g.asPoint()))
                            if QgsProject.instance().mapLayersByName('Chamber')[0].fields().indexFromName('AsBuiltYN'):
                                try:
                                    feat['AsBuiltYN'] = 'Y'
                                except:
                                    pass
                                finally:
                                    pass
                            QgsProject.instance().mapLayersByName('Chamber')[0].updateFeature(feat)

            for gc in gcFeatArr:
                for pa in QgsProject.instance().mapLayersByName('Postal address')[0].getFeatures():
                    if gc['ID'] == pa['PrimaryDP'] or gc['ID'] == pa['SecondaryDP']:
                        with edit(QgsProject.instance().mapLayersByName('Postal address')[0]):
                            pa['AsBuiltYN'] = 'Y'
                            paLayer.updateFeature(pa)
            for gc in gcFeatArr:
                unmatched = []
                for feat in QgsProject.instance().mapLayersByName('Demand point')[0].getFeatures():
                    if gc['ID'] == feat['ID']:
                        lyrCheck = 'DP'
                        g = gc.geometry()
                        with edit(QgsProject.instance().mapLayersByName('Demand point')[0]):
                            feat.setGeometry(QgsGeometry.fromPointXY(g.asPoint()))
                            if QgsProject.instance().mapLayersByName('Demand point')[0].fields().indexFromName('AsBuiltYN'):
                                try:
                                    feat['AsBuiltYN'] = 'Y'
                                except:
                                    pass
                                finally:
                                    pass
                            if QgsProject.instance().mapLayersByName('Demand point')[0].fields().indexFromName('Color'):
                                try:
                                    #color = gc['Color']
                                    #make dict of every color field name possibility with value, then check each for population and take value of field when has a value
                                    feat['Color'] = gc['Color']
                                except:
                                    pass
                                finally:
                                    pass
                            if QgsProject.instance().mapLayersByName('Demand point')[0].fields().indexFromName('Color_1'):
                                try:
                                    #color = gc['Color']
                                    #make dict of every color field name possibility with value, then check each for population and take value of field when has a value
                                    feat['Color'] = gc['Color']
                                except:
                                    pass
                                finally:
                                    pass
                            if QgsProject.instance().mapLayersByName('Demand point')[0].fields().indexFromName('Color_2'):
                                try:
                                    #color = gc['Color']
                                    #make dict of every color field name possibility with value, then check each for population and take value of field when has a value
                                    feat['Color'] = gc['Color']
                                except:
                                    pass
                                finally:
                                    pass
                            QgsProject.instance().mapLayersByName('Demand point')[0].updateFeature(feat)
                            gcFeatArr.remove(gc)
                    
                
            if len(gcFeatArr) > 0:
                for e in gcFeatArr:
                    self.textBrowser.append('Failed to match feature with ID: ')
                    self.textBrowser.append(gc['ID'])



        if lyrCheck == 'Line' and value == 'Feeder':
            #lanes = QgsProject.instance().mapLayersByName('Trench')[0]
            lanes = layer
            lines = QgsProject.instance().mapLayersByName('Feeder')[0]

            lanePts = []

            for lane in lanes.getFeatures():
                laneVerts = [v for v in lane.geometry().vertices()]
                for laneVert in laneVerts:
                    lanePt = QgsPointXY(laneVert.x(),laneVert.y())
                    laneVertGeo = QgsGeometry().fromPointXY(lanePt)
                    lanePts.append(laneVertGeo)


            with edit(lines):
                for line in lines.getFeatures():
                    lineVerts = [v for v in line.geometry().vertices()]
                    lineVerts.pop(0)
                    lineVerts.pop(-1)
                    dict = {}
                    index = 0
                    for vert in lineVerts:
                        linePt = QgsPointXY(vert.x(),vert.y())
                        lineVertGeo = QgsGeometry().fromPointXY(linePt)
                        n = 10
                        destination = []
                        for laneVert in lanePts:
                            d = lineVertGeo.distance(laneVert)
                            if d < n:
                                n = d
                                destination = laneVert.asPoint()
                        dict[index] = destination
                        index+=1
                        
                    for vertindex, newpoint in dict.items():
                        if newpoint == []:
                            pass
                        else:
                            QgsVectorLayerEditUtils(lines).moveVertex(newpoint.x(),newpoint.y(),line.id(),vertindex)

            for line in QgsProject.instance().mapLayersByName('Feeder')[0].getFeatures():
                #for lane in QgsProject.instance().mapLayersByName('Feeder_GC')[0].getFeatures():
                for lane in lanes.getFeatures():
                    if line['ID'] == lane['ID']:
                        with edit(lines):
                            idx = 0
                            for v in line.geometry().vertices():
                                hold = []
                                for v2 in line.geometry().vertices():
                                    if v == v2:
                                        hold.append(v2)
                                    if len(hold)>1:
                                        print(idx)
                                        QgsVectorLayerEditUtils(lines).deleteVertex(line.id(),idx)
                                idx+=1

######################################################################

  
#Find crossings
######################################################################
                            
            #from qgis.core import *
            #layer_1 = 
            #layer_2 = 

            def clipping1(layer_1, layer_2):
                layer_clip = processing.run('qgis:clip',
                    {'INPUT': layer_1,
                    'OVERLAY': layer_2,
                    'OUTPUT': "memory:"}
                )["OUTPUT"]

                return QgsProject.instance().addMapLayer(layer_clip)
                #return ["OUTPUT"]
                #print(["OUTPUT"])
                
            feedlyr = QgsProject.instance().mapLayersByName('Feeder')[0]
            clayer_1 = QgsProject.instance().mapLayersByName('Workzones')[0] #originally Dist Sectors # main layer
            clayer_2 = QgsProject.instance().mapLayersByName('Parcels')[0] # secondary layer

            clipping1(clayer_1, clayer_2)

            def clipping2(layer_1, layer_2):
                layer_clip = processing.run('qgis:clip',
                    {'INPUT': layer_1,
                    'OVERLAY': layer_2,
                    'OUTPUT': "memory:"}
                )["OUTPUT"]

                return QgsProject.instance().addMapLayer(layer_clip)
                #return ["OUTPUT"]
                #print(["OUTPUT"])
                
            feedlyr = QgsProject.instance().mapLayersByName('Feeder')[0]
            clayer_1 = QgsProject.instance().mapLayersByName('Workzones')[0] # main layer
            clayer_2 = QgsProject.instance().mapLayersByName('Parcels')[0] # secondary layer

            clipping2(clayer_1, clayer_2)

            def buffering(layer1):
                layer_buffer = processing.run("native:buffer", \
                    {'INPUT': layer1,\
                    'DISTANCE':8,'SEGMENTS':20,\
                    'END_CAP_STYLE':0,'JOIN_STYLE':0,\
                    'MITER_LIMIT':1,'DISSOLVE':False,\
                    'OUTPUT': "memory:"})["OUTPUT"]
                return QgsProject.instance().addMapLayer(layer_buffer)
                #return ["OUTPUT"]

            def differencing(layer_1, layer_2):
                layer_difference = processing.run('qgis:difference',
                    {'INPUT': layer_1,
                    'OVERLAY': layer_2,
                    'OUTPUT': "memory:"}
                )["OUTPUT"]
                
                return QgsProject.instance().addMapLayer(layer_difference)
                #return ["OUTPUT"]
                
            dlayer_3 = QgsProject.instance().mapLayersByName('Workzones')[0]
            #dlayer_4 = QgsProject.instance().mapLayersByName('output')[0]
            #dlayer_4 = clipping["OUTPUT"]

            #differencing(dlayer_3,buffering(clipping(clayer_1,clayer_2)))
            #Then do differnce

            #clip overlay with feeder to find crossings
            clipping2(feedlyr,differencing(dlayer_3,buffering(clipping1(clayer_1,clayer_2))))
            outputlayers = QgsProject.instance().mapLayersByName('output')
            for outlyr in outputlayers:
                if outlyr.name() == 'output' and outlyr.wkbType() != 5:
                    QgsProject.instance().removeMapLayer(outlyr)



###############################################
                                

        if lyrCheck == 'Line' and value == 'Distribution':
            #lanes = QgsProject.instance().mapLayersByName('Trench')[0]
            lanes = layer
            lines = QgsProject.instance().mapLayersByName('Distribution')[0]

            lanePts = []

            for lane in lanes.getFeatures():
                laneVerts = [v for v in lane.geometry().vertices()]
                for laneVert in laneVerts:
                    lanePt = QgsPointXY(laneVert.x(),laneVert.y())
                    laneVertGeo = QgsGeometry().fromPointXY(lanePt)
                    lanePts.append(laneVertGeo)


            with edit(lines):
                for line in lines.getFeatures():
                    lineVerts = [v for v in line.geometry().vertices()]
                    lineVerts.pop(0)
                    lineVerts.pop(-1)
                    dict = {}
                    index = 0
                    for vert in lineVerts:
                        linePt = QgsPointXY(vert.x(),vert.y())
                        lineVertGeo = QgsGeometry().fromPointXY(linePt)
                        n = 10
                        destination = []
                        for laneVert in lanePts:
                            d = lineVertGeo.distance(laneVert)
                            if d < n:
                                n = d
                                destination = laneVert.asPoint()
                        dict[index] = destination
                        index+=1
                        
                    for vertindex, newpoint in dict.items():
                        if newpoint == []:
                            pass
                        else:
                            QgsVectorLayerEditUtils(lines).moveVertex(newpoint.x(),newpoint.y(),line.id(),vertindex)

            for line in QgsProject.instance().mapLayersByName('Distribution')[0].getFeatures():
                #for lane in QgsProject.instance().mapLayersByName('Feeder_GC')[0].getFeatures():
                for lane in lanes.getFeatures():
                    if line['ID'] == lane['ID']:
                        with edit(lines):
                            idx = 0
                            for v in line.geometry().vertices():
                                hold = []
                                for v2 in line.geometry().vertices():
                                    if v == v2:
                                        hold.append(v2)
                                    if len(hold)>1:
                                        print(idx)
                                        QgsVectorLayerEditUtils(lines).deleteVertex(line.id(),idx)
                                idx+=1

###############################################