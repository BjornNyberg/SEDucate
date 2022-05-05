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
import os
from qgis.utils import iface


class LoadExample(QgsProcessingAlgorithm):

    raster = 'raster'
    bmap = 'bmap'
    dirname = os.path.dirname(__file__)
    edirname = os.path.join(dirname,'examples')

    def __init__(self):
        super().__init__()

    def name(self):
        return "Load Example"

    def tr(self, text):
        return QCoreApplication.translate("Load Example", text)

    def displayName(self):
        return self.tr("Load Example")

    def shortHelpString(self):
        return self.tr('''Load a sedimentary environment map example.\n Use the Help button for more information.''')

    def helpUrl(self):
        return "https://github.com/BjornNyberg/SEDucate"

    def createInstance(self):
        return type(self)()

    def examples(self):
        paths,c = {},0
        for p in os.listdir(self.edirname):
            if p.endswith('.tif'):
                paths[c] = p
                c+=1
        return paths

    def flags(self):
        return super().flags() | QgsProcessingAlgorithm.FlagNoThreading

    def initAlgorithm(self, config=None):

        options = self.examples()
        self.addParameter(QgsProcessingParameterEnum(self.raster, self.tr("Choose an example..."), options=options.values(), optional=False))

        self.addParameter(QgsProcessingParameterBoolean(self.bmap, self.tr("Load Google Satellite Basemap"),False))


    def processAlgorithm(self, parameters, context, feedback):

        raster = parameters[self.raster]
        bmap = parameters[self.bmap]

        name = self.examples()[raster]

        QgsProject.instance().setCrs(QgsCoordinateReferenceSystem('EPSG:4326'))

        if bmap == True:
            urlWithParams = 'type=xyz&url=https://mt1.google.com/vt/lyrs%3Ds%26x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D&zmax=18&zmin=0'
            rlayer2 = QgsRasterLayer(urlWithParams, 'Google Satellite', 'wms')
            QgsProject.instance().addMapLayer(rlayer2)

        fname = os.path.join(self.edirname,name)
        rlayer = QgsRasterLayer(fname, 'example','gdal')
        QgsProject.instance().addMapLayer(rlayer)

        path = os.path.join(self.dirname,'templateRaster.qml')
        rlayer.loadNamedStyle(path)
        rlayer.triggerRepaint()

        extent = rlayer.extent()
        feedback.pushInfo(QCoreApplication.translate('Update',str(extent)))
        canvas = iface.mapCanvas()
        canvas.setExtent(extent)
        canvas.refresh()

        self.rlayer = rlayer

        return {}
