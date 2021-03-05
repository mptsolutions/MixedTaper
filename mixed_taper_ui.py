# pyuic5 -o mixed_taper_template_ui.py mixed_taper_template.ui

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QTableWidget, QAbstractItemView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDropEvent

class TableWidgetRefresh(QTableWidget):
    keyPressed = QtCore.pyqtSignal(int)

    def keyPressEvent(self, event):
        super(TableWidgetRefresh, self).keyPressEvent(event)
        self.keyPressed.emit(event.key())

class TableWidgetDragRows(QTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setDragDropOverwriteMode(False)
        self.setDropIndicatorShown(True)
        self.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setDragDropMode(QAbstractItemView.DragDrop)

    def dropEvent(self, event: QDropEvent):
        if not event.isAccepted() and event.source() == self:
            drop_row = self.drop_on(event)
            rows = sorted(set(item.row() for item in self.selectedItems()))
            rows_to_move = [[QTableWidgetItem(self.item(row_index, column_index)) for column_index in range(self.columnCount())]
                            for row_index in rows]
            for row_index in reversed(rows):
                self.removeRow(row_index)
                if row_index < drop_row:
                    drop_row -= 1
            for row_index, data in enumerate(rows_to_move):
                row_index += drop_row
                self.insertRow(row_index)
                for column_index, column_data in enumerate(data):
                    self.setItem(row_index, column_index, column_data)
            event.accept()
            for row_index in range(len(rows_to_move)):
                self.item(drop_row + row_index, 0).setSelected(True)
                self.item(drop_row + row_index, 1).setSelected(True)
        super().dropEvent(event)

    def drop_on(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            return self.rowCount()
        return index.row() + 1 if self.is_below(event.pos(), index) else index.row()

    def is_below(self, pos, index):
        rect = self.visualRect(index)
        margin = 2
        if pos.y() - rect.top() < margin:
            return False
        elif rect.bottom() - pos.y() < margin:
            return True
        return rect.contains(pos, True) and not (int(self.model().flags(index)) & Qt.ItemIsDropEnabled) and pos.y() >= rect.center().y()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1600, 800)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(1600, 800))
        MainWindow.setMaximumSize(QtCore.QSize(1600, 800))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.artist_list = TableWidgetRefresh(self.centralwidget)
        self.artist_list.setGeometry(QtCore.QRect(0, 0, 301, 801))
        self.artist_list.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.artist_list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.artist_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.artist_list.setRowCount(0)
        self.artist_list.setColumnCount(1)
        self.artist_list.setHorizontalHeaderLabels(['ARTIST'])
        self.artist_list.setObjectName("artist_list")
        self.artist_list.horizontalHeader().setStretchLastSection(True)

        self.release_list = QtWidgets.QTableWidget(self.centralwidget)
        self.release_list.setGeometry(QtCore.QRect(300, 0, 361, 261))
        self.release_list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.release_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.release_list.setObjectName("release_list")
        self.release_list.setColumnCount(1)
        self.release_list.setHorizontalHeaderLabels(['RELEASES'])
        self.release_list.setRowCount(0)
        self.release_list.horizontalHeader().setStretchLastSection(True)

        self.track_list = QtWidgets.QTableWidget(self.centralwidget)
        self.track_list.setGeometry(QtCore.QRect(300, 260, 361, 541))
        self.track_list.setEditTriggers(QtWidgets.QAbstractItemView.SelectedClicked)
        self.track_list.setDragEnabled(False)
        self.track_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.track_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.track_list.setObjectName("track_list")
        self.track_list.setColumnCount(3)
        self.track_list.setHorizontalHeaderLabels(['POSITION', 'LENGTH', 'TITLE'])
        self.track_list.setRowCount(0)
        self.track_list.horizontalHeader().setStretchLastSection(True)

        self.side_a_list = TableWidgetDragRows(self.centralwidget)
        self.side_a_list.setGeometry(QtCore.QRect(670, 0, 651, 401))
        self.side_a_list.setObjectName("side_a_list")
        self.side_a_list.setEditTriggers(QtWidgets.QAbstractItemView.SelectedClicked)
        self.side_a_list.setColumnCount(5)
        self.side_a_list.setHorizontalHeaderLabels(['RELEASE', 'ARTIST', 'POSITION', 'LENGTH', 'TITLE'])
        self.side_a_list.setRowCount(0)
        self.side_a_list.horizontalHeader().setStretchLastSection(True)

        self.side_b_list = TableWidgetDragRows(self.centralwidget)
        self.side_b_list.setGeometry(QtCore.QRect(670, 400, 651, 401))
        self.side_b_list.setObjectName("side_b_list")
        self.side_b_list.setEditTriggers(QtWidgets.QAbstractItemView.SelectedClicked)
        self.side_b_list.setColumnCount(5)
        self.side_b_list.setHorizontalHeaderLabels(['RELEASE', 'ARTIST', 'POSITION', 'LENGTH', 'TITLE'])
        self.side_b_list.setRowCount(0)
        self.side_b_list.horizontalHeader().setStretchLastSection(True)

        self.calculate_button = QtWidgets.QPushButton(self.centralwidget)
        self.calculate_button.setGeometry(QtCore.QRect(1400, 20, 121, 23))
        font = QtGui.QFont()
        font.setFamily("Arial Black")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.calculate_button.setFont(font)
        self.calculate_button.setObjectName("calculate_button")

        self.save_button = QtWidgets.QPushButton(self.centralwidget)
        self.save_button.setGeometry(QtCore.QRect(1400, 210, 121, 23))
        font = QtGui.QFont()
        font.setFamily("Arial Black")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.save_button.setFont(font)
        self.save_button.setObjectName("save_button")

        self.clear_button = QtWidgets.QPushButton(self.centralwidget)
        self.clear_button.setGeometry(QtCore.QRect(1400, 760, 121, 23))
        self.clear_button.setFont(font)
        self.clear_button.setObjectName("clear_button")

        self.side_a_group_box = QtWidgets.QGroupBox(self.centralwidget)
        self.side_a_group_box.setGeometry(QtCore.QRect(1350, 50, 221, 71))
        font = QtGui.QFont()
        font.setFamily("Arial Black")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.side_a_group_box.setFont(font)
        self.side_a_group_box.setObjectName("side_a_group_box")
        self.side_a_time_label = QtWidgets.QLabel(self.side_a_group_box)
        self.side_a_time_label.setGeometry(QtCore.QRect(20, 30, 81, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.side_a_time_label.setFont(font)
        self.side_a_time_label.setObjectName("side_a_time_label")
        self.side_a_time_box = QtWidgets.QLineEdit(self.side_a_group_box)
        self.side_a_time_box.setGeometry(QtCore.QRect(110, 30, 91, 20))
        font = QtGui.QFont()
        font.setFamily("Courier")
        font.setPointSize(12)
        self.side_a_time_box.setFont(font)
        self.side_a_time_box.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.side_a_time_box.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.side_a_time_box.setObjectName("side_a_time_box")
        self.side_b_group_box = QtWidgets.QGroupBox(self.centralwidget)
        self.side_b_group_box.setGeometry(QtCore.QRect(1350, 130, 221, 71))
        font = QtGui.QFont()
        font.setFamily("Arial Black")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.side_b_group_box.setFont(font)
        self.side_b_group_box.setObjectName("side_b_group_box")
        self.side_b_time_label = QtWidgets.QLabel(self.side_b_group_box)
        self.side_b_time_label.setGeometry(QtCore.QRect(20, 30, 81, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.side_b_time_label.setFont(font)
        self.side_b_time_label.setObjectName("side_b_time_label")
        self.side_b_time_box = QtWidgets.QLineEdit(self.side_b_group_box)
        self.side_b_time_box.setGeometry(QtCore.QRect(110, 30, 91, 20))
        font = QtGui.QFont()
        font.setFamily("Courier")
        font.setPointSize(12)
        self.side_b_time_box.setFont(font)
        self.side_b_time_box.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.side_b_time_box.setObjectName("side_b_time_box")

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MixedTaper"))
        self.calculate_button.setText(_translate("MainWindow", "CALCULATE"))
        self.save_button.setText(_translate("MainWindow", "SAVE"))
        self.clear_button.setText(_translate("MainWindow", "CLEAR"))
        self.side_a_group_box.setTitle(_translate("MainWindow", "Side A"))
        self.side_a_time_label.setText(_translate("MainWindow", "Total Time:"))
        self.side_a_time_box.setText(_translate("MainWindow", "00:00:00"))
        self.side_b_group_box.setTitle(_translate("MainWindow", "Side B"))
        self.side_b_time_label.setText(_translate("MainWindow", "Total Time:"))
        self.side_b_time_box.setText(_translate("MainWindow", "00:00:00"))
