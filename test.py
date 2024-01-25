import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *

class HtmlViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Visor HTML")
        self.setGeometry(100, 100, 800, 600)

        # Crear el widget QWebEngineView
        self.webview = QWebEngineView(self)

        # Cargar HTML en el widget
        html_content = "<h1>Hola, este es un pedazo de HTML</h1>"
        self.webview.setHtml(html_content)

        # Establecer el widget como widget central
        self.setCentralWidget(self.webview)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HtmlViewer()
    window.show()
    sys.exit(app.exec_())