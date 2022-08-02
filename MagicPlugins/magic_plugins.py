"""
MagicPlugins by Gilles Vink (2022)

Script to automatically load gizmo, nk and library files
and create menus

"""

import os
import nuke
import sys

# Only load if we have a GUI
if nuke.GUI:
    import install_plugin_dialog
    from shutil import copy2


class MagicPlugins(object):
    """Main class containing all functions to
    populate our menu and load plugins"""

    def __init__(self):
        """In the init function we will create the variables
        we need in the entire script to load the plugins.

        Like the directory to scan for plugins, the current Nuke version,
        and the list of plugins we want to load.

        In the menu_name variable we can assign the name for the menu."""

        # Startup message
        magic_plugins_version = 1.1
        self.__print("Version %s" % str(magic_plugins_version))

        # Getting install location to load plugins
        self.script_directory = os.path.dirname(os.path.realpath(__file__))
        plugins_directory = os.path.join(self.script_directory, "plugins")

        # Fix for Windows based systems
        self.plugins_directory = plugins_directory.replace(os.sep, "/")

        # Getting the current Nuke version required
        # to define which library file to use
        self.nuke_version = str(
            ("%i.%i" % (nuke.NUKE_VERSION_MAJOR, nuke.NUKE_VERSION_MINOR))
        )

        # Always collect all the plugins when this script is initialized
        self.plugins = self.__locate_plugins(self.plugins_directory)

        # This is the name we use for our menu in Nuke
        self.menu_name = "MagicPlugins"

        # These are the plugins we would call library
        self.library_extensions = (".dll", ".so", ".dylib")

    def load_plugins(self):
        """We will always use this function to load plugins
        in the init.py file"""

        # Print out that we are starting to load the plugins
        self.__print("Loading all plugins")
        added_directories = []

        for plugin in self.plugins:
            file_path = plugin.get("file_path")
            plugin_directory = os.path.dirname(file_path)

            if plugin_directory not in added_directories:
                nuke.pluginAddPath(plugin_directory)
                added_directories.append(plugin_directory)

        self.__print("Loaded plugins")

    def build_menu(self):
        """We will use this function in the menu.py file
        to build the menus in the UI"""

        self.__print("Adding plugins to menu")

        # Defining the toolbar to add menus to
        magic_toolbar = nuke.toolbar("Nodes")

        # Getting the collected plugins
        plugins = self.plugins

        # Via the create menu function we will build the folders in the menu
        self.__create_menus(magic_toolbar, plugins)

        # Via the populate menu function we will add the plugins in the menu
        self.__populate_menu(magic_toolbar, plugins)

        self.__print("Done, menu builded and populated with plugins :)")

    def install_plugin(self):
        """Using this function the user can install plugins
        easily via Nuke itself using a popup where the user
        can select the path to the plugin, select an icon
        and click install."""

        plugin_dialog = install_plugin_dialog.InstallPluginDialog()
        plugin_dialog.setMinimumSize(360, 380)
        if plugin_dialog.showModalDialog():
            file_path = plugin_dialog.plugin_file_path.value()

            # Making sure file is selected
            if not file_path == "":
                extension = os.path.splitext(file_path)[1]
                icon_path = plugin_dialog.icon_file_path.value()
                category = plugin_dialog.plugin_category.value()

                nuke_version = None

                if icon_path is "":
                    icon_path = None

                if file_path.endswith((".dll", ".so", ".dylib")):
                    nuke_version = plugin_dialog.library_nuke_version.value()

                # Installing plugin
                installation = self.__install_to_plugins(
                    plugin_path=file_path,
                    category=category,
                    icon_path=icon_path,
                    extension=extension,
                    nuke_version=nuke_version,
                )

                nuke.message(installation)
                self.__print(installation)

            # If no file is selected, let user know
            else:
                nuke.message("Please select a plugin file to install")

            return

    @staticmethod
    def __print(text):
        message = "[MagicPlugins] %s" % text
        print(message)

    def __install_to_plugins(
        self,
        plugin_path,
        category,
        extension,
        icon_path=None,
        nuke_version=None,
    ):
        """This function contains all the logic to copy the
        provided tool to the correct folder and ingest it into the
        Nuke menu so the artist can use it."""

        # Extract the plugin name, so we can use it for the name in Nuke
        plugin_name = os.path.basename(plugin_path)

        # If a Nuke version is provided, we will need to build an extra folder
        # Other than that we will build the install directory given
        # the provided variables
        if nuke_version:
            install_directory = os.path.join(
                self.plugins_directory,
                "Internet",
                category,
                nuke_version,
            )

        else:
            install_directory = os.path.join(
                self.plugins_directory,
                "Internet",
                category,
            )

        # Now we will append the plugin name to complete the install path
        # for the plugin
        plugin_install_path = os.path.join(install_directory, plugin_name)
        plugin_install_path = plugin_install_path.replace(os.sep, "/")

        # If an icon path is provided, we will build the installation
        # path for that one too
        if icon_path is not None:
            # Basically we will just get the name from the plugin, and replace
            # the extension with png, so it matches the plugin name
            icon_name = plugin_name.replace(extension, ".png")
            icon_install_path = os.path.join(install_directory, icon_name)
            icon_install_path = icon_install_path.replace(os.sep, "/")

        # If a plugin already exists, ask the user if overwrite is desired
        if os.path.isfile(plugin_install_path):
            if not nuke.ask(
                "There is already a plugin installed in that directory, "
                "do you want to overwrite the file?"
            ):
                self.__print("Installation aborted")
                return "Installation aborted"

        try:
            # Let's copy the plugin
            copy2(plugin_path, plugin_install_path)
            if icon_path is not None:
                copy2(icon_path, icon_install_path)

                # Prevent loading if it is not the correct Nuke version
                if nuke_version:
                    if not nuke_version == self.nuke_version:
                        return "Installation succesful for %s" % plugin_name

                # Now we will add the plugin to the menu, here
                # we will add the icon too
                self.__add_plugin_to_menu(
                    file_path=plugin_install_path,
                    plugin_name=plugin_name,
                    icon_path=icon_install_path,
                )

            else:

                # Prevent loading if it is not the correct Nuke version
                if nuke_version:
                    if not nuke_version == self.nuke_version:
                        return "Installation succesful for %s" % plugin_name

                # Now we will add the plugin to the menu, without icon
                self.__add_plugin_to_menu(
                    file_path=plugin_install_path,
                    plugin_name=plugin_name,
                )

            # Append the plugin path to Nuke
            nuke.pluginAddPath(install_directory)

            return "Installation succesful for %s" % plugin_name

        # If something went wrong, we will catch the error here,
        # and the artist will see it
        except Exception as error:
            return "Something went wrong... %s" % str(error)

    def __add_plugin_to_menu(self, file_path, plugin_name, icon_path=None):
        """Basically the same as the populate menu function, except we
        won't walk through a directory to add every plugin"""

        # Create the toolbar to add the node command to
        magic_toolbar = nuke.toolbar("Nodes")

        # Node types where we use the createNode() function
        node_types = (".gizmo", ".dll", ".dylib", ".so")

        # Get the plugin category for the plugin given the file path
        # so we can build the correct name in the menu
        menu_name = self.__get_plugin_category(file_path)

        # We need to scan every directory again to see new created directories
        plugins = self.__locate_plugins(self.plugins_directory)

        # Build new menu's
        self.__create_menus(magic_toolbar, plugins)

        # If the current plugin is a node,
        # like we specified in the node_types variable,
        # build the createNode() function
        if file_path.endswith(node_types):
            magic_toolbar.addCommand(
                menu_name,
                "nuke.createNode('%s')" % plugin_name,
                icon=icon_path,
            )

        # If the plugin is a Nuke file, we use the nodePaste() function
        elif file_path.endswith(".nk"):
            magic_toolbar.addCommand(
                menu_name,
                "nuke.nodePaste('%s')" % file_path,
                icon=icon_path,
            )

    def __create_menus(self, toolbar, plugins):
        """Via this function we will build the folders in the menu.
        We could skip this function, but if we want icons,
        (of course we want icons!), we need to build the menu first."""

        # Getting the directory to scan for plugins
        plugins_directory = self.plugins_directory

        menu_name = self.menu_name
        menu_icon = os.path.join(
            self.script_directory, "resources", "icon.png"
        )
        menu_icon = menu_icon.replace(os.sep, "/")

        # Creating the main menu item
        toolbar.addMenu(menu_name, icon=menu_icon)

        # We are collecting the length for the directory, to only keep
        # the category names.
        # Like we have //network_drive/nuke_plugins/plugins/myplugins/folder/
        # we keep /plugins/myplugins/folder/
        plugins_directory_length = len(plugins_directory) + 1

        plugin_file_paths = []

        # We build a little dictionary for the folders we need to scan
        for plugin in plugins:
            file_path = plugin.get("file_path")
            plugin_file_paths.append(file_path)

        # Walk through the dictionary to scan every folder, and
        # if possible, add an icon.
        for root, dirs, files in os.walk(plugins_directory):
            for directory in sorted(dirs):
                directory_path = os.path.join(root, directory)
                directory_path = directory_path.replace(os.sep, "/")

                # If the folder is added in the plugin_file_paths list, add
                # the folder as a menu item. This makes sure no empty folders
                # are added.
                if any(directory_path in s for s in plugin_file_paths):
                    directory_dirname = os.path.dirname(directory_path)
                    directory_name = directory

                    # We will build the possible icon path, and check if the
                    # icon exists.
                    directory_icon = directory_name + ".png"
                    icon_path = os.path.join(directory_dirname, directory_icon)
                    icon_path = icon_path.replace(os.sep, "/")

                    # Here we will build the directory path to only contain the
                    # path after the plugins folder, so we can save it as a
                    # category path to add in the menu
                    category = directory_path[plugins_directory_length:]

                    category = os.path.join(menu_name, category)
                    category = category.replace(os.sep, "/")

                    # If the icon exists, add it, otherwise just
                    # create a simple menu item
                    if os.path.isfile(icon_path):
                        toolbar.addMenu(category, icon=icon_path)

                    else:
                        toolbar.addMenu(category)

        # Adding a divider line to distinguish commands and plugins
        divider_name = os.path.join(menu_name, "-")
        divider_name = divider_name.replace(os.sep, "/")
        toolbar.addCommand(divider_name, "")

        # Add install plugin button
        install_plugin_name = os.path.join(menu_name, "Install plugin")
        install_plugin_name = install_plugin_name.replace(os.sep, "/")

        # Getting the icon path
        plugin_icon = os.path.join(
            self.script_directory, "resources", "install_plugin.png"
        )
        plugin_icon = plugin_icon.replace(os.sep, "/")

        toolbar.addCommand(
            install_plugin_name,
            "magic_plugins.install_plugin()",
            icon=plugin_icon,
        )

        # Add install plugin button
        open_folder_name = os.path.join(menu_name, "Open plugin folder")
        open_folder_name = open_folder_name.replace(os.sep, "/")

        # Getting the icon path
        folder_icon = os.path.join(
            self.script_directory, "resources", "open_folder.png"
        )
        folder_icon = folder_icon.replace(os.sep, "/")

        toolbar.addCommand(
            open_folder_name,
            "magic_plugins.open_folder()",
            icon=folder_icon,
        )

    def open_folder(self):
        """Via this function the user can
        easily open the folder where the plugins are located.

        It will open de file browser depending on the
        system the user is using.
        """
        plugin_folder = self.plugins_directory
        operating_system = sys.platform

        if operating_system == "darwin":
            os.system("open %s" % plugin_folder)

        elif operating_system == "win32":
            plugin_folder = os.path.normpath(plugin_folder)
            os.system("explorer %s" % plugin_folder)

        elif operating_system == "linux":
            os.system('xdg-open "%s"' % plugin_folder)

        else:
            nuke.critical("Couldn't find operating system")

    def __populate_menu(self, magic_toolbar, plugins):
        """Via this function we will add all
        the available plugins in the menu

        To use this function we need a specified
        toolbar and a plugin dictionary.
        """

        # Iterate trough the provided dictionary to add plugins
        for plugin in plugins:
            # Get the data for the plugin necessary to build the menu item
            plugin_name = plugin.get("plugin_name")
            plugin_type = plugin.get("plugin_type")
            file_path = plugin.get("file_path")
            icon_path = plugin.get("icon_path")

            # Node types where we use the createNode() function
            node_types = ("gizmo", "dll", "dylib", "so")

            # Get the plugin category for the plugin given the file path
            # so we can build the correct name in the menu
            menu_name = self.__get_plugin_category(file_path)

            # If the current plugin is a node,
            # like we specified in the node_types variable,
            # build the createNode() function
            if any(s in plugin_type for s in node_types):
                magic_toolbar.addCommand(
                    menu_name,
                    "nuke.createNode('%s')" % plugin_name,
                    icon=icon_path,
                )

            # If the plugin is a Nuke file, we use the nodePaste() function
            elif plugin_type == "nk":
                magic_toolbar.addCommand(
                    menu_name,
                    "nuke.nodePaste('%s')" % file_path,
                    icon=icon_path,
                )

    def __locate_plugins(self, plugins_directory):
        """This function will scan the specified folder for
        plugins, and build a list containing all necessary information
        to load the plugins"""

        # First we create an empty list where we will add al the plugins
        # we want to process to load
        plugins = []

        # Now we will walk through the entire
        # specified directory to scan for plugins
        for root, dirs, files in os.walk(plugins_directory):
            for filename in files:
                # First we will build the path for the plugin we might
                # want to append to the list
                file_path = os.path.join(root, filename)
                # Small fix which is necessary for Windows systems
                file_path = file_path.replace(os.sep, "/")

                # If the file is a gizmo or a nk file, we just go ahead and
                # add it to our list
                if file_path.endswith((".gizmo", ".nk")):
                    # Add the plugin to the list to load
                    plugin_information = self.__collect_plugin(file_path)
                    plugins.append(plugin_information)

                # If the file is a library file (.dll, .so or .dylib),
                # we need to be a little bit more careful because
                # every library file is build for a specific version of Nuke.
                # So we don't want to add a library file thats build for
                # Nuke 12.2 when we are in Nuke 13.2
                elif file_path.endswith((".dll", ".so", ".dylib")):
                    # Here we will validate if we want to load this plugin
                    if self.__validate_plugin(file_path):
                        # We want to load this plugin! Let's add it
                        # to the list.
                        plugin_information = self.__collect_plugin(file_path)
                        plugins.append(plugin_information)

        return plugins

    def __validate_plugin(self, file_path):
        """This function will check if the plugin
        is ready to be loaded, or if we don't want to load it.

        It will check if the .dll, .so or .dylib file upper folder
        matches the current Nuke version.

        If you want to add plugins to load, always make sure to create
        a folder for the Nuke version where the plugins are compiled for.
        Like if you want to use a plugin for version 13.1,
        create a folder called '13.1' where you add the plugins inside."""

        # We will firstly assume we won't validate the plugin, unless
        # the plugin is indeed correct.
        validated = False

        # If the upper folder of the plugin matches the
        # current Nuke version (e.g 13.2) we will let the validation pass.
        dirname = os.path.dirname(file_path)
        basename = os.path.basename(dirname)

        if basename == str(self.nuke_version):
            validated = True

        return validated

    def __collect_plugin(self, file_path):
        """In this function we create a dictionary item for the plugin
        provided the file path. At the end we will return
        a dictionary item like this:

        plugin_information = {
            plugin_type: "gizmo",
            file_path: "path/to/my/MagicTool.gizmo",
            plugin_name: "MagicTool",
            icon_path: "path/to/my/MagicTool.png"
        }


        """

        # Get the file extension for the file, so we can
        # check the plugin type
        plugin_extension = os.path.splitext(file_path)[1]
        plugin_type = plugin_extension.replace(".", "")

        # Get the plugin name without the extension
        plugin_name = os.path.basename(file_path)
        plugin_name = os.path.splitext(plugin_name)[0]

        # Build the dictionary with the required data
        plugin_information = {
            "plugin_type": plugin_type,
            "file_path": file_path,
            "plugin_name": plugin_name,
            "icon_path": None,
        }

        # If there is an icon available, lets add it to the dictionary.
        icon_path = file_path.replace(plugin_extension, ".png")
        if os.path.isfile(icon_path):
            plugin_information["icon_path"] = icon_path

        return plugin_information

    def __get_plugin_category(self, file_path):
        """This function will detect the plugin dictionary
        given the file path of a plugin. This is necessary to build the
        correct menu name.

        File path: //path/to/plugins/folder/plugin.gizmo
        plugins directory: //path/to/plugins
        Category: /plugins/folder/"""

        # We need the plugins directory, to calculate the length
        # we need to strip to build the category path
        plugins_directory = self.plugins_directory

        # And of course we need the menu name to add in front of the category
        # because we want to add the item to our created menu
        menu_name = self.menu_name

        # Calculate the length of the path, to strip from the file path
        plugins_directory_length = len(plugins_directory) + 1

        # Here we remove the extension from the file path
        # because we only want the category
        file_path_category = os.path.splitext(file_path)[0]

        # Now we will strip the first part of the file path
        # to only keep the category
        category = file_path_category[plugins_directory_length:]

        # Finally we have to add the menu name in front of the category
        # because we want to add items to menu we created
        category = os.path.join(menu_name, category)
        # Small fix for Windows based systems
        category = category.replace(os.sep, "/")

        return category
