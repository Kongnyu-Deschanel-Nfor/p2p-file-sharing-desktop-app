import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QCheckBox, QLineEdit, QDialog, QListWidget, QMainWindow, QWidget
)

# Database setup
DB_NAME = "files.db"

def setup_database():
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

class FileUploadApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("File Upload with Access Control")
        self.setGeometry(200, 200, 400, 300)
        
        # Layout for the main window
        main_layout = QVBoxLayout()
        self.upload_button = QPushButton("Upload File")
        self.upload_button.clicked.connect(self.open_upload_modal)
        main_layout.addWidget(self.upload_button)
        
        # Central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def open_upload_modal(self):
        modal = FileUploadModal(self)
        modal.exec_()

class FileUploadModal(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set File Access Control")
        self.setGeometry(300, 300, 400, 300)
        
        # Layouts
        self.layout = QVBoxLayout()
        
        # File label
        self.file_label = QLabel("No file selected")
        self.layout.addWidget(self.file_label)
        
        # File picker
        self.pick_file_button = QPushButton("Select File")
        self.pick_file_button.clicked.connect(self.select_file)
        self.layout.addWidget(self.pick_file_button)
        
        # Access level checkboxes
        self.access_level_label = QLabel("Set Access Level:")
        self.layout.addWidget(self.access_level_label)
        
        self.public_checkbox = QCheckBox("Public")
        self.public_checkbox.clicked.connect(self.toggle_access_level)
        self.layout.addWidget(self.public_checkbox)
        
        self.private_checkbox = QCheckBox("Private")
        self.private_checkbox.clicked.connect(self.toggle_access_level)
        self.layout.addWidget(self.private_checkbox)
        
        # IP input for private access
        self.ip_label = QLabel("Allowed IPs:")
        self.ip_label.hide()
        self.layout.addWidget(self.ip_label)
        
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Enter IP address")
        self.ip_input.hide()
        self.layout.addWidget(self.ip_input)
        
        self.add_ip_button = QPushButton("Add IP")
        self.add_ip_button.clicked.connect(self.add_ip)
        self.add_ip_button.hide()
        self.layout.addWidget(self.add_ip_button)
        
        self.ip_list = QListWidget()
        self.ip_list.hide()
        self.layout.addWidget(self.ip_list)
        
        # Final upload button
        self.upload_button = QPushButton("Upload")
        self.upload_button.clicked.connect(self.upload_file)
        self.layout.addWidget(self.upload_button)
        
        self.setLayout(self.layout)
        self.selected_file = None
        self.access_level = "public"  # Default access level
        self.allowed_ips = []

    def select_file(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "Select File")
        if file_path:
            self.selected_file = file_path
            self.file_label.setText(f"Selected File: {file_path.split('/')[-1]}")

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

        # Save to database
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Insert file metadata
        cursor.execute("""
            INSERT INTO Files (file_name, file_path, access_level)
            VALUES (?, ?, ?)
        """, (self.selected_file.split('/')[-1], self.selected_file, self.access_level))
        file_id = cursor.lastrowid
        
        # Insert allowed IPs if private
        if self.access_level == "private":
            for ip in self.allowed_ips:
                cursor.execute("""
                    INSERT INTO AllowedIPs (file_id, ip_address)
                    VALUES (?, ?)
                """, (file_id, ip))
        
        conn.commit()
        conn.close()
        
        self.close()


