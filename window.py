import os
import subprocess
import sys
from datetime import datetime

import requests
from PyQt5.QtCore import Qt, QPoint, QThread
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, \
    QComboBox, QTextEdit, QDesktopWidget, QLineEdit, QFileDialog
import validate
from installer import InstallWorker
from redirector import StreamRedirector
from styles import console_style, dark_theme_style

version = "2.1.0"
update_url = "https://jbruth.com/v/updater.info.json"

class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super(CustomTitleBar, self).__init__(parent)
        self.setFixedHeight(30)

        # Create the header widget and its layout
        self.header = QWidget(self)
        self.header.setObjectName("header")
        headerLayout = QHBoxLayout(self.header)
        headerLayout.setContentsMargins(0, 0, 0, 0)
        headerLayout.setSpacing(0)

        # Create title and buttons
        self.title = QLabel("Custom Installer - v"+version, self.header)
        self.title.setObjectName("title")
        self.btn_minimize = QPushButton("-", self.header)
        self.btn_minimize.setObjectName("btn_minimize")
        self.btn_minimize.setFixedSize(30, 30)
        self.btn_close = QPushButton("x", self.header)
        self.btn_close.setObjectName("btn_close")
        self.btn_close.setFixedSize(30, 30)

        # Add widgets to the header layout
        headerLayout.addWidget(self.title)
        headerLayout.addWidget(self.btn_minimize)
        headerLayout.addWidget(self.btn_close)

        # Set the layout for the header widget
        self.header.setLayout(headerLayout)

        # Main layout for the CustomTitleBar
        layout = QHBoxLayout(self)
        layout.addWidget(self.header)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins to fit the header exactly
        layout.setSpacing(0)
        self.setLayout(layout)


        # Connect buttons to functions
        self.btn_close.clicked.connect(self.close_app)
        self.btn_minimize.clicked.connect(self.minimize_app)

        self.start = QPoint(0, 0)
        self.pressing = False

    def mousePressEvent(self, event):
        self.start = self.mapToGlobal(event.pos())
        self.pressing = True

    def mouseMoveEvent(self, event):
        if self.pressing:
            end = self.mapToGlobal(event.pos())
            movement = end - self.start
            self.parent().move(self.parent().pos() + movement)
            self.start = end

    def mouseReleaseEvent(self, event):
        self.pressing = False

    def close_app(self):
        self.parent().close()

    def minimize_app(self):
        self.parent().showMinimized()


