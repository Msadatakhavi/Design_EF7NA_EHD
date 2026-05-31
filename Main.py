# In the name of GOD

import os
import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QComboBox,
    QFileDialog,
    QMessageBox,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QGridLayout,
    QSizePolicy
)

from PySide6.QtCore import QTimer, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget

from data_loader import load_channel_folder
from contour_widget import ContourWidget
from profile_widget import ProfileWidget

from PySide6.QtWidgets import QSlider
from PySide6.QtCore import Qt


# ==========================================================
# SETUP WINDOW  (صفحه انتخاب پارامترها)
# ==========================================================

class SetupWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Engine Setup")
        self.resize(500, 650)

        self.data_root = None
        self.video_path = None

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # ---------------- Operating Point ----------------
        op_group = QGroupBox("Operating Point")
        op_layout = QVBoxLayout(op_group)

        self.ensp_combo = QComboBox()
        self.ensp_combo.addItems(["1000", "4500", "6000"])

        self.temp_combo = QComboBox()
        self.temp_combo.addItems(["60", "90", "140"])

        self.clrn_combo = QComboBox()
        self.clrn_combo.addItems(["17", "24", "33"])

        op_layout.addWidget(QLabel("Engine Speed (ENSP)"))
        op_layout.addWidget(self.ensp_combo)
        op_layout.addWidget(QLabel("Oil Temperature (TEMP)"))
        op_layout.addWidget(self.temp_combo)
        op_layout.addWidget(QLabel("Clearance (CLRN)"))
        op_layout.addWidget(self.clrn_combo)

        layout.addWidget(op_group)

        # ---------------- Channel Selection ----------------
        channel_group = QGroupBox("Select 4 Channels")
        channel_layout = QVBoxLayout(channel_group)

        self.channel_list = QListWidget()
        self.channel_list.setSelectionMode(QListWidget.MultiSelection)

        channels = [
            "BigEnd1/FILL", "BigEnd1/HOIL", "BigEnd1/PTOT",
            "MainBearing1/FILL", "MainBearing1/HOIL", "MainBearing1/PTOT",
            "MainBearing2/FILL", "MainBearing2/HOIL", "MainBearing2/PTOT",
            "MainBearing3/FILL", "MainBearing3/HOIL", "MainBearing3/PTOT",
        ]

        for ch in channels:
            QListWidgetItem(ch, self.channel_list)

        channel_layout.addWidget(self.channel_list)
        layout.addWidget(channel_group)

        # ---------------- Data Root ----------------
        self.data_btn = QPushButton("Select Data Root Folder")
        self.data_btn.clicked.connect(self.select_data_root)
        layout.addWidget(self.data_btn)

        # ---------------- Video ----------------
        self.video_btn = QPushButton("Select 3D Video")
        self.video_btn.clicked.connect(self.select_video)
        layout.addWidget(self.video_btn)

        # ---------------- Start ----------------
        self.run_btn = QPushButton("Start Visualization")
        self.run_btn.clicked.connect(self.start_visualization)
        layout.addWidget(self.run_btn)

        layout.addStretch()

    def select_data_root(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Data Root")
        if folder:
            self.data_root = folder

    def select_video(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select 3D Video",
            "",
            "Video Files (*.mp4 *.avi *.mov)"
        )
        if path:
            self.video_path = path

    def start_visualization(self):

        selected_items = self.channel_list.selectedItems()

        if len(selected_items) != 4:
            QMessageBox.warning(self, "Error", "Select exactly 4 channels")
            return

        params = {
            "ensp": self.ensp_combo.currentText(),
            "temp": self.temp_combo.currentText(),
            "clrn": self.clrn_combo.currentText(),
            "channels": [item.text() for item in selected_items],
            "data_root": self.data_root,
            "video_path": self.video_path
        }

        self.main_window = MainWindow(params)
        self.main_window.show()

        self.close()


# ==========================================================
# MAIN WINDOW (نمایش)
# ==========================================================

class MainWindow(QMainWindow):

    def __init__(self, params):
        super().__init__()

        self.params = params

        self.setWindowTitle("Engine Visualization Tool")
        #self.resize(1700, 950)
        self.resize(1280, 720)

        central = QWidget()
        self.setCentralWidget(central)

        # ================= OUTER LAYOUT =================
        self.outer_layout = QVBoxLayout(central)

        # ================= MAIN HORIZONTAL LAYOUT =================
        self.main_layout = QHBoxLayout()
        self.outer_layout.addLayout(self.main_layout)

        # ==========================================================
        # LEFT SIDE (VIDEO)
        # ==========================================================
        self.video_widget = QVideoWidget()
        self.video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()

        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)

        self.main_layout.addWidget(self.video_widget, 2)

        # ==========================================================
        # RIGHT SIDE (CONTOURS + PROFILES)
        # ==========================================================
        self.right_container = QWidget()
        self.right_layout = QGridLayout(self.right_container)
        self.right_layout.setHorizontalSpacing(15)
        self.right_layout.setVerticalSpacing(20)
        self.right_layout.setContentsMargins(10,10,10,10)


        self.main_layout.addWidget(self.right_container, 4)

        self.contour_widgets = []
        self.profile_widgets = []

        for i in range(4):

            container = QWidget()
            layout = QHBoxLayout(container)

            contour = ContourWidget()
            profile = ProfileWidget()

            contour.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            profile.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            layout.addWidget(contour, 4)
            layout.addWidget(profile, 3)

            self.right_layout.addWidget(container, i // 2, i % 2)

            self.contour_widgets.append(contour)
            self.profile_widgets.append(profile)

        # ==========================================================
        # PLAYBACK CONTROLS
        # ==========================================================
        self.control_container = QWidget()
        self.control_layout = QHBoxLayout(self.control_container)

        self.play_pause_btn = QPushButton("Pause")
        self.play_pause_btn.clicked.connect(self.toggle_play_pause)

        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setRange(0, 1000)
        self.timeline_slider.sliderMoved.connect(self.slider_moved)

        self.control_layout.addWidget(self.play_pause_btn)
        self.control_layout.addWidget(self.timeline_slider)

        self.outer_layout.addWidget(self.control_container)

        # ==========================================================
        # SIGNAL CONNECTIONS
        # ==========================================================
        self.media_player.positionChanged.connect(self.sync_animation_with_video)
        self.media_player.durationChanged.connect(self.update_slider_range)

        # ==========================================================
        # LOAD DATA
        # ==========================================================
        self.load_all_channels()

    # ==========================================================
    # LOAD ALL CHANNELS
    # ==========================================================

    def load_all_channels(self):

        ensp = self.params["ensp"]
        temp = self.params["temp"]
        clrn = self.params["clrn"]

        base_folder = os.path.join(
            self.params["data_root"],
            f"ENSP{ensp}_TEMP{temp}_CLRN{clrn}"
        )

        self.channel_frames = []
        self.channel_cranks = []

        for channel_name in self.params["channels"]:

            folder = os.path.join(base_folder, channel_name)

            frames, crank_angles = load_channel_folder(folder)

            self.channel_frames.append(frames)
            self.channel_cranks.append(crank_angles)

        # set contour & profile data
        for i in range(4):

            self.contour_widgets[i].set_data(self.channel_frames[i])

            channel_name = self.params["channels"][i]
            param = channel_name.split("/")[-1]

            if param == "PTOT":
                profile_values = [frame.max() for frame in self.channel_frames[i]]
            else:
                profile_values = [frame.min() for frame in self.channel_frames[i]]

            self.profile_widgets[i].set_profile(
                self.channel_cranks[i],
                profile_values,
                label=param
            )

        # load video
        if self.params["video_path"]:
            self.media_player.setSource(
                QUrl.fromLocalFile(self.params["video_path"])
            )
            self.media_player.play()

    # ==========================================================
    # PLAY / PAUSE
    # ==========================================================

    def toggle_play_pause(self):

        if self.media_player.playbackState() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.play_pause_btn.setText("Play")
        else:
            self.media_player.play()
            self.play_pause_btn.setText("Pause")

    # ==========================================================
    # UPDATE SLIDER RANGE
    # ==========================================================

    def update_slider_range(self, duration):
        self.timeline_slider.setRange(0, duration)

    # ==========================================================
    # SLIDER MOVED
    # ==========================================================

    def slider_moved(self, position):
        self.media_player.setPosition(position)

    # ==========================================================
    # SYNC VIDEO WITH ANIMATION
    # ==========================================================

    def sync_animation_with_video(self, position):

        if not hasattr(self, "channel_frames"):
            return

        duration = self.media_player.duration()
        if duration == 0:
            return

        # update slider safely
        self.timeline_slider.blockSignals(True)
        self.timeline_slider.setValue(position)
        self.timeline_slider.blockSignals(False)

        total_frames = len(self.channel_frames[0])

        frame_index = int((position / duration) * total_frames)

        if frame_index >= total_frames:
            frame_index = total_frames - 1

        for i in range(4):
            self.contour_widgets[i].update_frame(frame_index)
            self.profile_widgets[i].update_marker(frame_index)

# ==========================================================
# APPLICATION ENTRY
# ==========================================================

if __name__ == "__main__":
    os.environ["QT_OPENGL"] = "software"

    app = QApplication(sys.argv)

    setup = SetupWindow()
    setup.show()

    sys.exit(app.exec())
