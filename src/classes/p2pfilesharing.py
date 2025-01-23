from datetime import datetime
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
from classes.networkscanner import NetworkScanner
from components.peercard import PeerCard
from threads.fileserverthread import FileServerThread
from network_utils.network_utils import start_http_server, stop_http_server
from  db_access_control.access_control import FileUploadApp, setup_database

class P2PFileSharing(QMainWindow):
    def __init__(self,init_data):
        super().__init__()
        self.scanner_thread = None
        self.shared_folder = None
        self.download_folder = None
        self.server_thread = None
        self.init_data = init_data
        self.server_running=True
        self.initUI()
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F5F5;
            }
            QLabel {
                color: #333333;
                font-size: 14px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

    def initUI(self):
        self.setWindowTitle('P2P File Sharing')
        self.setGeometry(100, 100, 1000, 800)
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header section
        header = QWidget()
        header_layout = QHBoxLayout(header)
        status_widget = QWidget()
        status_layout = QVBoxLayout(status_widget)
        self.ip_label = QLabel(f'IP-IDENTIFIER: {self.init_data["wlan_ip"] if self.init_data["wlan_ip"] else "Not connected"}')
        self.ip_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.scan_button = StyledButton('Scan Network', 'SP_BrowserReload')
        self.scan_button.clicked.connect(self.start_network_scan)
        self.scan_button.setEnabled(bool(self.init_data['wlan_ip']))
        status_layout.addWidget(self.ip_label)
        header_layout.addWidget(status_widget)
        header_layout.addWidget(self.scan_button)
        layout.addWidget(header)

        # Folder selection section
        folder_widget = QWidget()
        folder_layout = QGridLayout(folder_widget)
        self.shared_label = QLabel(f'Server Running: http://{self.init_data["wlan_ip"]}:64547')
        self.toggle_server = StyledButton('Stop Server', 'SP_DirIcon')
        self.download_btn = StyledButton('Manage Shared files', 'SP_DirIcon')
        self.upload_btn = StyledButton('Upload File', 'SP_FileDialogStart')
        # self.toggle_server.clicked.connect(stop_http_server(lambda: self.init_data["http_server"]))
        
        self.upload_btn.clicked.connect(self.upload_file)
        
        folder_layout.addWidget(self.toggle_server, 0, 0)
        folder_layout.addWidget(self.shared_label, 0, 1)
        folder_layout.addWidget(self.download_btn, 1, 0)
        # folder_layout.addWidget(self.download_label, 1, 1)
        folder_layout.addWidget(self.upload_btn, 2, 0)
        layout.addWidget(folder_widget)

        # Peers section
        peers_container = QWidget()
        peers_layout = QVBoxLayout(peers_container)
        peers_label = QLabel('Available Peers')
        peers_label.setFont(QFont("Arial", 14, QFont.Bold))
        peers_layout.addWidget(peers_label)
        self.peers_grid = QWidget()
        self.peers_grid_layout = QGridLayout(self.peers_grid)
        scroll = QScrollArea()
        scroll.setWidget(self.peers_grid)
        scroll.setWidgetResizable(True)
        peers_layout.addWidget(scroll)
        layout.addWidget(peers_container)
    


    def add_peer(self, ip):
        row = self.peers_grid_layout.rowCount()
        col = self.peers_grid_layout.columnCount()
        if col == 0:
            col = 3  # Number of cards per row
        position = row * col + self.peers_grid_layout.count()
        self.peers_grid_layout.addWidget(PeerCard(ip, self.peers_grid), position // col, position % col)


    

    def download_file(self, ip, filename):
        if not self.download_folder:
            QMessageBox.warning(self, 'Error', 'Please select a download folder first')
            return
        try:
            response = requests.get(f"http://{ip}:8000/{filename}", stream=True)
            if response.status_code == 200:
                filepath = os.path.join(self.download_folder, filename)
                # Create progress dialog
                progress = QProgressDialog(f"Downloading {filename}...", "Cancel", 0, 100, self)
                progress.setWindowModality(Qt.WindowModal)
                # Get file size
                total_size = int(response.headers.get('content-length', 0))
                block_size = 8192
                downloaded = 0
                with open(filepath, 'wb') as f:
                    for data in response.iter_content(block_size):
                        if progress.wasCanceled():
                            return
                        downloaded += len(data)
                        f.write(data)
                        if total_size:
                            progress.setValue(int(downloaded * 100 / total_size))
                progress.close()
                QMessageBox.information(self, 'Success', f'File downloaded successfully to {filepath}')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to download file: {str(e)}')

    


    def start_network_scan(self):
        # Clear existing peers
        for i in reversed(range(self.peers_grid_layout.count())):
            self.peers_grid_layout.itemAt(i).widget().setParent(None)
        self.scan_button.setEnabled(False)
        # Create progress dialog
        self.progress_dialog = QProgressDialog("Scanning network...", "Cancel", 0, 100, self)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setWindowTitle("Network Scan")
        # Create scanner thread
        self.scanner_thread = NetworkScanner(self.init_data["wlan_ip"])
        self.scanner_thread.progress.connect(self.progress_dialog.setValue)
        self.scanner_thread.ip_found.connect(self.add_peer)
        self.scanner_thread.scan_complete.connect(self.scan_completed)
        # Connect cancel button
        self.progress_dialog.canceled.connect(self.scanner_thread.requestInterruption)
        self.scanner_thread.start()

    def scan_completed(self):
        self.scan_button.setEnabled(True)
        self.progress_dialog.close()
        peer_count = self.peers_grid_layout.count()
        if peer_count == 0:
            QMessageBox.information(self, 'Scan Complete', 'No peers found on the network')
        else:
            QMessageBox.information(self, 'Scan Complete', f'Found {peer_count} peers on the network')
    
    
    # def upload_file(self):
        
    #     # if not self.init_data['shared_folder']:
    #     #     QMessageBox.warning(self, 'Error', 'Please select a shared folder first')
    #     #     return
        
    #     file_path, _ = QFileDialog.getOpenFileName(self, 'Select File to Upload')
    #     if file_path:
    #         dest_path = os.path.join(self.init_data['shared_folder'], os.path.basename(file_path))
    #         try:
    #             shutil.copy2(file_path, dest_path)
    #             QMessageBox.information(self, 'Success', f'File uploaded to shared folder: {os.path.basename(file_path)}')
    #         except Exception as e:
    #             QMessageBox.warning(self, 'Error', f'Failed to upload file: {str(e)}')

    # def upload_file(self):
    #     if not self.selected_file:
    #         self.file_label.setText("Please select a file before uploading!")
    #         return

    #     try:
    #         # Get the current timestamp and date for folder naming
    #         timestamp_folder_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    #         dest_folder = os.path.join(self.init_data['shared_folder'], timestamp_folder_name)
    #         print(dest_folder)

    #         # Ensure the destination folder exists
    #         os.makedirs(dest_folder, exist_ok=True)

    #         try:
    #             for file_path in self.selected_file:  # Use selected files here
    #                 dest_path = os.path.join(dest_folder, os.path.basename(file_path))
    #                 shutil.copy2(file_path, dest_path)

    #             QMessageBox.information(
    #                 self, 
    #                 'Success', 
    #                 f'Files uploaded to folder: {timestamp_folder_name}'
    #             )
    #         except Exception as e:
    #             QMessageBox.warning(self, 'Error', f'Failed to upload files: {str(e)}')

    #         # Save to database
            
    #         print("Upload successful!")

    #         self.accept()

    #     except sqlite3.Error as e:
    #         print(f"Error uploading file: {e}")
    #         self.file_label.setText("Error uploading file.")

 

    def upload_file(self):
        # Prompt the user to select files
        self.selected_file, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files to Upload",
            "",
            "All Files (*)"
        )

        if not self.selected_file:
            self.file_label.setText("Please select a file before uploading!")
            return

        try:
            # Get the current timestamp and date for folder naming
            timestamp_folder_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            dest_folder = os.path.join(os.getcwd(), timestamp_folder_name)  # Store in the current working directory
            print(f"Destination folder: {dest_folder}")

            # Ensure the destination folder exists
            os.makedirs(dest_folder, exist_ok=True)

            try:
                for file_path in self.selected_file:  # Use selected files here
                    dest_path = os.path.join(dest_folder, os.path.basename(file_path))
                    shutil.copy2(file_path, dest_path)

                QMessageBox.information(
                    self, 
                    'Success', 
                    f'Files uploaded to folder: {timestamp_folder_name}'
                )
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Failed to upload files: {str(e)}')

            print("Upload successful!")

        except Exception as e:
            print(f"Error uploading file: {e}")
            self.file_label.setText("Error uploading file.")

    # def upload_files(self):
    #     setup_database()  # Ensure this is defined and functional
        
    #     # Check if QApplication instance exists
    #     app = QApplication.instance()
    #     if app is None:
    #         app = QApplication(sys.argv)

    #     # Create and display the modal dialog
    #     modal_window = FileUploadApp(self.init_data)
    #     modal_window.setModal(True)  # Make it modal
    #     modal_window.exec_()  # Show the dia # Start the event loop

        


        # file_paths, _ = QFileDialog.getOpenFileNames(self, 'Select Files to Upload')
        # if file_paths:
        #     # Get the current timestamp and date for folder naming
        #     timestamp_folder_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        #     dest_folder = os.path.join(self.init_data['shared_folder'], timestamp_folder_name)

        #     # Ensure the destination folder exists
        #     os.makedirs(dest_folder, exist_ok=True)

        #     try:
        #         for file_path in file_paths:
        #             dest_path = os.path.join(dest_folder, os.path.basename(file_path))
        #             shutil.copy2(file_path, dest_path)

        #         QMessageBox.information(
        #             self, 
        #             'Success', 
        #             f'Files uploaded to folder: {timestamp_folder_name}'
        #         )
        #     except Exception as e:
        #         QMessageBox.warning(self, 'Error', f'Failed to upload files: {str(e)}')
        # else:
        #     QMessageBox.warning(self, 'Error', 'No files selected for upload')