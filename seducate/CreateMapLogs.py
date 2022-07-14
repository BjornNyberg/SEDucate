#==================================

#Author Bjorn Burr Nyberg
#University of Bergen
#Contact bjorn.nyberg@uib.no
#Copyright 2013

#==================================

'''This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.'''

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import *
import processing as st
import os, random, math
import numpy as np
from PIL import Image
from osgeo import gdal,osr
from .algorithms import plot_grainsize,plotting,add_lines
from qgis.utils import iface
from PyQt5.QtGui import QFont

class CreateMapLogs(QgsProcessingAlgorithm):

    points = 'points'
    raster = 'raster'
    raster2 = 'raster2'
    logs = 'logs'
    sections = 'sections'
    probMatrix = 'probMatrix'
    dis = 'distance'
    extent = 'extent'
    folder = 'folder'
    output = 'output'

    def __init__(self):
        super().__init__()

    def name(self):
        return "1 Create Sedimentary Logs"

    def tr(self, text):
        return QCoreApplication.translate("Create Sedimentary Logs", text)

    def displayName(self):
        return self.tr("3. Create Sedimentary Logs")

    def group(self):
        return self.tr("Tools")

    def shortHelpString(self):
        return self.tr('''Create sedimentary logs based on a sedimentary environments map. The user may select the number of random sedimentary logs to create or provide a point vector layer. \n Use the Help button for more information.''')

    def helpUrl(self):
        return "https://github.com/BjornNyberg/SEDucate"

    def createInstance(self):
        return type(self)()

    def initAlgorithm(self, config=None):

        self.addParameter(QgsProcessingParameterRasterLayer(self.raster, self.tr("Sedimentary environments map"), None, False))

        self.addParameter(QgsProcessingParameterFeatureSource(self.points, self.tr("Sedimentary log locations"),[QgsProcessing.TypeVectorPoint],optional=True))

        self.addParameter(QgsProcessingParameterNumber(self.logs,
                                                       self.tr('Number of random sedimentary logs'),
                                                       QgsProcessingParameterNumber.Integer, 10,
                                                       minValue=1))

        param1 = QgsProcessingParameterNumber(self.sections,
                                                       self.tr('Number of environments per log'),
                                                       QgsProcessingParameterNumber.Integer, 3,
                                                       minValue=1)
        param2 = QgsProcessingParameterNumber(self.probMatrix,
                                                       self.tr('Probability matrix distance (in pixels)'),
                                                       QgsProcessingParameterNumber.Integer, 25,
                                                       minValue=4)
        param3 =  QgsProcessingParameterNumber(self.dis,
                                                       self.tr('Minimum distance between logs (map units)'),
                                                       QgsProcessingParameterNumber.Double, 0,
                                                       minValue=0)
        param4 = QgsProcessingParameterExtent(self.extent, self.tr("Extent of random logs"),optional=True)
        param5 = QgsProcessingParameterRasterLayer(self.raster2, self.tr("Current direction map"), None, True)

        param1.setFlags(param1.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        param2.setFlags(param2.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        param3.setFlags(param3.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        param4.setFlags(param4.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        param5.setFlags(param5.flags() | QgsProcessingParameterDefinition.FlagAdvanced)

        self.addParameter(param1)
        self.addParameter(param2)
        self.addParameter(param3)
        self.addParameter(param4)
        self.addParameter(param5)

        self.addParameter(QgsProcessingParameterFolderDestination(
            self.folder,
            self.tr("Output Image Folder")
        ))

        self.addParameter(QgsProcessingParameterFeatureSink(
            self.output,
            self.tr("Sedimentary Logs"),
            QgsProcessing.TypeVectorPoint))

    def processAlgorithm(self, parameters, context, feedback):

        layer = self.parameterAsVectorLayer(parameters, self.points, context)
        rlayer = self.parameterAsRasterLayer(parameters, self.raster, context)
        rlayer2 = self.parameterAsRasterLayer(parameters, self.raster2, context)
        sections = parameters[self.sections]
        logs = parameters[self.logs]
        probMatrix = parameters[self.probMatrix]
        dis = parameters[self.dis]
        extent = parameters[self.extent]
        folder = parameters[self.folder]

        dirname = os.path.dirname(__file__)  # directory to scripts

        if folder == 'TEMPORARY_OUTPUT':
            folder = os.path.join(dirname,'tempfiles')

        fet = QgsFeature()
        fs = QgsFields()

        fields = [QgsField('Number',QVariant.Int),QgsField('Log',QVariant.String),QgsField('Environment',QVariant.String),QgsField('Direction',QVariant.Double)]
        for field in fields:
            fs.append(field)

        cSize = rlayer.rasterUnitsPerPixelX()*probMatrix
        rProv = rlayer.dataProvider()
        ds = gdal.Open(rProv.dataSourceUri())
        if ds == None:
            feedback.reportError(
                QCoreApplication.translate('Error', 'Error - Invalid raster file provided.'))
            return {}

        prj = ds.GetProjection()

        if not layer:
            if extent:
                extent = extent.split(' ')[0].split(',')
                rect = QgsRectangle(float(extent[0]), float(extent[2]), float(extent[1]), float(extent[3]))
            else:
                rect = rlayer
            params = {'EXTENT':rect,'POINTS_NUMBER':logs,'MIN_DISTANCE':dis,'TARGET_CRS':prj,'MAX_ATTEMPTS':50,'OUTPUT':'TEMPORARY_OUTPUT'}
            points = st.run("native:randompointsinextent", params, context=context, feedback=None)
            layer = points['OUTPUT']

        params = {'INPUT':layer,'DISTANCE':cSize,'SEGMENTS':5,'END_CAP_STYLE':0,'JOIN_STYLE':0,'MITER_LIMIT':2,'DISSOLVE':False,'OUTPUT':'TEMPORARY_OUTPUT'}
        buffer = st.run("native:buffer", params, context=context, feedback=None)
        layer2 = buffer['OUTPUT']

        params = {'INPUT_RASTER':rlayer,'RASTER_BAND':1,'INPUT_VECTOR':layer2,'COLUMN_PREFIX':'HISTO_','OUTPUT':'TEMPORARY_OUTPUT'}
        histo = st.run("native:zonalhistogram", params, context=context, feedback=None)
        layer3 = histo['OUTPUT']

        outData = {}
        band2 = ds.RasterCount==2
        if rlayer2 == True or band2 == True:
            if rlayer2 == True:
                params = {'INPUT_RASTER': rlayer2, 'RASTER_BAND': 1, 'INPUT_VECTOR': layer2, 'COLUMN_PREFIX': 'HISTO_',
                          'OUTPUT': 'TEMPORARY_OUTPUT'}
            else:
                params = {'INPUT_RASTER': rlayer, 'RASTER_BAND': 2, 'INPUT_VECTOR': layer2, 'COLUMN_PREFIX': 'HISTO_',
                          'OUTPUT': 'TEMPORARY_OUTPUT'}

            histo = st.run("native:zonalhistogram", params, context=context, feedback=None)
            layer4 = histo['OUTPUT']
            fields = layer4.fields()

            for enum, feature in enumerate(layer4.getFeatures(QgsFeatureRequest())):
                try:
                    geom = feature.geometry().centroid()

                    directions = {1: 90, 2: 135, 4: 180, 8: 225, 16: 270, 32: 315, 64: 0, 128: 45}

                    x,y,m = 0,0,False ##Method for mean current direction within given radius
                    for field in fields:
                        if 'HISTO_' in field.name():
                            name = int(field.name()[6:])
                            l = int(feature[field.name()])
                            if name in directions and l > 0:
                                angle = directions[name]
                                x += math.cos(math.radians(angle)) * l
                                y += math.sin(math.radians(angle)) * l
                                m = True
                    if m:
                        mean = np.around(math.degrees(math.atan2(y, x)), decimals=4) 
                        outData[enum] = mean%360

                except Exception as e:
                    feedback.reportError(QCoreApplication.translate('Node Error', '%s' % (e)))

        fields = layer3.fields()

        (writer, dest_id) = self.parameterAsSink(parameters, self.output, context, fs, QgsWkbTypes.Point, layer.sourceCrs())

        path = os.path.join(dirname, 'environments.csv')  # csv file containing environments
        path2 = os.path.join(dirname, 'structures.csv')  # csv file containing sedimentary structures
        environments = np.recfromcsv(path,delimiter=';',encoding='utf-8')
        structures = np.recfromcsv(path2,delimiter=';',encoding='utf-8')

        paths = []
        for enum, feature in enumerate(layer3.getFeatures(QgsFeatureRequest())):
            try:
                geom = feature.geometry().centroid()

                sum = 0
                for field in fields:
                    if 'HISTO_' in field.name():
                        sum += feature[field.name()]

                if sum == 0:
                    feedback.reportError(QCoreApplication.translate('Error','No raster data found for log #{}.'.format(int(enum))))
                    continue

                options = {} #probability matrix
                for field in fields:
                    if 'HISTO_' in field.name():
                        options[field.name()[6:]]=feature[field.name()]/sum

                val = max(options, key=options.get)
                for code in options.keys():
                    if int(val) not in environments['code']:
                        feedback.reportError(QCoreApplication.translate('Error','Rater value {} is not defined as an environment. Please check and edit the environments.csv file located in the SEDucate plugin directory.'.format(int(val))))
                        return {}
                curEnv = environments[environments['code'] == int(val)]  # Start environment and variables for the sedimentary log
                outPath = os.path.join(folder,str(enum+1)+'.jpg')
                paths.append(outPath)

                if enum in outData:
                    v = float(round(outData[enum],2))
                else:
                    v = None

                rows = [enum+1,outPath,str(curEnv[0][1]),v]

                x,y,s,p,ystart = [],[],{},{},0
                curEnv = environments[environments['code'] == int(val)]
                envs = [curEnv]
                for n in range(sections-1):
                    val = np.random.choice(list(options.keys()), 1, p=list(options.values()))[0]  # Randomlly select new environment based on probability matrix
                    curEnv = environments[environments['code'] == int(val)]
                    envs.append(curEnv)

                for curEnv in envs[::-1]:
                    ID,env, code, startvalue, minvalue, maxvalue, thickness, sorting, contact = curEnv[0]
                    if env in structures['environment']:
                        ss = structures[structures['environment'] == env]
                        ssList = dict(zip(range(0,8),list(ss[0])[2:])) #Sedimentary structures list
                    else:
                        ssList = dict(zip(range(0, 8), ['no']*8))  # No sedimentary structures list available in structures.csv file
                    rx, ry, ystart, curS, curP = plot_grainsize(startvalue, minvalue, maxvalue, thickness, ystart, sorting,contact,ssList)
                    x += rx
                    y += ry
                    s.update(curS)
                    p.update(curP)

                plotting(x, y, v, p,s, outPath,dirname)

                fet.setGeometry(geom)
                fet.setAttributes(rows)
                writer.addFeature(fet, QgsFeatureSink.FastInsert)

            except Exception as e:
                feedback.reportError(QCoreApplication.translate('Node Error', '%s' % (e)))

        for i in range(0,len(paths),5):
            images = [Image.open(x) for x in paths[i:i+5]]
            widths, heights = zip(*(i.size for i in images))
            total_width = 800*len(images)
            max_height = 1000
            new_im = Image.new('RGB', (total_width, max_height))
            outPath = os.path.join(folder, 'logs_'+str(i)+'_'+str(i+5) + '.jpg')
            x_offset = 0
            for im in images:
                new_im.paste(im, (x_offset, 0))
                x_offset += im.size[0]
            new_im.save(outPath)

        self.dest_id = dest_id

        return {self.output:dest_id}

    def postProcessAlgorithm(self, context, feedback):

        output = QgsProcessingUtils.mapLayerFromString(self.dest_id, context)
        dirname = os.path.dirname(__file__)
        path = os.path.join(dirname,'template.qml')
        output.loadNamedStyle(path)
        output.triggerRepaint()

        return {self.output:self.dest_id}
