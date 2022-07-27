[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![MagicPlugins, automatic plugin loader for Nuke](/MagicPlugins/resources/MagicPlugins.png)

## What does it do?
It scans the MagicPlugins directory for plugins, and automatically adds them according to the folder/category created.

## Which versions of Nuke are supported?
* Currently Nuke 11+ is supported, and tested on Linux, Mac and Windows. But earlier versions should also just work fine.

## Which files are supported?
* `.gizmo`
* `.nk` 
* `.dll` (Windows), `.so` (Linux), `.dylib` (Mac OS)

## How to install
* Copy the entire contents of this repository in your `.nuke` folder.
* Add the line 
`nuke.pluginAddPath("./MagicPlugins")`
to your `init.py` file in your `.nuke` folder.
* Another option is to add the environment `NUKE_PATH` to your system with the value `your/MagicPlugins/installation/folder/`.

## How to use
All folders in the MagicPlugins directory are at startup scanned. If you add a gizmo in the home directory, it will be added to the menu. If you add the gizmo in a folder somewhere, all the folders will be created accordingly. This allows you to create categories.

### Installing via the GUI
When using the GUI installer, the plugin will be added inside the <i>Internet</i> folder/category.

1. Select the <i>Install plugin</i> option in the MagicPlugins menu.

![The option in the menu](/MagicPlugins/resources/installing_plugin_menu.png)

2. Select the plugin you want to install, and optionally you can select an icon as well.

![MagicPlugin installer](/MagicPlugins/resources/installing_plugin_ui.png)

3. If the file is one of the library files (`.dll`, `.so`, `.dylib`) you also need to specify the Nuke version for the selected file.

![MagicPlugin install library file](/MagicPlugins/resources/installing_plugin_library.png)


### Manually installing (multiple files)
All the files that are loaded in startup are located in the plugins folder inside the MagicPlugin folder. 

Every item that is added inside this folder will be added automatically to Nuke. So if you want to add a gizmo or a Nuke script file, just copy and paste it into there.

### Installing library files (`.dll`, `.so`, `.dylib`)
Because library files are compiled for every Nuke version specifically, you don't want to load a plugin compiled for Nuke 12.2 if you are in 13.0. Using MagicPlugins it's possible to load library files for the correct Nuke version, and skip the others. 
* When adding library files, create a folder named with the target Nuke version. So for example, if I want to add a plugin called myPlugin.dll for `Nuke 13.0`, it needs to be added like `myLibraryPluginsCategory/13.0/myPlugin.dll`.
* If you want to add the plugin for `Nuke 12.2`, it needs to be added like `myLibraryPluginsCategory/12.2/myPlugin.dll`, and so on
