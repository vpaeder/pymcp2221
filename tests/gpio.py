from .common import *

__all__ = ["TestWriteGPIO", "TestReadGPIO"]

class TestWriteGPIO(MCPTestWithReadMock):
    # command 0x50
    def setUp(self):
        super().setUp()
        self.mcp._read_response.return_value[0] = 0x50
    
    def test_write_gpio_value(self):
        for pin in range(4):
            self.mcp.gpio_write_value(pin, True)
            self.assertEqual(self.mcp.dev.write.call_args[0][0][2+pin*4], 0b1)
            self.assertEqual(self.mcp.dev.write.call_args[0][0][3+pin*4], 0b1)
            setattr(self.mcp, "gpio{:d}_value".format(pin), True)
            self.assertEqual(self.mcp.dev.write.call_args[0][0][2+pin*4], 0b1)
            self.assertEqual(self.mcp.dev.write.call_args[0][0][3+pin*4], 0b1)

    def test_write_gpio_direction(self):
        for pin in range(4):
            self.mcp.gpio_write_direction(pin, GPIODirection.Input)
            self.assertEqual(self.mcp.dev.write.call_args[0][0][4+pin*4], 0b1)
            self.assertEqual(self.mcp.dev.write.call_args[0][0][5+pin*4], 0b1)
            setattr(self.mcp, "gpio{:d}_direction".format(pin), GPIODirection.Input)
            self.assertEqual(self.mcp.dev.write.call_args[0][0][4+pin*4], 0b1)
            self.assertEqual(self.mcp.dev.write.call_args[0][0][5+pin*4], 0b1)


class TestReadGPIO(MCPTestWithReadMock):
    # command 0x51
    def setUp(self):
        super().setUp()
        self.mcp._read_response.return_value[0] = 0x51

    def test_read_gpio_value_ok(self):
        for pin in range(4):
            self.do_test_read_func_bool(self.mcp.gpio_read_value, 2+2*pin, pin)
            self.do_test_read_prop_bool("gpio{:d}_value".format(pin), 2+2*pin)

    def test_read_gpio_value_invalid(self):
        for pin in range(4):
            self.mcp._read_response.return_value[2+2*pin] = 0xee
            with self.assertWarns(InvalidReturnValueWarning):
                self.assertTrue(self.mcp.gpio_read_value(pin))
            with self.assertWarns(InvalidReturnValueWarning):
                self.assertTrue(getattr(self.mcp, "gpio{:d}_value".format(pin)))

    def test_read_gpio_direction(self):
        for pin in range(4):
            self.do_test_read_func_bool(self.mcp.gpio_read_direction, 3+2*pin, pin)
            self.do_test_read_prop_bool("gpio{:d}_direction".format(pin), 3+2*pin)

