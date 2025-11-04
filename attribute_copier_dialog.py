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

        self.stored_attrs_to_copy = None
        self.fill_listWidget_with_fields()

        canvas = iface.mapCanvas()
        canvas.currentLayerChanged.connect(self.fill_listWidget_with_fields)
        
        self.pb_select_all.clicked.connect(self.select_fields)
        self.pb_uncheck_all.clicked.connect(self.uncheck_fields)

        self.pb_confirm_choice.clicked.connect(self.activate_select_tool)
        self.pb_confirm_choice.clicked.connect(lambda : self.enable_widget(self.pb_copy_attributes))

        self.pb_copy_attributes.clicked.connect(self.copy_source)
        self.pb_copy_attributes.clicked.connect(lambda : self.enable_widget(self.pb_paste_attributes))
        
        self.pb_paste_attributes.clicked.connect(self.paste_attributes_from_source)
        
    def fill_listWidget_with_fields(self):

        self.listWidget.clear()
        layer = iface.activeLayer()

        if not layer:
            iface.messageBar().pushMessage("11:", "There is no active layer.", level=Qgis.Info)

        elif (layer.type() == QgsMapLayer.VectorLayer):
            
            fields = layer.fields()

            for field in fields:
                item = QListWidgetItem(field.name())
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                self.listWidget.addItem(item)
            self.listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        else:
            iface.messageBar().pushMessage("11:", "No vector layer was selected.", level=Qgis.Info)
            
            
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

    def activate_select_tool(self):
        layer = iface.activeLayer()
        iface.actionSelect().trigger()
        self.showMinimized()
        iface.messageBar().pushMessage("1:", "Select the object to copy attributes.", level=Qgis.Info)

    def deselect_all(self):
        layer = iface.activeLayer()
        if layer:
            layer.removeSelection()

    def copy_source(self):
        layer = iface.activeLayer()
        feats = layer.selectedFeatures()
        list_attr_to_copy = []
        list_index_attr_to_copy = []
        
        for x in range(self.listWidget.count()):
            item = self.listWidget.item(x)
            if item.checkState()==2:
                list_index_attr_to_copy.append(x)
        selection = layer.selectedFeatures()
        
        for feat in feats:
            for i in range(len(list_index_attr_to_copy)):
                id = int(list_index_attr_to_copy[i])
                list_attr_to_copy.append(feat[id])
                
        self.stored_attrs_to_copy = dict(zip(list_index_attr_to_copy, list_attr_to_copy))
        
        if layer:
            layer.removeSelection()
        self.showMinimized()
        iface.messageBar().pushMessage("2:", "Select target objects to modify attributes.", level=Qgis.Info)

    def enable_widget(self, widget):
        widget.setEnabled(True)
        
    def paste_attributes_from_source(self):
        layer = iface.activeLayer()
        feats = layer.selectedFeatures()
        fid_selected = []
        for feat in feats:
            fid_selected.append(feat.id())

        attrs = self.stored_attrs_to_copy
        caps = layer.dataProvider().capabilities()
        features = layer.getFeatures()
        
        for i in range(len(fid_selected)):
            fid = int(fid_selected[i])
            if caps & QgsVectorDataProvider.ChangeAttributeValues:
                layer.dataProvider().changeAttributeValues({ fid : attrs })

        if iface.mapCanvas().isCachingEnabled():
            layer.triggerRepaint()
        else:
            iface.mapCanvas().refresh()
            
        if layer:
            layer.removeSelection()
            
        self.showMinimized()
        iface.messageBar().pushMessage("3:",f"Number of objects modified: {len(fid_selected)}.", level=Qgis.Info)