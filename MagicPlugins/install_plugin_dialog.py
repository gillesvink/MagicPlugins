import nuke
import nukescripts
import os


class InstallPluginDialog(nukescripts.PythonPanel):
    def __init__(self):
        """Allows user to select plugin to install, we will ask the user
        a few things.

        We need the path to the plugin the user wants to install.
        We may want the icon path to the plugin.
        Then we want to specify a category for the plugin.

        And last but not least, if it is a library plugin, we need to
        correct Nuke version for the plugin. This option is only available
        if the plugin is a .dll, .so or a .dylib file."""
        nukescripts.PythonPanel.__init__(self, "MagicPlugins - Install plugin")

        plugin_categories = [
            "3D",
            "Blink",
            "Channel",
            "Color",
            "Deep",
            "Draw",
            "Filter",
            "Keyer",
            "Merge",
            "Other",
            "Transform",
        ]

        # Getting the current Nuke version
        current_nuke_version = str(
            ("%i.%i" % (nuke.NUKE_VERSION_MAJOR, nuke.NUKE_VERSION_MINOR))
        )

        # List containing all Nuke versions to date
        nuke_versions = [
            "13.2",
            "13.1",
            "13.0",
            "12.2",
            "12.1",
            "12.0",
            "11.3",
            "11.2",
            "11.1",
            "11.0",
        ]

        # Add Nuke version if it is not present in the list already
        # (new releases while code is not updated)
        if current_nuke_version not in nuke_versions:
            nuke_versions.append(current_nuke_version)

        # Defining extensions we would call basic
        self.basic_extensions = (
            ".nk",
            ".gizmo",
        )

        # These are the extensions that are Nuke specific plugins
        self.library_extensions = (
            ".dll",
            ".so",
            ".dylib",
        )

        # Getting the script location to locate the header image
        script_location = os.path.dirname(os.path.realpath(__file__))
        header_image = os.path.join(script_location, "resources", "header.png")
        header_image = header_image.replace(os.sep, "/")

        # Here we will create all the knobs

        self.header = nuke.Text_Knob(
            "header",
            "",
            "<img src='%s'>" % header_image,
        )
        self.help_text = nuke.Text_Knob(
            "helpText",
            "",
            "Select the file you want to install \n (.gizmo, .nk, .dll, .so "
            "and .dylib files are supported). \n You can optionally select an "
            "icon for the file to use.",
        )

        self.divider_1 = nuke.Text_Knob("divider1", "", "")

        self.plugin_file_path = nuke.File_Knob(
            "pluginPath", "Plugin file path"
        )

        self.divider_2 = nuke.Text_Knob("divider2", "", "")

        self.icon_file_path = nuke.File_Knob(
            "iconPath", "Icon file path (optional)"
        )

        self.divider_3 = nuke.Text_Knob("divider3", "", "")

        self.plugin_category = nuke.Enumeration_Knob(
            "pluginCategory", "Plugin category", plugin_categories
        )

        self.divider_4 = nuke.Text_Knob("divider4", "", "")

        self.library_nuke_version = nuke.Enumeration_Knob(
            "nukeVersion", "Nuke version", nuke_versions
        )
        self.library_nuke_version.setVisible(False)

        self.divider_5 = nuke.Text_Knob("divider5", "", "")
        self.divider_5.setVisible(False)

        # Now we will add the knobs to the dialog window
        for knob in (
            self.header,
            self.help_text,
            self.divider_1,
            self.plugin_file_path,
            self.divider_2,
            self.icon_file_path,
            self.divider_3,
            self.plugin_category,
            self.divider_4,
            self.library_nuke_version,
            self.divider_5,
        ):
            self.addKnob(knob)

    def knobChanged(self, knob):
        # If the knob is the plugin path, check and validate it
        if knob == self.plugin_file_path:
            file_path = knob.value()

            # Skip validation if the file path is empty
            if file_path is not "":

                # We will call the validation function to check the path
                validated = self.__validate_plugin_path(file_path)
                if validated is not True:

                    # Let the user know if it is not validated
                    nuke.message(validated)

                    # Set the knob to empty
                    knob.setValue("")

        # If the knob is the icon path, check and validate it
        elif knob == self.icon_file_path:
            file_path = knob.value()

            # Skip validation if the file path is empty
            if file_path is not "":

                # We will call the validation function to check the path
                validated = self.__validate_icon_path(file_path)
                if validated is not True:

                    # Let the user know if it is not validated
                    nuke.message(validated)

                    # Set the knob to empty
                    knob.setValue("")

    def __validate_plugin_path(self, file_path):
        """This function will validate the plugin, if the plugin is validated
        it will return True, else it will return a reason why
        it is not validated.

        Besides that, it will set the visibility for the version knobs. Because
        for the library plugins we will need to specify the Nuke version."""

        # First of all let's check if the file really exists on disk
        if os.path.isfile(file_path):

            # Let's assume we won't validate the file, and that we
            # don't want to see the Nuke version knob
            validated = False
            visibility = False

            # If the file ends with a basic extension (.nk and .gizmo) we
            # will accept it and set the nuke version visibility to false
            if file_path.endswith(self.basic_extensions):
                validated = True
                visibility = False

            # If the file ends with a library extension (.dll, .so and .dylib)
            # we will accept it and set the nuke version visibility to true
            elif file_path.endswith(self.library_extensions):
                validated = True
                visibility = True

            # If we can't validate it, the extension is not accepted
            else:
                validated = "Unknown extension"

            # Set the visibility for the Nuke version knob
            for knob in (
                self.library_nuke_version,
                self.divider_5,
            ):
                knob.setVisible(visibility)

            return validated

        # If the file is not found, let the user know
        else:
            return "File %s not found" % file_path

    def __validate_icon_path(self, file_path):
        """Function to validate the icon provided, if
        the file is validated we will return a True value. Otherwise
        a message containing the error will be provided."""

        # First of all let's check if the file exists
        if os.path.isfile(file_path):

            # Now we will check if the file is a png file
            if file_path.endswith(".png"):
                return True

            # If the file is something different than a png, we will
            # let the user know another file is needed
            else:
                return "File %s is not a png" % file_path

        # If the file is not found, we will let the user know the
        # file does not exist on disk
        else:
            return "File %s is not found" % file_path
