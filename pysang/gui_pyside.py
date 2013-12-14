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
matplotlib.rcParams['backend.qt4']='PySide'
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide import QtCore, QtGui

from parser import parse_abi
from plot import plot_chromatograph
from sequence_utils import reverse_complement



# Functions
def rgba_to_zeroone(rgba):
    return tuple(1.0 - 1.0 * c / 255.0 for c in rgba)



# Classes
class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, seq=None, parent=None, width=18, height=6, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.set_facecolor(rgba_to_zeroone(QtGui.QColor(QtGui.QPalette.Background).toTuple()))

        self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)

        # Store the sequence object
        self.seq = seq

        # Plot the chromatograph
        self.compute_initial_figure()
        #fig.tight_layout(rect=(0.03, 0, 0.98, 0.95))

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
    def __init__(self, seq=None):
        self.seq = seq

        QtGui.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("PySang")

        # Menu stuff
        self.file_menu = QtGui.QMenu('&File', self)
        self.file_menu.addAction('&Open', self.fileOpen,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_O)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.options_menu = QtGui.QMenu('&Options', self)
        self.options_menu.addAction('&Reverse complement', self.reverseComplement,
                                    QtCore.Qt.CTRL + QtCore.Qt.Key_R)
        self.menuBar().addMenu(self.options_menu)

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
        if seq is not None:
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
        self.seqtext = seqtext = QtGui.QLineEdit()
        self.set_seqstring(seq)
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
        self.range2 = ranget2 = QtGui.QLineEdit()
        ranget2.setValidator(QtGui.QIntValidator(0, 10000))
        self.set_seqrange(seq)
        self.goButton = rangegobutton = QtGui.QPushButton('Go')
        rangebox.addWidget(rangel1)
        rangebox.addWidget(ranget1)
        rangebox.addWidget(rangel2)
        rangebox.addWidget(ranget2)
        rangebox.addWidget(rangegobutton)
        l.addWidget(self.range_widget)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.statusBar().showMessage("Sample data loaded.", 2000)

        # Button Signal/Slots
        self.goButton.clicked.connect(self.update_plot)


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
        self.canvas.update_plot_range(r1, r2)
        self.set_seqstring(self.seq[r1: r2])


    def fileQuit(self):
        self.close()


    def fileOpen(self):
        fname, _ = QtGui.QFileDialog.getOpenFileName(self, 'Open file')
        if fname:
            self.seq = seq = parse_abi(fname)
            self.canvas.compute_new_figure(seq)
            self.set_seqstring(seq)
            self.set_seqrange(seq)
            self.statusBar().showMessage("Data loaded.", 2000)
        else:
            self.statusBar().showMessage("File not found.", 2000)


    def reverseComplement(self):
        self.seq = seq = reverse_complement(self.seq)
        self.canvas.compute_new_figure(seq)
        self.set_seqstring(seq)
        self.set_seqrange(seq)
        self.statusBar().showMessage("Reverse complement.", 2000)


    def closeEvent(self, ce):
        self.fileQuit()


    def about(self):
        QtGui.QMessageBox.about(self, "About",
"""PySang: a Sanger chromatograph viewer.

Fabio Zanini

License: PySang is donated to the public domain. You may therefore freely copy \
it for any legal purpose you wish. Acknowledgement of authorship and citation \
in publications is appreciated.

Note: This program uses other Python modules that might have different license \
agreement. Those copyrights are still valid beyond this agreement. Thanks to \
the authors of those modules for their hard work.

Disclaimer of warranty
THIS SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESS \
OR IMPLIED, INCLUDING WITHOUT LIMITATION IMPLIED WARRANTIES OF MERCHANTABILITY \
AND FITNESS FOR A PARTICULAR PURPOSE. 
"""
)


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
