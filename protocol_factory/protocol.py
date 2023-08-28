#!/usr/bin/env python3
# -*- coding: gb2312 -*-
from string import Template
import os

class DataBlock:
    #获取所有状态枚举
    def GetAllState(self):
        return []

    #生成所需宏定义
    def GenerateMicro(self):
        return ''

    #生成结构体内的数据结构定义
    def GenerateDataDefine(self):
        return ''

    #生成状态枚举值
    def GenerateStateEnum(self):
        AllState = self.GetAllState()

        strEnum = ''
        for strStateEnum in AllState:
            strEnum += '    ' + strStateEnum + ',\n'

        return strEnum

    #生成数据处理函数中的变量定义
    def GenerateFuncDataDefine(self):
        return ''

    #生成状态机的Case, 直接在Case中处理
    def GenerateCase(self, empty_state, next_state):
        return ''

    #生成状态机的Case, 调用处理函数处理
    def GenerateDealCase(self):
        return ''

    #生成处理函数
    def GenerateDealFunc(self):
        return ''

    #构造函数
    def __init__(self, module_name, name, endianness = 'small'):
        self.ByteLen = 0
        self.Endianness = endianness
        self.ModuleName = module_name
        self.Name = name

    #支持方括号下标索引获取其某个字节数
    def __getitem__(self, key):
        return self.Data[key]

    #支持方括号下标索引设置其某个字节数
    def __setitem__(self, key, value):
            self.Data[key] = value


class Protocol:
    #生成所需宏定义
    def GenerateMicro(self):
        strTemp = ''

        #遍历所有数据块，调用其生成的代码
        for objBlock in self.Datas:
            strTemp = strTemp + objBlock.GenerateMicro()

        return strTemp

    #生成状态枚举值
    def GenerateStateEnum(self):
        strTemp = ''

        #遍历所有数据块，调用其生成的代码
        for objBlock in self.Datas:
            strTemp = strTemp + objBlock.GenerateStateEnum()

        if strTemp[-1] == '\n':
            strTemp = strTemp[:-1]

        return strTemp

    #生成结构体内数据定义
    def GenerateStructDataDefine(self):
        strDataDefine = ''

        for objBlock in self.Datas:
            strDataDefine = strDataDefine + objBlock.GenerateDataDefine()

        return strDataDefine
    
    #生成函数内数据定义
    def GenerateFuncDataDefine(self):
        strDataDefine = ''

        for objBlock in self.Datas:
            strDataDefine = strDataDefine + objBlock.GenerateFuncDataDefine()

        return strDataDefine

    #生成状态机的Case, 直接在Case中处理
    #param[in]  empty_state: 空状态
    #param[in]  next_state: 该数据块接收完成后处于的状态
    def GenerateCase(self):
        strTemp = ''

        #遍历所有数据块，调用其生成的代码
        for BlockIndex in range(len(self.Datas) - 1):
            objBlock = self.Datas[BlockIndex]
            strNextState = self.Datas[BlockIndex + 1].GetAllState()[0]
            strTemp = strTemp + objBlock.GenerateCase(self.EmptyState, strNextState)

        strTemp = strTemp + self.Datas[-1].GenerateCase(self.EmptyState, '')

        return strTemp

    #生成状态机的Case, 调用处理函数处理
    def GenerateDealCase(self):
        strTemp = ''

        #遍历所有数据块，调用其生成的代码
        for objBlock in self.Datas:
            strTemp = strTemp + objBlock.GenerateDealCase()

        return strTemp

    #生成处理函数
    def GenerateDealFunc(self):
        strTemp = ''

        #遍历所有数据块，调用其生成的代码
        for objBlock in self.Datas:
            strTemp = strTemp + objBlock.GenerateDealFunc()

        return strTemp

    def GenerateH(self, file_name = ''):
        UpPath = os.path.abspath('.')  #表示当前所处的文件夹上一级文件夹的绝对路径
        if '' == file_name:
            file_name = UpPath + os.sep + r'output' + os.sep + self.Name + '.h'

        objFile = open(file_name, 'w', encoding = 'gb2312')
        objTemplateFile = open(UpPath + os.sep + 'template' + os.sep + 'ans.h.template', 'r', encoding = 'gb2312')
        strTemplate = objTemplateFile.read()
        objTemplateFile.close()
        objHTemplate = Template(strTemplate)

        strHFile = objHTemplate.substitute(MODULE_NAME_CAP = self.Name.upper(), FRAME_LENGTH = str(self.ByteLen), DEFINE_ALL_FRAME_HEADER = self.GenerateMicro(), 
            STATE_ENUM_VALUES = self.GenerateStateEnum(), DataDefine = self.GenerateStructDataDefine())
        
        objFile.write(strHFile)
        objFile.close()

        return
    
    def GenerateC(self, file_name = ''):
        UpPath = os.path.abspath('.')  #表示当前所处的文件夹上一级文件夹的绝对路径
        if '' == file_name:
            file_name = UpPath + os.sep + 'output' + os.sep + self.Name + '.c'

        objFile = open(file_name, 'w', encoding = 'gb2312')
        objTemplateFile = open(UpPath + os.sep + 'template' + os.sep + 'ans.c.template', 'r', encoding = 'gb2312')
        strTemplate = objTemplateFile.read()
        objTemplateFile.close()
        objHTemplate = Template(strTemplate)

        strHFile = objHTemplate.substitute(MODULE_NAME_CAP = self.Name.upper(), MODULE_NAME = self.Name, 
            RECEIVE_FUNC_DATA_DEFINE = self.GenerateFuncDataDefine(), STATE_NONE = '0', ALL_STATE_CASES = self.GenerateCase())
        
        objFile.write(strHFile)
        objFile.close()

        return

    def GenerateCode(self):
        self.GenerateH()
        self.GenerateC()

    #构造函数
    def __init__(self, name, data):
        self.Name = name
        self.Datas = data
        self.BlockCount = len(self.Datas)
        self.ByteLen = 0

        for i in range(len(self.Datas)):
            self.ByteLen += self.Datas[i].ByteLen

        self.EmptyState = self.Datas[0].GetAllState()[0]

    #支持方括号下标索引获取其某个字节数
    def __getitem__(self, key):
        return self.Datas[key]

    #支持方括号下标索引设置其某个字节数
    def __setitem__(self, key, value):
            self.Datas[key] = value
