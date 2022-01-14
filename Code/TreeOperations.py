import json
import os
from datetime import datetime
import sys
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, \
    QMainWindow, QLabel, QGridLayout, QDateEdit, \
    QLineEdit, QMessageBox, QTreeWidgetItem, QAbstractItemView, QTreeWidget, \
    QHBoxLayout, QComboBox, QDialog, QListWidget, QVBoxLayout, QInputDialog, QFileDialog, QFrame, QSizePolicy
from Member import Member


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # ---------------------------- Special Class Variables ---------------------- #
        self.focused_window = None
        self.selected_member = None
        self.config_file_path = f'{os.getcwd()}/config.json'
        self.draft_path = f'{os.getcwd()}/draft.json'

        # ---------------------------- App Configuration ---------------------------- #
        with open(self.config_file_path) as config_json:
            config_file = json.load(config_json)
            self.active_tree_path = config_file['active_tree_path']
            self.source_tree_path = config_file['source_tree_path']
            self.id_counter = config_file['global_id_counter']

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

        # ---------------------------- Create Tree Button --------------------------- #
        self.new_tree_button = QPushButton(text="Create Tree")
        self.new_tree_button.clicked.connect(self.create_tree_operation)

        # ---------------------------- Import Tree Button --------------------------- #
        self.import_tree_button = QPushButton(text="Import Tree")
        self.import_tree_button.clicked.connect(self.import_tree_operation)

        # ---------------------------- Export Tree Button ---------------------------- #
        self.export_tree_button = QPushButton(text="Export Tree")
        self.export_tree_button.clicked.connect(self.export_tree_operation)

        # ---------------------------- Add Member Button ---------------------------- #
        self.add_member_button = QPushButton(text="Add Member")
        self.add_member_button.clicked.connect(lambda: self.add_member_operation(self.id_counter, self.selected_member))

        # ---------------------------- Check Relation Button ------------------------ #
        self.check_relation_button = QPushButton(text="Check Relation")
        self.check_relation_button.clicked.connect(self.check_relation_operation)

        # ---------------------------- Add Filter Button ---------------------------- #
        self.filter_button = QPushButton(text="Filter")
        self.filter_button.clicked.connect(self.filter_operation)

        # ---------------------------- Save As Image Button ------------------------- #
        self.save_as_image_button = QPushButton(text="Save As Image")
        self.save_as_image_button.clicked.connect(self.save_as_image_operation)

        # ---------------------------- Tree Widget ---------------------------------- #
        self.tree = QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels([" ", " "])
        self.tree.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding))
        self.tree.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.tree.itemClicked.connect(self.item_selected)
        self.set_button_states(mode="disabled")
        self.import_tree_operation(import_on_load=True)

        # ---------------------------- Member Info Tab ------------------------------ #
        self.member_info_frame = QFrame()
        self.member_info_frame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        member_info_layout = QGridLayout()
        member_info_layout.addWidget(QLabel("Name"), 0, 0)
        member_info_layout.addWidget(QLabel("Surname"), 1, 0)
        member_info_layout.addWidget(QLabel("Age"), 2, 0)
        member_info_layout.addWidget(QLabel("Birthday"), 3, 0)
        member_info_layout.addWidget(QLabel("Gender"), 4, 0)

        self.name_info = QLineEdit("Name")
        self.name_info.setDisabled(True)
        self.surname_info = QLineEdit("Surname")
        self.surname_info.setDisabled(True)
        self.age_info = QLineEdit("Age")
        self.age_info.setDisabled(True)
        self.birthday_info = QLineEdit("Birthday")
        self.birthday_info.setDisabled(True)
        self.gender_info = QLineEdit("Gender")
        self.gender_info.setDisabled(True)
        member_info_layout.addWidget(self.name_info, 0, 1)
        member_info_layout.addWidget(self.surname_info, 1, 1)
        member_info_layout.addWidget(self.age_info, 2, 1)
        member_info_layout.addWidget(self.birthday_info, 3, 1)
        member_info_layout.addWidget(self.gender_info, 4, 1)

        self.member_info_frame.setLayout(member_info_layout)

        # ---------------------------- Add Widgets To Layout ------------------------ #
        self.layout.addWidget(self.tree, 0, 1, 8, 2)
        self.layout.addWidget(self.new_tree_button, 0, 0)
        self.layout.addWidget(self.import_tree_button, 1, 0)
        self.layout.addWidget(self.export_tree_button, 2, 0)
        self.layout.addWidget(self.add_member_button, 3, 0)
        self.layout.addWidget(self.check_relation_button, 4, 0)
        self.layout.addWidget(self.filter_button, 5, 0)
        self.layout.addWidget(self.save_as_image_button, 6, 0)
        self.layout.addWidget(self.member_info_frame, 0, 3, 5, 1)

        self.central_widget.setLayout(self.layout)

    @pyqtSlot()
    def add_member_operation(self, id_counter, parent):

        class AddPersonInfoWindow(QWidget):

            add_signal = QtCore.pyqtSignal(Member, QTreeWidgetItem, str)
            add_top_signal = QtCore.pyqtSignal(Member, str)

            def __init__(self):
                super().__init__()
                self.setWindowTitle("Add New Member")
                self.setWindowModality(QtCore.Qt.ApplicationModal)
                self.parent = parent
                if self.parent is None:
                    self.parent_text = ""
                else:
                    self.parent_text = self.parent.text(0)
                layout = QGridLayout()

                # ---------------------------- Labels ------------------------------- #
                layout.addWidget(QLabel(f"Connecting To"), 0, 0)
                layout.addWidget(QLabel(f"Relation"), 1, 0)
                layout.addWidget(QLabel("Name"), 2, 0)
                layout.addWidget(QLabel("Surname"), 3, 0)
                layout.addWidget(QLabel("Age*"), 4, 0)
                layout.addWidget(QLabel("Birthday*"), 5, 0)
                layout.addWidget(QLabel("Gender"), 6, 0)

                # ---------------------------- Input Fields ------------------------- #
                self.input_connection = QLineEdit()
                self.input_connection.setDisabled(True)
                self.input_connection.setText(self.parent_text)
                self.input_relation = QComboBox()
                self.input_relation.addItems(["Child", "Spouse"])
                self.input_name = QLineEdit()
                self.input_surname = QLineEdit()
                self.input_age = QLineEdit()
                self.input_birthday = QDateEdit(calendarPopup=True)
                self.input_birthday.setDateTime(QtCore.QDateTime(1900, 1, 1, 0, 0))
                self.input_gender = QComboBox()
                self.input_gender.addItems(["Male", "Female"])
                layout.addWidget(self.input_connection, 0, 1)
                layout.addWidget(self.input_relation, 1, 1)
                layout.addWidget(self.input_name, 2, 1)
                layout.addWidget(self.input_surname, 3, 1)
                layout.addWidget(self.input_age, 4, 1)
                layout.addWidget(self.input_birthday, 5, 1)
                layout.addWidget(self.input_gender, 6, 1)

                # ---------------------------- Confirmation Buttons ----------------- #
                self.add_member_button = QPushButton("Add")
                self.cancel_action_button = QPushButton("Cancel")
                self.add_member_button.clicked.connect(self.emit_add_signal)
                self.cancel_action_button.clicked.connect(self.cancel_action)
                layout.addWidget(self.add_member_button, 7, 0)
                layout.addWidget(self.cancel_action_button, 7, 1)

                layout.addWidget(QLabel("* Optional"), 8, 0)
                self.setLayout(layout)

            def emit_add_signal(self):
                name = self.input_name.text()
                surname = self.input_surname.text()
                age = self.input_age.text()
                birthday = self.input_birthday.text()
                gender = self.input_gender.currentText()
                relation = self.input_relation.currentText()

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
                    age = int((datetime.now() - birthday_datetime).days / 365.2425)

                new_member = Member(member_id=id_counter,
                                    name=name,
                                    surname=surname,
                                    age=age,
                                    gender=gender,
                                    birthday=birthday)

                if self.parent is None:
                    self.add_top_signal.emit(new_member, relation)
                else:
                    self.add_signal.emit(new_member, self.parent, relation)
                self.close()

            def cancel_action(self):
                self.close()

        @pyqtSlot(Member, str)
        def add_member_top(member, relation):
            child = QTreeWidgetItem([member.full_name()])
            child.setFlags(child.flags() | Qt.ItemIsSelectable)
            child.setToolTip(0, str(member.member_id))
            self.tree.insertTopLevelItem(0, child)
            self.data["family_members"].append({"parents": [member.to_dict()], "children": None})
            self.id_counter += 1

        @pyqtSlot(Member, QTreeWidgetItem, str)
        def add_member(member, add_member_on, relation):
            add_member_on_id = self.selected_member.toolTip(0)

            def find_member_to_add_on(current_node):
                parents = current_node['parents']
                children = current_node['children']

                if int(add_member_on_id) in [x["id"] for x in parents]:
                    if children is None:
                        children = []
                    children.append({"parents": [member.to_dict()], "children": None})
                    return
                if children is None:
                    return
                for child_ in children:
                    find_member_to_add_on(child_)

            if relation == "Child":
                child = QTreeWidgetItem([member.full_name()])
                child.setFlags(child.flags() | Qt.ItemIsSelectable)
                child.setToolTip(0, str(member.member_id))
                add_member_on.addChild(child)
                for member_node in self.data["family_members"]:
                    find_member_to_add_on(member_node)
            elif relation == "Spouse":
                self.selected_member.setText(1, member.full_name())
                self.selected_member.setToolTip(1, str(member.member_id))
            self.id_counter += 1

        if self.focused_window is None or self.focused_window != AddPersonInfoWindow():
            self.focused_window = AddPersonInfoWindow()
            self.focused_window.add_signal.connect(add_member)
            self.focused_window.add_top_signal.connect(add_member_top)
        self.focused_window.show()

    @pyqtSlot()
    def create_tree_operation(self):
        try:
            if os.path.isfile(self.active_tree_path):
                msg = QMessageBox()
                msg.setWindowTitle("Warning")
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Do you want to save your changes made on the currently active tree?")
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
                x = msg.exec_()
                if x == QMessageBox.Yes:
                    with open(self.source_tree_path, 'w+') as tree_json:
                        json.dump(self.data, tree_json)
                    self.active_tree_path = None
                    self.source_tree_path = None
                    self.data = None
                    self.tree.clear()
                elif x == QMessageBox.No:
                    self.active_tree_path = None
                    self.source_tree_path = None
                    self.data = None
                    self.tree.clear()
                elif x == QMessageBox.Cancel:
                    msg.close()
        except TypeError:
            pass

        family_name, ok = QInputDialog.getText(self, "Family Name", "Create Tree")
        if family_name.isalpha():
            with open(self.draft_path, mode="w+") as draft_json:
                draft_data = {"family_name": family_name, "family_members": []}
                json.dump(draft_data, draft_json)
            self.active_tree_path = self.draft_path
            self.set_button_states(mode="enabled")
            self.tree.clear()

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

                self.setWindowTitle("Add or Remove Filter")
                self.box = QComboBox()
                self.box.addItem("Age")
                self.box.addItem("Gender")
                self.box.addItem("Birthday")

                vertical_layout.addWidget(self.box)

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
                self.setWindowTitle("Filters")
                self.setLayout(horizontal_layout)

            def add_operation(self):
                row = self.list.currentRow()

                # if the markdown selection is age
                if self.box.currentText() == "Age":
                    integer, ok = QInputDialog.getInt(window, "Input Integer", "Number:",
                                                      10, 0, 100, 1)
                    if ok and integer is not None:
                        self.list.insertItem(row, f"{str(self.box.currentText())}: {integer}")

                # if the markdown selection is gender
                elif self.box.currentText() == "Gender":

                    # -----input validation for multiple gender filters------
                    male_count = self.list.findItems("Gender: Male", QtCore.Qt.MatchExactly)
                    female_count = self.list.findItems("Gender: Female", QtCore.Qt.MatchExactly)
                    if not len(male_count) > 0 and not len(female_count) > 0:
                        options = ("Male", "Female")
                        string, ok = QInputDialog.getItem(window, "Select Gender", "Option:",
                                                          options, 0, False)
                        if ok and string is not None:
                            self.list.insertItem(row, f"{str(self.box.currentText())}: {string}")
                    else:  # error message box for multiple gender filter validation
                        msg = QMessageBox()
                        msg.setWindowTitle("Warning")
                        msg.setIcon(QMessageBox.Warning)
                        msg.setText("You cannot add multiple gender filters.")
                        msg.exec()

                # if the markdown selection is birthday
                elif self.box.currentText() == "Birthday":
                    string, ok = QInputDialog.getText(self, "Add Filter",
                                                      self.title)
                    if ok and string is not None:
                        self.list.insertItem(row, f"{str(self.box.currentText())}: {string}")

            def edit_operation(self):
                row = self.list.currentRow()
                filter_ = self.list.item(row)
                if filter_ is not None:
                    if filter_.text().startswith("Age"):
                        filter_name, ok = QInputDialog.getInt(window, "Input Integer", "Number:",
                                                              10, 0, 100, 1)
                        if ok and filter_name is not None:
                            filter_.setText(f"Age: {filter_name}")

                    elif filter_.text().startswith("Gender"):
                        options = ("Male", "Female")
                        filter_name, ok = QInputDialog.getItem(window, "Select Gender", "Option:",
                                                               options, 0, False)
                        if ok and filter_name is not None:
                            filter_.setText(f"Gender: {filter_name}")

                    elif filter_.text().startswith("Birthday: "):
                        filter_name, ok = QInputDialog.getText(self, "Add Filter",
                                                               self.title)

                        if ok and filter_name is not None:
                            filter_.setText(f"Birthday: {filter_name}")

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
                layout.addWidget(QLabel("Name: "), 0, 0)
                layout.addWidget(QLabel("Name: "), 1, 0)
                layout.addWidget(QLabel("Surname: "), 0, 2)
                layout.addWidget(QLabel("Surname: "), 1, 2)

                self.first_input_name = QLineEdit()
                self.first_input_surname = QLineEdit()

                layout.addWidget(self.first_input_name, 0, 1)
                layout.addWidget(self.first_input_surname, 0, 3)

                self.second_input_name = QLineEdit()
                self.second_input_surname = QLineEdit()

                layout.addWidget(self.second_input_name, 1, 1)
                layout.addWidget(self.second_input_surname, 1, 3)

                self.check_relation_button = QPushButton("Check")
                self.cancel_action_button = QPushButton("Cancel")

                self.cancel_action_button.clicked.connect(self.cancel_action)

                layout.addWidget(self.check_relation_button, 4, 2)
                layout.addWidget(self.cancel_action_button, 4, 3)

                self.setLayout(layout)

            def cancel_action(self):
                self.close()

        if self.focused_window is None or self.focused_window != AddRelationInfoWindow():
            self.focused_window = AddRelationInfoWindow()
        self.focused_window.show()

    @pyqtSlot()
    def import_tree_operation(self, import_on_load=False):

        try:
            if import_on_load and self.active_tree_path is None:
                self.data = None
                return
            try:
                if import_on_load and os.path.isfile(self.active_tree_path):
                    self.import_tree(self.active_tree_path)
                    items = []
                    [self.initialize_data(node, items) for node in self.data['family_members']]
                    self.tree.insertTopLevelItems(0, items)
                    return
                elif import_on_load:
                    with open(self.config_file_path, mode="w+") as config_json:
                        config_file = {"active_tree_path": None,
                                       "source_tree_path": None,
                                       "global_id_counter": self.id_counter}
                        json.dump(config_file, config_json)
                    self.set_button_states(mode="disabled")
                    self.active_tree_path = None
                    self.source_tree_path = None
                    self.tree.clear()
                    return
                if os.path.isfile(self.active_tree_path):
                    msg = QMessageBox()
                    msg.setWindowTitle("Warning")
                    msg.setIcon(QMessageBox.Warning)
                    msg.setText("Do you want to save your changes made on the currently active tree?")
                    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
                    x = msg.exec_()
                    if x == QMessageBox.Yes:
                        with open(self.source_tree_path, 'w+') as tree_json:
                            json.dump(self.data, tree_json)
                        self.active_tree_path = None
                        self.source_tree_path = None
                        self.tree.clear()
                    elif x == QMessageBox.No:
                        self.active_tree_path = None
                        self.source_tree_path = None
                        self.tree.clear()
                    elif x == QMessageBox.Cancel:
                        msg.close()
            except TypeError:
                pass

            if self.active_tree_path is None:
                file_path, _ = QFileDialog.getOpenFileName(self, "Import Tree", "", "JSON Files (*.json)")
                if file_path != "":
                    self.import_tree(file_path)
                    items = []
                    [self.initialize_data(node, items) for node in self.data['family_members']]
                    self.tree.insertTopLevelItems(0, items)
        except KeyError:
            msg = QMessageBox()
            msg.setWindowTitle("Warning")
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Tree file you've selected is either corrupted or not accepted as a tree file.")
            msg.exec_()
            with open(self.config_file_path, mode="w+") as config_json:
                config_file = {"active_tree_path": None,
                               "global_id_counter": self.id_counter}
                json.dump(config_file, config_json)
            self.set_button_states(mode="disabled")
            self.active_tree_path = None
            self.data = None
            self.tree.clear()

    def import_tree(self, tree_path):
        with open(self.config_file_path, mode="w+") as config_json:
            config_file = {"active_tree_path": self.draft_path,
                           "source_tree_path": tree_path,
                           "global_id_counter": self.id_counter}
            json.dump(config_file, config_json)

        self.set_button_states(mode="enabled")
        self.active_tree_path = self.draft_path
        self.source_tree_path = tree_path

        with open(tree_path, 'r') as tree_json:
            self.data = json.load(tree_json)

    def initialize_data(self, current_node, items, parent_item=None):
        parents = current_node['parents']
        children = current_node['children']

        member_pair = []
        for parent in parents:
            member_pair.append(f"{parent['name']} {parent['surname']}")

        item = QTreeWidgetItem(member_pair)
        item.setFlags(item.flags() | Qt.ItemIsSelectable)

        for i in range(len(parents)):
            item.setToolTip(i, str(parents[i]['id']))

        if parent_item is None:
            items.append(item)
        else:
            parent_item.addChild(item)

        if children is None:
            return
        for child in children:
            self.initialize_data(child, items, item)

    @pyqtSlot()
    def export_tree_operation(self, auto_save=False):
        if auto_save:
            file_path = f'{os.getcwd()}/draft.json'
        else:
            file_path, _ = QFileDialog.getSaveFileName(self, "Export Tree", "", "JSON Files (*.json)")
        if file_path != "":
            with open(file_path, mode="w+") as new_tree_file:
                json.dump(self.data, new_tree_file)

    @pyqtSlot(QTreeWidgetItem, int)
    def item_selected(self, selected_item, selected_index):
        member_id = int(selected_item.toolTip(selected_index))

        def find_member(current_node):
            parents = current_node['parents']
            children = current_node['children']
            for node in parents:
                if member_id == node["id"]:
                    self.name_info.setText(node["name"])
                    self.surname_info.setText(node["surname"])
                    self.age_info.setText(str(node["age"]))
                    self.birthday_info.setText(node["birthday"])
                    self.gender_info.setText(node["gender"])
                    return
            if children is None:
                return
            for child_ in children:
                find_member(child_)

        for member_node in self.data['family_members']:
            find_member(member_node)

        if self.selected_member == selected_item:
            self.selected_member = None
            self.tree.setCurrentItem(None)
        else:
            self.selected_member = selected_item

    def set_button_states(self, mode):
        if mode == "enabled":
            self.add_member_button.setEnabled(True)
            self.check_relation_button.setEnabled(True)
            self.filter_button.setEnabled(True)
            self.export_tree_button.setEnabled(True)
            self.save_as_image_button.setEnabled(True)
        elif mode == "disabled":
            self.add_member_button.setDisabled(True)
            self.check_relation_button.setDisabled(True)
            self.filter_button.setDisabled(True)
            self.export_tree_button.setDisabled(True)
            self.save_as_image_button.setDisabled(True)

    @pyqtSlot()
    def save_as_image_operation(self):
        screen = QApplication.primaryScreen()
        self.tree.expandAll()
        screenshot = screen.grabWindow(self.tree.winId())
        file_name, _ = QFileDialog.getSaveFileName(self, 'Save File', '', '*.jpg;;*.jpeg;;*.png;;*.bmp')
        screenshot.save(file_name, _[2:])

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Exit',
                                     'Are you sure you want to exit?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.export_tree_operation(auto_save=True)
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
