import unittest
from unittest.mock import patch, Mock

import mcp2221
from mcp2221.enums import *
from mcp2221.exceptions import *

class MCPTestCase(unittest.TestCase):
    def setUp(self):
        # this is the kind of reply expected for 0xb0 command (read flash settings registers)
        self.xb0_00 = [176, 0, 10, 0, 124, 18, 18, 108, 216, 4, 221, 0, 128, 50, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        # this is the kind of reply expected for 0x61 command (read SRAM settings registers)
        self.x61 = [97, 0, 18, 4, 120, 18, 104, 108, 216, 4, 221, 0, 128, 50, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 45, 0, 73, 0, 50, 0, 67, 0, 47, 0, 85, 0, 65, 0, 82, 0, 84, 0, 32, 0, 67, 0, 111, 0, 109, 0, 98, 0, 111, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.mcp = mcp2221.MCP2221()
        self.mcp.dev = Mock()
        self.mcp._opened = True
    
    def __wbytes_to_int(self, bytes):
        return (bytes[0] & 0xff) + (bytes[1] << 8)

    def do_test_read_func_word(self, func, idx0:int, value:int = 0xffff, *args) -> None:
        self.mcp._read_response.return_value[idx0:idx0+2] = [0, 0]
        self.assertEqual(func(*args), 0)
        self.mcp._read_response.return_value[idx0:idx0+2] = [value & 0xff, value >> 8]
        self.assertEqual(func(*args), value)

    def do_test_read_func_byte(self, func, idx:int, value:int = 0xff, *args) -> None:
        self.mcp._read_response.return_value[idx] = 0
        self.assertEqual(func(*args), 0)
        self.mcp._read_response.return_value[idx] = value
        self.assertEqual(func(*args), value)
    
    def do_test_read_func_bool(self, func, idx:int, *args) -> None:
        self.mcp._read_response.return_value[idx] = 0
        self.assertFalse(func(*args))
        self.mcp._read_response.return_value[idx] = 0x01
        self.assertTrue(func(*args))

    def do_test_read_func_bit(self, func, byte:int, bit:int, *args) -> None:
        self.mcp._read_response.return_value[byte] = 0
        self.assertFalse(func(*args))
        self.mcp._read_response.return_value[byte] = (1 << bit)
        self.assertTrue(func(*args))

    def do_test_write_func_word(self, func, idx0:int, valuemin:int = 0, valuemax:int = 0xffff, argsmin:list = [0], argsmax:list = [0xffff]) -> None:
        func(*argsmin)
        self.assertEqual(self.__wbytes_to_int(self.mcp.dev.write.call_args[0][0][idx0:idx0+2]), valuemin)
        func(*argsmax)
        self.assertEqual(self.__wbytes_to_int(self.mcp.dev.write.call_args[0][0][idx0:idx0+2]), valuemax)
    
    def do_test_write_func_byte(self, func, idx:int, valuemin:int = 0, valuemax:int = 0xff, argsmin:list = [0], argsmax:list = [0xff]) -> None:
        func(*argsmin)
        self.assertEqual(self.mcp.dev.write.call_args[0][0][idx], valuemin)
        func(*argsmax)
        self.assertEqual(self.mcp.dev.write.call_args[0][0][idx], valuemax)
    
    def do_test_write_func_bool(self, func, idx:int, argsFalse:list = [False], argsTrue:list = [True]) -> None:
        func(*argsFalse)
        self.assertEqual(self.mcp.dev.write.call_args[0][0][idx], 0)
        func(*argsTrue)
        self.assertEqual(self.mcp.dev.write.call_args[0][0][idx], 1)

    def do_test_write_func_bit(self, func, byte:int, bit:int, argsFalse:list = [False], argsTrue:list = [True]) -> None:
        func(*argsFalse)
        self.assertEqual(self.mcp.dev.write.call_args[0][0][byte], 0)
        func(*argsTrue)
        self.assertEqual(self.mcp.dev.write.call_args[0][0][byte], 1 << bit)

    def do_test_read_prop_word(self, prop:str, idx0:int, value:int = 0xffff) -> None:
        self.do_test_read_func_word(lambda:getattr(self.mcp, prop), idx0, value)
    
    def do_test_read_prop_byte(self, prop:str, idx:int, value:int = 0xff) -> None:
        self.do_test_read_func_byte(lambda:getattr(self.mcp, prop), idx, value)
    
    def do_test_read_prop_bool(self, prop:str, idx:int) -> None:
        self.do_test_read_func_bool(lambda:getattr(self.mcp, prop), idx)
    
    def do_test_read_prop_bit(self, prop:str, byte:int, bit:int) -> None:
        self.do_test_read_func_bit(lambda:getattr(self.mcp, prop), byte, bit)
    
    def do_test_write_prop_word(self, prop:str, idx0:int, valuemin:int = 0, valuemax:int = 0xffff, argsmin:list = [0], argsmax:list = [0xffff]) -> None:
        self.do_test_write_func_word(lambda v:setattr(self.mcp, prop, v), idx0, valuemin, valuemax, argsmin, argsmax)
    
    def do_test_write_prop_byte(self, prop:str, idx:int, valuemin:int = 0, valuemax:int = 0xff, argsmin:list = [0], argsmax:list = [0xff]) -> None:
        self.do_test_write_func_byte(lambda v:setattr(self.mcp, prop, v), idx, valuemin, valuemax, argsmin, argsmax)
    
    def do_test_write_prop_bool(self, prop:str, idx:int, argsFalse:list = [False], argsTrue:list = [True]) -> None:
        self.do_test_write_func_bool(lambda v:setattr(self.mcp, prop, v), idx, argsFalse, argsTrue)

    def do_test_write_prop_bit(self, prop:str, byte:int, bit:int, argsFalse:list = [False], argsTrue:list = [True]) -> None:
        self.do_test_write_func_bit(lambda v:setattr(self.mcp, prop, v), byte, bit, argsFalse, argsTrue)


class MCPTestWithReadMock(MCPTestCase):
    def setUp(self):
        super().setUp()
        self.mcp._read_response = Mock()
        self.mcp._read_response.return_value = bytearray(64)
