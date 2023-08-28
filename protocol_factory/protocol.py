#!/usr/bin/env python3
# -*- coding: gb2312 -*-
from string import Template
import os

class DataBlock:
    #��ȡ����״̬ö��
    def GetAllState(self):
        return []

    #��������궨��
    def GenerateMicro(self):
        return ''

    #���ɽṹ���ڵ����ݽṹ����
    def GenerateDataDefine(self):
        return ''

    #����״̬ö��ֵ
    def GenerateStateEnum(self):
        AllState = self.GetAllState()

        strEnum = ''
        for strStateEnum in AllState:
            strEnum += '    ' + strStateEnum + ',\n'

        return strEnum

    #�������ݴ������еı�������
    def GenerateFuncDataDefine(self):
        return ''

    #����״̬����Case, ֱ����Case�д���
    def GenerateCase(self, empty_state, next_state):
        return ''

    #����״̬����Case, ���ô���������
    def GenerateDealCase(self):
        return ''

    #���ɴ�����
    def GenerateDealFunc(self):
        return ''

    #���캯��
    def __init__(self, module_name, name, endianness = 'small'):
        self.ByteLen = 0
        self.Endianness = endianness
        self.ModuleName = module_name
        self.Name = name

    #֧�ַ������±�������ȡ��ĳ���ֽ���
    def __getitem__(self, key):
        return self.Data[key]

    #֧�ַ������±�����������ĳ���ֽ���
    def __setitem__(self, key, value):
            self.Data[key] = value


class Protocol:
    #��������궨��
    def GenerateMicro(self):
        strTemp = ''

        #�����������ݿ飬���������ɵĴ���
        for objBlock in self.Datas:
            strTemp = strTemp + objBlock.GenerateMicro()

        return strTemp

    #����״̬ö��ֵ
    def GenerateStateEnum(self):
        strTemp = ''

        #�����������ݿ飬���������ɵĴ���
        for objBlock in self.Datas:
            strTemp = strTemp + objBlock.GenerateStateEnum()

        if strTemp[-1] == '\n':
            strTemp = strTemp[:-1]

        return strTemp

    #���ɽṹ�������ݶ���
    def GenerateStructDataDefine(self):
        strDataDefine = ''

        for objBlock in self.Datas:
            strDataDefine = strDataDefine + objBlock.GenerateDataDefine()

        return strDataDefine
    
    #���ɺ��������ݶ���
    def GenerateFuncDataDefine(self):
        strDataDefine = ''

        for objBlock in self.Datas:
            strDataDefine = strDataDefine + objBlock.GenerateFuncDataDefine()

        return strDataDefine

    #����״̬����Case, ֱ����Case�д���
    #param[in]  empty_state: ��״̬
    #param[in]  next_state: �����ݿ������ɺ��ڵ�״̬
    def GenerateCase(self):
        strTemp = ''

        #�����������ݿ飬���������ɵĴ���
        for BlockIndex in range(len(self.Datas) - 1):
            objBlock = self.Datas[BlockIndex]
            strNextState = self.Datas[BlockIndex + 1].GetAllState()[0]
            strTemp = strTemp + objBlock.GenerateCase(self.EmptyState, strNextState)

        strTemp = strTemp + self.Datas[-1].GenerateCase(self.EmptyState, '')

        return strTemp

    #����״̬����Case, ���ô���������
    def GenerateDealCase(self):
        strTemp = ''

        #�����������ݿ飬���������ɵĴ���
        for objBlock in self.Datas:
            strTemp = strTemp + objBlock.GenerateDealCase()

        return strTemp

    #���ɴ�����
    def GenerateDealFunc(self):
        strTemp = ''

        #�����������ݿ飬���������ɵĴ���
        for objBlock in self.Datas:
            strTemp = strTemp + objBlock.GenerateDealFunc()

        return strTemp

    def GenerateH(self, file_name = ''):
        UpPath = os.path.abspath('.')  #��ʾ��ǰ�������ļ�����һ���ļ��еľ���·��
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
        UpPath = os.path.abspath('.')  #��ʾ��ǰ�������ļ�����һ���ļ��еľ���·��
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

    #���캯��
    def __init__(self, name, data):
        self.Name = name
        self.Datas = data
        self.BlockCount = len(self.Datas)
        self.ByteLen = 0

        for i in range(len(self.Datas)):
            self.ByteLen += self.Datas[i].ByteLen

        self.EmptyState = self.Datas[0].GetAllState()[0]

    #֧�ַ������±�������ȡ��ĳ���ֽ���
    def __getitem__(self, key):
        return self.Datas[key]

    #֧�ַ������±�����������ĳ���ֽ���
    def __setitem__(self, key, value):
            self.Datas[key] = value
