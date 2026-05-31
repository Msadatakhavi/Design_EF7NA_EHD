from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.figure import Figure
import numpy as np

class ProfileWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.figure.subplots_adjust(left=0.2, right=0.95, top=0.92, bottom=0.15)
        #self.figure.set_constrained_layout(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

        self.cranks = []
        self.values = []
        self.marker = None

    def set_profile(self, crank_angles, values, label="Profile"):
        self.cranks = crank_angles
        self.values = values

        self.ax.clear()
        self.ax.plot(self.cranks, self.values, linewidth=1)
        self.ax.set_aspect('auto')
        self.ax.relim()
        self.ax.autoscale_view()
        self.marker, = self.ax.plot(
            self.cranks[0], self.values[0],
            "ro", markersize=8
        )
        self.ax.set_aspect('auto')
        self.ax.relim()
        self.ax.autoscale_view()

        #self.ax.set_title(label, fontsize=9, pad=4)
        self.ax.set_xlabel("Crank Angle", fontsize=7, labelpad=6)
        self.ax.set_ylabel("Value", fontsize=7, labelpad=5)
        self.ax.tick_params(labelsize=5)
        self.ax.set_aspect('auto')
        self.ax.relim()
        self.ax.autoscale_view()

        self.canvas.draw_idle()

    def update_marker(self, idx):
        if idx >= len(self.cranks):
            return

        self.marker.set_data(
            [self.cranks[idx]],
            [self.values[idx]],
        )
        #self.figure.tight_layout()
        self.canvas.draw_idle()