class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data = None
        self.fetch_data()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("SIT Tarkov Installer")
        self.setGeometry(100, 100, 400, 475)  # x, y, width, height
        self.setStyleSheet(dark_theme_style)
        self.titleBar = CustomTitleBar(self)
        self.titleBar.setObjectName("test")
        self.setMenuWidget(self.titleBar)  # Set the custom title bar
        self.centerWindow()
        self.initUI()
        self.checkForUpdates()
        self.show()
        self.updateSize()


    def initUI(self):
        # Redirect stdout
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet(console_style)  # Keep console style unchanged
        self.original = None # sys.stdout
        sys.stdout = StreamRedirector(self.console)
        sys.stderr = StreamRedirector(self.console)
        # Central widget and layout
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        layout = QVBoxLayout()
        centralWidget.setObjectName("main")

        # Update banner
        self.updateBanner = QWidget()
        self.updateBanner.setObjectName("banner")
        updateBannerLayout = QHBoxLayout(self.updateBanner)
        updateBannerLayout.setContentsMargins(0, 0, 0, 0)  # Adjust margins as needed

        updateLabel = QLabel("Update available")
        updateBannerLayout.addWidget(updateLabel)

        # self.downloadButton = QPushButton("Download")
        # self.downloadButton.clicked.connect(self.downloadUpdate)  # Implement this method
        # updateBannerLayout.addWidget(self.downloadButton)

        dismissButton = QPushButton("X")
        dismissButton.setObjectName("dismiss-update")
        dismissButton.clicked.connect(self.updateBanner.hide)  # Simply hide the banner for dismiss
        dismissButton.setFixedWidth(40)
        updateBannerLayout.addWidget(dismissButton)

        layout.addWidget(self.updateBanner)

        horz = QHBoxLayout()
        horz.addWidget(QLabel("      Game"))
        # Game selection
        self.gameCombo = QComboBox()
        self.gameCombo.addItems(self.fetch_games())
        self.gameCombo.currentIndexChanged.connect(self.game_changed)  # Connect game change signal to handler
        horz.addWidget(self.gameCombo,1)
        layout.addLayout(horz)

        horz = QHBoxLayout()
        horz.addWidget(QLabel("   Version"))
        # Version selection
        self.versionCombo = QComboBox()
        versions = self.fetch_versions(self.gameCombo.currentText())
        self.versionCombo.addItems(versions)
        self.versionCombo.currentIndexChanged.connect(self.version_changed)  # Connect version change signal to handler
        horz.addWidget(self.versionCombo,1)
        layout.addLayout(horz)


        horz = QHBoxLayout()
        horz.addWidget(QLabel("Directory"))
        self.filePath = QLineEdit()
        self.filePath.setPlaceholderText("Directory")
        self.filePath.setText(os.path.join(os.getcwd()))
        horz.addWidget(self.filePath)
        self.browseButton = QPushButton('Browse...')
        self.browseButton.clicked.connect(self.browse_file_path)
        horz.addWidget(self.browseButton)
        layout.addLayout(horz)

        # Buttons
        buttonLayout = QHBoxLayout()
        self.installButton = QPushButton("Install")
        self.installButton.clicked.connect(self.startInstall)
        buttonLayout.addWidget(self.installButton)
        self.setupInstall()

        self.verifyButton = QPushButton("Verify")
        self.verifyButton.clicked.connect(self.verify)
        buttonLayout.addWidget(self.verifyButton)

        layout.addLayout(buttonLayout)

        # Console output area
        layout.addWidget(self.console)

        centralWidget.setLayout(layout)
        self.loadVersionDetails()

    def closeEvent(self, event):
        # Restore the original stdout and stderr before closing the window
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        super().closeEvent(event)

    def scroll(self):
        self.console.verticalScrollBar().setValue(self.console.verticalScrollBar().maximum())

    def browse_file_path(self):
        # Open a dialog to choose a directory instead of a file
        directory_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory_path:  # Check if a directory was selected
            self.filePath.setText(directory_path)  # Update the line edit with the selected directory path

    def fetch_data(self):
        # Mocked method to return your JSON data
        # Replace with actual fetching code if needed
        response = requests.get(update_url)
        self.data = response.json()  # Use this line if fetching from URL
        # data = your_json_data_here  # Use your provided JSON data

    def fetch_games(self):
        # Assuming 'data' is the JSON from the provided URL or example
        return list(self.data['games'].keys())

    def fetch_versions(self, game):
        versions = list(self.data['games'][game]['versions'].keys())
        return versions

    def game_changed(self, index):
        selected_game = self.gameCombo.currentText()
        versions = self.fetch_versions(selected_game)
        self.versionCombo.clear()
        self.versionCombo.addItems(versions)

    def version_changed(self, index):
        selected_version = self.versionCombo.currentText()

    def checkForUpdates(self):
        try:
            local_manager_version = version
            remote_manager_version = self.data["manager"]
            self.hideUpdateBanner()
            # if validate.newer(remote_manager_version, local_manager_version):
            #     self.hideUpdateBanner()
            # else:
            #     self.showUpdateBanner()

        except Exception as e:
            print(f"Error checking for updates: {e}")

    def showUpdateBanner(self):
        # Show the update banner
        self.updateBanner.show()

    def hideUpdateBanner(self):
        # Hide the update banner
        self.updateBanner.hide()

    def loadVersionDetails(self):
        try:
            version_details = self.getVersion()
            self.console.clear()
            steps = version_details["steps"]
            # for step in steps:
            #     print(f"{step['name']}: ✔️")
        except requests.RequestException as e:
            print(f"Failed to load version details: {e}")

    def centerWindow(self):
        qt_rectangle = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())

    def disableControls(self):
        self.installButton.setDisabled(True)
        self.verifyButton.setDisabled(True)
        self.downloadButton.setDisabled(True)
        self.versionCombo.setDisabled(True)

    def enableControls(self):
        self.installButton.setDisabled(False)
        self.verifyButton.setDisabled(False)
        self.downloadButton.setDisabled(False)
        self.versionCombo.setDisabled(False)

    def updateSize(self):
        self.scrollToBottomButton = QPushButton("▼", self)
        self.scrollToBottomButton.setObjectName("scroll-to-bottom")
        self.scrollToBottomButton.resize(10, 12)
        self.scrollToBottomButton.clicked.connect(
            lambda: self.console.verticalScrollBar().setValue(self.console.verticalScrollBar().maximum()))
        scrollbar = self.console.verticalScrollBar()

        def updateButtonPosition():
            self.scrollToBottomButton.setVisible(scrollbar.maximum() > 0)

        self.console.resizeEvent = lambda event: updateButtonPosition()
        scrollbar.rangeChanged.connect(updateButtonPosition)  # Connect to rangeChanged for content changes
        updateButtonPosition()  # Initial positioning and visibility check
        console = self.console
        self.scrollToBottomButton.move(console.x() + console.width() - 10, console.y() + console.height() + 18)
        # self.scrollToBottomButton.show()
        self.scroll()
    def getVersion(self):
        return self.data["games"][self.gameCombo.currentText()]["versions"][self.versionCombo.currentText()]

    def setupInstall(self):
        # Setup the thread and worker
        self.thread = QThread()
        self.worker = InstallWorker(self.getVersion, self.gameCombo, self.versionCombo, self.filePath)
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(self.done)  # Clean up the thread when done
        self.worker.progress.connect(self.updateConsole)  # Connect to a method to update the console
        self.thread.started.connect(self.worker.run)

    def done(self):
        self.thread.quit()
    def updateConsole(self,msg):
        if(len(msg) <= 0):
            return
        console = self.console.toPlainText()
        if '\r' in msg:
            console = console[0:console.rindex('\n')]
            self.console.setPlainText(console + msg)
            cursor = self.console.textCursor()
            cursor.movePosition(cursor.End)
            self.console.setTextCursor(cursor)
        else:
            self.console.insertPlainText(msg)
        if self.console.verticalScrollBar().value() < self.console.verticalScrollBar().maximum():
            self.scroll()

    def startInstall(self):
        path = self.filePath.text() + "/" + self.gameCombo.currentText() + "." + self.versionCombo.currentText()
        log_path = os.path.join(path, f"logs/{self.gameCombo.currentText()}.{self.versionCombo.currentText()}.log")
        sys.stdout = StreamRedirector(self.console, log_path)
        sys.stderr = StreamRedirector(self.console, log_path)
        os.makedirs(path, exist_ok=True)
        os.makedirs(os.path.join(path,"logs"), exist_ok=True)

        self.console.clear()
        self.setupInstall()  # Setup the thread and worker
        self.thread.start()  # Start the thread

    # Slot for query button click
    def verify(self):
        # self.disableControls()
        print("Verifying...")




# Main application code
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainUI = MainUI()
    sys.exit(app.exec_())
