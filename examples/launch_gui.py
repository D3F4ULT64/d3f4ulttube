"""
Launch the optional desktop GUI programmatically.

Requires: pip install d3f4ulttube[gui]   (or d3f4ulttube[gui-qt5])

Equivalent to running `d3f4ulttube-gui` from the command line.
"""

from d3f4ulttube.gui.app import main

if __name__ == "__main__":
    main()
