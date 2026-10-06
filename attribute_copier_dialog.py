# -*- coding: utf-8 -*-

# Copyright (C) 2025, Natalia Budzińska
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import os
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.core import *
import qgis.utils
from qgis.utils import iface 
from qgis.PyQt.QtWidgets import QListWidgetItem
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtWidgets import QAbstractItemView

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'attribute_copier_dialog_base.ui'))

class AttributeCopierDialog(QtWidgets.QWidget, FORM_CLASS):
    def __init__(self, parent=None):
        super(AttributeCopierDialog, self).__init__(parent)
        self.setupUi(self)

        self.stored_names_attrs_to_copy = None
        self.stored_values_attrs_to_copy = None
        self.stored_dict_names_and_values = None
        self.fill_listWidget_with_fields()
        self.source_layer = None

        canvas = iface.mapCanvas()
        canvas.currentLayerChanged.connect(self.fill_listWidget_with_fields)
        
        self.pb_select_all.clicked.connect(self.select_fields)
        self.pb_uncheck_all.clicked.connect(self.uncheck_fields)

        self.pb_confirm_choice.clicked.connect(self.confirm_layer_and_activate_select_tool)
        self.pb_confirm_choice.clicked.connect(lambda checked=False: self.enable_widget(self.pb_copy_attributes))

        self.pb_copy_attributes.clicked.connect(self.copy_source)
        self.pb_copy_attributes.clicked.connect(lambda checked=False: self.enable_widget(self.pb_paste_attributes))
        
        self.pb_paste_attributes.clicked.connect(self.paste_attributes_from_source)
        
    def fill_listWidget_with_fields(self):

        self.listWidget.clear()
        layer = iface.activeLayer()
        if not layer:
            iface.messageBar().pushMessage("Warning:", "There is no active vector layer selected.", level=Qgis.MessageLevel.Info)
        elif (layer.type() == QgsMapLayerType.VectorLayer):
            fields = layer.fields()
            for field in fields:
                item = QListWidgetItem(field.name())
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
                self.listWidget.addItem(item)
            self.listWidget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        else:
            iface.messageBar().pushMessage("Warning:", "There is no active vector layer selected.", level=Qgis.MessageLevel.Info)
            
    def select_fields(self):
        for x in range(self.listWidget.count()):
            item = self.listWidget.item(x)
            if item.text()== 'fid':
                item.setCheckState(Qt.CheckState.Unchecked)
            else:
                item.setCheckState(Qt.CheckState.Checked)
            
    def uncheck_fields(self):
        for x in range(self.listWidget.count()):
            item = self.listWidget.item(x)
            item.setCheckState(Qt.CheckState.Unchecked)

    def confirm_layer_and_activate_select_tool(self):
        self.source_layer= iface.activeLayer()
        layer = self.source_layer
        if not layer or layer.type() != QgsMapLayerType.VectorLayer:
            iface.messageBar().pushMessage("Error", "Select a vector layer.", level=Qgis.MessageLevel.Critical)
            return
        else:
            iface.actionSelect().trigger()
            iface.messageBar().pushMessage("1:", "Select the object to copy attributes.", level=Qgis.MessageLevel.Info)

    def copy_source(self):
        layer = self.source_layer
        if not layer or layer.type() != QgsMapLayerType.VectorLayer:
            iface.messageBar().pushMessage("Error", "Select a vector layer.", level=Qgis.MessageLevel.Critical)
            return
        
        feats = layer.selectedFeatures()
        if len(feats) != 1:
            iface.messageBar().pushMessage("Error", "Select exactly 1 object from which you want to copy attributes.", level=Qgis.MessageLevel.Critical)
            return
        
        list_attr_values_to_copy = []
        list_names_attr_to_copy = []
        
        for x in range(self.listWidget.count()):
            item = self.listWidget.item(x)
            if item.checkState() == Qt.CheckState.Checked:
                list_names_attr_to_copy.append(item.text())
        
        feat = feats[0]
        for i in range(len(list_names_attr_to_copy)):
            attr_val = list_names_attr_to_copy[i]
            list_attr_values_to_copy.append(feat[attr_val])

        self.stored_names_attrs_to_copy = list_names_attr_to_copy
        self.stored_values_attrs_to_copy = list_attr_values_to_copy
        self.stored_dict_names_and_values = dict(zip(list_names_attr_to_copy,list_attr_values_to_copy))
        
        if layer:
            layer.removeSelection()
        iface.messageBar().pushMessage("2:", "Select target objects to modify attributes.", level=Qgis.MessageLevel.Info)

    def enable_widget(self, widget):
        widget.setEnabled(True)

    def paste_attributes_from_source(self):
        if self.checkBox_diffrent_layers.isChecked():
            layer = iface.activeLayer()
        else:
            layer = self.source_layer

        if not layer or layer.type() != QgsMapLayerType.VectorLayer:
            iface.messageBar().pushMessage("Error", "Select a vector layer.", level=Qgis.MessageLevel.Critical)
            return
        
        feats = layer.selectedFeatures()
        if not feats:
            iface.messageBar().pushMessage("Information", "No targets selected for modification.", level=Qgis.MessageLevel.Info)
            return
        
        fid_selected = []
        for feat in feats:
            fid_selected.append(feat.id())

        if self.stored_names_attrs_to_copy is None:
            iface.messageBar().pushMessage("Error", "First, copy the attributes from the source object.", level=Qgis.MessageLevel.Critical)
            return
        
        fields_names = self.stored_names_attrs_to_copy
        fields_indices = []
        fields_names_consistent = []
        for i in range(len(fields_names)):
            field_index = layer.fields().indexFromName(fields_names[i])
            if field_index != -1:
                fields_indices.append(field_index)
                fields_names_consistent.append(fields_names[i])

        layer_s = self.source_layer 
        fields_types_in_source = []
        for name in fields_names_consistent:
            fields_types_in_source.append(layer_s.fields().field(name).typeName().lower())

        fields_types_in_target = []
        for name in fields_names_consistent:
            fields_types_in_target.append(layer.fields().field(name).typeName().lower())

        def get_type_group(t_name):
            if 'int' in t_name: return 'int'
            if t_name in ['real', 'double', 'float', 'decimal', 'numeric']: return 'float'
            if 'string' in t_name or 'text' in t_name or 'char' in t_name: return 'string'
            if 'date' in t_name or 'time' in t_name: return 'date'
            if 'bool' in t_name: return 'bool'
            return t_name


        diff_in_field_types = []
        for i, (a, b) in enumerate(zip(fields_types_in_source, fields_types_in_target)):
            grp_a = get_type_group(a)
            grp_b = get_type_group(b)
            
            if grp_a != grp_b:
                if grp_a == 'int' and grp_b == 'float':
                    pass 
                else:
                    diff_in_field_types.append(i)
        
        new_fields_indices = [x for i, x in enumerate(fields_indices) if i not in diff_in_field_types]
        fields_names_approved = [x for i, x in enumerate(fields_names_consistent) if i not in diff_in_field_types]
        fields_values_approved = [self.stored_dict_names_and_values[k] for k in fields_names_approved]
        self.attrs_to_paste = dict(zip(new_fields_indices, fields_values_approved))


        warning_messages = []
        for name in fields_names_approved:
            source_field = layer_s.fields().field(name)
            target_field = layer.fields().field(name)
            
            s_len = source_field.length()
            t_len = target_field.length()
            s_prec = source_field.precision()
            t_prec = target_field.precision()

            warnings_for_field = []
            
            if t_len > 0 and s_len > t_len:
                warnings_for_field.append(f"Length {s_len}->{t_len}")
                
            if t_prec > 0 and s_prec > t_prec:
                warnings_for_field.append(f"Precision {s_prec}->{t_prec}")
                
            if warnings_for_field:
                warning_messages.append(f"{name} ({', '.join(warnings_for_field)})")

        if warning_messages:
            msg = "Potential data truncation for fields: " + " | ".join(warning_messages)
            iface.messageBar().pushMessage("Warning", msg, level=Qgis.MessageLevel.Warning)

        if not layer.isEditable():
            layer.startEditing()

        layer.beginEditCommand("Paste Attributes")
        try:
            for fid in fid_selected:
                for field_index, value in self.attrs_to_paste.items():
                    layer.changeAttributeValue(fid, int(field_index), value)
            layer.endEditCommand()
            iface.messageBar().pushMessage("Success", f"Modified {len(fid_selected)} objects. (Press Ctrl+Z to undo)", level=Qgis.MessageLevel.Info)

        except Exception as e:
            layer.destroyEditCommand()
            iface.messageBar().pushMessage("Error", str(e), level=Qgis.MessageLevel.Critical)

        layer.triggerRepaint()
        if layer:
            layer.removeSelection()