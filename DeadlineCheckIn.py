#coding:gbk
#from PyQt4.Qt import QMainWindow, QMessageBox
r"""
Created on 2015-2-28
@contact:    power_zzj@163.com
@deffield    updated: Updated
@author: zhaozhongjie
@mender: TianD
usage:

import sys
sys.path.append(r'E:\Pluto\workspace')
import PlutoPip.MyLib.PPrnd.MusterCheckIn as isp
reload(isp)
isp.main()

"""
import os, sys, socket, shutil, getpass, time
import subprocess
import json
import SearchImageSequence as sis
reload(sis)
from PySide.QtGui import *
from PySide.QtCore import *
import sip
#import maya.cmds as cmds
import pymel.core as pm
parentWindow = None

def getMayaWindow():
    import maya.OpenMayaUI as apiUI
    ptr = apiUI.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QObject)


try:
    parentWindow = getMayaWindow()
except:
    pass

def main():
    import maya.OpenMayaUI as apiUI
    oldDialog = apiUI.MQtUtil.findWindow('DeadlineCheckIn')
    try:
        sip.wrapinstance(long(oldDialog), QWidget).close()
    except:
        pass

    pgw = DeadlineCheckIn()
    pgw.show()


inMaya = 0

class DeadlineCheckIn(QMainWindow):
    """
    classdocs
    """
    FILE = __file__
    Folder, FileName = os.path.split(FILE)
    UI = os.path.splitext(FILE)[0] + '.ui'
    HELP = os.path.join(Folder, 'help.mht')
    JsonFile = os.path.join(Folder, 'config.ini')
    with open(JsonFile, 'r') as f:
        json_data = json.loads(f.read(), encoding='gbk')
    Mrtool = json_data['Mrtool']
    NetRenderRoot = json_data['NetRenderRootPath']
    UserOrHost = json_data['UserOrHost']
    Dispatcher = json_data['Dispatcher']
    User = json_data['User']
    Password = json_data['Password']
    RenderFarm = json_data['RenderFarm']
    #MaxCpu = json_data['MaxCpu']
    #MaxCpu_Min = json_data['MaxCpu_Min']
    #MaxCpu_Max = json_data['MaxCpu_Max']
    Priority = json_data['Priority']
    Priority_Min = json_data['Priority_Min']
    Priority_Max = json_data['Priority_Max']
    Packet = json_data['Packet']
    _HOST = socket.gethostname()
    _USER = getpass.getuser()
    Project_Name = _USER
    if UserOrHost == 'host':
        Project_Name = _HOST
    CMD = ''

    def __init__(self, parent = parentWindow):
        """
        Constructor
        """
        super(DeadlineCheckIn, self).__init__(parent)
        self.closeExistingWindow()
        self.setWindowTitle(u'�ύDeadline')
        self.setObjectName('DeadlineCheckIn')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.resize(600, 600)
        from PySide.QtUiTools import QUiLoader
        self.win = QUiLoader().load(self.UI)
        self.setCentralWidget(self.win)
        self.show()
        self.INIT_UI()
        self.CONNECT()

    def CONNECT(self):
        self.win.QC_BT_OpenProjFolder.clicked.connect(lambda : os.startfile(self.Project_Path))
        self.win.QC_CKB_DisplayAllTexture.clicked.connect(self.INIT_ListView)
        self.win.QC_BT_UpdateTexture.clicked.connect(self.INIT_ListView)
        self.win.QC_LV_TextureList.clicked.connect(self.MyCMD_selectTexture)
        self.win.QC_BT_CheckInText_Selected.clicked.connect(self.MyCMD_checkTexture_selected)
        self.win.QC_BT_CheckInText_All.clicked.connect(self.MyCMD_checkTexture_all)
        self.win.QC_BT_CheckMayaFile.clicked.connect(self.MyCMD_checkFile)
        self.win.QC_BT_Submit.clicked.connect(self.MyCMD_submit)
        self.win.QC_MU_Help.triggered.connect(self.help)

    	self.win.QC_CKB_DisplayAllCache.clicked.connect(self.INIT_CacheListView)
    	self.win.QC_BT_UpdateCache.clicked.connect(self.INIT_CacheListView)
    	self.win.QC_LV_CacheList.clicked.connect(self.MyCMD_selectCache)
    	self.win.QC_BT_CheckInCache_Selected.clicked.connect(self.MyCMD_checkCache_selected)
    	self.win.QC_BT_CheckInCache_All.clicked.connect(self.MyCMD_checkCache_all)	

    def INIT_UI(self):
        self.Project_Path = os.path.join(self.NetRenderRoot, self.Project_Name)
        self.win.QC_LB_ProjectFolder.setText(self.Project_Path)
        self.Create_Project_Folder()
        serverIP = self.Dispatcher
        pool = self.RenderFarm
        user = self.User
        password = self.Password
        self.win.QC_CBB_ServerIP.clear()
        self.win.QC_CBB_ServerIP.addItems(serverIP)
        self.win.QC_CBB_Pool.clear()
        self.win.QC_CBB_Pool.addItems(pool)
        self.win.QC_LE_User.setText(user)
        self.win.QC_LE_Password.setText(password)
        self.INIT_ListView()
        self.INIT_CacheListView()
        fileName = 'xxx.mb'
        #fileName = cmds.file(q=1, sn=1, shn=1)
        fileName = pm.Env().sceneName().basename()
        self.win.QC_LB_MayaFileName.setText(fileName)
        jobName = os.path.splitext(fileName)[0]
        sf = '1'
        ef = '10'
        #sf = str(int(cmds.getAttr('defaultRenderGlobals.fs')))
        #ef = str(int(cmds.getAttr('defaultRenderGlobals.ef')))
        sf = str(int(pm.PyNode('defaultRenderGlobals.fs').get()))
        ef = str(int(pm.PyNode('defaultRenderGlobals.ef').get()))
        self.win.QC_LB_MayaFileName.setText(fileName)
        self.win.QC_LE_JobName.setText(jobName)
        self.win.QC_LE_OutputFolder.setText(self.images)
        self.win.QC_LE_Sf.setText(sf)
        self.win.QC_LE_Ef.setText(ef)
        #self.win.QC_SPB_MaxCpu.setValue(self.MaxCpu)
        #self.win.QC_SPB_MaxCpu.setRange(self.MaxCpu_Min, self.MaxCpu_Max)
        self.win.QC_SPB_Priority.setValue(self.Priority)
        self.win.QC_SPB_Priority.setRange(self.Priority_Min, self.Priority_Max)
        #self.win.QC_SPB_Packet.setValue(self.Packet)

    def closeExistingWindow(self):
        for qt in qApp.topLevelWidgets():
            try:
                if qt.__class__.__name__ == self.__class__.__name__:
                    qt.close()
            except:
                pass

    def help(self):
        os.startfile(self.HELP)

    def Create_Project_Folder(self):
        project = os.path.join(self.NetRenderRoot, self.Project_Name)
        scenes = os.path.join(project, 'scenes')
        sourceimages = os.path.join(project, 'sourceimages')
        alembics = os.path.join(project, 'cache/alembic')
        data = os.path.join(project, 'data')
        particles = os.path.join(project, 'particles')
        images = os.path.join(project, 'images')
        self.sourceimages = sourceimages
        self.alembics = alembics
        self.images = images
        folders = [project,
	     alembics,
         scenes,
         sourceimages,
         data,
         particles,
         images]
        for f in folders:
            if not os.path.exists(f):
                try:
                    os.makedirs(f)
                except:
                    QMessageBox.critical(None, u'ע��', u'�����޷����������ļ���:\n' + f)
                    return

        return

    def MyCMD_checkTexture_cmd(self, image_group, folder):
               
        for image in image_group:
            try:
                shutil.copy2(image, folder)
                print 'copy ' + image + ' to ' + folder
            except Exception as e:
                print e
                return 0

        onlinePath = os.path.join(folder, os.path.split(image_group[0])[1])
        
        return onlinePath
    
    def MyCMD_checkCache_cmd(self, cache_group, folder):   
        for cache in cache_group:
            try:
                shutil.copy2(cache, folder)
                print 'copy ' + cache + ' to ' + folder
            except Exception as e:
                print e
                return 0
        
        onlinePath = os.path.join(folder, os.path.split(cache_group[0])[1])
        
        return onlinePath
    
    def MyCMD_checkTexture_selected(self):
        selected = []
        for s in self.win.QC_LV_TextureList.selectedIndexes():
            selected.append(self.tablemodel._datas[s.row()])

        for s in selected:
            fileName, image_group = s
            onlinePath = self.MyCMD_checkTexture_cmd(image_group, self.sourceimages)
            if onlinePath:
                try:
                    #cmds.setAttr(fileName + '.fileTextureName', onlinePath, type='string')
		            pm.PyNode(fileName).fileTextureName.set(onlinePath)
                except:
                    pass
                
        QMessageBox.information(self.win, u'��ʾ', u'�ϴ���ͼ���\n')
        self.INIT_ListView()

    def MyCMD_checkCache_selected(self):
        selected = []
        for s in self.win.QC_LV_CacheList.selectedIndexes():
            selected.append(self.cachemodel._datas[s.row()])

        for s in selected:
            fileName, cache_group = s
            onlinePath = self.MyCMD_checkCache_cmd(cache_group, self.alembics)
            if onlinePath:
                try:
                    #cmds.setAttr(fileName + '.fileTextureName', onlinePath, type='string')
		            pm.PyNode(fileName).abc_File.set(onlinePath)
                except:
                    pass
                
        QMessageBox.information(self.win, u'��ʾ', u'�ϴ��������\n')
        self.INIT_CacheListView()

    def MyCMD_checkTexture_all(self):
        selected = []
        for s in self.tablemodel._datas:
            selected.append(s)

        for s in selected:
            fileName, image_group = s
            onlinePath = self.MyCMD_checkTexture_cmd(image_group, self.sourceimages)
            if onlinePath:
                try:
                    #cmds.setAttr(fileName + '.fileTextureName', onlinePath, type='string')
		            pm.PyNode(fileName).fileTextureName.set(onlinePath)
                except:
                    pass
        
        QMessageBox.information(self.win, u'��ʾ', u'�ϴ���ͼ���\n')
        self.INIT_ListView()
	
    def MyCMD_checkCache_all(self):
        selected = []
        for s in self.cachemodel._datas:
            selected.append(s)

        for s in selected:
            fileName, cache_group = s
            onlinePath = self.MyCMD_checkCache_cmd(cache_group, self.alembics)
            if onlinePath:
                try:
                    #cmds.setAttr(fileName + '.fileTextureName', onlinePath, type='string')
		            pm.PyNode(fileName).abc_File.set(onlinePath)
                except:
                    pass
        
        QMessageBox.information(self.win, u'��ʾ', u'�ϴ��������\n')
        self.INIT_CacheListView()

    def MyCMD_selectTexture(self, QModelIndex):
        selected = []
        for s in self.win.QC_LV_TextureList.selectedIndexes():
            selected.append(self.tablemodel._datas[s.row()][0])

        if len(selected):
            #cmds.select(selected)
	        pm.select(selected)

    def MyCMD_selectCache(self, QModelIndex):
        selected = []
        for s in self.win.QC_LV_CacheList.selectedIndexes():
            selected.append(self.cachemodel._datas[s.row()][0])

        if len(selected):
            #cmds.select(selected)
	        pm.select(selected)

    def INIT_ListView(self):
        textures = []
        #files = cmds.ls(type='file')
        files = pm.ls(type='file')
        for f in files:
            #image = cmds.getAttr(f + '.fileTextureName')
            image = pm.PyNode(f + '.fileTextureName').get()
            #if not cmds.getAttr(f + '.useFrameExtension'):
            if not pm.PyNode(f + '.useFrameExtension').get():
                textures.append([f, [image]])
            else:
                tmp = [f, []]
                for a in sis.Get(image).rv:
                    tmp[1].append(a)

                textures.append(tmp)

        self.tablemodel = MyModel(textures)
        self.win.QC_LV_TextureList.setModel(self.tablemodel)
        showAllBox = self.win.QC_CKB_DisplayAllTexture.isChecked()
        if showAllBox:
            for i in self.tablemodel.hideGroup:
                self.win.QC_LV_TextureList.setRowHidden(i, 0)

        else:
            for i in self.tablemodel.hideGroup:
                self.win.QC_LV_TextureList.setRowHidden(i, 1)
		
    def INIT_CacheListView(self):
        caches = []
        nodes = pm.ls(type='AlembicNode')
        for n in nodes:
            abc = n.abc_File.get()
            caches.append([n.name(), [abc]])
        
        self.cachemodel = MyCacheModel(caches)
        self.win.QC_LV_CacheList.setModel(self.cachemodel)
        showAllBox = self.win.QC_CKB_DisplayAllCache.isChecked()
        if showAllBox:
            for i in self.cachemodel.hideGroup:
                self.win.QC_LV_CacheList.setRowHidden(i, 0)
        
        else:
            for i in self.cachemodel.hideGroup:
                self.win.QC_LV_CacheList.setRowHidden(i, 1)

    def MyCMD_checkFile(self):
        saveMode = self.win.QC_CBB_SaveMode.currentIndex()
        #currentFile = cmds.file(q=1, sn=1)
        currentFile = "%s" %pm.Env().sceneName()
        projectFolder = str(self.win.QC_LB_ProjectFolder.text())
        mayaFileName = str(self.win.QC_LB_MayaFileName.text())
        SaveName = projectFolder + '\\scenes\\' + mayaFileName
        __ifSeccess = 0
        if saveMode == 0:
            try:
                #cmds.file(rename=SaveName)
                #cmds.file(force=1, save=1)
                pm.saveAs(SaveName, f=1)
                __ifSeccess = 1
            except:
                __ifSeccess = 0

        elif saveMode == 1:
            if os.path.exists(currentFile):
                try:
                    shutil.copyfile(currentFile, SaveName)
                    __ifSeccess = 1
                except:
                    __ifSeccess = 0

            else:
                QMessageBox.question(None, u'ע��', u'��ǰ�ļ�������:\n' + currentFile)
        if __ifSeccess == 1:
            QMessageBox.information(None, u'�ɹ�', u'�����ļ��ϴ��ɹ�:\n' + SaveName)
            self.win.QC_LB_MayaFilePath.setText(SaveName)
        elif __ifSeccess == 0:
            QMessageBox.critical(None, u'ʧ��', u'�����ļ��ϴ�ʧ��:\n' + SaveName)
        return

    def MyCMD_submit(self):
        # �ύ��deadline
        # ������ȡ����, ����job_info.job ��  plug_info.job
        pass
        


