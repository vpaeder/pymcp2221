from .common import *

__all__ = ["TestReadWriteMemory"]

class TestReadWriteMemory(MCPTestCase):
    def test_read_flash_ok(self):
        self.mcp.dev.read.return_value = self.xb0_00
        self.assertEqual(self.mcp._read_flash(FlashDataSubcode.ChipSettings), self.xb0_00[4:14])
    
    def test_read_sram_ok(self):
        self.mcp.dev.read.return_value = self.x61
        self.assertEqual(self.mcp._read_sram(SramDataSubcode.ChipSettings), self.x61[4:22])
        self.assertEqual(self.mcp._read_sram(SramDataSubcode.GPSettings), self.x61[22:26])
    
    def test_read_flash_byte_ok(self):
        self.mcp.dev.read.return_value = self.xb0_00
        for n in range(0,9):
            result = self.mcp._read_flash_byte(FlashDataSubcode.ChipSettings, n, range(8))
            value = int("".join(["1" if x else "0" for x in reversed(result)]),2)
            self.assertEqual(value, self.xb0_00[4+n])

    def test_read_sram_byte_ok(self):
        self.mcp.dev.read.return_value = self.x61
        for n in range(0,9):
            result = self.mcp._read_sram_byte(SramDataSubcode.ChipSettings, n, range(8))
            value = int("".join(["1" if x else "0" for x in reversed(result)]),2)
            self.assertEqual(value, self.x61[4+n])

    def test_write_flash_byte_ok(self):
        # tests that 'write_flash_byte' sends the right data to hid write command
        xb1_00 = bytearray(64)
        xb1_00[0] = 0xb1
        with patch.object(self.mcp, "_read_response", return_value = self.xb0_00):
            for byte in range(9):
                for bit in range(8):
                    xb1_00[2:12] = self.xb0_00[4:14]
                    xb1_00[2+byte] = self.mcp._MCP2221__and(xb1_00[2+byte], 0xff - (1<<bit))
                    self.mcp._write_flash_byte(FlashDataSubcode.ChipSettings, byte, [bit], [False])
                    self.assertEqual(self.mcp.dev.write.call_args[0][0], xb1_00)
        
    def test_write_sram_ok(self):
        # tests that 'write_sram' sends the right data to hid write command
        with patch.object(self.mcp, "_read_response", return_value = self.x61):
            v = 0xff
            for byte in range(9):
                self.mcp._write_sram(SramDataSubcode.ChipSettings, byte, v)
                self.assertEqual(self.mcp.dev.write.call_args[0][0][2+byte], v)

