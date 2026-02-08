# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    Qt,
    QTime,
    QUrl,
)
from PySide6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMenuBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from .widgets.treeview import VTreeView


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1188, 869)
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionRefresh_Assembly_List = QAction(MainWindow)
        self.actionRefresh_Assembly_List.setObjectName("actionRefresh_Assembly_List")
        self.actionHide_Toolbar = QAction(MainWindow)
        self.actionHide_Toolbar.setObjectName("actionHide_Toolbar")
        self.actionHide_Toolbar.setCheckable(True)
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.action_hide_files = QAction(MainWindow)
        self.action_hide_files.setObjectName("action_hide_files")
        self.action_hide_files.setCheckable(True)
        self.action_hide_files.setChecked(True)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_2 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.splitter_2 = QSplitter(self.centralwidget)
        self.splitter_2.setObjectName("splitter_2")
        self.splitter_2.setOrientation(Qt.Orientation.Horizontal)
        self.splitter = QSplitter(self.splitter_2)
        self.splitter.setObjectName("splitter")
        self.splitter.setOrientation(Qt.Orientation.Vertical)
        self.groupBox = QGroupBox(self.splitter)
        self.groupBox.setObjectName("groupBox")
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.lw_favorites = QListWidget(self.groupBox)
        self.lw_favorites.setObjectName("lw_favorites")
        sizePolicy1 = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(
            self.lw_favorites.sizePolicy().hasHeightForWidth()
        )
        self.lw_favorites.setSizePolicy(sizePolicy1)
        font = QFont()
        font.setBold(True)
        self.lw_favorites.setFont(font)
        self.lw_favorites.setAcceptDrops(True)
        self.lw_favorites.setDragEnabled(True)
        self.lw_favorites.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.lw_favorites.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.lw_favorites.setAlternatingRowColors(False)
        self.lw_favorites.setSortingEnabled(False)

        self.verticalLayout.addWidget(self.lw_favorites)

        self.splitter.addWidget(self.groupBox)
        self.layoutWidget = QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_3 = QVBoxLayout(self.layoutWidget)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pbBack = QPushButton(self.layoutWidget)
        self.pbBack.setObjectName("pbBack")

        self.horizontalLayout.addWidget(self.pbBack)

        self.pb_root = QPushButton(self.layoutWidget)
        self.pb_root.setObjectName("pb_root")

        self.horizontalLayout.addWidget(self.pb_root)

        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.verticalLayout_3.addLayout(self.horizontalLayout)

        self.gb_file_browser = QGroupBox(self.layoutWidget)
        self.gb_file_browser.setObjectName("gb_file_browser")
        self.gb_file_browser.setStyleSheet("")
        self.verticalLayout_2 = QVBoxLayout(self.gb_file_browser)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.treeView = VTreeView(self.gb_file_browser)
        self.treeView.setObjectName("treeView")
        sizePolicy2 = QSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding
        )
        sizePolicy2.setHorizontalStretch(1)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.treeView.sizePolicy().hasHeightForWidth())
        self.treeView.setSizePolicy(sizePolicy2)
        self.treeView.setAcceptDrops(False)
        self.treeView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.treeView.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked
            | QAbstractItemView.EditTrigger.EditKeyPressed
        )
        self.treeView.setDragEnabled(True)
        self.treeView.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)
        self.treeView.setDefaultDropAction(Qt.DropAction.CopyAction)
        self.treeView.setAlternatingRowColors(True)
        self.treeView.setIndentation(7)
        self.treeView.setRootIsDecorated(False)
        self.treeView.setItemsExpandable(False)
        self.treeView.setSortingEnabled(True)
        self.treeView.setAnimated(True)
        self.treeView.header().setVisible(False)
        self.treeView.header().setCascadingSectionResizes(False)
        self.treeView.header().setProperty("showSortIndicator", False)
        self.treeView.header().setStretchLastSection(True)

        self.verticalLayout_2.addWidget(self.treeView)

        self.verticalLayout_3.addWidget(self.gb_file_browser)

        self.splitter.addWidget(self.layoutWidget)
        self.splitter_2.addWidget(self.splitter)
        self.browser = QWebEngineView(self.splitter_2)
        self.browser.setObjectName("browser")
        sizePolicy3 = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        sizePolicy3.setHorizontalStretch(1)
        sizePolicy3.setVerticalStretch(1)
        sizePolicy3.setHeightForWidth(self.browser.sizePolicy().hasHeightForWidth())
        self.browser.setSizePolicy(sizePolicy3)
        self.browser.setStyleSheet("")
        self.browser.setUrl(QUrl("about:blank"))
        self.splitter_2.addWidget(self.browser)

        self.horizontalLayout_2.addWidget(self.splitter_2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 1188, 34))
        self.menuOptions = QMenu(self.menubar)
        self.menuOptions.setObjectName("menuOptions")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuOptions.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuOptions.addAction(self.action_hide_files)
        self.menuOptions.addAction(self.actionHide_Toolbar)
        self.menuHelp.addAction(self.actionAbout)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("")
        self.actionExit.setText(QCoreApplication.translate("MainWindow", "Exit", None))
        self.actionRefresh_Assembly_List.setText(
            QCoreApplication.translate("MainWindow", "Refresh Assembly List", None)
        )
        self.actionHide_Toolbar.setText(
            QCoreApplication.translate("MainWindow", "Hide Toolbar", None)
        )
        self.actionAbout.setText(
            QCoreApplication.translate("MainWindow", "About", None)
        )
        self.action_hide_files.setText(
            QCoreApplication.translate("MainWindow", "Hide Files", None)
        )
        self.groupBox.setTitle(
            QCoreApplication.translate("MainWindow", "Favorites:", None)
        )
        self.pbBack.setText(QCoreApplication.translate("MainWindow", "< Back", None))
        self.pb_root.setText(QCoreApplication.translate("MainWindow", "Root", None))
        self.gb_file_browser.setTitle("")
        self.menuOptions.setTitle(
            QCoreApplication.translate("MainWindow", "Options", None)
        )
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", "Help", None))

    # retranslateUi
