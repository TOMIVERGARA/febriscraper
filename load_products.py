import os
import json
from PyQt5 import QtWidgets, QtGui
import subprocess
import webbrowser

from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *

class PyQtApplication(QtWidgets.QMainWindow):
    def __init__(self, starting_folder):
        super(PyQtApplication, self).__init__()

        self.setWindowTitle("Product Viewer")
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)

        # Variables to store JSON data
        self.data = {"name": "", "description": ""}

        # Create widgets
        self.number_label = QtWidgets.QLabel('product 1 of 321', self)
        self.label_name = QtWidgets.QLabel("Name:")
        self.text_name = QtWidgets.QTextEdit(self.central_widget)
        self.text_name.setFixedHeight(30)

        self.launch_button = QtWidgets.QPushButton("Launch Kiboo Search")
        self.launch_button.clicked.connect(self.launch_kiboo)

        self.copy_button_name = QtWidgets.QPushButton("Copy")
        self.copy_button_name.clicked.connect(self.copy_text_name)

        self.label_cat = QtWidgets.QLabel("Category:")
        self.text_cat = QtWidgets.QTextEdit(self.central_widget)
        self.text_cat.setFixedHeight(30)

        self.label_description = QtWidgets.QLabel("Description:")
        self.text_description = QWebEngineView(self)
        self.text_description.setFixedHeight(150)
        self.copy_button_description = QtWidgets.QPushButton("Copy")
        self.copy_button_description.clicked.connect(self.copy_text_description)

        self.button_next = QtWidgets.QPushButton("Next Product")
        self.button_next.clicked.connect(self.load_next_product)

        # Initialize with the specified starting folder
        self.current_folder = starting_folder
        self.product_list = self.get_product_list()

        if self.product_list:
            self.current_product_index = 0
            self.load_current_product()

        # Layout setup
        layout = QtWidgets.QGridLayout(self.central_widget)
        layout.addWidget(self.number_label, 0, 2)
        layout.addWidget(self.label_name, 1, 0)
        layout.addWidget(self.text_name, 1, 1)
        layout.addWidget(self.copy_button_name, 1, 2)
        layout.addWidget(self.launch_button, 2, 0, 1, 3)
        layout.addWidget(self.label_cat, 3, 0)
        layout.addWidget(self.text_cat, 3, 1)
        layout.addWidget(self.label_description, 4, 0)
        layout.addWidget(self.text_description, 4, 1)
        layout.addWidget(self.copy_button_description, 4, 2)
        layout.addWidget(self.button_next, 5, 0, 1, 3)

    def load_current_product(self):
        if self.product_list:
            current_product = self.product_list[self.current_product_index]
            text = f'product {self.current_product_index + 1} of 321'
            self.number_label.setText(text)
            self.load_product_data(current_product)

    def open_finder_window(self, path):
        subprocess.run(['open', path])

    def close_finder_windows(self):
        applescript_code = """
        tell application "Finder"
            close every window
        end tell
        """

        subprocess.run(["osascript", "-e", applescript_code])

    def load_next_product(self):
        self.close_finder_windows()
        product = self.product_list[self.current_product_index]
        new_name = os.path.join(self.current_folder, ('.' + product))
        os.rename(os.path.join(self.current_folder, product), new_name)
        if self.product_list:
            self.current_product_index += 1

            if self.current_product_index < len(self.product_list):
                self.load_current_product()
            else:
                QtWidgets.QMessageBox.information(self, "End of List", "No more products in this folder.")
                self.close()  # Close the application when reaching the end

    def load_product_data(self, product):
        json_path = os.path.join(self.current_folder, product, f"data_{product}.json")
        try:
            with open(json_path, "r") as json_file:
                product_data = json.load(json_file)
                self.data["name"] = product_data['name']
                self.data['cat'] = product_data['category']
                self.data["description"] = product_data['description']
                self.data["sku"] = product_data['entity_data']['sku']

                print(self.data)
                self.open_finder_window(os.path.join(self.current_folder, product, 'imagenes'))
        except FileNotFoundError:
            QtWidgets.QMessageBox.critical(self, "Error", f"JSON file not found at {json_path}")
            return
        except json.JSONDecodeError:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error decoding JSON file at {json_path}")
            return

        self.update_widgets()

    def update_widgets(self):
        self.text_name.setPlainText(self.data["name"])
        self.text_cat.setPlainText(self.data['cat'])
        self.text_description.setHtml(self.data["description"])

    def get_product_list(self):
        try:
            product_list = sorted(item for item in os.listdir(self.current_folder) if not item.startswith('.'))
            return product_list
        except FileNotFoundError:
            QtWidgets.QMessageBox.critical(self, "Error", f"Folder not found: {self.current_folder}")
            return None

    def copy_text_name(self):
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(self.data["name"])

    def copy_text_description(self):
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(self.data["description"])

    def launch_kiboo(self):
        webbrowser.open(f'https://app.kibooerp.com.ar/#/es-AR/workspace/products?quickFilterInput={self.data["sku"]}&pageIndex=0&pageSize=15')

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    starting_folder = "productos"  # Reemplaza con la ruta de tu carpeta inicial
    main_app = PyQtApplication(starting_folder)
    main_app.show()
    sys.exit(app.exec_())
