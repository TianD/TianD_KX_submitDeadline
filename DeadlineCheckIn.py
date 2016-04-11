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
import xml.etree.cElementTree as ET
import subprocess
import json
import SearchImageSequence as sis
reload(sis)
from PySide.QtGui import *
from PySide.QtCore import *   
import sip
#import maya.cmds as cmds
import pymel.core as pm

deadlinePath = "//KX-REN04/DeadlineRepository7/submission/Maya/Main"

deadlinePath in sys.path or sys.path.append(deadlinePath)

import MayaJigsaw

import DeadlineJobFile as job

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
    #JobTempPath = os.path.expanduser('~/AppData/Local/Thinkbox/Deadline7/temp')
    JobTempPath = 'e:/'
    DefaultJobInfo = os.path.join(Folder, 'default_maya_job_info.job')
    DefaultPluginInfo = os.path.join(Folder, 'default_maya_plugin_info.job')

    def __init__(self, parent = parentWindow):
        """
        Constructor
        """
        super(DeadlineCheckIn, self).__init__(parent)
        self.closeExistingWindow()
        self.setWindowTitle(u'提交Deadline')
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
        caches = os.path.join(project, 'cache/nCache/{0}'.format(pm.Env().sceneName().namebase))
        data = os.path.join(project, 'data')
        particles = os.path.join(project, 'particles')
        images = os.path.join(project, 'images')
        self.sourceimages = sourceimages
        self.alembics = alembics
        self.caches = caches
        self.images = images
        folders = [project,
	     alembics,
         caches,
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
                    QMessageBox.critical(None, u'注意', u'程序无法创建下列文件夹:\n' + f)
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
                
        QMessageBox.information(self.win, u'提示', u'上传贴图完成\n')
        self.INIT_ListView()

    def MyCMD_checkCache_selected(self):
        selected = []
        for s in self.win.QC_LV_CacheList.selectedIndexes():
            selected.append(self.cachemodel._datas[s.row()])

        for s in selected:
            fileName, cache_group = s
            if pm.PyNode(fileName).type() == "cacheFile":
                onlinePath = self.MyCMD_checkCache_cmd(cache_group, self.caches)
            elif pm.PyNode(fileName).type() == "AlembicNode":
                onlinePath = self.MyCMD_checkCache_cmd(cache_group, self.alembics)
            else :
                onlinePath = ''
            if onlinePath:
                if pm.PyNode(fileName).type() == "AlembicNode":
                    pm.PyNode(fileName).abc_File.set(onlinePath)
                elif pm.PyNode(fileName).type() == "cacheFile":
                    pm.PyNode(fileName).cachePath.set(os.path.dirname(onlinePath))
                
        QMessageBox.information(self.win, u'提示', u'上传缓存完成\n')
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
        
        QMessageBox.information(self.win, u'提示', u'上传贴图完成\n')
        self.INIT_ListView()

    def MyCMD_checkCache_all(self):
        selected = []
        for s in self.cachemodel._datas:
            selected.append(s)

        for s in selected:
            fileName, cache_group = s
            if pm.PyNode(fileName).type() == "cacheFile":
                onlinePath = self.MyCMD_checkCache_cmd(cache_group, self.caches)
            elif pm.PyNode(fileName).type() == "AlembicNode":
                onlinePath = self.MyCMD_checkCache_cmd(cache_group, self.alembics)
            else :  
                onlinePath = ''
            if onlinePath:
                if pm.PyNode(fileName).type() == "AlembicNode":
                    pm.PyNode(fileName).abc_File.set(onlinePath)
                elif pm.PyNode(fileName).type() == "cacheFile":
                    pm.PyNode(fileName).cachePath.set(os.path.dirname(onlinePath))
        
        QMessageBox.information(self.win, u'提示', u'上传缓存完成\n')
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
        sf = int(pm.PyNode('defaultRenderGlobals.fs').get())
        ef = int(pm.PyNode('defaultRenderGlobals.ef').get())
        textures = []
        #files = cmds.ls(type='file')
        files = pm.ls(type='file')
        for f in files:
            #image = cmds.getAttr(f + '.fileTextureName')
            image = f.fileTextureName.get()
            #if not cmds.getAttr(f + '.useFrameExtension'):
            if not f.useFrameExtension.get():
                textures.append([f.name(), [image]])
            else:
                offset = f.frameOffset.get()
                tmp = [f.name(), []]
                for a in sis.Get(image).rv:
                    tmp[1].append(a)
                if len(tmp[1]) > offset:
                    temp = [tmp[0], tmp[1][(offset):(offset + ef - sf + 1)]]
                else :
                    temp = tmp
                textures.append(temp)

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
        
        cacheFile = pm.ls(type = 'cacheFile')
        for c in cacheFile: 
            cachePath = c.cachePath.get()
            cacheName = c.cacheName.get()
            xml = os.path.join(cachePath, "{name}.xml".format(name = cacheName))
            if os.path.exists(xml):
                tree = ET.ElementTree(file = xml)
                type = list(tree.iter('cacheType'))[0].attrib['Format']
                perF = list(tree.iter('cacheTimePerFrame'))[0].attrib['TimePerFrame']
                timeRange = list(tree.iter('time'))[0].attrib['Range']
                perFrame = list(tree.iter('cacheTimePerFrame'))[0].attrib['TimePerFrame']
                startFrame, endFrame = timeRange.split('-')
                files = [xml]
                for i in range(int(startFrame)/int(perFrame), int(endFrame)/int(perFrame)+1):
                    cacheFile = os.path.join(cachePath, "{name}Frame{num}.{exr}".format(name = cacheName, num = i, exr = type))
                    files.append(cacheFile)
                caches.append([c.name(), files])
            
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
                QMessageBox.question(None, u'注意', u'当前文件不存在:\n' + currentFile)
        if __ifSeccess == 1:
            QMessageBox.information(None, u'成功', u'下列文件上传成功:\n' + SaveName)
            self.win.QC_LB_MayaFilePath.setText(SaveName)
        elif __ifSeccess == 0:
            QMessageBox.critical(None, u'失败', u'下列文件上传失败:\n' + SaveName)
        return

    def MyCMD_submit(self):
        # 提交到deadline
        # 从面板获取数据, 构造job_info.job 和  plug_info.job
        jobName = self.win.QC_LE_JobName.text()
        outputDir = self.win.QC_LE_OutputFolder.text()
        sceneFile = self.win.QC_LB_MayaFilePath.text()
        projectPath = self.win.QC_LB_ProjectFolder.text()
        outputFilePath = self.win.QC_LE_OutputFolder.text()
        renderer = self.win.QC_CBB_Renderer.currentText()
        priority = self.win.QC_SPB_Priority.value()
        build = self.win.QC_CBB_Build.currentText()
        version = self.win.QC_CBB_Version.currentText()
        startFrame = self.win.QC_LE_Sf.text()
        endFrame = self.win.QC_LE_Ef.text()
        frames = "{start}-{end}".format(start=startFrame, end=endFrame)
        if startFrame == endFrame: 
            frames = startFrame
            
        jobFile = os.path.join(self.JobTempPath, 'maya_job_info.job')
        jobinfo = job.JobInfo(jobFile)
        jobinfoLst = jobinfo.read(file = self.DefaultJobInfo)
        jobinfo.create(key = [i[0] for i in jobinfoLst], value = [i[1] for i in jobinfoLst])
        jobinfo.write(key = ['Name', 'Priority', 'Frames', 'OutputDirectory0'], value = [jobName, priority, frames, outputDir])
        
        pluginFile = os.path.join(self.JobTempPath, 'maya_plugin_info.job')
        pluginfo = job.JobInfo(pluginFile)
        pluginfoLst = pluginfo.read(file = self.DefaultPluginInfo)
        pluginfo.create(key = [i[0] for i in pluginfoLst], value = [i[1] for i in pluginfoLst])
        pluginfo.write(key = ['SceneFile', 'Version', 'Build', 'ProjectPath', 'Renderer', 'OutputFilePath'], value = [sceneFile, version, build, projectPath, renderer, outputFilePath])
        
        output = MayaJigsaw.CallDeadlineCommand([jobFile, pluginFile], True)
        return output
    

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
        print self._datas
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
        __cachePath = self._datas[__row][1]
        if role == Qt.ForegroundRole:
            if __row not in self.hideGroup:
                return QBrush(Qt.red)
        elif role == Qt.DisplayRole:
            Display = __cachePath[0]
            if len(__cachePath) > 1:
                Display += ' ( --sequence : %i images )' % len(__cachePath)
            return Display

    def rowCount(self, parent):
        return len(self._datas)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    pgw = MusterCheckIn()
    app.exec_()

