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
from plot import plot_chromatograph, closest_peak, peak_position, highlight_base
from sequence_utils import reverse_complement
from info import aboutMessage



# Functions



# Classes
class SingleChromCanvas(FigureCanvas):
    """Canvas with one chromatograph."""
    def __init__(self, parent=None, width=18, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)  # Parent is the main widget

        self.fig.set_facecolor(self.rgba_to_zeroone(QtGui.QColor(QtGui.QPalette.Background).toTuple()))
        self.axes = self.fig.add_subplot(111)


        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


    @staticmethod
    def rgba_to_zeroone(rgba):
        return tuple(1.0 - 1.0 * c / 255.0 for c in rgba)



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
        self.initFigure()

        # Sequence row
        self.initSequenceWidget()

        # Range row
        self.initRangeWidget()

        # Button Signal/Slots
        self.goButton.clicked.connect(self.updatePlotRange)
        self.canvas.mpl_connect('button_press_event', self.toggleHighlight)

    
    # Initialization functions
    def initMenuBar(self):
        self.fileMenu = QtGui.QMenu('&File', self)
        self.fileMenu.addAction('&Open', self.fileOpen,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_O)
        self.fileMenu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.fileMenu)

        self.viewMenu = QtGui.QMenu('&View', self)
        self.viewMenu.addAction('&View complete sequence', self.viewViewCompleteSeq,
                                QtCore.Qt.CTRL + QtCore.Qt.Key_H)
        self.viewMenu.addAction('&Reverse complement', self.viewReverseComplement,
                                QtCore.Qt.CTRL + QtCore.Qt.Key_R)
        self.menuBar().addMenu(self.viewMenu)

        self.helpMenu = QtGui.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.helpMenu)
        self.helpMenu.addAction('&About', self.helpAbout)


    def initTitleWidget(self):
        self.title = QtGui.QLabel()
        if self.seq is not None:
            self.title.setText(self.seq.name)
        titlefont = QtGui.QFont()
        titlefont.setPointSize(14)
        self.title.setFont(titlefont)
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.vboxl.addWidget(self.title)


    def initFigure(self):
        plot_chromatograph(self.seq, self.canvas.axes)
        self.statusBar().showMessage("Sample data loaded.", 2000)


    def initSequenceWidget(self):
        self.seq_widget = QtGui.QWidget(self.main_widget)
        seqbox = QtGui.QHBoxLayout(self.seq_widget)
        seqTextl = QtGui.QLabel()
        seqTextl.setText('Sequence: ')
        self.seqText = seqText = QtGui.QLineEdit()
        self.setSeqString(self.seq)
        seqbox.addWidget(seqTextl)
        seqbox.addWidget(seqText)
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
        self.setSeqRange(self.seq)
        self.goButton = rangegobutton = QtGui.QPushButton('Go')
        rangebox.addWidget(rangel1)
        rangebox.addWidget(ranget1)
        rangebox.addWidget(rangel2)
        rangebox.addWidget(ranget2)
        rangebox.addWidget(rangegobutton)
        self.vboxl.addWidget(self.range_widget)


    # Getters & setters
    def seqString(self):
        '''Get the sequence string'''
        return self.seqText.text()


    def setSeqString(self, seq):
        '''Set the sequence string'''
        if seq:
            self.seqText.setText(str(seq.seq))
        else:
            self.seqText.setText('')
        self.seqText.setReadOnly(True)


    def setSeqRange(self, seq):
        '''Update the seqranges'''
        self.range1.clear()
        self.range2.clear()
        if seq is not None:
            self.range1.insert('0')
            self.range2.insert(str(len(seq)))


    def updatePlotRange(self):
        start = int(self.range1.text())
        end = int(self.range2.text())
        self.canvas.axes.clear()
        plot_chromatograph(self.seq, self.canvas.axes, peaklim=[start, end])
        if hasattr(self, 'hl_base'):
            if not (start <= self.hl_base['index'] < end):
                del self.hl_base
            else:
                self.hl_base = highlight_base(self.hl_base['peak'], self.seq, self.canvas.axes)
        self.setSeqString(self.seq[start: end + 1])
        if hasattr(self, 'hl_base'):
            self.seqText.setCursorPosition(max(0, self.hl_base['index'] - 5))
            self.seqText.repaint()
            self.seqText.setSelection(self.hl_base['index'] - int(self.range1.text()), 1)
        self.canvas.draw()


    def computeNewFigure(self, seq):
        self.canvas.axes.clear()
        plot_chromatograph(self.seq, self.canvas.axes,
                           xlim=(int(self.range1.text()), int(self.range2.text())))
        self.statusBar().showMessage("New data loaded.", 2000)


    # Menu Events
    def fileQuit(self):
        self.close()


    def fileOpen(self):
        fname, _ = QtGui.QFileDialog.getOpenFileName(self, 'Open file')
        if fname:
            self.seq = seq = parse_abi(fname)
            self.computeNewFigure(seq)
            if self.seq is not None:
                self.title.setText(self.seq.name)
            self.setSeqString(seq)
            self.setSeqRange(seq)
            self.canvas.draw()
            self.statusBar().showMessage("Data loaded.", 2000)
        else:
            self.statusBar().showMessage("File not found.", 2000)


    def viewViewCompleteSeq(self):
        self.setSeqRange(self.seq)
        self.updatePlotRange()


    def viewReverseComplement(self):
        self.seq = seq = reverse_complement(self.seq)
        self.computeNewFigure(seq)
        if hasattr(self, 'hl_base'):
            pos_click = peak_position(len(seq) - 1 - self.hl_base['index'], self.seq)
            try:
                self.hl_base = highlight_base(pos_click, self.seq, self.canvas.axes)
            except ValueError:
                del self.hl_base
        self.setSeqString(self.seq[int(self.range1.text()): int(self.range2.text())])
        if hasattr(self, 'hl_base'):
            self.seqText.setCursorPosition(max(0, self.hl_base['index'] - 5))
            self.seqText.repaint()
            self.seqText.setSelection(self.hl_base['index'] - int(self.range1.text()), 1)
        self.canvas.draw()
        self.statusBar().showMessage("Reverse complement.", 2000)


    def closeEvent(self, ce):
        self.fileQuit()


    def helpAbout(self):
        QtGui.QMessageBox.about(self, "About", aboutMessage)


    # Other events
    def toggleHighlight(self, ev):
        '''Toggle highlight of a base if it's clicked'''
        if ev.inaxes != self.canvas.axes:
            return

        if hasattr(self, 'hl_base'):
            self.hl_base['rec'].remove()
            if self.hl_base['index'] == closest_peak(ev.xdata, self.seq)['index']:
                del self.hl_base
                return
        try:
            self.hl_base = highlight_base(ev.xdata, self.seq, self.canvas.axes)
        except ValueError:
            return
        self.canvas.draw()

        if hasattr(self, 'hl_base'):
            self.seqText.setCursorPosition(max(0, self.hl_base['index'] - 5))
            self.seqText.repaint()
            self.seqText.setSelection(self.hl_base['index'] - int(self.range1.text()), 1)



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
