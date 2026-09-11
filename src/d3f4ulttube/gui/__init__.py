"""
Optional desktop GUI for d3f4ulttube, built with PySide6 (or PySide2 as a
Qt5 fallback — note that Qt5's official Python binding is packaged as
"PySide2", not "PySide5").

This subpackage is never imported by the core library. Nothing under
`d3f4ulttube.gui` runs unless you explicitly launch it, so the base
package stays fully usable without Qt installed at all.

Install with GUI support:

    pip install d3f4ulttube[gui]       # PySide6 (Qt6, recommended)
    pip install d3f4ulttube[gui-qt5]   # PySide2 (Qt5)

Launch:

    d3f4ulttube-gui
    # or
    python -m d3f4ulttube.gui
"""
