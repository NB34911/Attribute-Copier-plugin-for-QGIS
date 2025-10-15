

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


class AttributeCopierDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(AttributeCopierDialog, self).__init__(parent)
        self.setupUi(self)
        
        #warstwa wejściowa
        layer = iface.activeLayer()
        
        #miejsce na kopiowane atrybuty
        self.stored_attrs_to_copy = None

        #dodanie pól do listy
        self.listWidget.clear()
        fields = layer.fields()

        for field in fields:
            item = QListWidgetItem(field.name())
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.listWidget.addItem(item)
        self.listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        #zaznaczanie wszystkich pól i odznaczanie
        self.zaznacz_wszystko.clicked.connect(self.zaznacz_pola)
        self.odznacz_wszystko.clicked.connect(self.odznacz_pola)
        
        #potwierdzenie wyboru pól do skopiowania i uaktywnienie przycisku wybierz_source
        self.potwierdz_wybor.clicked.connect(self.activate_select_tool)
        self.potwierdz_wybor.clicked.connect(lambda : self.enable_widget(self.wybierz_source))
        
        #potwierdzenie wyboru obiektu źródłowego i uaktywnienie następnych przycisków
        self.wybierz_source.clicked.connect(self.kopiuj_zrodlo)
        self.wybierz_source.clicked.connect(lambda : self.enable_widget(self.wybierz_destination))
        
        self.wybierz_destination.clicked.connect(self.wklej_atrybuty_zrodlowe)
        self.wybierz_destination.clicked.connect(lambda : self.enable_widget(self.cofnij_destination))
        
    def zaznacz_pola(self):
        for x in range(self.listWidget.count()):
            item = self.listWidget.item(x)
            if item.text()== 'fid':
                item.setCheckState(Qt.Unchecked)
            else:
                item.setCheckState(Qt.Checked)
            
    def odznacz_pola(self):
        for x in range(self.listWidget.count()):
            item = self.listWidget.item(x)
            item.setCheckState(Qt.Unchecked)

    def activate_select_tool(self):
        layer = iface.activeLayer()
        iface.actionSelect().trigger()
        self.showMinimized()
        iface.messageBar().pushMessage("1:", "Wybierz obiekt do skopiowania atrybutów.", level=Qgis.Info)

        
    def deselect_all(self):
        layer = iface.activeLayer()
        if layer:
            layer.removeSelection()

    def kopiuj_zrodlo(self):
        
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
                
        #to są atrybuty do skopiowania do docelowych obiektów
        self.stored_attrs_to_copy = dict(zip(list_index_attr_to_copy, list_attr_to_copy))
        
        if layer:
            layer.removeSelection()
            
        self.showMinimized()
        iface.messageBar().pushMessage("2:", "Wybierz obiekty docelowe do modyfikacji atrybutów.", level=Qgis.Info)


    def enable_widget(self, widget):
        widget.setEnabled(True)
        
    def wklej_atrybuty_zrodlowe(self):
        # pobranie id zaznaczonych obiektów docelowych
        layer = iface.activeLayer()
        feats = layer.selectedFeatures()
        fid_selected = []
        for feat in feats:
            fid_selected.append(feat.id())

        #zmiana atrybutów
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
        iface.messageBar().pushMessage("3:",f"Liczba zmodyfikowanych obiektów: {len(fid_selected)}.", level=Qgis.Info)
        

    
    
    
 
