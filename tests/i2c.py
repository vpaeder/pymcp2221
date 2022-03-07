from .common import *

__all__ = ["TestI2C", "TestI2CStatus"]

class TestI2C(MCPTestWithReadMock):
    # commands 0x90 - 0x94
    def test_i2c_write_data_fail(self):
        with self.assertRaises(InvalidParameterException):
            self.mcp.i2c_write_data(0xff, "")
        with self.assertRaises(InvalidParameterException):
            self.mcp.i2c_write_data(0x7f, " "*65536)
    
    def test_i2c_write_data_short_ok(self):
        for mode in I2CMode:
            self.mcp._read_response.return_value[0] = mode
            self.mcp.i2c_write_data(0x7f, "blablabla", mode)
            self.assertEqual(self.mcp.dev.write.call_args[0][0][3], 0x7f << 1)
            self.assertEqual(self.mcp.dev.write.call_args[0][0][1], 9) # data length

    def test_i2c_write_data_long_ok(self):
        for mode in I2CMode:
            self.mcp._read_response.return_value[0] = mode
            data = "a"*500
            self.mcp.i2c_write_data(0x7f, data, mode)
            self.assertEqual(self.mcp.dev.write.call_args[0][0][3], 0x7f << 1)
            self.assertEqual(self.mcp.dev.write.call_args[0][0][1], 500 & 0xff)
            self.assertEqual(self.mcp.dev.write.call_args[0][0][2], 500 >> 8)
            self.assertEqual(self.mcp.dev.write.call_count % 9, 0) # 9 write operations

    def test_i2c_read_data_fail_params(self):
        with self.assertRaises(InvalidParameterException):
            self.mcp.i2c_read_data(0x7f, 10, I2CMode.NoStop)
        with self.assertRaises(InvalidParameterException):
            self.mcp.i2c_read_data(0xff, 10)
    
    def test_i2c_read_data_fail_slave(self):
        for mode in [I2CMode.Start, I2CMode.RepeatedStart]:
            self.mcp._read_response.return_value[:4] = [0x40, 0, 0, 0x7f]
            with self.assertRaises(FailedCommandException):
                self.mcp.i2c_read_data(0x7f, 50, mode)

    def test_i2c_read_data_short_ok(self):
        data = "".join([chr(n) for n in range(64,114)]).encode("utf-8")
        for mode in [I2CMode.Start, I2CMode.RepeatedStart]:
            self.mcp._read_response.return_value[:4] = [0x40, 0, 0, 50]
            self.mcp._read_response.return_value[4:54] = data
            ret = self.mcp.i2c_read_data(0x7f, 50, mode)
            self.assertEqual(ret, data)

    def test_i2c_read_data_long_ok(self):
        data = 10*"".join([chr(n) for n in range(64,124)]).encode("utf-8")
        for mode in [I2CMode.Start, I2CMode.RepeatedStart]:
            self.mcp._read_response.return_value[:4] = [0x40, 0, 0, 60]
            self.mcp._read_response.return_value[4:54] = data
            ret = self.mcp.i2c_read_data(0x7f, len(data), mode)
            self.assertEqual(ret, data)
            self.assertEqual(self.mcp.dev.write.call_count % 10, 0) # 10 read operations


class TestI2CStatus(MCPTestWithReadMock):
    def setUp(self):
        super().setUp()
        self.mcp._read_response.return_value[0] = 0x10
    
    def test_i2c_requested_transfer_length(self):
        self.do_test_read_prop_word("i2c_requested_transfer_length", 9)
    
    def test_i2c_already_transferred_length(self):
        self.do_test_read_prop_word("i2c_already_transferred_length", 11)
    
    def test_i2c_internal_buffer_counter(self):
        self.do_test_read_prop_byte("i2c_internal_buffer_counter", 13)

    def test_i2c_slave_address(self):
        self.do_test_read_prop_word("i2c_slave_address", 16)

    def test_i2c_scl_state(self):
        self.do_test_read_prop_bool("i2c_scl_state", 22)

    def test_i2c_sda_state(self):
        self.do_test_read_prop_bool("i2c_sda_state", 23)
    
    def test_i2c_has_pending_value(self):
        for n in range(3):
            self.mcp._read_response.return_value[25] = n
            self.assertEqual(self.mcp.i2c_has_pending_value(), n)
