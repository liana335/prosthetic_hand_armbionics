from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QWidget,
    QLabel
)
from PySide6.QtCore import (
    QPropertyAnimation,
    QEasingCurve,
    QPoint
)


WINDOW_WIDTH = 500
WINDOW_HEIGHT = 300

SPACING = 50

FIELD_HEIGHT = 40
BUTTON_HEIGHT = 40

SHAKE_ANIMATION_DURATION = 300


class AddUserWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Add user")
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setObjectName("addUserWindow")
        self.setModal(True)

        (self.name_container, self.name_input, self.name_error) = self.create_field_with_error("Name")
        (self.surname_container, self.surname_input, self.surname_error) = self.create_field_with_error("Surname")
        (self.prosthesis_container, self.prosthesis_input, self.prosthesis_error) = self.create_field_with_error("Prosthesis type")

        form_layout = QFormLayout()
        form_layout.addRow(self.name_container)
        form_layout.addRow(self.surname_container)
        form_layout.addRow(self.prosthesis_container)

        self.add_button = QPushButton("Add")
        self.cancel_button = QPushButton("Cancel")

        self.add_button.clicked.connect(self.add_user)
        self.cancel_button.clicked.connect(self.reject)

        self.add_button.setFixedHeight(BUTTON_HEIGHT)
        self.cancel_button.setFixedHeight(BUTTON_HEIGHT)

        self.add_button.setObjectName("userButton")
        self.cancel_button.setObjectName("userButton")

        button_layout = QHBoxLayout()

        button_layout.addStretch()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.cancel_button)

        layout = QVBoxLayout()
        layout.setContentsMargins(SPACING, SPACING, SPACING, SPACING)

        layout.addLayout(form_layout)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def create_field_with_error(self, placeholder):
        container = QWidget()

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setFixedHeight(FIELD_HEIGHT)

        error_label = QLabel()
        error_label.setStyleSheet("color: red;")
        error_label.hide()

        layout.addWidget(input_field)
        layout.addWidget(error_label)

        return container, input_field, error_label

    def set_field_error(self, error_label, message):
        if message:
            error_label.setText(message)
            error_label.show()
        else:
            error_label.clear()
            error_label.hide()

    def shake_field_error(self, requirement):
        animation = QPropertyAnimation(requirement, b"pos", self)

        animation.setDuration(SHAKE_ANIMATION_DURATION)

        start_position = requirement.pos()

        animation.setKeyValueAt( 0, start_position ) 
        animation.setKeyValueAt( 0.2, start_position + QPoint(-6, 0) ) 
        animation.setKeyValueAt( 0.4, start_position + QPoint(6, 0) ) 
        animation.setKeyValueAt( 0.6, start_position + QPoint(-5, 0) ) 
        animation.setKeyValueAt( 0.8, start_position + QPoint(5, 0) ) 
        animation.setKeyValueAt( 1, start_position )

        animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def add_user(self):
        name = self.name_input.text().strip()
        surname = self.surname_input.text().strip()
        prosthesis_type = self.prosthesis_input.text().strip()

        valid = True

        # Name
        if not name:
            self.set_field_error(self.name_error, "Please enter your name.")
            self.shake_field_error(self.name_error)
            valid = False

        elif not name.isalpha():
           self.set_field_error(self.name_error, "Name should contain letters only.")
           self.shake_field_error(self.name_error)
           valid = False

        else:
            self.set_field_error(self.name_error, "")

        # Surname
        if not surname:
            self.set_field_error(self.surname_error, "Please enter your surname.")
            self.shake_field_error(self.surname_error)
            valid = False
        elif not surname.isalpha():
            self.set_field_error(self.surname_error, "Surname should contain letters only.")
            self.shake_field_error(self.surname_error)
            valid = False
        else:
            self.set_field_error(self.surname_error, "")

        # Prosthesis type
        if not prosthesis_type:
            self.set_field_error(self.prosthesis_error, "Please enter prosthesis type.")
            self.shake_field_error(self.prosthesis_error)
            valid = False

        if not valid:
            return
        
        self.accept()

    def get_user_data(self):
        return {
            "name": self.name_input.text().strip(),
            "surname": self.surname_input.text().strip(),
            "prosthesis_type": self.prosthesis_input.text().strip(),
        }