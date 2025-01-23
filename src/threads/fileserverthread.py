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


class FileServerHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=kwargs.pop('directory'), **kwargs)




class FileServerThread(threading.Thread):
    def __init__(self, shared_folder, wlan_ip):
        super().__init__()
        self.shared_folder = shared_folder
        self.wlan_ip = wlan_ip
        self.httpd = None

    def run(self):
        handler = lambda *args, **kwargs: FileServerHandler(*args, directory=self.shared_folder, **kwargs)
        self.httpd = socketserver.TCPServer((self.wlan_ip, 64547), handler)
        self.httpd.serve_forever()

    def stop(self):
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()