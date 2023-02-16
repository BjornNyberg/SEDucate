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

class CreateEnvironment(QgsProcessingAlgorithm):

    nameV = 'name'
    startV = 'startValue'
    minV = 'minValue'
    maxV = 'maxValue'
    thickness = 'thickness'
    trend = 'trend'
    contact = 'contact'
    str1 = 'str1'
    str2 = 'str2'
    str3 = 'str3'
    str4 = 'str4'
    str5 = 'str5'
    str6 = 'str6'
    str7 = 'str7'
    str8 = 'str8'
    str9 = 'str9'
    str10 = 'str10'

    def __init__(self):
        super().__init__()

    def name(self):
        return "5. Create New Environment"

    def tr(self, text):
        return QCoreApplication.translate("5. Create New Environment", text)

    def displayName(self):
        return self.tr("5. Create New Environment")

    def group(self):
        return self.tr("Tools")

    def shortHelpString(self):
        return self.tr('''Define a new sedimentary log signature for an environment, facies association or facies.\n Use the Help button for more information.''')

    def helpUrl(self):
        return "https://github.com/BjornNyberg/SEDucate/wiki"

    def createInstance(self):
        return type(self)()

    def structures(self):
        dirname = os.path.dirname(__file__)  # directory to scripts
        path = os.path.join(dirname, 'structures')  # excel file containing environments
        structures = os.listdir(path)
        values = [s[:-4] for s in structures]
        return values

    def initAlgorithm(self, config=None):

        self.addParameter(QgsProcessingParameterString(self.nameV,
                                                       self.tr('Name'),
                                                       'Name'))
        self.addParameter(QgsProcessingParameterEnum(self.startV,
                                                     self.tr('Start Grainsize'),
                                                     options=[self.tr('mud'),self.tr('silt'),self.tr('v. fine'),self.tr('fine'),self.tr('medium'),self.tr('coarse'),self.tr('v. coarse'),self.tr('Granule'),self.tr('Pebble'),self.tr('Cobble')], defaultValue=0))
        self.addParameter(QgsProcessingParameterEnum(self.minV,
                                                     self.tr('Min Grainsize'),
                                                     options=[self.tr('mud'),self.tr('silt'),self.tr('v. fine'),self.tr('fine'),self.tr('medium'),self.tr('coarse'),self.tr('v. coarse'),self.tr('Granule'),self.tr('Pebble'),self.tr('Cobble')], defaultValue=0))
        self.addParameter(QgsProcessingParameterEnum(self.maxV,
                                                     self.tr('Max Grainsize'),
                                                     options=[self.tr('mud'),self.tr('silt'),self.tr('v. fine'),self.tr('fine'),self.tr('medium'),self.tr('coarse'),self.tr('v. coarse'),self.tr('Granule'),self.tr('Pebble'),self.tr('Cobble')], defaultValue=0))
        self.addParameter(QgsProcessingParameterNumber(self.thickness,
                                                       self.tr('Thickness Ratio'), QgsProcessingParameterNumber.Integer, 3,
                                                       minValue=1,maxValue=5))
        self.addParameter(QgsProcessingParameterEnum(self.trend,
                                                     self.tr('Trend'),
                                                     options=['None','Coarsening Upwards', 'Fining Upwards'], defaultValue=0))
        self.addParameter(QgsProcessingParameterEnum(self.contact,
                                                     self.tr('Contact'),
                                                     options=['Sharp','Erosional'], defaultValue=0))

        options = self.structures()

        param1 = QgsProcessingParameterEnum(self.str1,
                                            self.tr('Clay Grain Size Structures'),
                                            options=options, allowMultiple=True, optional=True)
        param2 = QgsProcessingParameterEnum(self.str2,
                                            self.tr('Silt Grain Size Structures'),
                                            options=options, allowMultiple=True, optional=True)
        param3 = QgsProcessingParameterEnum(self.str3,
                                            self.tr('V. Fine Grain Size Structures'),
                                            options=options, allowMultiple=True, optional=True)
        param4 = QgsProcessingParameterEnum(self.str4,
                                            self.tr('Fine Grains Size Structures'),
                                            options=options, allowMultiple=True, optional=True)
        param5 = QgsProcessingParameterEnum(self.str5,
                                            self.tr('Medium Grain Size Structures'),
                                            options=options, allowMultiple=True, optional=True)
        param6 = QgsProcessingParameterEnum(self.str6,
                                            self.tr('Coarse Grain Size Structures'),
                                            options=options, allowMultiple=True, optional=True)
        param7 = QgsProcessingParameterEnum(self.str7,
                                            self.tr('V. Coarse Grain Size Structures'),
                                            options=options, allowMultiple=True, optional=True)
        param8 = QgsProcessingParameterEnum(self.str8,
                                            self.tr('Granule Grain Size Structures'),
                                            options=options, allowMultiple=True, optional=True)
        param9 = QgsProcessingParameterEnum(self.str9,
                                            self.tr('Pebble Grain Size Structures'),
                                            options=options, allowMultiple=True, optional=True)
        param10 = QgsProcessingParameterEnum(self.str10,
                                            self.tr('Cobble Grain Size Structures'),
                                            options=options, allowMultiple=True, optional=True)

        param1.setFlags(param1.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        param2.setFlags(param2.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        param3.setFlags(param3.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        param4.setFlags(param4.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        param5.setFlags(param5.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        param6.setFlags(param6.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        param7.setFlags(param7.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        param8.setFlags(param8.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        param9.setFlags(param9.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        param10.setFlags(param10.flags() | QgsProcessingParameterDefinition.FlagAdvanced)

        self.addParameter(param1)
        self.addParameter(param2)
        self.addParameter(param3)
        self.addParameter(param4)
        self.addParameter(param5)
        self.addParameter(param6)
        self.addParameter(param7)
        self.addParameter(param8)
        self.addParameter(param9)
        self.addParameter(param10)

    def processAlgorithm(self, parameters, context, feedback):

        name = parameters[self.nameV]
        startV = parameters[self.startV]
        minV = parameters[self.minV]
        maxV = parameters[self.maxV]
        thickness = parameters[self.thickness]
        trend = parameters[self.trend]
        contact = parameters[self.contact]

        options = self.structures()
        sNames = dict(zip(range(len(options)),options))

        str1 = [sNames[s] for s in parameters[self.str1]]
        str2 = [sNames[s] for s in parameters[self.str2]]
        str3 = [sNames[s] for s in parameters[self.str3]]
        str4 = [sNames[s] for s in parameters[self.str4]]
        str5 = [sNames[s] for s in parameters[self.str5]]
        str6 = [sNames[s] for s in parameters[self.str6]]
        str7 = [sNames[s] for s in parameters[self.str7]]
        str8 = [sNames[s] for s in parameters[self.str8]]
        str9 = [sNames[s] for s in parameters[self.str9]]
        str10 = [sNames[s] for s in parameters[self.str10]]

        if len(str1) == 0:
            str1 = ['no']
        if len(str2) == 0:
            str2 = ['no']
        if len(str3) == 0:
            str3 = ['no']
        if len(str4) == 0:
            str4 = ['no']
        if len(str5) == 0:
            str5 = ['no']
        if len(str6) == 0:
            str6 = ['no']
        if len(str7) == 0:
            str7 = ['no']
        if len(str8) == 0:
            str8 = ['no']
        if len(str9) == 0:
            str9 = ['no']
        if len(str10) == 0:
            str10 = ['no']

        dirname = os.path.dirname(__file__)  # directory to scripts
        path = os.path.join(dirname, 'environments.csv')  # excel file containing environments
        environments = np.recfromcsv(path, delimiter=';', encoding='utf-8')

        name = name.lower().replace('_',' ')

        if name in environments['environment']:
            feedback.reportError(QCoreApplication.translate('Error','Error - Environment already exists in the database.'))
            return {}
        if minV > maxV:
            feedback.reportError(QCoreApplication.translate('Error','Error - Minimum grainsize is larger than maximum grainsize.'))
            return {}
        if startV > maxV or startV < minV:
            feedback.reportError(QCoreApplication.translate('Error','Error - Start grainsize is either lower than the minimum grainsize or larger than maximum grainsize.'))
            return {}

        code = str(environments['code'].max()+1)
        contactDict = {0:'Sharp',1:'Erosional'}
        trendDict = {0:'None',1:'CU',2:'FU'}

        data = [code,name,code,str(startV+1),str(minV+1),str(maxV+1),str(thickness),trendDict[trend],contactDict[contact]]

        with open(path, "a") as output:
            text = ';'.join(data) + '\n'
            output.write(text)

        path2 = os.path.join(dirname, 'structures.csv')  # excel file containing environments
        structures = np.recfromcsv(path2, delimiter=';', encoding='utf-8')

        data2 = [code, name, 'no',','.join(str1),','.join(str2),','.join(str3),','.join(str4),','.join(str5),','.join(str6),','.join(str7),','.join(str8),','.join(str9),','.join(str10)]

        with open(path2, "a") as output:
            text = ';'.join(data2) + '\n'
            output.write(text)

        feedback.pushInfo(QCoreApplication.translate('Contour Grid', '\nINFO - New {} environment created with a raster code of {}.\n'.format(name,code)))

        return {}