class MyModel(QAbstractListModel):

    def __init__(self, datas = []):
        super(MyModel, self).__init__()
        self._datas = datas
        self.hideGroup = self.My_SetHideGroup()

    def My_SetHideGroup(self):
        rv = []
        for i in range(len(self._datas)):
            if self._datas[i][1][0][0] not in 'cdefghiCDEFGGI':
                rv.append(i)

        return rv

    def data(self, index, role = Qt.DisplayRole):
        __row = index.row()
        __fileName = self._datas[__row][0]
        __imagePath = self._datas[__row][1]
        if role == Qt.ForegroundRole:
            if __row not in self.hideGroup:
                return QBrush(Qt.red)
        elif role == Qt.DisplayRole:
            Display = __imagePath[0]
            if len(__imagePath) > 1:
                Display += ' ( --sequence : %i images )' % len(__imagePath)
            return Display

    def rowCount(self, parent):
        return len(self._datas)

class MyCacheModel(QAbstractListModel):

    def __init__(self, datas = []):
        super(MyCacheModel, self).__init__()
        self._datas = datas
        self.hideGroup = self.My_SetHideGroup()

    def My_SetHideGroup(self):
        rv = []
        for i in range(len(self._datas)):
            if self._datas[i][1][0][0] not in 'cdefghiCDEFGGI':
                rv.append(i)
        
        return rv

    def data(self, index, role = Qt.DisplayRole):
        __row = index.row()
        __fileName = self._datas[__row][0]
        __imagePath = self._datas[__row][1]
        if role == Qt.ForegroundRole:
            if __row not in self.hideGroup:
                return QBrush(Qt.red)
        elif role == Qt.DisplayRole:
            Display = __imagePath
            return Display

    def rowCount(self, parent):
        return len(self._datas)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    pgw = MusterCheckIn()
    app.exec_()

