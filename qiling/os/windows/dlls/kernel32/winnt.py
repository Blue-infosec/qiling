#!/usr/bin/env python3
#
# Cross Platform and Multi Architecture Advanced Binary Emulation Framework
# Built on top of Unicorn emulator (www.unicorn-engine.org)

import struct
import time
from qiling.os.windows.const import *
from qiling.os.fncc import *
from qiling.os.windows.fncc import *
from qiling.os.windows.utils import *
from qiling.os.memory import align
from qiling.os.windows.thread import *
from qiling.os.windows.handle import *
from qiling.exception import *


# LONG InterlockedExchange(
#  LONG volatile *Target,
#  LONG          Value
# );
@winapi(cc=STDCALL, params={
    "Target": POINTER,
    "Value": UINT
})
def hook_InterlockedExchange(ql, address, params):
    old = int.from_bytes(ql.uc.mem_read(params['Target'], ql.pointersize), byteorder='little')
    ql.uc.mem_write(params['Target'], params['Value'].to_bytes(length=ql.pointersize, byteorder='little'))
    return old


# LONG InterlockedIncrement(
#  LONG volatile *Target,
# );
@winapi(cc=STDCALL, params={
    "Target": POINTER
})
def hook_InterlockedIncrement(ql, address, params):
    val = int.from_bytes(ql.uc.mem_read(params['Target'], ql.pointersize), byteorder='little')
    val += 1 & (2 ** ql.pointersize * 8)  # increment and overflow back to 0 if applicable
    ql.uc.mem_write(params['Target'], val.to_bytes(length=ql.pointersize, byteorder='little'))
    return val


# NTSYSAPI ULONGLONG VerSetConditionMask(
#   ULONGLONG ConditionMask, => 64bit param
#   DWORD     TypeMask,
#   BYTE      Condition
# );
@winapi(cc=STDCALL, params={
    "ConditionMask": ULONGLONG,
    "TypeMask": DWORD,
    "Condition": BYTE
})
def hook_VerSetConditionMask(ql, address, params):
    ConditionMask = params["ConditionMask"]
    TypeMask = params["TypeMask"]
    Condition = params["Condition"]
    if TypeMask == 0:
        ret = ConditionMask
    else:
        Condition &= VER_CONDITION_MASK
        if Condition == 0:
            ret = ConditionMask
        else:
            ullCondMask = Condition
            if TypeMask & VER_PRODUCT_TYPE:
                ConditionMask |= ullCondMask << (7 * VER_NUM_BITS_PER_CONDITION_MASK)
            elif TypeMask & VER_SUITENAME:
                ConditionMask |= ullCondMask << (6 * VER_NUM_BITS_PER_CONDITION_MASK)
            elif TypeMask & VER_SERVICEPACKMAJOR:
                ConditionMask |= ullCondMask << (5 * VER_NUM_BITS_PER_CONDITION_MASK)
            elif TypeMask & VER_SERVICEPACKMINOR:
                ConditionMask |= ullCondMask << (4 * VER_NUM_BITS_PER_CONDITION_MASK)
            elif TypeMask & VER_PLATFORMID:
                ConditionMask |= ullCondMask << (3 * VER_NUM_BITS_PER_CONDITION_MASK)
            elif TypeMask & VER_BUILDNUMBER:
                ConditionMask |= ullCondMask << (2 * VER_NUM_BITS_PER_CONDITION_MASK)
            elif TypeMask & VER_MAJORVERSION:
                ConditionMask |= ullCondMask << (1 * VER_NUM_BITS_PER_CONDITION_MASK)
            elif TypeMask & VER_MINORVERSION:
                ConditionMask |= ullCondMask << (0 * VER_NUM_BITS_PER_CONDITION_MASK)
            ret = ConditionMask
    return ret
