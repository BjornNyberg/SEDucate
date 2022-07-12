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

import os, subprocess, tempfile
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import QgsProcessingAlgorithm
from qgis.utils import iface
from PyQt5.QtWidgets import QMessageBox, QFileDialog,QInputDialog,QLineEdit


class configureSeducate(QgsProcessingAlgorithm):

    def __init__(self):
        super().__init__()

    def name(self):
        return "Configure"

    def tr(self, text):
        return QCoreApplication.translate("Configure Seducate", text)

    def displayName(self):
        return self.tr("1. Configure Seducate")

    def group(self):
        return self.tr("Configure")

    def shortHelpString(self):
        return self.tr("Seducate requires matplotlib for plotting which is not available in QGIS by default. This script will help to install matplotlib for the Windows operating system.")

    def helpUrl(self):
        return "https://github.com/BjornNyberg/NetworkGT/wiki/Installation"

    def createInstance(self):
        return type(self)()
    def initAlgorithm(self, config=None):
        pass

    def processAlgorithm(self, parameters, context, feedback):
        if os.name == 'nt':
            reply = QMessageBox.question(iface.mainWindow(), 'Install Seducate Dependencies',
                     'WARNING: Installing dependencies for Seducate may break the dependencies of other plugins and/or python modules. Do you wish to continue?', QMessageBox.Yes, QMessageBox.No)

            if reply == QMessageBox.Yes:
                try:
                    is_admin = os.getuid() == 0
                except AttributeError:
                    import ctypes
                    is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

                modules = ['matplotlib']

                for module in modules:
                    try:
                        if is_admin:
                            status = subprocess.check_call(['python3','-m', 'pip', 'install', module])
                        else:
                            status = subprocess.check_call(['python3','-m', 'pip', 'install', module,'--user'])

                        if status != 0:
                            feedback.reportError(QCoreApplication.translate('Warning','Failed to install %s - consider installing manually'%(module)))
                    except Exception:
                        feedback.reportError(QCoreApplication.translate('Warning','Failed to install %s - consider installing manually'%(module)))
                        continue

        if os.name != 'nt':
            feedback.reportError(QCoreApplication.translate('Warning','For macOS and Linux users - manually install required modules.'))

        return {}
