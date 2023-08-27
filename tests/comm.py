from .common import *

__all__ = ["TestOpenClose", "TestHIDCommands"]

class TestOpenClose(unittest.TestCase):
    def setUp(self):
        self.mcp = mcp2221.MCP2221()

    def test_open_ok(self):
        with patch("hid.device"):
            with self.assertRaises(FailedCommandException):
                # since there's no real device connected, the ADC state fix
                # won't work => return empty response
                self.mcp.open({"path":b""})
            self.assertTrue(self.mcp._opened)

    def test_open_fail(self):
        with self.assertRaises(IOException):
            self.mcp.open({"path":b""})
        self.assertFalse(self.mcp._opened)
    
    def test_open_no_path(self):
        with self.assertRaises(KeyError):
            self.mcp.open({"nopath":""})
    
    def test_close(self):
        self.mcp._opened = True
        self.mcp.dev = Mock()
        self.mcp.close()
        self.assertFalse(self.mcp._opened)


class TestHIDCommands(MCPTestCase):
    def test_read_response_fail_empty(self):
        self.mcp.dev.read.return_value = b""
        with self.assertRaises(mcp2221.exceptions.FailedCommandException):
            self.mcp._read_response(0x10)
    
    def test_read_response_fail_wrong_code(self):
        self.mcp.dev.read.return_value = [0x11]
        with self.assertRaises(mcp2221.exceptions.FailedCommandException):
            self.mcp._read_response(0x10)

    def test_read_response_fail_error(self):
        self.mcp.dev.read.return_value = [0x10, 0x01]
        with self.assertRaises(mcp2221.exceptions.FailedCommandException):
            self.mcp._read_response(0x10)

    def test_read_response_fail_not_open(self):
        self.mcp._opened = False
        with self.assertRaises(mcp2221.exceptions.IOException):
            self.mcp._read_response(0x10)

    def test_read_response_ok(self):
        self.mcp.dev.read.return_value = [0x10, 0x00]
        self.assertEqual(self.mcp._read_response(0x10), self.mcp.dev.read.return_value)

    def test_write_ok(self):
        cmd = self.mcp._build_command(0x10)
        self.mcp.dev.read.return_value = cmd
        self.assertEqual(self.mcp._write(0x10), cmd)
    
    def test_write_fail_not_open(self):
        self.mcp._opened = False
        with self.assertRaises(mcp2221.exceptions.IOException):
            self.mcp._write(0x10)

