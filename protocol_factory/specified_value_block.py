#!/usr/bin/env python3
# -*- coding: gb2312 -*-
from protocol_factory.protocol import DataBlock
from string import Template
import os

#����ֵ���ݿ飬Ҫ���յ��������������ֵֵ��˳�����
class SpecifiedValueBlock (DataBlock):
    #����AllState
    def _RefreshAllState(self):
        objTemplate = Template(u'${MODULE_NAME_CAP}_STATE_WAIT_${WAIT_DATA_NAME}')

        self.AllState.clear()

        #ֻ��һ���ֽڵĲ�Ҫ������
        if 1 == len(self.Data):
            strEnumTemp = objTemplate.substitute(MODULE_NAME_CAP = self.ModuleName.upper(), WAIT_DATA_NAME = self.Name.upper())
            #��ӵ��ֵ���
            self.AllState[self.Data[0]] = strEnumTemp

            return

        #����ģ��Ͳ�������ö�ٶ���
        for ValueByteIndex in range(len(self.Data)):
            strEnumTemp = objTemplate.substitute(MODULE_NAME_CAP = self.ModuleName.upper(), WAIT_DATA_NAME = self.Name.upper() + str(ValueByteIndex))
            #��ӵ��ֵ���
            self.AllState[self.Data[ValueByteIndex]] = strEnumTemp

        return

    #��ȡ����״̬ö��
    def GetAllState(self):
        States = []
        for strEnumTemp in self.AllState.values():
            States.append(strEnumTemp)
        return States

    #��������궨��
    def GenerateMicro(self):
        objTemplate = Template(u'#define ${MODULE_NAME_CAP}_${BLOCK_NAME_CAP}${HEADER_BYTE_NUM} (${FRAME_HEADER_BYTE})\t\t/* ${BLOCK_NAME_CAP}��$HEADER_BYTE_NUM�ֽ� */'.expandtabs(4))

        strFrameHeaderDefine = ''

        #����ģ��Ͳ��������ļ�
        for ValueByteIndex in range(len(self.Data)):
            #����ģ������֡ͷ��i���ֽڵĺ궨��
            strDefineTemp = objTemplate.substitute(MODULE_NAME_CAP = self.ModuleName.upper(), BLOCK_NAME_CAP = self.Name.upper(),
                HEADER_BYTE_NUM = str(ValueByteIndex), FRAME_HEADER_BYTE = hex(self.Data[ValueByteIndex]))

            #���ö�����֮ǰ�ĺϲ�����������ĩ��ӻ���
            strFrameHeaderDefine = strFrameHeaderDefine + strDefineTemp + '\n'

        return strFrameHeaderDefine

    #����״̬����Case, ֱ����Case�д���
    def GenerateCase(self, empty_state, next_state):
        UpPath = os.path.abspath('.')  #��ʾ��ǰ�������ļ�����һ���ļ��еľ���·��
        TemplateFile = open(UpPath + os.sep + 'template' + os.sep + 'specified_value_case.template', 'r', encoding = 'gb2312')
        strTemplate = TemplateFile.read()
        TemplateFile.close()
        objTemplate = Template(strTemplate)

        strCase = ''
        NextValue = self.Data[0]

        strNextStateEnum = self.AllState[self.Data[0]]

        #����ģ��Ͳ�������ö�ٶ���
        for ValueIndex in range(len(self.Data) - 1):
            NowValue = self.Data[ValueIndex]
            NextValue = self.Data[ValueIndex + 1]
            strNowStateEnum = self.AllState[NowValue]
            strNextStateEnum = self.AllState[NextValue]
            #����ģ������һ��case
            strCaseTemp = objTemplate.substitute(NOW_STATE_ENUM = strNowStateEnum, SPECIFIED_VALUE = hex(NowValue), 
                NEXT_STATE_ENUM = strNextStateEnum, STATE_EMPTY = empty_state, OPT_ON_NEXT_STATE = '')

            #����case��֮ǰ�ĺϲ�����������ĩ��ӻ���
            strCase = strCase + strCaseTemp + '\n\n'

        #���һ��״̬����λ��־λ
        if '' == next_state:
            strOptNextState = '\n            ' + self.ModuleName.upper() + '_HasNewData = SET;'
            next_state = empty_state
        else:
            strOptNextState = ''

        #���һ�����⴦����Ϊ������һ��״̬���ɱ����ݿ����
        strCaseTemp = objTemplate.substitute(NOW_STATE_ENUM = strNextStateEnum, SPECIFIED_VALUE = hex(NextValue), 
                NEXT_STATE_ENUM = next_state, STATE_EMPTY = empty_state, OPT_ON_NEXT_STATE = strOptNextState)
        #����case��֮ǰ�ĺϲ�����������ĩ��ӻ���
        strCase = strCase + strCaseTemp + '\n'

        return strCase

    #����״̬����Case, ���ô���������
    def GenerateDealCase(self):
        return ''

    #���ɴ�����
    def GenerateDealFunc(self):
        return ''

    #���캯��
    def __init__(self, module_name, name, data):
        self.AllState = {}
        super().__init__(module_name, name)
        self.Data = data
        self._RefreshAllState()

    #֧�ַ������±�������ȡ��ĳ���ֽ���
    def __getitem__(self, key):
        return self.Data[key]

    #֧�ַ������±�����������ĳ���ֽ���
    def __setitem__(self, key, value):
            self.Data[key] = value


#���Դ���
if __name__ == '__main__':
    print('Test...')
    objBlock = SpecifiedValueBlock('zkq', 'test', [0xaa, 0xab])
    strDefine = objBlock.GenerateMicro()
    strEnum = objBlock.GenerateStateEnum()
    strCase = objBlock.GenerateCase('STATE_EMPTY', 'NEXT_STATE')
    print(strDefine)
    print(strEnum)
    print(strCase)