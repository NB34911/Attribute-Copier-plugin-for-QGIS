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
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QAbstractItemView

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'attribute_copier_dialog_base.ui'))

class AttributeCopierDialog(QtWidgets.QWidget, FORM_CLASS):
    def __init__(self, parent=None):
        super(AttributeCopierDialog, self).__init__(parent)
        self.setupUi(self)

        self.stored_names_attrs_to_copy = None
        self.stored_values_attrs_to_copy = None
        self.stored_names_attrs_to_paste = None
        self.stored_dict_names_and_values = None
        self.fill_listWidget_with_fields()
        self.layer_to_modify = None

        canvas = iface.mapCanvas()
        canvas.currentLayerChanged.connect(self.fill_listWidget_with_fields)
        
        self.pb_select_all.clicked.connect(self.select_fields)
        self.pb_uncheck_all.clicked.connect(self.uncheck_fields)

        self.pb_confirm_choice.clicked.connect(self.confirm_layer_and_activate_select_tool)
        self.pb_confirm_choice.clicked.connect(lambda : self.enable_widget(self.pb_copy_attributes))

        self.pb_copy_attributes.clicked.connect(self.copy_source)
        self.pb_copy_attributes.clicked.connect(lambda : self.enable_widget(self.pb_paste_attributes))
        
        self.pb_paste_attributes.clicked.connect(self.paste_attributes_from_source)
        
    def fill_listWidget_with_fields(self):

        self.listWidget.clear()
        layer = iface.activeLayer()
        if not layer:
            iface.messageBar().pushMessage("Warning:", "There is no active vector layer selected.", level=Qgis.Info)
        elif (layer.type() == QgsMapLayer.VectorLayer):
            fields = layer.fields()
            for field in fields:
                item = QListWidgetItem(field.name())
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                self.listWidget.addItem(item)
            self.listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        else:
            iface.messageBar().pushMessage("Warning:", "There is no active vector layer selected.", level=Qgis.Info)
            
    def select_fields(self):
        for x in range(self.listWidget.count()):
            item = self.listWidget.item(x)
            if item.text()== 'fid':
                item.setCheckState(Qt.Unchecked)
            else:
                item.setCheckState(Qt.Checked)
            
    def uncheck_fields(self):
        for x in range(self.listWidget.count()):
            item = self.listWidget.item(x)
            item.setCheckState(Qt.Unchecked)

    def confirm_layer_and_activate_select_tool(self):
        self.layer_to_modify= iface.activeLayer()
        layer = self.layer_to_modify
        if not layer or layer.type() != QgsMapLayer.VectorLayer:
            iface.messageBar().pushMessage("Error", "Select a vector layer.", level=Qgis.Critical)
            return
        else:
            iface.actionSelect().trigger()
            iface.messageBar().pushMessage("1:", "Select the object to copy attributes.", level=Qgis.Info)

    def copy_source(self):
        layer = self.layer_to_modify
        if not layer or layer.type() != QgsMapLayer.VectorLayer:
            iface.messageBar().pushMessage("Error", "Select a vector layer.", level=Qgis.Critical)
            return
        
        feats = layer.selectedFeatures()
        if len(feats) != 1:
            iface.messageBar().pushMessage("Error", "Select exactly 1 object from which you want to copy attributes.", level=Qgis.Critical)
            return
        
        list_attr_values_to_copy = []
        list_names_attr_to_copy = []
        
        for x in range(self.listWidget.count()):
            item = self.listWidget.item(x)
            if item.checkState()==2:
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
        iface.messageBar().pushMessage("2:", "Select target objects to modify attributes.", level=Qgis.Info)

    def enable_widget(self, widget):
        widget.setEnabled(True)
        
    def paste_attributes_from_source(self):
        target_fields = None
        if self.checkBox_diffrent_layers.isChecked():
            layer = iface.activeLayer()
            target_fields = layer.fields()
        else:
            layer = self.layer_to_modify
    
        if not layer or layer.type() != QgsMapLayer.VectorLayer:
            iface.messageBar().pushMessage("Error", "Select a vector layer.", level=Qgis.Critical)
            return
        
        feats = layer.selectedFeatures()
        if not feats:
            iface.messageBar().pushMessage("Information", "No targets selected for modification.", level=Qgis.Info)
            return
        fid_selected = []
        for feat in feats:
            fid_selected.append(feat.id())

        if self.stored_names_attrs_to_copy is None:
            iface.messageBar().pushMessage("Error", "First, copy the attributes from the source object.", level=Qgis.Critical)
            return
        
        fields_names = self.stored_names_attrs_to_copy
        fields_values = self.stored_values_attrs_to_copy
        dictionary = self.stored_dict_names_and_values

        fields_names_approved = []
        fields_values_approved = []
        if self.checkBox_diffrent_layers.isChecked():
            for field_name in fields_names:
                if target_fields and (field_name in  target_fields):
                    fields_names_approved.append(field_name)
                    fields_values_approved.append(dictionary.get(field_name))
            fields_names = fields_names_approved
            fields_values = fields_values_approved
        else:
            pass

        fields_indices = []
        for i in range(len(fields_names)):
            fields_indices.append(layer.fields().indexFromName(fields_names[i]))

        self.attrs_to_paste = dict(zip(fields_indices, fields_values))

        caps = layer.dataProvider().capabilities()
        for i in range(len(fid_selected)):
            fid = int(fid_selected[i])
            if caps & QgsVectorDataProvider.ChangeAttributeValues:
                layer.dataProvider().changeAttributeValues({ fid : self.attrs_to_paste })

        if iface.mapCanvas().isCachingEnabled():
            layer.triggerRepaint()
        else:
            iface.mapCanvas().refresh()
            
        if layer:
            layer.removeSelection()
        iface.messageBar().pushMessage("3:",f"Number of objects modified: {len(fid_selected)}.", level=Qgis.Info)