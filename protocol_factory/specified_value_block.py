#!/usr/bin/env python3
# -*- coding: gb2312 -*-
from protocol_factory.protocol import DataBlock
from string import Template
import os

#给定值数据块，要求收到的数必须跟给定值值和顺序都相等
class SpecifiedValueBlock (DataBlock):
    #更新AllState
    def _RefreshAllState(self):
        objTemplate = Template(u'${MODULE_NAME_CAP}_STATE_WAIT_${WAIT_DATA_NAME}')

        self.AllState.clear()

        #只有一个字节的不要带数字
        if 1 == len(self.Data):
            strEnumTemp = objTemplate.substitute(MODULE_NAME_CAP = self.ModuleName.upper(), WAIT_DATA_NAME = self.Name.upper())
            #添加到字典里
            self.AllState[self.Data[0]] = strEnumTemp

            return

        #根据模板和参数生成枚举定义
        for ValueByteIndex in range(len(self.Data)):
            strEnumTemp = objTemplate.substitute(MODULE_NAME_CAP = self.ModuleName.upper(), WAIT_DATA_NAME = self.Name.upper() + str(ValueByteIndex))
            #添加到字典里
            self.AllState[self.Data[ValueByteIndex]] = strEnumTemp

        return

    #获取所有状态枚举
    def GetAllState(self):
        States = []
        for strEnumTemp in self.AllState.values():
            States.append(strEnumTemp)
        return States

    #生成所需宏定义
    def GenerateMicro(self):
        objTemplate = Template(u'#define ${MODULE_NAME_CAP}_${BLOCK_NAME_CAP}${HEADER_BYTE_NUM} (${FRAME_HEADER_BYTE})\t\t/* ${BLOCK_NAME_CAP}第$HEADER_BYTE_NUM字节 */'.expandtabs(4))

        strFrameHeaderDefine = ''

        #根据模板和参数生成文件
        for ValueByteIndex in range(len(self.Data)):
            #根据模板生成帧头第i个字节的宏定义
            strDefineTemp = objTemplate.substitute(MODULE_NAME_CAP = self.ModuleName.upper(), BLOCK_NAME_CAP = self.Name.upper(),
                HEADER_BYTE_NUM = str(ValueByteIndex), FRAME_HEADER_BYTE = hex(self.Data[ValueByteIndex]))

            #将该定义与之前的合并，并且在行末添加换行
            strFrameHeaderDefine = strFrameHeaderDefine + strDefineTemp + '\n'

        return strFrameHeaderDefine

    #生成状态机的Case, 直接在Case中处理
    def GenerateCase(self, empty_state, next_state):
        UpPath = os.path.abspath('.')  #表示当前所处的文件夹上一级文件夹的绝对路径
        TemplateFile = open(UpPath + os.sep + 'template' + os.sep + 'specified_value_case.template', 'r', encoding = 'gb2312')
        strTemplate = TemplateFile.read()
        TemplateFile.close()
        objTemplate = Template(strTemplate)

        strCase = ''
        NextValue = self.Data[0]

        strNextStateEnum = self.AllState[self.Data[0]]

        #根据模板和参数生成枚举定义
        for ValueIndex in range(len(self.Data) - 1):
            NowValue = self.Data[ValueIndex]
            NextValue = self.Data[ValueIndex + 1]
            strNowStateEnum = self.AllState[NowValue]
            strNextStateEnum = self.AllState[NextValue]
            #依据模板生成一个case
            strCaseTemp = objTemplate.substitute(NOW_STATE_ENUM = strNowStateEnum, SPECIFIED_VALUE = hex(NowValue), 
                NEXT_STATE_ENUM = strNextStateEnum, STATE_EMPTY = empty_state, OPT_ON_NEXT_STATE = '')

            #将该case与之前的合并，并且在行末添加换行
            strCase = strCase + strCaseTemp + '\n\n'

        #最后一个状态则置位标志位
        if '' == next_state:
            strOptNextState = '\n            ' + self.ModuleName.upper() + '_HasNewData = SET;'
            next_state = empty_state
        else:
            strOptNextState = ''

        #最后一个特殊处理，因为它的下一个状态不由本数据块决定
        strCaseTemp = objTemplate.substitute(NOW_STATE_ENUM = strNextStateEnum, SPECIFIED_VALUE = hex(NextValue), 
                NEXT_STATE_ENUM = next_state, STATE_EMPTY = empty_state, OPT_ON_NEXT_STATE = strOptNextState)
        #将该case与之前的合并，并且在行末添加换行
        strCase = strCase + strCaseTemp + '\n'

        return strCase

    #生成状态机的Case, 调用处理函数处理
    def GenerateDealCase(self):
        return ''

    #生成处理函数
    def GenerateDealFunc(self):
        return ''

    #构造函数
    def __init__(self, module_name, name, data):
        self.AllState = {}
        super().__init__(module_name, name)
        self.Data = data
        self._RefreshAllState()

    #支持方括号下标索引获取其某个字节数
    def __getitem__(self, key):
        return self.Data[key]

    #支持方括号下标索引设置其某个字节数
    def __setitem__(self, key, value):
            self.Data[key] = value


#测试代码
if __name__ == '__main__':
    print('Test...')
    objBlock = SpecifiedValueBlock('zkq', 'test', [0xaa, 0xab])
    strDefine = objBlock.GenerateMicro()
    strEnum = objBlock.GenerateStateEnum()
    strCase = objBlock.GenerateCase('STATE_EMPTY', 'NEXT_STATE')
    print(strDefine)
    print(strEnum)
    print(strCase)