# Copyright (c) 2009 by Enthought, Inc.
# All rights reserved.

"""
This module provides an interface to appinst which allows installing
applications by specifying the path to a data file.  For an example of
such a data file see examples/appinst.dat, the example file contains
detailed comments about how this is done exactly.
"""


import sys

from appinst.application_menus import install, uninstall
from os.path import abspath, dirname, isfile, join


BIN_DIR = join(sys.prefix, 'Scripts' if sys.platform == 'win32' else 'bin')


def transform_shortcut(dat_dir, sc):
    """
    Transform the shortcuts relative paths to absolute paths.

    """
    # Make the path to the executable absolute
    bin = sc['cmd'][0]
    if bin.startswith('..'):
        bin = abspath(join(dat_dir, bin))
    else:
        bin = join(BIN_DIR, bin)
    sc['cmd'][0] = bin

    if (sys.platform == 'win32' and sc['terminal'] is False):
        script = bin + '-script.py'
        print script, isfile(script)
        if isfile(script):
            argv = [join(sys.prefix, 'pythonw.exe'), script]
            argv.extend(sc['cmd'][1:])
            sc['cmd'] = argv

    # Make the path of to icon files absolute
    for kw in ('icon', 'icns'):
        if kw in sc:
            sc[kw] = abspath(join(dat_dir, sc[kw]))


def transform(path):
    """
    Reads and parses the appinst data file and returns a tuple
    (menus, shortcuts) where menus and shortcuts are objects which
    the funtions install() and uninstall() in the application_menus
    module expects.

    """
    # default values
    d = {'MENUS': []}
    execfile(path, d)

    shortcuts = d['SHORTCUTS']
    for sc in shortcuts:
        transform_shortcut(dirname(path), sc)

    return d['MENUS'], shortcuts


def install_from_dat(path):
    """
    Does a complete install given a data file.
    
    For an example see examples/appinst.dat.

    """
    install(*transform(path))


def uninstall_from_dat(path):
    """
    Uninstalls all items in a data file.

    """
    uninstall(*transform(path))

