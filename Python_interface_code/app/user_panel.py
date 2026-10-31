from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QMessageBox
)
from PySide6.QtCore import Signal, QSignalBlocker
import os
from app.add_user_window import AddUserWindow
from user.user_info import User
from user.history_save_load import save_user, load_user


HORIZONTAL_SPACING = 5
VERTICAL_SPACING = 5
SPACING = 20

BUTTON_HEIGHT = 40

DATA_FOLDER = "data"


class UserPanel(QFrame):
    emg_pause_requested = Signal()
    user_changed = Signal(object)

    def __init__(self, user):
        super().__init__()

        self.user = user

        self.setup_ui()
        self.refresh_user_combo()

    def setup_ui(self):
        layout = QHBoxLayout()

        # Grid layout
        grid_layout = QGridLayout()

        grid_layout.setContentsMargins(SPACING, SPACING, SPACING, SPACING)
        grid_layout.setHorizontalSpacing(HORIZONTAL_SPACING)
        grid_layout.setVerticalSpacing(VERTICAL_SPACING)

        # Column titles
        row_0_title = QLabel("")
        row_0_title.setObjectName("rowTitle")

        title = QLabel("User")
        title.setObjectName("columnTitle")

        grid_layout.addWidget(row_0_title, 0, 0)
        grid_layout.addWidget(title, 0, 1)

        # ID
        row_1_title = QLabel("ID: ")
        row_1_title.setObjectName("rowTitle")

        self.id = QLabel(str(self.user.id))

        grid_layout.addWidget(row_1_title, 1, 0)
        grid_layout.addWidget(self.id, 1, 1)

        # Name
        row_2_title = QLabel("Name: ")
        row_2_title.setObjectName("rowTitle")

        self.name = QLabel(str(self.user.name))

        grid_layout.addWidget(row_2_title, 2, 0)
        grid_layout.addWidget(self.name, 2, 1)

        # Surname
        row_3_title = QLabel("Surname: ")
        row_3_title.setObjectName("rowTitle")

        self.surname = QLabel(str(self.user.surname))

        grid_layout.addWidget(row_3_title, 3, 0)
        grid_layout.addWidget(self.surname, 3, 1)

        # Prosthesis type
        row_4_title = QLabel("Prosthesis type: ")
        row_4_title.setObjectName("rowTitle")

        self.prosthesis_type = QLabel(str(self.user.prosthesis_type))

        grid_layout.addWidget(row_4_title, 4, 0)
        grid_layout.addWidget(self.prosthesis_type, 4, 1)

        # Add user button
        add_user_button = QPushButton("Add user")
        add_user_button.setFixedHeight(BUTTON_HEIGHT)
        add_user_button.setObjectName("button")
        add_user_button.clicked.connect(self.open_add_user_dialog)

        # Delete user button
        delete_user_button = QPushButton("Delete user")
        delete_user_button.setFixedHeight(BUTTON_HEIGHT)
        delete_user_button.setObjectName("button")
        delete_user_button.clicked.connect(self.delete_user)

        # Change user combo
        self.change_user_combo = QComboBox()
        self.change_user_combo.setFixedHeight(BUTTON_HEIGHT)

        self.change_user_combo.currentIndexChanged.connect(self.change_user)

        button_layout = QVBoxLayout()
        button_layout.setContentsMargins(SPACING, SPACING, SPACING, SPACING)

        button_layout.addWidget(add_user_button)
        button_layout.addWidget(delete_user_button)
        button_layout.addWidget(self.change_user_combo)

        layout.addLayout(grid_layout, 3)
        layout.addLayout(button_layout, 1)

        self.setLayout(layout)

    def open_add_user_dialog(self):
        self.emg_pause_requested.emit()

        dialog = AddUserWindow(self)

        if dialog.exec():
            user_data = dialog.get_user_data()
            self.add_user(user_data)

    def add_user(self, user_data):
        user_id = self.generate_user_id()

        user = User(id=user_id, name=user_data["name"], surname=user_data["surname"], prosthesis_type=user_data["prosthesis_type"])
        filename = os.path.join(DATA_FOLDER, f"user{user_id}.json")

        save_user(user=user, filename=filename)

        self.set_current_user(user)
        self.refresh_user_combo()

    def delete_user(self):
        self.emg_pause_requested.emit()

        if str(self.user.id) == "000":
            return

        reply = QMessageBox.question(
            self,
            "Delete user",
            f"Are you sure you want to delete "
            f"{self.user.name} {self.user.surname}?\n\n"
            f"All saved sessions for this user will be deleted.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        filename = os.path.join(DATA_FOLDER, f"user{self.user.id}.json")

        if not os.path.exists(filename):
            return

        try:
            os.remove(filename)

        except OSError as error:
            QMessageBox.critical(
                self,
                "Delete user",
                f"Could not delete user. \n\n {error}"
            )
            return

        anonymous_filename = os.path.join(DATA_FOLDER, "user000.json")

        try:
            anonymous_user = load_user(anonymous_filename)

        except Exception as error:
            print("Could not load anonymous user", error)
            return

        self.set_current_user(anonymous_user)

        self.refresh_user_combo()

    def refresh_user_combo(self):
        blocker = QSignalBlocker(self.change_user_combo)

        self.change_user_combo.clear()

        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)

        users = []

        for filename in os.listdir(DATA_FOLDER):
            if not filename.startswith("user") or not filename.endswith(".json"):
                continue

            filepath = os.path.join(DATA_FOLDER, filename)

            try:
                user = load_user(filepath)
                users.append((user, filepath))

            except Exception as error:
                print("Could not load user: ", filepath)
                print(error)

        users.sort(key=lambda item: int(item[0].id))

        current_index = 0

        for index, (user, filepath) in enumerate(users):
            display_name = f"{user.id} | {user.name} {user.surname}".strip()

            self.change_user_combo.addItem(display_name, filepath)

            if str(user.id) == str(self.user.id):
                current_index = index

        self.change_user_combo.setCurrentIndex(current_index)

        del blocker

    def change_user(self, index):
        if index < 0:
            return

        filepath = self.change_user_combo.itemData(index)

        if not filepath:
            return

        user = load_user(filepath)

        self.set_current_user(user)

    def set_current_user(self, user):
        self.user = user

        self.update_user_display()

        self.user_changed.emit(user)

    def generate_user_id(self):
        os.makedirs(DATA_FOLDER, exist_ok=True)

        existing_ids = set()

        for filename in os.listdir(DATA_FOLDER):
            if not filename.startswith("user") or not filename.endswith(".json"):
                continue

            user_id = filename[4:-5]

            if user_id.isdigit():
                existing_ids.add(int(user_id))

        for number in range(1, 1000):
            if number not in existing_ids:
                return f"{number:03d}"

        raise RuntimeError("No available user IDs.")

    def update_user_display(self):
        self.id.setText(str(self.user.id))
        self.name.setText(str(self.user.name))
        self.surname.setText(str(self.user.surname))
        self.prosthesis_type.setText(str(self.user.prosthesis_type))