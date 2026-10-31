import sys
from PySide6.QtWidgets import QApplication
from app.main_window import MainWindow

app = QApplication(sys.argv)

with open("app/styles/main.qss", "r") as file:
    app.setStyleSheet(file.read())

window = MainWindow()
window.show()

sys.exit(app.exec())