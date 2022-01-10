from datetime import datetime
import sys
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMenu, QWidget, QPushButton, QApplication, QMainWindow, QLabel, QGridLayout, QDateEdit, \
    QLineEdit, QMessageBox


# This layout looks promising
# https://www.geeksforgeeks.org/pyqt5-qdockwidget-setting-allowed-areas/?ref=rp

# Draw line between rectangles
# https://stackoverflow.com/questions/55078456/pyqt5-drawing-line


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.item_location_index = 0
        self.pos = None
        self.startPoint = None
        self.selected_object = None
        self.focused_window = None

        self.resize(800, 600)
        self.init_ui()

        self.setAcceptDrops(True)
        self.show()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.label = QLabel(self.central_widget)
        self.label.setGeometry(100, 0, 600, 600)

        canvas = QtGui.QPixmap(600, 600)
        canvas.fill(QtGui.QColor("darkgray"))
        self.label.setPixmap(canvas)

        self.add_member_button = QPushButton(text="Add Member", parent=self.central_widget)
        self.add_member_button.setGeometry(QtCore.QRect(0, 0, 100, 100))
        self.add_member_button.clicked.connect(self.add_member_operation)

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
            add_signal = QtCore.pyqtSignal(dict)

            def __init__(self):
                super().__init__()
                self.setWindowTitle("Add New Member")
                self.setWindowModality(QtCore.Qt.ApplicationModal)
                layout = QGridLayout()
                layout.addWidget(QLabel("Name"), 0, 0)
                layout.addWidget(QLabel("Surname"), 1, 0)
                layout.addWidget(QLabel("Age*"), 2, 0)
                layout.addWidget(QLabel("Birthday*"), 3, 0)

                self.input_name = QLineEdit()
                self.input_surname = QLineEdit()
                self.input_age = QLineEdit()
                self.input_birthday = QDateEdit(calendarPopup=True)
                self.input_birthday.setDateTime(QtCore.QDateTime(1900, 1, 1, 0, 0))

                layout.addWidget(self.input_name, 0, 1)
                layout.addWidget(self.input_surname, 1, 1)
                layout.addWidget(self.input_age, 2, 1)
                layout.addWidget(self.input_birthday, 3, 1)

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
                if birthday_datetime < datetime_control:  # If older than oldest person alive
                    birthday = None
                elif birthday_datetime > datetime.now():
                    msg.setText("You cannot choose a date from the future.")
                    x = msg.exec_()
                    return -1
                else:
                    age = int((datetime.now() - birthday_datetime).days/365.2425)

                new_member = {"name": name,
                              "surname": surname,
                              "age": age,
                              "birthday": birthday}
                self.add_signal.emit(new_member)
                self.close()

            def cancel_action(self):
                self.close()

        @pyqtSlot(dict)
        def add_member(member_dict):
            print(member_dict)
            # noinspection PyArgumentList
            push_button = DraggableButton(text=f"{member_dict['name']}\n{member_dict['surname']}",
                                          parent=self.central_widget,
                                          objectName=f'push_button{self.item_location_index}')
            push_button.setGeometry(QtCore.QRect(700, self.item_location_index * 100, 100, 100))
            push_button.source_signal.connect(self.receive_button_name)
            self.item_location_index += 1
            push_button.show()

        if self.focused_window is None:
            self.focused_window = AddPersonInfoWindow()
            self.focused_window.add_signal.connect(add_member)
        self.focused_window.show()

    @pyqtSlot(QPushButton, bool)
    def receive_button_name(self, source, is_first_target):
        obj_name = source.objectName()
        obj_pos = source.pos()
        if self.selected_object is None and is_first_target:
            print(f'Selected: {obj_name}')
            self.selected_object = obj_name
        elif self.selected_object != obj_name and self.selected_object is not None:
            print(f'Bound {self.selected_object} to {obj_name}')
            self.selected_object = None


class DraggableButton(QPushButton):

    source_signal = QtCore.pyqtSignal(QPushButton, bool)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == QtCore.Qt.RightButton:
            self.right_click_dropdown(event)
        elif event.button() == QtCore.Qt.LeftButton:
            self.mouse_pos = event.pos()
            self.source_signal.emit(self, False)

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            mime_data = QtCore.QMimeData()
            byte_array = QtCore.QByteArray()
            stream = QtCore.QDataStream(byte_array, QtCore.QIODevice.WriteOnly)

            stream.writeQString(self.objectName())
            stream.writeQVariant(self.mouse_pos)

            mime_data.setData('myApp/QtWidget', byte_array)
            drag = QtGui.QDrag(self)

            drag.setPixmap(self.grab())
            drag.setMimeData(mime_data)

            drag.setHotSpot(self.mouse_pos - self.rect().topLeft())
            drag.exec_()

    def right_click_dropdown(self, event):
        if event.buttons() == QtCore.Qt.RightButton:
            context_menu = QMenu(self)

            sub_menu = QMenu(context_menu)
            sub_menu.setTitle("Create Relation")

            bind_parent = sub_menu.addAction("Parent")
            bind_child = sub_menu.addAction("Child")

            context_menu.addMenu(sub_menu)
            action = context_menu.exec_(self.mapToGlobal(event.pos()))

            if action == bind_parent:
                self.source_signal.emit(self, True)
            elif action == bind_child:
                self.source_signal.emit(self, True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
