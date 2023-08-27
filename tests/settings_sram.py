from .common import *

__all__ = ["TestReadSRAMChipSettings", "TestWriteSRAMChipSettings",
           "TestGPIOFunctionSRAM"]

class TestReadSRAMChipSettings(MCPTestWithReadMock):
    def setUp(self):
        super().setUp()
        self.mcp._read_response.return_value = self.x61
        self.x61[4:] = bytearray(60)
        self.mcp.set_default_memory_target(MemoryType.SRAM)

    def test_read_clock_output_duty_cycle(self):
        self.x61[5] = 0b00011000
        v = self.mcp.read_clock_output_duty_cycle()
        self.assertEqual(v, ClockDutyCycle.Percent_75)
        v = self.mcp.clock_output_duty_cycle
        self.assertEqual(v, ClockDutyCycle.Percent_75)

    def test_read_clock_output_frequency(self):
        self.x61[5] = 0b00000111
        v = self.mcp.read_clock_output_frequency()
        self.assertEqual(v, ClockFrequency.Clock_375kHz)
        v = self.mcp.clock_output_frequency
        self.assertEqual(v, ClockFrequency.Clock_375kHz)

    def test_read_dac_reference_voltage(self):
        self.x61[6] = 0b11000000
        v = self.mcp.read_dac_reference_voltage()
        self.assertEqual(v, ReferenceVoltageValue.Voltage4_096V)
        v = self.mcp.dac_reference_voltage
        self.assertEqual(v, ReferenceVoltageValue.Voltage4_096V)

    def test_read_dac_reference_source(self):
        self.do_test_read_func_bit(self.mcp.read_dac_reference_source, 6, 5)
        self.do_test_read_prop_bit("dac_reference_source", 6, 5)

    def test_read_interrupt_on_falling_edge(self):
        self.do_test_read_func_bit(self.mcp.read_interrupt_on_falling_edge, 7, 6)
        self.do_test_read_prop_bit("interrupt_on_falling_edge", 7, 6)
    
    def test_read_interrupt_on_rising_edge(self):
        self.do_test_read_func_bit(self.mcp.read_interrupt_on_rising_edge, 7, 5)
        self.do_test_read_prop_bit("interrupt_on_rising_edge", 7, 5)

    def test_read_adc_reference_voltage(self):
        self.x61[7] = 0b00011000
        v = self.mcp.read_adc_reference_voltage()
        self.assertEqual(v, ReferenceVoltageValue.Voltage4_096V)
        v = self.mcp.adc_reference_voltage
        self.assertEqual(v, ReferenceVoltageValue.Voltage4_096V)

    def test_read_adc_reference_source(self):
        self.do_test_read_func_bit(self.mcp.read_adc_reference_source, 7, 2)
        self.do_test_read_prop_bit("adc_reference_source", 7, 2)


