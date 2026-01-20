# QGIS Attribute Copier Plugin

This plugin allows you to copy attributes from a source object to one or more target objects. It supports copying within a single vector layer or **between two different vector layers**.

## Usage

The animation below demonstrates the basic usage of the plugin:

![Plugin Usage Demonstration](https://raw.githubusercontent.com/NB34911/Attribute-Copier-plugin-for-QGIS/main/images/Usage_of_Plugin.gif)

*(Note: The interface has been updated to support cross-layer copying, but the core workflow remains similar.)*

### How to use with different layers:
1. Open the plugin.
2. Select the **Source Layer** in the Layers Panel (the attribute list will update automatically).
3. Check the attributes you want to copy in the list and click **"Confirm selected fields"**.
4. Select one source object on the map and click **"Copy attributes"**.
5. (Optional) Check **"Allow copying between different layers"** and switch to your **Target Layer** in the Layers Panel.
6. Select target objects on the map.
7. Click **"Paste attributes"**. 
   * The plugin will automatically enable **Edit Mode** on the target layer.
   * You can **Undo (Ctrl+Z)** the changes if needed before saving.

## Features

*   **Attribute Selection:** Ability to choose exactly which attributes (fields) to transfer.
*   **Cross-Layer Support:** Copy attributes between different vector layers (requires matching field names).
*   **Safe Editing:** Pasting triggers the QGIS Edit Buffer. Changes are not saved immediately to the file/database, allowing you to review them and use standard **Undo/Redo** functionality.
*   **Batch Processing:** Transfer values from one source object to multiple target objects simultaneously.
*   **User Friendly:** Logic prevents accidental copying of system identifiers (like `fid`).

## Installation

### 1. From the official QGIS Plugin Repository

The plugin is available in the official QGIS repository.
1. Open QGIS.
2. Go to **Plugins -> Manage and Install Plugins...**.
3. Search for **Attribute Copier**.
4. Click **Install Plugin**.

### 2. Manual Installation from ZIP

1.  Navigate to the main page of this repository and click the green `<> Code` button.
2.  Select **Download ZIP**.
3.  In QGIS, go to **Plugins -> Manage and Install Plugins...**.
4.  In the new window, switch to the **Install from ZIP** tab.
5.  Browse to the downloaded ZIP file and click **Install Plugin**.

## Future Development

Planned features for future releases include:

*   Option to automatically create new fields in the target layer if they don't exist in the source layer.
*   Improved support for different field types mapping.

## Acknowledgements

The initial structure of this plugin was generated using the excellent [QGIS Plugin Builder](https://g-sherman.github.io/Qgis-Plugin-Builder/). A big thank you to its author for creating a tool that significantly speeds up development.