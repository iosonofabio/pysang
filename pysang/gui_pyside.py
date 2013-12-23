# vim: fdm=indent
'''
author:     Fabio Zanini
date:       10/12/13
content:    GUI interface for Sanger chromatographs, using PySide (QT).
'''
# Modules
import sys
import matplotlib
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4'] = 'PySide'
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide import QtCore, QtGui

from parser import parse_abi
from plot import plot_chromatograph
from sequence_utils import reverse_complement
from info import aboutMessage



# Functions
def rgba_to_zeroone(rgba):
    return tuple(1.0 - 1.0 * c / 255.0 for c in rgba)



# Classes
class SingleChromCanvas(FigureCanvas):
    """Canvas with one chromatograph."""
    def __init__(self, parent=None, width=18, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)  # Parent is the main widget

        self.fig.set_facecolor(rgba_to_zeroone(QtGui.QColor(QtGui.QPalette.Background).toTuple()))
        self.axes = self.fig.add_subplot(111)


        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)



class ApplicationWindow(QtGui.QMainWindow):
    '''Main window of PySang'''

    def __init__(self, seq=None):
        # For the time being, work with a single chromatograph
        self.seq = seq

        QtGui.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("PySang")

        # Menu stuff
        self.initMenuBar()

        # Main widget (everything but menu/status bar, and possible dock widgets)
        self.main_widget = QtGui.QWidget(self)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        self.vboxl = QtGui.QVBoxLayout(self.main_widget)

        # Title row
        self.initTitleWidget()

        # Main figure
        self.canvas = SingleChromCanvas(self.main_widget, dpi=100)
        self.vboxl.addWidget(self.canvas)
        self.compute_initial_figure()

        # Sequence row
        self.initSequenceWidget()

        # Range row
        self.initRangeWidget()

        # Button Signal/Slots
        self.goButton.clicked.connect(self.update_plot)

    
    def initMenuBar(self):
        self.file_menu = QtGui.QMenu('&File', self)
        self.file_menu.addAction('&Open', self.fileOpen,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_O)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.options_menu = QtGui.QMenu('&Options', self)
        self.options_menu.addAction('&Reverse complement', self.optionsReverseComplement,
                                    QtCore.Qt.CTRL + QtCore.Qt.Key_R)
        self.menuBar().addMenu(self.options_menu)

        self.help_menu = QtGui.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.helpAbout)


    def initTitleWidget(self):
        self.title = QtGui.QLabel()
        if self.seq is not None:
            self.title.setText(self.seq.name)
        titlefont = QtGui.QFont()
        titlefont.setPointSize(14)
        self.title.setFont(titlefont)
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.vboxl.addWidget(self.title)


    def initSequenceWidget(self):
        self.seq_widget = QtGui.QWidget(self.main_widget)
        seqbox = QtGui.QHBoxLayout(self.seq_widget)
        seqtextl = QtGui.QLabel()
        seqtextl.setText('Sequence: ')
        self.seqtext = seqtext = QtGui.QLineEdit()
        self.set_seqstring(self.seq)
        seqbox.addWidget(seqtextl)
        seqbox.addWidget(seqtext)
        self.vboxl.addWidget(self.seq_widget)


    def initRangeWidget(self):
        self.range_widget = QtGui.QWidget(self.main_widget)
        rangebox = QtGui.QHBoxLayout(self.range_widget)
        rangel1 = QtGui.QLabel()
        rangel1.setText('Show from nucleotide: ')
        rangel2 = QtGui.QLabel()
        rangel2.setText(' to: ')
        self.range1 = ranget1 = QtGui.QLineEdit()
        ranget1.setValidator(QtGui.QIntValidator(0, 10000))
        self.range2 = ranget2 = QtGui.QLineEdit()
        ranget2.setValidator(QtGui.QIntValidator(0, 10000))
        self.set_seqrange(self.seq)
        self.goButton = rangegobutton = QtGui.QPushButton('Go')
        rangebox.addWidget(rangel1)
        rangebox.addWidget(ranget1)
        rangebox.addWidget(rangel2)
        rangebox.addWidget(ranget2)
        rangebox.addWidget(rangegobutton)
        self.vboxl.addWidget(self.range_widget)


    def set_seqstring(self, seq):
        '''Seq the sequence string'''
        if seq:
            self.seqtext.setText(str(seq.seq))
        else:
            self.seqtext.setText('')
        self.seqtext.setReadOnly(True)


    def set_seqrange(self, seq):
        '''Update the seqranges'''
        self.range1.clear()
        self.range2.clear()
        if seq is not None:
            self.range1.insert('0')
            self.range2.insert(str(len(seq)))


    def update_plot(self):
        '''Update plot according to ranges'''
        r1 = int(self.range1.text())
        r2 = int(self.range2.text())
        self.update_plot_range(r1, r2)
        self.set_seqstring(self.seq[r1: r2])


    def compute_initial_figure(self):
        plot_chromatograph(self.seq, self.canvas.axes)
        self.statusBar().showMessage("Sample data loaded.", 2000)


    def update_plot_range(self, start, end):
        self.canvas.axes.clear()
        plot_chromatograph(self.seq, self.canvas.axes, xlim=[start, end])
        self.canvas.draw()


    def compute_new_figure(self, seq):
        self.canvas.axes.clear()
        self.compute_initial_figure()
        self.canvas.draw()


    # Menu Events
    def fileQuit(self):
        self.close()


    def fileOpen(self):
        fname, _ = QtGui.QFileDialog.getOpenFileName(self, 'Open file')
        if fname:
            self.seq = seq = parse_abi(fname)
            self.compute_new_figure(seq)
            self.set_seqstring(seq)
            self.set_seqrange(seq)
            self.statusBar().showMessage("Data loaded.", 2000)
        else:
            self.statusBar().showMessage("File not found.", 2000)


    def optionsReverseComplement(self):
        self.seq = seq = reverse_complement(self.seq)
        self.compute_new_figure(seq)
        self.set_seqstring(seq)
        self.set_seqrange(seq)
        self.statusBar().showMessage("Reverse complement.", 2000)


    def closeEvent(self, ce):
        self.fileQuit()


    def helpAbout(self):
        QtGui.QMessageBox.about(self, "About", aboutMessage)


def main():

    from pkg_resources import resource_stream
    input_file = resource_stream(__name__, 'data/FZ01_A12_096.ab1')
    seq = parse_abi(input_file)

    app = QtGui.QApplication.instance()
    if app is None:
            app = QtGui.QApplication(sys.argv)

    win = ApplicationWindow(seq)
    win.show()
    sys.exit(app.exec_())



# Script
if __name__ == '__main__':

    main()
