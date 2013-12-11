# vim: fdm=indent
'''
author:     Fabio Zanini
date:       10/12/13
content:    GUI interface for Sanger chromatographs.
'''
# Modules
import sys
import matplotlib
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4']='PySide'
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide import QtCore, QtGui

from plot import plot_chromatograph


# Functions
def rgba_to_zeroone(rgba):
    return tuple(1.0 - 1.0 * c / 255.0 for c in rgba)



# Classes
class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, seq, parent=None, width=18, height=6, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.set_facecolor(rgba_to_zeroone(QtGui.QColor(QtGui.QPalette.Background).toTuple()))

        self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)

        # Store the sequence object
        self.seq = seq

        # Plot the chromatograph
        self.compute_initial_figure()
        fig.tight_layout(rect=(0.03, 0, 0.98, 0.95))

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


    def compute_initial_figure(self):
        self.axes.hold(True)
        plot_chromatograph(self.seq, self.axes)
        self.axes.hold(False)


    def update_plot_range(self, start, end):
        self.axes.clear()
        self.axes.hold(True)
        plot_chromatograph(self.seq, self.axes, xlim=[start, end])
        self.axes.hold(False)
        self.draw()


    def compute_new_figure(self, seq):
        self.seq = seq
        self.axes.clear()
        self.compute_initial_figure()
        self.draw()



class ApplicationWindow(QtGui.QMainWindow):
    def __init__(self, seq):
        QtGui.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("PySang")

        self.file_menu = QtGui.QMenu('&File', self)
        self.file_menu.addAction('&Open', self.fileOpen,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_O)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QtGui.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)

        self.main_widget = QtGui.QWidget(self)
        l = QtGui.QVBoxLayout(self.main_widget)

        # Title row
        self.title_widget = QtGui.QWidget(self.main_widget)
        titlebox = QtGui.QHBoxLayout(self.title_widget)
        titlefont = QtGui.QFont()
        titlefont.setPointSize(14)
        title = QtGui.QLabel()
        title.setText(seq.name)
        title.setFont(titlefont)
        titlebox.addWidget(title, alignment=QtCore.Qt.AlignCenter)
        l.addWidget(self.title_widget)

        # Main figure
        self.canvas = sc = MyMplCanvas(seq, self.main_widget, dpi=100)
        l.addWidget(sc)

        # Sequence row
        self.seq_widget = QtGui.QWidget(self.main_widget)
        seqbox = QtGui.QHBoxLayout(self.seq_widget)
        seqtextl = QtGui.QLabel()
        seqtextl.setText('Sequence: ')
        seqtext = QtGui.QLineEdit()
        seqtext.setText(str(seq.seq))
        seqtext.setReadOnly(True)
        seqbox.addWidget(seqtextl)
        seqbox.addWidget(seqtext)
        l.addWidget(self.seq_widget)

        # Range row
        self.range_widget = QtGui.QWidget(self.main_widget)
        rangebox = QtGui.QHBoxLayout(self.range_widget)
        rangel1 = QtGui.QLabel()
        rangel1.setText('Show from nucleotide: ')
        rangel2 = QtGui.QLabel()
        rangel2.setText(' to: ')
        self.range1 = ranget1 = QtGui.QLineEdit()
        ranget1.setValidator(QtGui.QIntValidator(0, 10000))
        ranget1.insert('0')
        self.range2 = ranget2 = QtGui.QLineEdit()
        ranget2.setValidator(QtGui.QIntValidator(0, 10000))
        ranget2.insert(str(len(seq)))
        self.goButton = rangegobutton = QtGui.QPushButton('Go')
        rangebox.addWidget(rangel1)
        rangebox.addWidget(ranget1)
        rangebox.addWidget(rangel2)
        rangebox.addWidget(ranget2)
        rangebox.addWidget(rangegobutton)
        l.addWidget(self.range_widget)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.statusBar().showMessage("All hail matplotlib!", 2000)

        # Button Signal/Slots
        self.goButton.clicked.connect(self.update_plot)

    def update_plot(self):
        '''Update plot according to ranges'''
        r1 = int(self.range1.text())
        r2 = int(self.range2.text())
        self.canvas.update_plot_range(r1, r2)


    def fileQuit(self):
        self.close()


    def fileOpen(self):
        fname, _ = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '/home')
        if fname:
            seq = parse_abi(fname)
            self.canvas.compute_new_figure(seq)


    def closeEvent(self, ce):
        self.fileQuit()


    def about(self):
        QtGui.QMessageBox.about(self, "About",
"""embedding_in_qt4.py example
Copyright 2005 Florent Rougon, 2006 Darren Dale

This program is a simple example of a Qt4 application embedding matplotlib
canvases.

It may be used and modified with no restriction; raw copies as well as
modified versions may be distributed without limitation."""
)



# Test script
if __name__ == '__main__':

    from parser import parse_abi
    filename = 'test_data/FZ01_A12_096.ab1'
    seq = parse_abi(filename)

    app = QtGui.QApplication.instance()
    if app is None:
            app = QtGui.QApplication(sys.argv)

    win = ApplicationWindow(seq)
    win.show()
    sys.exit(app.exec_())
