# vim: fdm=indent
'''
author:     Fabio Zanini
date:       13/12/13
content:    GUI interface for Sanger chromatographs, using Tk.
'''
# Modules
import sys
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvas
from matplotlib.figure import Figure
from Tkinter import *
import tkFileDialog, tkMessageBox

from parser import parse_abi
from plot import plot_chromatograph
from sequence_utils import reverse_complement



# Classes
class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, seq=None, parent=None, width=18, height=6, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.set_facecolor(parent['background'])

        self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)

        # Store the sequence object
        self.seq = seq

        # Plot the chromatograph
        self.compute_initial_figure()
        #fig.tight_layout(rect=(0.03, 0, 0.98, 0.95))

        FigureCanvas.__init__(self, fig, master=parent)


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



class ApplicationWindow(Tk):
    def __init__(self, seq=None):
        self.seq = seq

        Tk.__init__(self)
        self.title("PySang")

        # Menu stuff
        menu = Menu(self)
        self.config(menu=menu)
        self.file_menu = Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open", command=self.fileOpen, accelerator="Ctrl+O")
        self.file_menu.add_command(label="Quit", command=self.fileQuit, accelerator="Ctrl+Q")

        self.options_menu = Menu(menu, tearoff=0)
        menu.add_cascade(label='Options', menu=self.options_menu)
        self.options_menu.add_command(label='Reverse complement',
                                      command=self.reverseComplement,
                                      accelerator='Ctrl+R')

        self.help_menu = Menu(menu, tearoff=0)
        menu.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About", command=self.about)

        # Bind menu hotkeys
        self.bind_all("<Control-o>", self.fileOpen)
        self.bind_all("<Control-q>", self.fileQuit)
        self.bind_all("<Control-r>", self.reverseComplement)

        # Title row
        self.titlew = title = Label(master=self)
        if seq is not None:
            title.config(text=seq.name)
        title['font'] = ((title['font'], 14))
        title.pack(side=TOP, fill=BOTH, expand=1)

        # Main figure
        self.canvas = sc = MyMplCanvas(seq, self)
        sc.show()
        sc.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

        # Sequence row
        self.seq_widget = Frame(self)
        seqtextl = Label(master=self.seq_widget, text='Sequence: ')
        seqtextl.pack(side=LEFT, fill=BOTH, expand=0, padx=5)
        self.seqtext = seqtext = Entry(master=self.seq_widget)
        self.set_seqstring(seq)
        seqtext.pack(side=LEFT, fill=BOTH, expand=1, padx=5)
        self.seq_widget.pack(side=TOP, fill=BOTH, expand=1)

        # Range row
        self.integerValidatorCommand = self.register(self.integerValidator)
        self.range_widget = Frame(self)
        rangel1 = Label(master=self.range_widget, text='Show from nucleotide: ')
        rangel1.pack(side=LEFT, fill=BOTH, expand=0, padx=5)
        self.range1 = ranget1 = Entry(master=self.range_widget,
                                      validate='all',
                                      validatecommand=(self.integerValidatorCommand, '%P'))
        ranget1['background'] = '#FFFFFF'
        ranget1.pack(side=LEFT, fill=BOTH, expand=0, padx=5)
        rangel2 = Label(master=self.range_widget, text=' to: ')
        rangel2.pack(side=LEFT, fill=BOTH, expand=0, padx=5)
        self.range2 = ranget2 = Entry(master=self.range_widget,
                                      validate='all',
                                      validatecommand=(self.integerValidatorCommand, '%P'))
        ranget2['background'] = '#FFFFFF'
        ranget2.pack(side=LEFT, fill=BOTH, expand=0, padx=5)
        self.set_seqrange(seq)
        self.goButton = Button(master=self.range_widget, text='Go', command=self.update_plot)
        self.goButton.pack(side=LEFT, fill=BOTH, expand=1, padx=5)
        self.range_widget.pack(side=TOP, fill=BOTH, expand=1)

        # Status bar
        self.statusBar = Label(master=self, text="Sample data loaded", bd=1, relief=SUNKEN, anchor=W)
        self.statusBar.pack(side=BOTTOM, fill=X)


    def integerValidator(self, text):
        '''Check that the empty string or a positive integer has been entered'''
        if not text:
            return True
        try:
            i = int(text)
            return i >= 0
        except ValueError:
            return False
        

    def set_seqstring(self, seq):
        '''Seq the sequence string'''
        self.seqtext.config(state=NORMAL)
        self.seqtext.delete(0, END)
        if seq:
            self.seqtext.insert(END, str(seq.seq))
        self.seqtext.config(state="readonly")
        self.seqtext.config(background='#FFFFFF',
                            readonlybackground='#FFFFFF')


    def set_seqrange(self, seq):
        '''Update the seqranges'''
        self.range1.delete(0, END)
        self.range2.delete(0, END)
        if seq is not None:
            self.range1.insert(END, '0')
            self.range2.insert(END, str(len(seq)))


    def update_plot(self):
        '''Update plot according to ranges'''
        r1 = int(self.range1.get())
        r2 = int(self.range2.get())
        self.canvas.update_plot_range(r1, r2)
        self.set_seqstring(self.seq[r1: r2])


    def fileQuit(self, event=None):
        self.quit()


    def fileOpen(self, event=None):
        fname = tkFileDialog.askopenfilename()
        if fname:
            self.seq = seq = parse_abi(fname)
            self.canvas.compute_new_figure(seq)
            if seq is not None:
                self.titlew.config(text=seq.name)
            self.set_seqstring(seq)
            self.set_seqrange(seq)
            self.statusBar.config(text="Data loaded.")


    def reverseComplement(self, event=None):
            self.seq = seq = reverse_complement(self.seq)
            self.canvas.compute_new_figure(seq)
            self.set_seqstring(seq)
            self.set_seqrange(seq)
            self.statusBar.config(text="Reverse complement.")


    def closeEvent(self, ce):
        self.fileQuit()


    def about(self):
        tkMessageBox.showinfo("About",
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

    win = ApplicationWindow(seq)
    win.mainloop()
    

# Script
if __name__ == '__main__':

    main()
