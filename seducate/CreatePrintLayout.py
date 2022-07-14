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
import random,string
from qgis.utils import iface
from PyQt5.QtGui import QFont

class CreatePrintLayout(QgsProcessingAlgorithm):

    extent = 'extent'

    def __init__(self):
        super().__init__()

    def name(self):
        return "Print Layout Template"

    def tr(self, text):
        return QCoreApplication.translate("Print Layout Template", text)

    def displayName(self):
        return self.tr("4. Print Layout Template")

    def group(self):
        return self.tr("Tools")

    def shortHelpString(self):
        return self.tr('''Create a print layout template for map excerices based on a desired extent. Find the resulting print layout under Project -> layouts. \n Use the Help button for more information.''')

    def helpUrl(self):
        return "https://github.com/BjornNyberg/SEDucate/wiki"

    def createInstance(self):
        return type(self)()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterExtent(self.extent,
                                                       self.tr("Extent")))

    def processAlgorithm(self, parameters, context, feedback):

        extent = parameters[self.extent]
        project = QgsProject.instance()
        manager = project.layoutManager()
        layout = QgsPrintLayout(project)
        layoutName = 'Map_'+''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

        # initializes default settings for blank print layout canvas
        layout.initializeDefaults()

        layout.setName(layoutName)
        manager.addLayout(layout)

        map = QgsLayoutItemMap(layout)
        map.setFrameEnabled(True)
        map.setRect(20, 20, 20, 20)

        # Set Map Extent
        extent = extent.split(' ')[0].split(',')
        rect = QgsRectangle(float(extent[0]),float(extent[2]),float(extent[1]),float(extent[3]))
        map.setExtent(rect)

        layout.addLayoutItem(map)

        # Move & Resize map on print layout canvas
        map.attemptMove(QgsLayoutPoint(5, 20, QgsUnitTypes.LayoutMillimeters))
        map.attemptResize(QgsLayoutSize(290, 170, QgsUnitTypes.LayoutMillimeters))

        title = QgsLayoutItemLabel(layout)
        title.setText("Paleogeographic Map")
        title.setFont(QFont("Arial", 28))
        title.adjustSizeToText()
        layout.addLayoutItem(title)
        title.attemptMove(QgsLayoutPoint(100, 4, QgsUnitTypes.LayoutMillimeters))

        scale = QgsLayoutItemScaleBar(layout)
        scale.setLinkedMap(map)
        scale.setHeight(3)
        scale.setSegmentSizeMode(1)
        scale.setMinimumBarWidth(10)
        scale.setMaximumBarWidth(70)
        scale.setUnitLabel('km')
        scale.setUnits(QgsUnitTypes.DistanceKilometers)
        scale.attemptMove(QgsLayoutPoint(10, 195, QgsUnitTypes.LayoutMillimeters))
        layout.addLayoutItem(scale)

        return {}
