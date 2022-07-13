#==================================

#Author Bjorn Burr Nyberg
#University of Bergen
#Contact bjorn.nyberg@uib.no
#Copyright 2021

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
import numpy as np

class DeleteEnvironment(QgsProcessingAlgorithm):

    environment = 'environment'

    dirname = os.path.dirname(__file__)  # directory to scripts
    path = os.path.join(dirname, 'environments.csv')  # excel file containing environments
    environments = np.recfromcsv(path, delimiter=';', encoding='utf-8')
    values = {enum:e for enum,e in enumerate(environments['environment'])}

    def __init__(self):
        super().__init__()

    def name(self):
        return "6. Delete Environment"

    def tr(self, text):
        return QCoreApplication.translate("6. Delete Environment", text)

    def displayName(self):
        return self.tr("6. Delete Environment")

    def group(self):
        return self.tr("Tools")

    def shortHelpString(self):
        return self.tr('''Delete an existing sedimentary environment or facies log sequence.\n Use the Help button for more information.''')

    def helpUrl(self):
        return "https://github.com/BjornNyberg/SEDucate"

    def createInstance(self):
        return type(self)()

    def enviros(self):
        dirname = os.path.dirname(__file__)  # directory to scripts
        path = os.path.join(dirname, 'environments.csv')  # excel file containing environments
        environments = np.recfromcsv(path, delimiter=';', encoding='utf-8')
        values = list(environments['environment'])
        return values

    def initAlgorithm(self, config=None):

        options = self.enviros()

        self.addParameter(QgsProcessingParameterEnum(self.environment,
                                                     self.tr('Select Environment'),
                                                     options=options, defaultValue=0))

    def processAlgorithm(self, parameters, context, feedback):

        delRow = parameters[self.environment]+1

        dirname = os.path.dirname(__file__)  # directory to scripts

        path = os.path.join(dirname, 'environments.csv')
        patho = os.path.join(dirname, 'environments_copy.csv')

        os.rename(path,patho)
        with open(path,'w') as dst :
            with open(patho, "r" ) as source:
                for enum,line in enumerate(source):
                    if enum != delRow:
                        dst.write( line )
        os.remove(patho)

        path = os.path.join(dirname, 'structures.csv')
        patho = os.path.join(dirname, 'structures_copy.csv')

        os.rename(path,patho)
        with open(path,'w') as dst :
            with open(patho, "r" ) as source:
                for enum,line in enumerate(source):
                    if enum != delRow:
                        dst.write( line )
        os.remove(patho)

        return {}
