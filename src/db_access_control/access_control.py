import os
import shutil
import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QCheckBox, QLineEdit, QDialog, QListWidget, QMessageBox
)
from datetime import datetime
# Database setup
DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files.db")  # Absolute path


def setup_database():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Create Files table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                access_level TEXT CHECK(access_level IN ('public', 'private')) NOT NULL,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create AllowedIPs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS AllowedIPs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER NOT NULL,
                ip_address TEXT NOT NULL,
                FOREIGN KEY (file_id) REFERENCES Files(id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        conn.close()
        print(f"Database setup complete. Database located at: {DB_NAME}")

    except sqlite3.Error as e:
        print(f"Error setting up the database: {e}")


class FileUploadApp(QDialog):
    def __init__(self, init_data):
        super().__init__()
        self.init_data = init_data
        
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("File Upload with Access Control")
        self.setGeometry(300, 300, 400, 300)

        # Layout for the main modal window
        layout = QVBoxLayout()

        # File label
        self.file_label = QLabel("No file selected")
        layout.addWidget(self.file_label)

        # File picker
        self.pick_file_button = QPushButton("Select File")
        self.pick_file_button.clicked.connect(self.select_file)
        layout.addWidget(self.pick_file_button)

        # Access level checkboxes
        self.access_level_label = QLabel("Set Access Level:")
        layout.addWidget(self.access_level_label)

        self.public_checkbox = QCheckBox("Public")
        self.public_checkbox.clicked.connect(self.toggle_access_level)
        layout.addWidget(self.public_checkbox)

        self.private_checkbox = QCheckBox("Private")
        self.private_checkbox.clicked.connect(self.toggle_access_level)
        layout.addWidget(self.private_checkbox)

        # IP input for private access
        self.ip_label = QLabel("Allowed IPs:")
        self.ip_label.hide()
        layout.addWidget(self.ip_label)

        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Enter IP address")
        self.ip_input.hide()
        layout.addWidget(self.ip_input)

        self.add_ip_button = QPushButton("Add IP")
        self.add_ip_button.clicked.connect(self.add_ip)
        self.add_ip_button.hide()
        layout.addWidget(self.add_ip_button)

        self.ip_list = QListWidget()
        self.ip_list.hide()
        layout.addWidget(self.ip_list)

        # Final upload button
        self.upload_button = QPushButton("Upload")
        self.upload_button.clicked.connect(self.upload_file)
        layout.addWidget(self.upload_button)

        # Display uploaded files and IPs
        self.display_label = QLabel("Uploaded Files will appear here")
        layout.addWidget(self.display_label)

        self.setLayout(layout)
        self.selected_file = None
        self.access_level = "public"  # Default access level
        self.allowed_ips = []

  
    def select_file(self):
        file_dialog = QFileDialog(self)
        # Allow multiple files to be selected
        file_paths, _ = file_dialog.getOpenFileNames(self, "Select Files")

        if file_paths:
            # Store selected files
            self.selected_file = file_paths  # List of selected file paths
            # Display the file names in the label
            file_names = ", ".join([os.path.basename(file) for file in file_paths])
            self.file_label.setText(f"Selected Files: {file_names}")


    def toggle_access_level(self):
        if self.private_checkbox.isChecked():
            self.access_level = "private"
            self.ip_label.show()
            self.ip_input.show()
            self.add_ip_button.show()
            self.ip_list.show()
            self.public_checkbox.setChecked(False)
        elif self.public_checkbox.isChecked():
            self.access_level = "public"
            self.ip_label.hide()
            self.ip_input.hide()
            self.add_ip_button.hide()
            self.ip_list.hide()
            self.private_checkbox.setChecked(False)

    def add_ip(self):
        ip_address = self.ip_input.text().strip()
        if ip_address:
            self.allowed_ips.append(ip_address)
            self.ip_list.addItem(ip_address)
            self.ip_input.clear()

    def upload_file(self):
        if not self.selected_file:
            self.file_label.setText("Please select a file before uploading!")
            return

        try:
            # Get the current timestamp and date for folder naming
            timestamp_folder_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            dest_folder = os.path.join(self.init_data['shared_folder'], timestamp_folder_name)
            print(dest_folder)

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

            # Save to database
            
            print("Upload successful!")

            self.accept()

        except sqlite3.Error as e:
            print(f"Error uploading file: {e}")
            self.file_label.setText("Error uploading file.")

  