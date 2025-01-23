import sqlite3
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
import sqlite3
import requests
import re
from PyQt5.QtWidgets import QListWidgetItem, QApplication, QStyle, QMessageBox

# class PeerFileExplorer(QWidget):
#     def __init__(self, peer_ip, parent=None):
#         super().__init__(parent)
#         self.peer_ip = peer_ip
#         self.initUI()

#     def initUI(self):
#         layout = QVBoxLayout(self)
#         self.setWindowTitle(f'Files from {self.peer_ip}')
#         self.file_list = QListWidget()
#         self.refresh_btn = StyledButton('Refresh', 'SP_BrowserReload')
#         self.refresh_btn.clicked.connect(self.load_files)
#         self.download_btn = StyledButton('Download', 'SP_ArrowDown')
#         self.download_btn.clicked.connect(self.download_selected_file)
        
#         layout.addWidget(self.refresh_btn)
#         layout.addWidget(self.file_list)
#         layout.addWidget(self.download_btn)
        
#         self.load_files()

#     def load_files(self):
#         self.file_list.clear()
#         try:
#             response = requests.get(f"http://{self.peer_ip}:64547/")
#             if response.status_code == 200:
#                 files = re.findall(r'href="([^"]+)"', response.text)
#                 for file in files:
#                     if file != "../":
#                         item = QListWidgetItem(file)
#                         item.setIcon(QApplication.style().standardIcon(QStyle.SP_FileIcon))
#                         self.file_list.addItem(item)
#         except Exception as e:
#             QMessageBox.warning(self, 'Error', f'Failed to retrieve file list from {self.peer_ip}: {str(e)}')

    
    
    
    
    
    
    
    
    
    
    
    
#     def download_selected_file(self):
#         selected_item = self.file_list.currentItem()
#         if not selected_item:
#             QMessageBox.warning(self, 'Error', 'Please select a file to download')
#             return

#         filename = selected_item.text()
#         save_path, _ = QFileDialog.getSaveFileName(
#             self, 'Save File As', filename  # Start with the filename as default
#         )

#         if not save_path:
#             return  # User canceled the save dialog

#         try:
#             response = requests.get(f"http://{self.peer_ip}:64547/{filename}", stream=True)
#             if response.status_code == 200:
#                 with open(save_path, 'wb') as file:
#                     total_size = int(response.headers.get('content-length', 0))
#                     block_size = 8192
#                     downloaded = 0

#                     # Create a progress dialog
#                     progress = QProgressDialog(
#                         f"Downloading {filename}...", "Cancel", 0, 100, self
#                     )
#                     progress.setWindowModality(Qt.WindowModal)

#                     # Write the file and update progress
#                     for data in response.iter_content(block_size):
#                         if progress.wasCanceled():
#                             QMessageBox.warning(self, 'Error', 'Download canceled')
#                             return

#                         file.write(data)
#                         downloaded += len(data)
#                         if total_size:
#                             progress.setValue(int(downloaded * 100 / total_size))
#                     progress.close()

#                 QMessageBox.information(
#                     self, 'Success', f'File downloaded successfully to {save_path}'
#                 )
#             else:
#                 QMessageBox.warning(
#                     self, 'Error', f'Failed to download file: {response.status_code}'
#                 )
#         except Exception as e:
#             QMessageBox.warning(self, 'Error', f'Failed to download file: {str(e)}')

