#!/usr/bin/env python3
# -*- coding: gb2312 -*-
from protocol_factory.protocol import Protocol
from protocol_factory.real_num_block import RealNumBlock
from protocol_factory.specified_value_block import SpecifiedValueBlock

#���Դ���
#һ��Э�� ֡ͷ{0x7e, 0x7d} + uint32���� + ֡β{0xe7}
if __name__ == '__main__':
    FrameHeader = SpecifiedValueBlock('ccd', 'header', [0x7e, 0x7d])
    ParamUint32 = RealNumBlock('ccd', 'length', 'uint32')
    FrameEnd = SpecifiedValueBlock('ccd', 'end', [0xe7])
    TestProtocol = Protocol('ccd', [FrameHeader, ParamUint32, FrameEnd])

    TestProtocol.GenerateH()
    TestProtocol.GenerateC()