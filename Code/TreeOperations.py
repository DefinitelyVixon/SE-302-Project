import json
import os
from datetime import datetime
import sys
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QMenu, QWidget, QPushButton, QApplication, \
    QMainWindow, QLabel, QGridLayout, QDateEdit, \
    QLineEdit, QMessageBox, QTreeWidgetItem, QAbstractItemView, QTreeWidget, \
    QHBoxLayout, QComboBox, QDialog, QListWidget, QVBoxLayout, QInputDialog
from Code.Member import Member


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # ---------------------------- Special Class Variables ---------------------- #
        self.item_location_index = 0
        self.pos = None
        self.startPoint = None
        self.selected_object = None
        self.focused_window = None
        self.data = None  # self.import_tree_operation("Test")

        # ---------------------------- Main Window Properties ----------------------- #
        self.setWindowTitle("Family Tree Builder")
        self.layout = QGridLayout()
        self.resize(800, 600)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.init_ui()
        self.setAcceptDrops(True)
        self.show()

    # noinspection PyAttributeOutsideInit
    def init_ui(self):

        # ---------------------------- Tree Widget ---------------------------------- #
        self.tree = QTreeWidget()
        self.tree.setGeometry(QtCore.QRect(100, 0, 700, 700))
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels([" ", " "])
        self.tree.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.tree.itemClicked.connect(self.item_selected)

        # ---------------------------- Create Tree Button --------------------------- #
        self.new_tree_button = QPushButton(text="Create Tree")
        self.new_tree_button.clicked.connect(self.create_tree_operation)

        # ---------------------------- Import Tree Button --------------------------- #
        self.import_tree_button = QPushButton(text="Import Tree")
        self.import_tree_button.clicked.connect(self.import_tree_operation)

        # ---------------------------- Export Tree Button ---------------------------- #
        self.export_tree_button = QPushButton(text="Export Tree")
        self.export_tree_button.setDisabled(True)
        self.export_tree_button.clicked.connect(self.export_tree)

        # ---------------------------- Add Member Button ---------------------------- #
        self.add_member_button = QPushButton(text="Add Member")
        self.add_member_button.setDisabled(True)
        self.add_member_button.clicked.connect(self.add_member_operation)

        # ---------------------------- Check Relation Button ------------------------ #
        self.check_relation_button = QPushButton(text="Check Relation")
        self.check_relation_button.setDisabled(True)
        self.check_relation_button.clicked.connect(self.check_relation_operation)

        # ---------------------------- Add Filter Button ---------------------------- #
        self.filter_button = QPushButton(text="Filter")
        self.filter_button.setDisabled(True)
        self.filter_button.clicked.connect(self.filter_operation)

        # ---------------------------- Add Widgets To Layout ------------------------ #
        self.layout.addWidget(self.tree, 0, 1, 8, 2)
        self.layout.addWidget(self.new_tree_button, 0, 0)
        self.layout.addWidget(self.import_tree_button, 1, 0)
        self.layout.addWidget(self.export_tree_button, 2, 0)
        self.layout.addWidget(self.add_member_button, 3, 0)
        self.layout.addWidget(self.check_relation_button, 4, 0)
        self.layout.addWidget(self.filter_button, 5, 0)

        self.central_widget.setLayout(self.layout)



    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('myApp/QtWidget'):
            event.accept()

    def dropEvent(self, event):
        stream = QtCore.QDataStream(event.mimeData().data('myApp/QtWidget'))
        object_name = stream.readQString()
        widget = self.findChild(QWidget, object_name)
        if not widget:
            return
        widget.move(event.pos() - stream.readQVariant())

    @pyqtSlot()
    def add_member_operation(self):

        class AddPersonInfoWindow(QWidget):

            add_signal = QtCore.pyqtSignal(Member)

            def __init__(self):
                super().__init__()
                self.setWindowTitle("Add New Member")
                self.setWindowModality(QtCore.Qt.ApplicationModal)
                layout = QGridLayout()

                # ---------------------------- Labels ------------------------------- #
                layout.addWidget(QLabel("Name"), 0, 0)
                layout.addWidget(QLabel("Surname"), 1, 0)
                layout.addWidget(QLabel("Age*"), 2, 0)
                layout.addWidget(QLabel("Birthday*"), 3, 0)

                # ---------------------------- Input Fields ------------------------- #
                self.input_name = QLineEdit()
                self.input_surname = QLineEdit()
                self.input_age = QLineEdit()
                self.input_birthday = QDateEdit(calendarPopup=True)
                self.input_birthday.setDateTime(QtCore.QDateTime(1900, 1, 1, 0, 0))
                layout.addWidget(self.input_name, 0, 1)
                layout.addWidget(self.input_surname, 1, 1)
                layout.addWidget(self.input_age, 2, 1)
                layout.addWidget(self.input_birthday, 3, 1)

                # ---------------------------- Confirmation Buttons ----------------- #
                self.add_member_button = QPushButton("Add")
                self.cancel_action_button = QPushButton("Cancel")
                self.add_member_button.clicked.connect(self.emit_add_signal)
                self.cancel_action_button.clicked.connect(self.cancel_action)
                layout.addWidget(self.add_member_button, 4, 0)
                layout.addWidget(self.cancel_action_button, 4, 1)

                layout.addWidget(QLabel("* Optional"), 5, 0)
                self.setLayout(layout)

            def emit_add_signal(self):
                name = self.input_name.text()
                surname = self.input_surname.text()
                age = self.input_age.text()
                birthday = self.input_birthday.text()

                msg = QMessageBox()
                msg.setWindowTitle("Error")
                msg.setIcon(QMessageBox.Warning)

                birthday_datetime = datetime.strptime(birthday, "%d/%m/%Y")
                datetime_control = datetime.strptime("02/01/1903", "%d/%m/%Y")

                # ---------------------------- Input Validation --------------------- #
                if not name.isalpha():
                    msg.setText("Name must only include letters.")
                    x = msg.exec_()
                    return -1
                elif not surname.isalpha():
                    msg.setText("Surname must only include letters.")
                    x = msg.exec_()
                    return -1
                if age == "":
                    age = None
                elif not age.isdigit() or (age.isdigit() and 0 > int(age)):
                    msg.setText("Age must be non-negative integer value.")
                    x = msg.exec_()
                    return -1

                # If older than oldest person alive
                if birthday_datetime < datetime_control:
                    birthday = None
                elif birthday_datetime > datetime.now():
                    msg.setText("You cannot choose a date from the future.")
                    x = msg.exec_()
                    return -1
                else:
                    age = int((datetime.now() - birthday_datetime).days/365.2425)

                new_member = Member(name=name,
                                    surname=surname,
                                    age=age,
                                    gender=None,
                                    birthday=birthday)
                self.add_signal.emit(new_member)
                self.close()

            def cancel_action(self):
                self.close()

        @pyqtSlot(Member)
        def add_member(member):
            self.tree.insertTopLevelItem(0, QTreeWidgetItem([str(member)]))

        if self.focused_window is None or self.focused_window != AddPersonInfoWindow():
            self.focused_window = AddPersonInfoWindow()
            self.focused_window.add_signal.connect(add_member)
        self.focused_window.show()

    @pyqtSlot()
    def create_tree_operation(self):
        self.add_member_button.setEnabled(True)
        self.check_relation_button.setEnabled(True)
        self.filter_button.setEnabled(True)
        self.export_tree_button.setEnabled(True)

    @pyqtSlot()
    def filter_operation(self):
        class FilterInfoWindow(QDialog):
            add_signal = QtCore.pyqtSignal()

            def __init__(self, name="filter", filters=None):
                super(FilterInfoWindow, self).__init__()
                self.name = name
                self.list = QListWidget()
                self.title = "Please enter filter: "

                self.setWindowModality(QtCore.Qt.ApplicationModal)

                if filters is not None:
                    self.list.addItems(filters)
                    self.list.setCurrentRow(0)

                vertical_layout = QVBoxLayout()

                # code down below may get deleted in the future
                # ---------------------------------------------------
                markdown_list = QVBoxLayout()

                self.setWindowTitle("Add or Remove Filter")
                self.box = QComboBox()
                self.box.addItem("Age")
                self.box.addItem("Gender")
                self.box.addItem("Birthday")

                markdown_list.addWidget(self.box)
                # ---------------------------------------------------

                self.add_button = QPushButton("Add")
                self.edit_button = QPushButton("Edit")
                self.remove_button = QPushButton("Remove")
                self.close_button = QPushButton("Close")

                vertical_layout.addWidget(self.add_button)
                vertical_layout.addWidget(self.edit_button)
                vertical_layout.addWidget(self.remove_button)
                vertical_layout.addWidget(self.close_button)

                self.add_button.clicked.connect(self.add_operation)
                self.edit_button.clicked.connect(self.edit_operation)
                self.remove_button.clicked.connect(self.remove_operation)
                self.close_button.clicked.connect(self.close_operation)

                horizontal_layout = QHBoxLayout()
                horizontal_layout.addWidget(self.list)
                horizontal_layout.addLayout(vertical_layout)
                horizontal_layout.addLayout(markdown_list)
                self.setWindowTitle("Filters")
                self.setLayout(horizontal_layout)

            def add_operation(self):
                row = self.list.currentRow()
                string, ok = QInputDialog.getText(self, "Add Filter",
                                                  self.title)
                if ok and string is not None:
                    self.list.insertItem(row, string)

            def edit_operation(self):
                row = self.list.currentRow()
                filter_ = self.list.item(row)
                if filter_ is not None:
                    filter_name, ok = QInputDialog.getText(self, "Edit Filter",
                                                           self.title,
                                                           QLineEdit.Normal,
                                                           filter_.text())
                    if ok and filter_name is not None:
                        filter_.setText(filter_name)

            def remove_operation(self):
                row = self.list.currentRow()
                filter_ = self.list.item(row)
                if filter_ is None:
                    return
                else:
                    filter_ = self.list.takeItem(row)
                    del filter_

            def close_operation(self):
                self.close()

        if self.focused_window is None or self.focused_window != FilterInfoWindow():
            self.focused_window = FilterInfoWindow()
        self.focused_window.show()

    @pyqtSlot()
    def check_relation_operation(self):

        class AddRelationInfoWindow(QWidget):
            add_signal = QtCore.pyqtSignal()

            def __init__(self):
                super().__init__()
                self.setWindowTitle("Check Relation")
                self.setWindowModality(QtCore.Qt.ApplicationModal)
                layout = QGridLayout()
                layout.addWidget(QLabel("First Person"), 0, 0)
                layout.addWidget(QLabel("Second Person"), 1, 0)

                self.first_input_name = QLineEdit()
                self.first_input_surname = QLineEdit()

                layout.addWidget(self.first_input_name, 0, 1)
                layout.addWidget(self.first_input_surname, 0, 2)

                self.second_input_name = QLineEdit()
                self.second_input_surname = QLineEdit()

                layout.addWidget(self.second_input_name, 1, 1)
                layout.addWidget(self.second_input_surname, 1, 2)

                self.check_relation_button = QPushButton("Check")
                self.cancel_action_button = QPushButton("Cancel")

                self.cancel_action_button.clicked.connect(self.cancel_action)

                layout.addWidget(self.check_relation_button, 4, 0)
                layout.addWidget(self.cancel_action_button, 4, 1)

                self.setLayout(layout)

            def cancel_action(self):
                self.close()

        if self.focused_window is None or self.focused_window != AddRelationInfoWindow():
            self.focused_window = AddRelationInfoWindow()
        self.focused_window.show()

    @pyqtSlot()
    def import_tree_operation(self, family_name="Test"):

        def initialize_data(current_node, parent_item=None):
            parents = current_node['parents']
            children = current_node['children']

            member_pair = []
            for parent in parents:
                member_pair.append(f"{parent['name']} {parent['surname']}")

            item = QTreeWidgetItem(member_pair)
            item.setFlags(item.flags() | Qt.ItemIsSelectable)

            if parent_item is None:
                items.append(item)
            else:
                parent_item.addChild(item)

            if children is None:
                return
            for child in children:
                initialize_data(child, item)

        if self.data is None:
            with open(f"{os.getcwd()}/data/{family_name}.json") as tree_json:
                self.data = json.load(tree_json)
        items = []
        [initialize_data(node) for node in self.data['family_members']]
        self.tree.insertTopLevelItems(0, items)

        self.add_member_button.setEnabled(True)
        self.check_relation_button.setEnabled(True)
        self.filter_button.setEnabled(True)

    @pyqtSlot()
    def export_tree(self):
        # this is just a template for the main window
        # directory view will be implemented later
        pass

    @pyqtSlot(QTreeWidgetItem, int)
    def item_selected(self, selected_item, selected_index):
        # print(selected_item.text(selected_index))
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
