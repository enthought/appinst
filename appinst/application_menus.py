# Copyright (c) 2008-2009 by Enthought, Inc.
# All rights reserved.


import os
import platform
import sys
import warnings

from os.path import dirname, join


# The custom_tools package is importable when the Python was created by an
# "enicab" installer, in which case the directory custom_tools contains 
# platform-independent install information in __init__.py and platform-specific
# information about user setting chosen during the install process. 
# For example, on Windows the enicab generated MSI creates a file called 
# Property.dat with settings such as whether or not the user granted permission
# to create desktop and quicklaunch icons, and whether the user chose to make
# this a user-specific install or an install for all users.
try:
    import custom_tools as ct
    HAS_CUSTOM = True
except ImportError:
    HAS_CUSTOM = False


# Determine the version of the current Python interpreter.
PY_MAJOR, PY_MINOR = sys.version_info[0:2]


def determine_platform():
    """
    Determine our current platform and version.  This needs to distinguish
    between, not only different OSes, but also different OS flavors
    (i.e Linux distributions) and versions of OSes.
    """
    plat = platform.system().lower()
    if plat == 'linux':
        plat, pver = platform.dist()[:2]
    elif plat == 'windows':
        pver = platform.win32_ver()[0]
    elif plat == 'darwin':
        pver = platform.mac_ver()[0]
    
    return plat, pver
PLAT, PVER = determine_platform()


def get_default_menu():
    if HAS_CUSTOM:
        return [
          { # Top-level menu corresponds to manufacturer.
            'id': ct.Manufacturer.lower(),
            'name': ct.Manufacturer,
            'sub-menus': [
                { # Sub-menu correspond to product name and version.
                    'id': '%s-%s' % (ct.NAME.lower(), ct.FULL_VERSION.lower()),
                    'name': ct.FULL_NAME,
                    }],
            }]
    else:
        return [
          {
            'id': 'enthought',
            'name': 'Enthought',
            'sub-menus': [
                {
                    'id': 'python-2.5',
                    'name': 'Python-2.5',
                    }]
            }]


