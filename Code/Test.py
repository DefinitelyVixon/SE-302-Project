import sys
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QMenu, QWidget, QPushButton, QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QPainter, QPen


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

        tracker = MouseTracker(self.label)
        tracker.position_changed.connect(self.on_position_changed)

        self.add_button = QPushButton(text="Add Member", parent=self.central_widget)
        self.add_button.setGeometry(QtCore.QRect(700, 0, 100, 100))
        self.add_button.clicked.connect(self.add_member)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.startPoint is None:
            # print("Drawing On")
            self.startPoint = event.pos()
        elif event.button() == Qt.LeftButton and self.startPoint is not None:
            # print("Drawing Off")
            self.startPoint = None

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

    @pyqtSlot(QtCore.QPoint)
    def on_position_changed(self, pos):
        self.label.pixmap().fill(QtGui.QColor("darkgray"))
        if self.startPoint is not None:
            painter = QPainter(self.label.pixmap())
            painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
            painter.drawLine(pos.x(), pos.y(), self.startPoint.x() - 100, self.startPoint.y())
            painter.end()
            self.update()

    @pyqtSlot()
    def add_member(self):
        push_button = DraggableButton(text="AAAAAA\nBBBBBB",
                                      parent=self.central_widget,
                                      objectName=f'push_button{self.item_location_index}')
        push_button.setGeometry(QtCore.QRect(0, self.item_location_index * 100, 100, 100))
        # push_button.setStyleSheet("background-color: white; border: 1px solid lightgray")
        push_button.test_signal.connect(self.receive_button_name)
        self.item_location_index += 1
        push_button.show()

    @pyqtSlot(QPushButton, bool)
    def receive_button_name(self, source, is_first_target):
        obj_name = source.objectName()
        obj_pos = source.pos()
        if self.selected_object is None and is_first_target:
            print(f'First Selected: {obj_name}')
            self.selected_object = obj_name
        elif self.selected_object != obj_name and self.selected_object is not None:
            print(f'Bound {self.selected_object} to {obj_name}')
            self.selected_object = None
            # print(position)


class MouseTracker(QtCore.QObject):
    position_changed = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, widget):
        super().__init__(widget)
        self._widget = widget
        self.widget.setMouseTracking(True)
        self.widget.installEventFilter(self)

    @property
    def widget(self):
        return self._widget

    def eventFilter(self, o, e):
        if o is self.widget and e.type() == QtCore.QEvent.MouseMove:
            self.position_changed.emit(e.pos())
        return super().eventFilter(o, e)


class DraggableButton(QPushButton):

    test_signal = QtCore.pyqtSignal(QPushButton, bool)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == QtCore.Qt.RightButton:
            self.right_click_dropdown(event)
        elif event.button() == QtCore.Qt.LeftButton:
            self.mouse_pos = event.pos()
            self.test_signal.emit(self, False)

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
            # context_menu.setStyleSheet('QPushButton:hover{background-color: black;}')
            create_relation = context_menu.addAction("Create Relation")
            action = context_menu.exec_(self.mapToGlobal(event.pos()))
            if action == create_relation:
                self.test_signal.emit(self, True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
