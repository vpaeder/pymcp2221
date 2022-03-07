from .common import *

__all__ = ["TestSendFlashAccessPassword", "TestMiscFunctions"]

class TestSendFlashAccessPassword(MCPTestWithReadMock):
    # command 0xb2
    def setUp(self):
        super().setUp()
        self.mcp._read_response.return_value[0] = 0xb2
    
    def test_unlock(self):
        self.mcp.unlock("password")
        self.assertEqual(self.mcp.dev.write.call_args[0][0][2:10], b"password")
        self.mcp.password = "password"
        self.assertEqual(self.mcp.dev.write.call_args[0][0][2:10], b"password")
    
    def test_write_flash_access_password(self):
        self.mcp._read_response.return_value[:3] = [0xb0, 0, 10]
        self.mcp.write_flash_access_password("password")
        self.assertEqual(self.mcp.dev.write.call_args[0][0][12:20], b"password")


class TestMiscFunctions(MCPTestWithReadMock):
    def test_reset_chip(self):
        self.mcp._read_response.return_value[0] = 0x70
        self.mcp.reset_chip()
        self.assertEqual(self.mcp.dev.write.call_args[0][0][:4], bytearray([0x70, 0xab, 0xcd, 0xef]))
