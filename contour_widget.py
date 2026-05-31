# Contour Plot .py
#=============================================================================================
# Import Library
from PySide6.QtWidgets import QWidget, QVBoxLayout
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1 import make_axes_locatable
#=============================================================================================

class ContourWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.figure.subplots_adjust(left=0.18, right=0.95/1.09, top=0.92, bottom=0.12)
        #self.figure.set_constrained_layout(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

        self.frames = []
        self.contour = None
        self.cbar = None
        
        # Color bar setting
        divider = make_axes_locatable(self.ax)
        self.cax = divider.append_axes(
            position="right",
            size="4%",     # 👈 ضخامت colorbar
            pad=0.04      # 👈 فاصله از کانتور
        )

    def set_data(self, frames):
        self.frames = frames

        self.ax.clear()
        self.cax.clear()

        # Cmap setting
        self.contour = self.ax.contourf(
            self.frames[0].T,
            levels=30,
            cmap="jet"
        )

        self.cbar = self.figure.colorbar(
            self.contour,
            cax=self.cax
        )

        self.ax.set_title("Contour")
        self.canvas.draw_idle()
        self.style_axes()


    def update_frame(self, idx):
        self.ax.clear()

        self.contour = self.ax.contourf(
            self.frames[idx].T,
            levels=15,
            cmap="jet"
        )

        #self.ax.set_aspect('equal')
        self.cbar.update_normal(self.contour)

        # Title setting
        self.ax.set_title(f"Frame {idx}", fontsize=6,pad=2)
        #self.figure.tight_layout()
        self.canvas.draw_idle()
        self.style_axes()



    def style_axes(self):
        # Axis setting
        self.ax.set_xlabel("X", fontsize=6, labelpad=2)
        self.ax.set_ylabel("Y", fontsize=6, labelpad=1)

        self.ax.tick_params(
            axis="both",
            labelsize=6,
            pad=2
        )

        if self.cbar:
            self.cbar.ax.tick_params(labelsize=6, pad=2)
            self.cbar.set_label("", fontsize=9, labelpad=3)

    
