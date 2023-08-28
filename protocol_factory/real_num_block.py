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

#实数数据块，会将收到的若干字节数据转换成基础数据类型
class RealNumBlock (DataBlock):
    #获取所有状态枚举
    def GetAllState(self):
        objTemplate = Template(u'${MODULE_NAME_CAP}_STATE_WAIT_${WAIT_DATA_NAME}')
        strEnum = objTemplate.substitute(MODULE_NAME_CAP = self.ModuleName.upper(), WAIT_DATA_NAME = self.Name.upper())

        return [strEnum]

    #生成结构体内的数据结构定义
    def GenerateDataDefine(self):
        objTemplate = Template(u'    ${TYPE_NAME} ${BLOCK_NAME};')
        strDataDefine = objTemplate.substitute(TYPE_NAME = TYPE_INFO[self.NumType][1], BLOCK_NAME = self.Name.capitalize())

        return strDataDefine

    #生成数据处理函数中的变量定义
    def GenerateFuncDataDefine(self):
        objTemplate = Template(u'    uint32_t ${BLOCK_NAME_FIRST_CAP}ReceiveNum = 0;\n')
        strDataDefine = objTemplate.substitute(BLOCK_NAME_FIRST_CAP = self.Name.capitalize())

        return strDataDefine

    #生成状态机的Case, 直接在Case中处理
    def GenerateCase(self, empty_state, next_state):
        UpPath = os.path.abspath('.')  #表示当前所处的文件夹上一级文件夹的绝对路径
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

        #最后一个状态则置位标志位
        if '' == next_state:
            strOptNextState = '\n            ' + self.ModuleName.upper() + '_HasNewData = SET;'
        else:
            strOptNextState = ''

        #根据模板和参数生成枚举定义
        strCase = objTemplate.substitute(NOW_STATE_ENUM = self.GetAllState()[0], VARIABLE_NAME = VariableName,
            STRUCT_NAME = 'mParseAns', SPLICING_OPT = strSplicing, NEXT_STATE_ENUM = next_state, OPT_ON_NEXT_STATE = strOptNextState)

        strCase += '\n\n'

        return strCase

    #生成状态机的Case, 调用处理函数处理
    def GenerateDealCase(self):
        return ''

    #生成处理函数
    def GenerateDealFunc(self):
        return ''

    #构造函数
    def __init__(self, module_name, name, num_type, endianness = 'small'):
        super().__init__(module_name, name, endianness)
        self.AllState = []
        self.NumType = num_type
        self.ByteLen = TYPE_INFO[num_type][0]

    #支持方括号下标索引获取其某个字节数
    def __getitem__(self, key):
        return self.Data[key]

    #支持方括号下标索引设置其某个字节数
    def __setitem__(self, key, value):
            self.Data[key] = value

#测试代码
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