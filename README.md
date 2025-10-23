# QGIS Attribute Copier Plugin

This plugin allows you to copy attributes from a source object to one or more target objects within a vector layer.

## Usage

The animation below demonstrates the basic usage of the plugin:

![Plugin Usage Demonstration](https://raw.githubusercontent.com/NB34911/Attribute-Copier-plugin-for-QGIS/main/images/Usage_of_Plugin.gif)

## Features

*   Ability to choose which attributes to transfer.
*   An easy way to transfer values from one object to multiple others within the same active vector layer.
*   Operate directly on the map canvas, without the necessity of opening the attribute table.

## Installation

### 1. From the official QGIS Plugin Repository (Coming Soon)

Once the plugin is approved, it will be available to install directly from the QGIS Plugin Manager.

### 2. Manual Installation from ZIP

1.  Navigate to the main page of this repository and click the green `<> Code` button.
2.  Select **Download ZIP**.
3.  In QGIS, go to **Plugins -> Manage and Install Plugins...**.
4.  In the new window, switch to the **Install from ZIP** tab.
5.  Browse to the downloaded ZIP file and click **Install Plugin**.
6.  After installation, ensure the plugin is enabled in the **Installed** tab of the Plugin Manager.

## Future Development

Planned features for future releases include:

*   An "Undo" button to revert the last modification.
*   Ability to copy attributes between different vector layers, with an option to automatically create new fields in the target layer if they don't exist.
*   Extended recognition of primary keys in different layers (currently, only `fid` in GeoPackage is recognized) to prevent errors.
