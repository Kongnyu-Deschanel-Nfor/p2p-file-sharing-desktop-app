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



class NetworkScanner(QThread):
    progress = pyqtSignal(int)
    ip_found = pyqtSignal(str)
    scan_complete = pyqtSignal()

    def __init__(self, wlan_ip):
        super().__init__()
        self.wlan_ip = wlan_ip

    def run(self):
        if not self.wlan_ip:
            return
        subnet = '.'.join(self.wlan_ip.split('.')[:-1])
        total_ips = 254
        current_ip = 0
        for i in range(1, 255):
            if self.isInterruptionRequested():
                break
            target_ip = f"{subnet}.{i}"
            if target_ip != self.wlan_ip:
                current_ip += 1
                self.progress.emit(int((current_ip / total_ips) * 100))
                try:
                    if sys.platform.startswith('win'):
                        ping = subprocess.Popen(
                            ['ping', '-n', '1', '-w', '200', target_ip],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                        )
                    else:
                        ping = subprocess.Popen(
                            ['ping', '-c', '1', '-W', '1', target_ip],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                        )
                    out, _ = ping.communicate()
                    if ping.returncode == 0:
                        self.ip_found.emit(target_ip)
                except:
                    continue
        self.scan_complete.emit()
