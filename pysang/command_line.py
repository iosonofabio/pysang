# vim: fdm=indent
'''
author:     Fabio Zanini
date:       26/01/15
content:    Parser for command line arguments to PySang.
'''
# Modules
import sys
import argparse as ap


def main():
    parser = ap.ArgumentParser(description='PySang - Sanger chromatograph viewer',
                               formatter_class=ap.ArgumentDefaultsHelpFormatter)    
    parser.add_argument('--version', action='store_true',
                        help='Print version and exit')

    args = parser.parse_args()
    print_version = args.version

    if print_version:
        from pkg_resources import require
        print require('PySang')[0].version
        sys.exit()

    from gui import main as main_gui
    main_gui()


if __name__ == '__main__':
    main()
