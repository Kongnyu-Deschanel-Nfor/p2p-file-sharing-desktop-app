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
from styles.styles import StyledButton
from components.fileexplorer import PeerFileExplorer

class PeerCard(QFrame):
    def __init__(self, ip, parent=None):
        super().__init__(parent)
        self.ip = ip
        self.initUI()

    def initUI(self):
        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 8px;
                padding: 12px;
                margin: 8px;
                border: 1px solid #E0E0E0;
            }
            QFrame:hover {
                border: 1px solid #2196F3;
            }
            QLabel {
                color: #333333;
                font-size: 14px;
            }
        """)
        layout = QVBoxLayout(self)
        try:
         hostname = socket.gethostbyaddr(self.ip)[0]
         ip_label = QLabel(f"IP: {self.ip} --> {hostname}")
        except (socket.herror, socket.gaierror):
         ip_label = QLabel(f"IP: {self.ip} (Hostname not found)")
        
        ip_label.setFont(QFont("Arial", 12, QFont.Bold))
        view_files_btn = StyledButton("View Files", "SP_FileDialogContentsView")
        view_files_btn.clicked.connect(self.open_file_explorer)
        layout.addWidget(ip_label)
        layout.addWidget(view_files_btn)
        layout.setSpacing(8)

    def open_file_explorer(self):
        explorer = PeerFileExplorer(self.ip, self.parent().parent().parent())
        explorer.show()
