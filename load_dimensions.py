import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QFileDialog, QCheckBox
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
import pandas as pd

class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Visualizador de Datos CSV')
        self.setGeometry(100, 100, 600, 300)

        self.currentIndex = 0
        self.filePath = None

        layout = QVBoxLayout()

        self.tableWidget = QTableWidget(self)
        layout.addWidget(self.tableWidget)

        btnLoad = QPushButton('Cargar CSV', self)
        btnLoad.clicked.connect(self.loadCSV)
        layout.addWidget(btnLoad)

        btnLaunchKiboo = QPushButton('Launch Kiboo Search', self)
        btnLaunchKiboo.clicked.connect(self.launchKibooSearch)
        layout.addWidget(btnLaunchKiboo)

        btnPrev = QPushButton('Anterior', self)
        btnPrev.clicked.connect(self.showPrevProduct)
        layout.addWidget(btnPrev)

        btnNext = QPushButton('Siguiente', self)
        btnNext.clicked.connect(self.showNextProduct)
        layout.addWidget(btnNext)


        self.setLayout(layout)

    def loadCSV(self):
        filePath, _ = QFileDialog.getOpenFileName(self, 'Cargar archivo CSV', '', 'CSV Files (*.csv)')

        if filePath:
            self.filePath = filePath
            try:
                self.df = pd.read_csv(filePath, encoding='latin-1', sep=';')
                self.addLoadedColumn()
                self.adjustInitialIndex()
                self.displayData()
            except pd.errors.ParserError as e:
                error_line = int(str(e).split('line ')[1].split(',')[0])
                error_message = f'Error en la línea {error_line}: {str(e)}'

                with open(filePath, 'r', encoding='latin-1') as file:
                    lines = file.readlines()
                    error_line_content = lines[error_line - 1].strip()

                full_error_message = f'{error_message}\nContenido de la línea: {error_line_content}'
                print(full_error_message)

    def addLoadedColumn(self):
        if 'Cargado' not in self.df.columns:
            self.df['Cargado'] = False

    def adjustInitialIndex(self):
        if hasattr(self, 'df') and 'Cargado' in self.df.columns:
            first_unloaded_index = self.df.index[self.df['Cargado'] == False].min()
            if first_unloaded_index is not None:
                self.currentIndex = first_unloaded_index

    def displayData(self):
        if not hasattr(self, 'df') or self.df.empty or 'Nombre' not in self.df.columns:
            return

        self.tableWidget.clear()

        self.tableWidget.setRowCount(1)
        self.tableWidget.setColumnCount(5)  # Añade una columna adicional para la checkbox

        # Establece los encabezados de columna
        headers = ['Nombre', 'Peso (kg)', 'Alto (cm)', 'Ancho (cm)', 'Cargado']
        self.tableWidget.setHorizontalHeaderLabels(headers)

        for i, (index, row) in enumerate(self.df.iloc[self.currentIndex:self.currentIndex+1].iterrows()):
            self.tableWidget.setItem(0, 0, QTableWidgetItem(str(row['Nombre'])))
            self.tableWidget.setItem(0, 1, QTableWidgetItem(str(row['Peso (kg)'])))
            self.tableWidget.setItem(0, 2, QTableWidgetItem(str(row['Alto (cm)'])))
            self.tableWidget.setItem(0, 3, QTableWidgetItem(str(row['Ancho (cm)'])))

            # Añade un checkbox en la columna 4 para la columna 'Cargado'
            checkbox = QCheckBox()
            checkbox.setChecked(row['Cargado'])
            checkbox.stateChanged.connect(lambda state, index=index: self.checkboxStateChanged(state, index))
            self.tableWidget.setCellWidget(0, 4, checkbox)

    def checkboxStateChanged(self, state, index):
        # Actualiza el valor en el DataFrame cuando el estado de la checkbox cambia
        self.df.at[index, 'Cargado'] = state == Qt.Checked
        self.saveCSV()

    def saveCSV(self):
        if hasattr(self, 'df') and self.filePath:
            self.df.to_csv(self.filePath, index=False, encoding='latin-1', sep=';')

    def showPrevProduct(self):
        if hasattr(self, 'df') and not self.df.empty:
            self.currentIndex = (self.currentIndex - 1) % len(self.df)
            self.displayData()

    def showNextProduct(self):
        if hasattr(self, 'df') and not self.df.empty:
            self.df.at[self.currentIndex, 'Cargado'] = True
            self.currentIndex = (self.currentIndex + 1) % len(self.df)
            self.saveCSV()  # Guarda antes de mostrar el siguiente producto
            self.displayData()

    def launchKibooSearch(self):
        if hasattr(self, 'df') and not self.df.empty:
            sku = self.df.at[self.currentIndex, 'SKU']
            kiboo_url = f'https://app.kibooerp.com.ar/#/es-AR/workspace/products?quickFilterInput={sku}&pageIndex=0&pageSize=15'
            QDesktopServices.openUrl(QUrl(kiboo_url))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    ex.show()
    sys.exit(app.exec_())
