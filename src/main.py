import sys
import os
import socket
import subprocess
import socketserver
import re
import threading
import shutil
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QFileDialog, QLabel, QMessageBox, QProgressDialog, 
                             QFrame, QScrollArea, QGridLayout, QStyle, QListWidget, QListWidgetItem)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QUrl, QSize
from PyQt5.QtGui import QColor, QPalette, QFont, QIcon
import requests
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QIcon

from classes.p2pfilesharing import P2PFileSharing


from classes.initialisation import InitializationWindow






if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = InitializationWindow()
    ex.show()
    sys.exit(app.exec_())


