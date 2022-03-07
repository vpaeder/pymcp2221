from .common import *

__all__ = ["TestStatusSetParameters"]

class TestStatusSetParameters(MCPTestWithReadMock):
    # command 0x10
    def setUp(self):
        super().setUp()
        self.mcp._read_response.return_value[0x10]
        self.x10 = self.mcp._read_response.return_value

    def test_i2c_cancel_transfer(self):
        for v in I2CCancelTransferResponse:
            self.x10[2] = v
            ret = self.mcp.i2c_cancel_transfer()
            self.assertEqual(self.mcp.dev.write.call_args[0][0][2], 0x10)
            self.assertEqual(ret, v)
    
    def test_i2c_write_speed(self):
        for v in I2CSetSpeedResponse:
            self.x10[3] = v
            for w in I2CSpeed:
                self.x10[14] = w
                ret = self.mcp.i2c_write_speed(w)
                self.assertEqual(self.mcp.dev.write.call_args[0][0][3], 0x20)
                self.assertEqual(self.mcp.dev.write.call_args[0][0][4], w)
                self.assertEqual(ret, v)
                self.mcp.i2c_speed = w
                self.assertEqual(self.mcp.dev.write.call_args[0][0][3], 0x20)
                self.assertEqual(self.mcp.dev.write.call_args[0][0][4], w)
    
    def test_i2c_read_speed(self):
        for w in I2CSpeed:
            self.x10[14] = w
            self.assertEqual(self.mcp.i2c_read_speed(), w)
            self.assertEqual(self.mcp.i2c_speed, w)

    def test_read_interrupt_flag(self):
        self.do_test_read_func_bool(self.mcp.read_interrupt_flag, 24)
        self.do_test_read_prop_bool("interrupt_flag", 24)
    
    def test_read_adc(self):
        for n in range(3):
            self.do_test_read_func_word(self.mcp.read_adc, 50+2*n, 31, n)
            self.do_test_read_prop_word("adc{:d}_value".format(n), 50+2*n)
    
    def test_read_firmware_version(self):
        self.x10[46:50] = b"ABCD"
        self.assertEqual(self.mcp.read_firmware_version(), "ABCD")
        self.assertEqual(self.mcp.firmware_version, "ABCD")