def install(menus, shortcuts, install_mode='user', uninstall=False):
    """
    Install an application menu according to the specified mode.

    This call is meant to work on all platforms.  If done on Linux, the menu
    will be installed to both Gnome and KDE desktops if they're available.

    Note that the information required is sufficient to install application
    menus on systems that follow the format of the Desktop Entry Specification
    by freedesktop.org.  See:
            http://freedesktop.org/Standards/desktop-entry-spec

    menus: A list of menu descriptions that will be added/merged into the OS's
        application menu.   A menu description is a dictionary containing the
        following keys and meanings:
            category: An optional identifier used to locate shortcuts within a
                menu.  Note that the string you specify here is not necessarily
                the full category you'll need to use in your shortcut as this
                package ensures uniqueness of category values by concatenating
                them as it goes down the menu hierarchy, using a '.' as the
                separator char.  For example, if a menu with category 'Abc'
                contains a sub-menu who's category is 'Def', then the full
                category for the sub-menu will be 'Abc.Def'.
            id: A string that can be used to represent the resources needed to
                represent the menu.  i.e. on Linux, the id is used for the name
                of the '.directory' file.  If no category is explicitly
                specified, the id is capitalized and used as the category
                specification.
            name: The display name of the menu.
            sub-menus: A list of menu descriptions that make up sub-menus of
                this menu.

    shortcuts: A list of shortcut specifications to be created within the
        previously specified menus.   A shortcut specification is a dictionary
        consisting of the following keys and values:
            categories: A list of the menu categories this shortcut should
                appear in.  We only support your own menus at this time due to
                cross-platform difficulties with identifying "standard"
                locations.
            cmd: A list of strings where the first item in the list is the
                executable command and the other items are arguments to be
                passed to that command.   Each argument should be a separate
                item in the list.   Note that you can use the special text
                markers listed here as the first command string to represent
                standard commands that are platform dependent:

                '{{FILEBROWSER}}' specifies that the following arguments are
                    paths to be opened in the OS's file system explorer.
                '{{WEBBROWSER}}' specifies that the following arguments are
                    paths to be opened in the OS's standard, or user's default,
                    web browser.

            comment: A description for the shortcut, typically becomes fly-over
                help.
            icon: An optional path to an .ico file to use as the icon for this
                shortcut.
            id: A string that can be used to represent the resources needed to
                represent the shortcut.  i.e. on Linux, the id is used for the
                name of the '.desktop' file.  If no id is provided, the name
                is lowercased and used as the id.
            name: The display name for this shortcut.
            terminal: A boolean value representing whether the shortcut should
                run within a shell / terminal.

    install_mode: should be either 'user' or 'system' and controls where the
        menus and shortcuts are installed on the system, depending on platform.

    TODO: Create separate APIs for product-specific shortcuts vs. generic
    shortcuts

    """
    # If we can, determine the install mode the user chose during the install
    # process.
    if HAS_CUSTOM:
        # FIXME: For now, we can only trust Property.dat on Windows.
        if sys.platform == 'win32':
            props = {}
            execfile(join(dirname(ct.__file__), 'Property.dat'), props)
            if props['ALLUSERS'] == '1':
                install_mode = 'system'

    # Validate we have a valid install mode.
    if install_mode not in ('user', 'system'):
        warnings.warn('Unknown install mode.  Must be either "user" or '
            '"system" but got "%s"' % install_mode)
        return

    # FIXME: Uninstall only support for Windows at this point.
    if uninstall and PLAT != 'windows':
        warnings.warn("Uninstall is currently only supported for Windows, "
            "not for platform: %s" % PLAT)
        return
    # 
    if not menus:
        menus = get_default_menu()
        product_category = '%s-%s' % (ct.NAME, ct.FULL_VERSION)
        product_category = product_category.lower().capitalize()
        for sc in shortcuts:
            sc['categories'] = [ct.Manufacturer + '.' + product_category]

    # XXX
    import pprint
    pp = pprint.PrettyPrinter(indent=4, width=20)
    print 'MENUS: %s' % pp.pformat(menus)
    print 'SHORTCUTS: %s' % pp.pformat(shortcuts)
    print 'INSTALL_MODE: %s' % install_mode

    # Dispatch for RedHat 3.
    if PLAT.startswith('redhat') and PVER[0] == '3':
        from appinst.platforms.rh3 import RH3
        RH3().install_application_menus(menus, shortcuts, install_mode)

    # Dispatch for RedHat 4.
    elif PLAT.startswith('redhat') and PVER[0] == '4':
        from appinst.platforms.rh4 import RH4
        RH4().install_application_menus(menus, shortcuts, install_mode)

    # Dispatch for RedHat 5.
    elif PLAT.startswith('redhat') and PVER[0] == '5':
        from appinst.platforms.rh5 import RH5
        RH5().install_application_menus(menus, shortcuts, install_mode)

    # Dispatch for all versions of OS X
    elif PLAT == 'darwin':
        from appinst.platforms.osx import OSX
        OSX().install_application_menus(menus, shortcuts, install_mode)

    # Dispatch for all versions of Windows (tested on XP only)
    elif PLAT == 'windows':
        from appinst.platforms.win32 import Win32
        Win32().install_application_menus(menus, shortcuts, install_mode,
            uninstall=uninstall)

    # Handle all other platforms with a warning until we implement for them.
    else:
        warnings.warn('Unhandled platform (%s) and version (%s). Unable '
            'to create application menu(s).' % (PLAT, PVER))

    return


def uninstall(menus, shortcuts, install_mode='user'):
    """
    Uninstall application menus.

    FIXME: This currently only works for Windows which can determine the install
    mode from the registry entry. There should be a method for linux as well
    which determines the installation type possibly from the install directory,
    a stored value, or user input.
    """
    install(menus, shortcuts, install_mode, uninstall=True)