class PeerFileExplorer(QWidget):
    def __init__(self, peer_ip, parent=None):
        super().__init__(parent)
        self.peer_ip = peer_ip
        self.current_path = ''  # To track navigation within directories
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f'Files from {self.peer_ip}')
        layout = QVBoxLayout(self)

        # File list area
        self.file_list = QListWidget()
        self.file_list.itemDoubleClicked.connect(self.navigate_or_download)

        # Buttons
        button_layout = QHBoxLayout()
        self.refresh_btn = StyledButton('Refresh', 'SP_BrowserReload')
        self.refresh_btn.clicked.connect(self.load_files)
        self.cancel_btn = StyledButton('Cancel', 'SP_DialogCancelButton')
        self.cancel_btn.clicked.connect(self.close)

        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.cancel_btn)

        # Add widgets to the layout
        layout.addWidget(self.file_list)
        layout.addLayout(button_layout)

        self.load_files()  # Initial load

    def load_files(self):
        """Fetch and display files and directories from the peer server."""
        self.file_list.clear()
        try:
            url = f"http://{self.peer_ip}:64547/{self.current_path}"
            response = requests.get(url)
            if response.status_code == 200:
                files = re.findall(r'href="([^"]+)"', response.text)
                for file in files:
                    if file == "../":
                        continue  # Skip parent directory link
                    item = QListWidgetItem(file)
                    if file.endswith('/'):  # Directory indicator
                        item.setIcon(QApplication.style().standardIcon(QStyle.SP_DirIcon))
                    else:
                        item.setIcon(QApplication.style().standardIcon(QStyle.SP_FileIcon))
                    self.file_list.addItem(item)
            else:
                QMessageBox.warning(self, 'Error', f'Failed to retrieve files: {response.status_code}')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Error loading files: {str(e)}')





    # def load_files(self):
    #         """Fetch and display files from a peer machine, with access control enforced."""
    #         self.file_list.clear()
    #         try:
    #             # Request files from the peer machine
    #             url = f"http://{self.peer_ip}:64547/{self.current_path}"
    #             response = requests.get(url)

    #             if response.status_code != 200:
    #                 QMessageBox.warning(self, 'Error', f'Failed to retrieve files: {response.status_code}')
    #                 return

    #             # Parse the files received from the peer machine
    #             files = re.findall(r'href="([^"]+)"', response.text)
    #             accessible_files = []  # To store files that pass the access checks
    #             print(files)
    #             # Connect to the local SQLite database
    #             conn = sqlite3.connect("path_to_your_database.db")
    #             cursor = conn.cursor()

    #             # Check access for each file
    #             for file in files:
    #                 if file == "../":
    #                     continue  # Skip parent directory link

    #                 # Get file access details
    #                 cursor.execute("""
    #                     SELECT f.access_level, aip.ip_address
    #                     FROM Files f
    #                     LEFT JOIN AllowedIPs aip ON f.id = aip.file_id
    #                     WHERE f.file_name = ?
    #                 """, (file,))
    #                 result = cursor.fetchall()
    #                 print(accessible_files)
    #                 # Determine if the file is accessible
    #                 is_accessible = False
    #                 for access_level, ip_address in result:
    #                     if access_level == 'public':
    #                         is_accessible = True
    #                         break
    #                     elif access_level == 'private' and ip_address == self.peer_ip:
    #                         is_accessible = True
    #                         break

    #                 if is_accessible:
    #                     accessible_files.append(file)

    #             conn.close()

    #             # Display accessible files in the UI
    #             for file in accessible_files:
    #                 item = QListWidgetItem(file)
    #                 if file.endswith('/'):  # Directory indicator
    #                     item.setIcon(QApplication.style().standardIcon(QStyle.SP_DirIcon))
    #                 else:
    #                     item.setIcon(QApplication.style().standardIcon(QStyle.SP_FileIcon))
    #                 self.file_list.addItem(item)

    #         except sqlite3.Error as db_error:
    #                 QMessageBox.warning(self, 'Database Error', f"Error accessing database: {str(db_error)}")
    #         except requests.RequestException as req_error:
    #                 QMessageBox.warning(self, 'Network Error', f"Error fetching files: {str(req_error)}")       
    #         except Exception as e:
    #                 QMessageBox.warning(self, 'Error', f"Error loading files: {str(e)}")




    def navigate_or_download(self, item):
            """Handle double-click: Navigate if directory, download if file."""
            name = item.text()
            if name.endswith('/'):  # Directory navigation
                self.current_path += name
                self.load_files()
            else:  # File download
                self.download_selected_file(name)

    def download_selected_file(self, filename=None):
        """Download the selected file."""
        if not filename:
            selected_item = self.file_list.currentItem()
            if not selected_item:
                QMessageBox.warning(self, 'Error', 'Please select a file to download')
                return
            filename = selected_item.text()

        save_path, _ = QFileDialog.getSaveFileName(self, 'Save File As', filename)
        if not save_path:
            return

        try:
            url = f"http://{self.peer_ip}:64547/{self.current_path}{filename}"
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(save_path, 'wb') as file:
                    total_size = int(response.headers.get('content-length', 0))
                    block_size = 8192
                    downloaded = 0
                    progress = QProgressDialog(f"Downloading {filename}...", "Cancel", 0, 100, self)
                    progress.setWindowModality(Qt.WindowModal)

                    for data in response.iter_content(block_size):
                        if progress.wasCanceled():
                            QMessageBox.warning(self, 'Error', 'Download canceled')
                            return
                        file.write(data)
                        downloaded += len(data)
                        if total_size:
                            progress.setValue(int(downloaded * 100 / total_size))
                    progress.close()

                QMessageBox.information(self, 'Success', f'File downloaded to {save_path}')
            else:
                QMessageBox.warning(self, 'Error', f'Failed to download file: {response.status_code}')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to download file: {str(e)}')
