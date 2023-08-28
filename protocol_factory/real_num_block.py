#!/usr/bin/env python3
# -*- coding: gb2312 -*-
from protocol_factory.protocol import DataBlock
from string import Template
from enum import Enum
import os

TYPE_INFO = {
    'uint8' : [1, 'uint8_t'],
    'int8' : [1, 'int8_t'],
    'uint16' : [2, 'uint16_t'],
    'int16' : [2, 'int16_t'],
    'uint32' : [4, 'uint32_t'],
    'int32' : [4, 'int32_t'],
    'float' : [4, 'float'],
    'double' : [8, 'double']
}

#ʵ�����ݿ飬�Ὣ�յ��������ֽ�����ת���ɻ�����������
class RealNumBlock (DataBlock):
    #��ȡ����״̬ö��
    def GetAllState(self):
        objTemplate = Template(u'${MODULE_NAME_CAP}_STATE_WAIT_${WAIT_DATA_NAME}')
        strEnum = objTemplate.substitute(MODULE_NAME_CAP = self.ModuleName.upper(), WAIT_DATA_NAME = self.Name.upper())

        return [strEnum]

    #���ɽṹ���ڵ����ݽṹ����
    def GenerateDataDefine(self):
        objTemplate = Template(u'    ${TYPE_NAME} ${BLOCK_NAME};')
        strDataDefine = objTemplate.substitute(TYPE_NAME = TYPE_INFO[self.NumType][1], BLOCK_NAME = self.Name.capitalize())

        return strDataDefine

    #�������ݴ������еı�������
    def GenerateFuncDataDefine(self):
        objTemplate = Template(u'    uint32_t ${BLOCK_NAME_FIRST_CAP}ReceiveNum = 0;\n')
        strDataDefine = objTemplate.substitute(BLOCK_NAME_FIRST_CAP = self.Name.capitalize())

        return strDataDefine

    #����״̬����Case, ֱ����Case�д���
    def GenerateCase(self, empty_state, next_state):
        UpPath = os.path.abspath('.')  #��ʾ��ǰ�������ļ�����һ���ļ��еľ���·��
        TemplateFile = open(UpPath + os.sep + 'template' + os.sep + 'real_num_case.template', 'r', encoding = 'gb2312')
        strTemplate = TemplateFile.read()
        TemplateFile.close()
        objTemplate = Template(strTemplate)

        VariableName = self.Name.capitalize()

        strCase = ''

        if 'small' == self.Endianness:
            splicing = '*((uint8_t*)(&${STRUCT_NAME}.${VARIABLE_NAME})) &= Byte << ${BLOCK_NAME_FIRST_CAP}ReceiveNum;'
        else:
            splicing = '*((uint8_t*)(&${STRUCT_NAME}.${VARIABLE_NAME})) &= Byte << (sizeof(${STRUCT_NAME}.${VARIABLE_NAME}) - ${BLOCK_NAME_FIRST_CAP}ReceiveNum);'
        objSplicingTemplate = Template(splicing)
        strSplicing = objSplicingTemplate.substitute(STRUCT_NAME = 'mParseAns', VARIABLE_NAME = VariableName, BLOCK_NAME_FIRST_CAP = VariableName)

        #���һ��״̬����λ��־λ
        if '' == next_state:
            strOptNextState = '\n            ' + self.ModuleName.upper() + '_HasNewData = SET;'
        else:
            strOptNextState = ''

        #����ģ��Ͳ�������ö�ٶ���
        strCase = objTemplate.substitute(NOW_STATE_ENUM = self.GetAllState()[0], VARIABLE_NAME = VariableName,
            STRUCT_NAME = 'mParseAns', SPLICING_OPT = strSplicing, NEXT_STATE_ENUM = next_state, OPT_ON_NEXT_STATE = strOptNextState)

        strCase += '\n\n'

        return strCase

    #����״̬����Case, ���ô���������
    def GenerateDealCase(self):
        return ''

    #���ɴ�����
    def GenerateDealFunc(self):
        return ''

    #���캯��
    def __init__(self, module_name, name, num_type, endianness = 'small'):
        super().__init__(module_name, name, endianness)
        self.AllState = []
        self.NumType = num_type
        self.ByteLen = TYPE_INFO[num_type][0]

    #֧�ַ������±�������ȡ��ĳ���ֽ���
    def __getitem__(self, key):
        return self.Data[key]

    #֧�ַ������±�����������ĳ���ֽ���
    def __setitem__(self, key, value):
            self.Data[key] = value

#���Դ���
if __name__ == '__main__':
    print('Test...')
    objBlock = RealNumBlock('zkq', 'param', 'uint32')
    strDefine = objBlock.GenerateMicro()
    strEnum = objBlock.GenerateStateEnum()
    strCase = objBlock.GenerateCase('STATE_EMPTY', 'NEXT_STATE')
    strDataDefine = objBlock.GenerateFuncDataDefine()
    print(strDefine)
    print(strEnum)
    print(strCase)
    print(strDataDefine)