class TestWriteSRAMChipSettings(MCPTestWithReadMock):
    def setUp(self):
        super().setUp()
        self.x61[4:] = bytearray(60)
        self.mcp._read_response.return_value = self.x61
        self.mcp.set_default_memory_target(MemoryType.SRAM)

    def test_write_clock_output_duty_cycle(self):
        self.mcp.write_clock_output_duty_cycle(ClockDutyCycle.Percent_75)
        self.assertEqual(self.mcp.dev.write.call_args[0][0][2], 0b10011000)
        self.mcp.clock_output_duty_cycle = ClockDutyCycle.Percent_75
        self.assertEqual(self.mcp.dev.write.call_args[0][0][2], 0b10011000)

    def test_write_clock_output_frequency(self):
        self.mcp.write_clock_output_frequency(ClockFrequency.Clock_375kHz)
        self.assertEqual(self.mcp.dev.write.call_args[0][0][2], 0b10000111)
        self.mcp.clock_output_frequency = ClockFrequency.Clock_375kHz
        self.assertEqual(self.mcp.dev.write.call_args[0][0][2], 0b10000111)

    def test_write_dac_reference_voltage(self):
        self.mcp.write_dac_reference_voltage(ReferenceVoltageValue.Voltage4_096V)
        self.assertEqual(self.mcp.dev.write.call_args[0][0][3], 0b10000110)
        self.mcp.dac_reference_voltage = ReferenceVoltageValue.Voltage4_096V
        self.assertEqual(self.mcp.dev.write.call_args[0][0][3], 0b10000110)

    def test_write_dac_reference_source(self):
        self.mcp.write_dac_reference_source(ReferenceVoltageSource.Internal)
        self.assertEqual(self.mcp.dev.write.call_args[0][0][3], 0b10000001)
        self.mcp.dac_reference_source = ReferenceVoltageSource.Internal
        self.assertEqual(self.mcp.dev.write.call_args[0][0][3], 0b10000001)
    
    def test_write_dac(self):
        self.mcp.write_dac(31)
        self.assertEqual(self.mcp.dev.write.call_args[0][0][4], 0b10011111)
        self.mcp.dac_value = 31
        self.assertEqual(self.mcp.dev.write.call_args[0][0][4], 0b10011111)

    def test_write_adc_reference_voltage(self):
        self.mcp.write_adc_reference_voltage(ReferenceVoltageValue.Voltage4_096V)
        self.assertEqual(self.mcp.dev.write.call_args[0][0][5], 0b10000110)
        self.mcp.adc_reference_voltage = ReferenceVoltageValue.Voltage4_096V
        self.assertEqual(self.mcp.dev.write.call_args[0][0][5], 0b10000110)

    def test_write_adc_reference_source(self):
        self.mcp.write_adc_reference_source(ReferenceVoltageSource.Internal)
        self.assertEqual(self.mcp.dev.write.call_args[0][0][5], 0b10000001)
        self.mcp.adc_reference_source = ReferenceVoltageSource.Internal
        self.assertEqual(self.mcp.dev.write.call_args[0][0][5], 0b10000001)

    def test_write_interrupt_on_falling_edge(self):
        self.mcp.write_interrupt_on_falling_edge(True)
        self.assertEqual(self.mcp.dev.write.call_args[0][0][6], 0b10011000)
        self.mcp.interrupt_on_falling_edge = True
        self.assertEqual(self.mcp.dev.write.call_args[0][0][6], 0b10011000)
    
    def test_write_interrupt_on_rising_edge(self):
        self.mcp.write_interrupt_on_rising_edge(True)
        self.assertEqual(self.mcp.dev.write.call_args[0][0][6], 0b10000110)
        self.mcp.interrupt_on_rising_edge = True
        self.assertEqual(self.mcp.dev.write.call_args[0][0][6], 0b10000110)
    
    def test_clear_interrupt_flag(self):
        self.mcp.clear_interrupt_flag()
        self.assertEqual(self.mcp.dev.write.call_args[0][0][6], 0b10000001)


class TestGPIOFunctionSRAM(MCPTestWithReadMock):
    # command 0x50
    def setUp(self):
        super().setUp()
        self.x61[4:] = bytearray(60)
        self.mcp._read_response.return_value = self.x61
        self.mcp.set_default_memory_target(MemoryType.SRAM)
    
    def test_write_gpio_function(self):
        for pin in range(4):
            value = getattr(mcp2221.enums, "GPIO{:d}Function".format(pin))(2)
            getattr(self.mcp, "gpio{:d}_write_function".format(pin))(value)
            pin_args = self.mcp.dev.write.call_args_list[-2][0][0]
            self.assertEqual(pin_args[7], 0b10000000)
            self.assertEqual(pin_args[8+pin], 0b00000010)
            setattr(self.mcp, "gpio{:d}_function".format(pin), value)
            self.assertEqual(pin_args[7], 0b10000000)
            self.assertEqual(pin_args[8+pin], 0b00000010)
    
    def test_read_gpio_function(self):
        for pin in range(4):
            self.x61[22+pin] = 0b00000010
            expected = getattr(mcp2221.enums, "GPIO{:d}Function".format(pin))(2)
            v = getattr(self.mcp, "gpio{:d}_read_function".format(pin))()
            self.assertEqual(v, expected)
            v = getattr(self.mcp, "gpio{:d}_function".format(pin))
            self.assertEqual(v, expected)
