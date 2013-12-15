# vim: fdm=indent
'''
author:     Fabio Zanini
date:       13/12/13
content:    GUI for Sanger chromatographs, GUI library hub.
'''
# Functions
def main():

    try:
        import PySide
        from gui_pyside import main as main_gui

    except ImportError:
        try:
            import Tkinter
            from gui_tk import main as main_gui

        except ImportError:
            raise ImportError('Neither PySide nor Tk libraries found')

    main_gui()


# Script
if __name__ == '__main__':

    main()
