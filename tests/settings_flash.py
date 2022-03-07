from .common import *

__all__ = ["TestReadFlashChipSettings", "TestWriteFlashChipSettings",
           "TestReadFlashUSBDescriptors", "TestWriteFlashUSBDescriptors",
           "TestReadFlashGPSettings", "TestWriteFlashGPSettings"]

class TestReadFlashChipSettings(MCPTestWithReadMock):
    def setUp(self):
        super().setUp()
        self.xb0_00[4:] = bytearray(60)
        self.mcp._read_response.return_value = self.xb0_00
        self.mcp.set_default_memory_target(MemoryType.Flash)

    def test_read_cdc_sn_enumeration_enable(self):
        self.do_test_read_func_bit(self.mcp.read_cdc_sn_enumeration_enable, 4, 7)
        self.do_test_read_prop_bit("cdc_sn_enumeration_enable_flag", 4, 7)

    def test_read_led_idle_uart_rx_level(self):
        self.do_test_read_func_bit(self.mcp.read_led_idle_uart_rx_level, 4, 6)
        self.do_test_read_prop_bit("led_idle_uart_rx_level", 4, 6)

    def test_read_led_idle_uart_tx_level(self):
        self.do_test_read_func_bit(self.mcp.read_led_idle_uart_tx_level, 4, 5)
        self.do_test_read_prop_bit("led_idle_uart_tx_level", 4, 5)

    def test_read_led_idle_i2c_level(self):
        self.do_test_read_func_bit(self.mcp.read_led_idle_i2c_level, 4, 4)
        self.do_test_read_prop_bit("led_idle_i2c_level", 4, 4)

    def test_read_suspend_mode_logic_level(self):
        self.do_test_read_func_bit(self.mcp.read_suspend_mode_logic_level, 4, 3)
        self.do_test_read_prop_bit("suspend_mode_logic_level", 4, 3)

    def test_read_usb_configured_logic_level(self):
        self.do_test_read_func_bit(self.mcp.read_usb_configured_logic_level, 4, 2)
        self.do_test_read_prop_bit("usb_configured_logic_level", 4, 2)

    def test_read_security_option(self):
        self.xb0_00[4] = 0b00000010
        v = self.mcp.read_security_option()
        self.assertEqual(v, SecurityOption.PermanentlyLocked)
        v = self.mcp.security_option
        self.assertEqual(v, SecurityOption.PermanentlyLocked)
    
    def test_read_clock_output_duty_cycle(self):
        self.xb0_00[5] = 0b00011000
        v = self.mcp.read_clock_output_duty_cycle()
        self.assertEqual(v, ClockDutyCycle.Percent_75)
        v = self.mcp.clock_output_duty_cycle
        self.assertEqual(v, ClockDutyCycle.Percent_75)

    def test_read_clock_output_frequency(self):
        self.xb0_00[5] = 0b00000111
        v = self.mcp.read_clock_output_frequency()
        self.assertEqual(v, ClockFrequency.Clock_375kHz)
        v = self.mcp.clock_output_frequency
        self.assertEqual(v, ClockFrequency.Clock_375kHz)

    def test_read_dac_reference_voltage(self):
        self.xb0_00[6] = 0b11000000
        v = self.mcp.read_dac_reference_voltage()
        self.assertEqual(v, ReferenceVoltageValue.Voltage4_096V)
        v = self.mcp.dac_reference_voltage
        self.assertEqual(v, ReferenceVoltageValue.Voltage4_096V)

    def test_read_dac_reference_source(self):
        self.xb0_00[6] = 0b00100000
        v = self.mcp.read_dac_reference_source()
        self.assertEqual(v, ReferenceVoltageSource.Internal)
        v = self.mcp.dac_reference_source
        self.assertEqual(v, ReferenceVoltageSource.Internal)

    def test_read_dac_powerup_value(self):
        self.xb0_00[6] = 0b00011111
        v = self.mcp.read_dac_powerup_value()
        self.assertEqual(v, 31)
        v = self.mcp.dac_powerup_value
        self.assertEqual(v, 31)

    def test_read_interrupt_on_falling_edge(self):
        self.xb0_00[7] = 0b01000000
        v = self.mcp.read_interrupt_on_falling_edge()
        self.assertTrue(v)
        v = self.mcp.interrupt_on_falling_edge
        self.assertTrue(v)
    
    def test_read_interrupt_on_rising_edge(self):
        self.xb0_00[7] = 0b00100000
        v = self.mcp.read_interrupt_on_rising_edge()
        self.assertTrue(v)
        v = self.mcp.interrupt_on_rising_edge
        self.assertTrue(v)

    def test_read_adc_reference_voltage(self):
        self.xb0_00[7] = 0b00011000
        v = self.mcp.read_adc_reference_voltage()
        self.assertEqual(v, ReferenceVoltageValue.Voltage4_096V)
        v = self.mcp.adc_reference_voltage
        self.assertEqual(v, ReferenceVoltageValue.Voltage4_096V)

    def test_read_adc_reference_source(self):
        self.xb0_00[7] = 0b00000100
        v = self.mcp.read_adc_reference_source()
        self.assertEqual(v, ReferenceVoltageSource.Internal)
        v = self.mcp.adc_reference_source
        self.assertEqual(v, ReferenceVoltageSource.Internal)

    def test_read_usb_vid(self):
        self.do_test_read_func_word(self.mcp.read_usb_vid, 8)
        self.do_test_read_prop_word("usb_vid", 8)

    def test_read_usb_pid(self):
        self.do_test_read_func_word(self.mcp.read_usb_pid, 10)
        self.do_test_read_prop_word("usb_pid", 10)
    
    def test_read_usb_self_powered_attribute(self):
        self.do_test_read_func_bit(self.mcp.read_usb_self_powered_attribute, 12, 6)
        self.do_test_read_prop_bit("usb_self_powered_attribute", 12, 6)

    def test_read_usb_remote_wake_up_attribute(self):
        self.do_test_read_func_bit(self.mcp.read_usb_remote_wake_up_attribute, 12, 5)
        self.do_test_read_prop_bit("usb_remote_wake_up_attribute", 12, 5)

    def test_read_usb_current(self):
        self.xb0_00[13] = 0xff
        v = self.mcp.read_usb_current()
        self.assertEqual(v, 2*0xff)
        v = self.mcp.usb_current
        self.assertEqual(v, 2*0xff)


class TestWriteFlashChipSettings(MCPTestWithReadMock):
    def setUp(self):
        super().setUp()
        self.mcp._read_response.return_value[:3] = [0xb0, 0, 10]
        self.mcp.set_default_memory_target(MemoryType.Flash)

    def test_write_cdc_sn_enumeration_enable(self):
        self.do_test_write_func_bit(self.mcp.write_cdc_sn_enumeration_enable, 2, 7)
        self.do_test_write_prop_bit("cdc_sn_enumeration_enable_flag", 2, 7)

    def test_write_led_idle_uart_rx_level(self):
        self.do_test_write_func_bit(self.mcp.write_led_idle_uart_rx_level, 2, 6)
        self.do_test_write_prop_bit("led_idle_uart_rx_level", 2, 6)

    def test_write_led_idle_uart_tx_level(self):
        self.do_test_write_func_bit(self.mcp.write_led_idle_uart_tx_level, 2, 5)
        self.do_test_write_prop_bit("led_idle_uart_tx_level", 2, 5)

    def test_write_led_idle_i2c_level(self):
        self.do_test_write_func_bit(self.mcp.write_led_idle_i2c_level, 2, 4)
        self.do_test_write_prop_bit("led_idle_i2c_level", 2, 4)

    def test_write_suspend_mode_logic_level(self):
        self.do_test_write_func_bit(self.mcp.write_suspend_mode_logic_level, 2, 3)
        self.do_test_write_prop_bit("suspend_mode_logic_level", 2, 3)

    def test_write_usb_configured_logic_level(self):
        self.do_test_write_func_bit(self.mcp.write_usb_configured_logic_level, 2, 2)
        self.do_test_write_prop_bit("usb_configured_logic_level", 2, 2)

    def test_write_security_option(self):
        self.mcp.write_security_option(SecurityOption.PermanentlyLocked)
        self.assertEqual(self.mcp.dev.write.call_args[0][0][2], 0b00000010)
        self.mcp.security_option = SecurityOption.PasswordProtected
        self.assertEqual(self.mcp.dev.write.call_args[0][0][2], 0b00000001)

    def test_write_clock_output_duty_cycle(self):
        self.mcp.write_clock_output_duty_cycle(ClockDutyCycle.Percent_25)
        self.assertEqual(self.mcp.dev.write.call_args[0][0][3], 0b00001000)
        self.mcp.clock_output_duty_cycle = ClockDutyCycle.Percent_50
        self.assertEqual(self.mcp.dev.write.call_args[0][0][3], 0b00010000)

    def test_write_clock_output_frequency(self):
        self.mcp.write_clock_output_frequency(ClockFrequency.Clock_750kHz)
        self.assertEqual(self.mcp.dev.write.call_args[0][0][3], 0b00000110)
        self.mcp.clock_output_frequency = ClockFrequency.Clock_24MHz
        self.assertEqual(self.mcp.dev.write.call_args[0][0][3], 0b00000001)

    def test_write_dac_reference_voltage(self):
        self.mcp.write_dac_reference_voltage(ReferenceVoltageValue.Voltage2_048V)
        self.assertEqual(self.mcp.dev.write.call_args[0][0][4], 0b10000000)
        self.mcp.dac_reference_voltage = ReferenceVoltageValue.Voltage1_024V
        self.assertEqual(self.mcp.dev.write.call_args[0][0][4], 0b01000000)

    def test_write_dac_reference_source(self):
        self.mcp.write_dac_reference_source(ReferenceVoltageSource.Internal)
        self.assertEqual(self.mcp.dev.write.call_args[0][0][4], 0b00100000)
        self.mcp.dac_reference_source = ReferenceVoltageSource.Vdd
        self.assertEqual(self.mcp.dev.write.call_args[0][0][4], 0b00000000)

    def test_write_dac_powerup_value(self):
        self.do_test_write_func_byte(self.mcp.write_dac_powerup_value, 4, 0, 31, [0], [31])
        self.do_test_write_prop_byte("dac_powerup_value", 4, 0, 31, [0], [31])

    def test_write_interrupt_on_falling_edge(self):
        self.do_test_write_func_bit(self.mcp.write_interrupt_on_falling_edge, 5, 6)
        self.do_test_write_prop_bit("interrupt_on_falling_edge", 5, 6)
    
    def test_write_interrupt_on_rising_edge(self):
        self.do_test_write_func_bit(self.mcp.write_interrupt_on_rising_edge, 5, 5)
        self.do_test_write_prop_bit("interrupt_on_rising_edge", 5, 5)

    def test_write_adc_reference_voltage(self):
        self.mcp.write_adc_reference_voltage(ReferenceVoltageValue.Voltage2_048V)
        self.assertEqual(self.mcp.dev.write.call_args[0][0][5], 0b00010000)
        self.mcp.adc_reference_voltage = ReferenceVoltageValue.Voltage1_024V
        self.assertEqual(self.mcp.dev.write.call_args[0][0][5], 0b00001000)

    def test_write_adc_reference_source(self):
        self.mcp.write_adc_reference_source(ReferenceVoltageSource.Internal)
        self.assertEqual(self.mcp.dev.write.call_args[0][0][5], 0b00000100)
        self.mcp.adc_reference_source = ReferenceVoltageSource.Vdd
        self.assertEqual(self.mcp.dev.write.call_args[0][0][5], 0b00000000)

    def test_write_usb_vid(self):
        self.do_test_write_func_word(self.mcp.write_usb_vid, 6)
        self.do_test_write_prop_word("usb_vid", 6)

    def test_write_usb_pid(self):
        self.do_test_write_func_word(self.mcp.write_usb_pid, 8)
        self.do_test_write_prop_word("usb_pid", 8)

    def test_write_usb_self_powered_attribute(self):
        self.do_test_write_func_bit(self.mcp.write_usb_self_powered_attribute, 10, 6)
        self.do_test_write_prop_bit("usb_self_powered_attribute", 10, 6)

    def test_write_usb_remote_wake_up_attribute(self):
        self.do_test_write_func_bit(self.mcp.write_usb_remote_wake_up_attribute, 10, 5)
        self.do_test_write_prop_bit("usb_remote_wake_up_attribute", 10, 5)

    def test_write_usb_current(self):
        self.mcp.write_usb_current(2*0xff)
        self.assertEqual(self.mcp.dev.write.call_args[0][0][11], 0xff)
        self.mcp.usb_current = 2*0x11
        self.assertEqual(self.mcp.dev.write.call_args[0][0][11], 0x11)


class TestReadFlashUSBDescriptors(MCPTestCase):
    def setUp(self):
        super().setUp()
        self.descr = "".join([chr(x) for x in range(64,94)])
        xb0_0x = bytearray(64)
        xb0_0x[0] = 0xb0
        xb0_0x[2] = 62 # 2 + 2*30 characters (2 extra characters for endianness, by utf-16 standard)
        xb0_0x[3] = 3 # per datasheet, this byte must be 0x03
        xb0_0x[4:64] = self.descr.encode("utf-16")
        self.mcp.dev.read.return_value = xb0_0x
        self.mcp.set_default_memory_target(MemoryType.Flash)

    def test_read_usb_manufacturer_descriptor(self):
        v = self.mcp.read_usb_manufacturer_descriptor()
        self.assertEqual(v, self.descr)
        v = self.mcp.usb_manufacturer_descriptor
        self.assertEqual(v, self.descr)

    def test_read_usb_product_descriptor(self):
        v = self.mcp.read_usb_product_descriptor()
        self.assertEqual(v, self.descr)
        v = self.mcp.usb_product_descriptor
        self.assertEqual(v, self.descr)

    def test_read_usb_serial_number_descriptor(self):
        v = self.mcp.read_usb_serial_number_descriptor()
        self.assertEqual(v, self.descr)
        v = self.mcp.usb_serial_number_descriptor
        self.assertEqual(v, self.descr)

    def test_read_usb_serial_number_descriptor(self):
        sn = "".join([chr(x) for x in range(64,124)])
        self.mcp.dev.read.return_value[2] = 60
        self.mcp.dev.read.return_value[4:64] = sn.encode("utf-8")
        v = self.mcp.read_chip_factory_serial_number()
        self.assertEqual(v, sn)
        v = self.mcp.chip_factory_serial_number
        self.assertEqual(v, sn)


class TestWriteFlashUSBDescriptors(MCPTestCase):
    def setUp(self):
        super().setUp()
        self.descr = "".join([chr(x) for x in range(64,94)])
        xb0 = bytearray(64)
        xb0[0:3] = [0xb0]
        self.mcp._read_response = Mock()
        self.mcp._read_response.return_value = xb0

    def test_write_usb_manufacturer_descriptor(self):
        self.mcp.write_usb_manufacturer_descriptor(self.descr)
        self.assertEqual(int(self.mcp.dev.write.call_args[0][0][2]), 2*len(self.descr)+2)
        self.assertEqual(self.mcp.dev.write.call_args[0][0][4:].decode("utf-16"), self.descr)
        self.mcp.usb_manufacturer_descriptor = self.descr
        self.assertEqual(int(self.mcp.dev.write.call_args[0][0][2]), 2*len(self.descr)+2)
        self.assertEqual(self.mcp.dev.write.call_args[0][0][4:].decode("utf-16"), self.descr)
        
    def test_write_usb_product_descriptor(self):
        self.mcp.write_usb_product_descriptor(self.descr)
        self.assertEqual(int(self.mcp.dev.write.call_args[0][0][2]), 2*len(self.descr)+2)
        self.assertEqual(self.mcp.dev.write.call_args[0][0][4:].decode("utf-16"), self.descr)
        self.mcp.usb_product_descriptor = self.descr
        self.assertEqual(int(self.mcp.dev.write.call_args[0][0][2]), 2*len(self.descr)+2)
        self.assertEqual(self.mcp.dev.write.call_args[0][0][4:].decode("utf-16"), self.descr)

    def test_write_usb_serial_number_descriptor(self):
        self.mcp.write_usb_serial_number_descriptor(self.descr)
        self.assertEqual(int(self.mcp.dev.write.call_args[0][0][2]), 2*len(self.descr)+2)
        self.assertEqual(self.mcp.dev.write.call_args[0][0][4:].decode("utf-16"), self.descr)
        self.mcp.usb_serial_number_descriptor = self.descr
        self.assertEqual(int(self.mcp.dev.write.call_args[0][0][2]), 2*len(self.descr)+2)
        self.assertEqual(self.mcp.dev.write.call_args[0][0][4:].decode("utf-16"), self.descr)

    def test_write_chip_factory_serial_number(self):
        sn = "".join([chr(x) for x in range(64,124)])
        self.mcp.write_chip_factory_serial_number(sn)
        self.assertEqual(int(self.mcp.dev.write.call_args[0][0][2]), len(sn))
        self.assertEqual(self.mcp.dev.write.call_args[0][0][4:].decode("utf-8"), sn)
        self.mcp.chip_factory_serial_number = sn
        self.assertEqual(int(self.mcp.dev.write.call_args[0][0][2]), len(sn))
        self.assertEqual(self.mcp.dev.write.call_args[0][0][4:].decode("utf-8"), sn)


class TestReadFlashGPSettings(MCPTestWithReadMock):
    def setUp(self):
        super().setUp()
        self.xb0_01 = bytearray(64)
        self.xb0_01[:3] = [0xb0, 0, 4]
        self.mcp._read_response.return_value = self.xb0_01
        self.mcp.set_default_memory_target(MemoryType.Flash)

    def test_read_gpio_powerup_value(self):
        for pin in range(4):
            self.do_test_read_func_bit(self.mcp.gpio_read_powerup_value, 4+pin, 4, pin)
            self.do_test_read_prop_bit("gpio{:d}_powerup_value".format(pin), 4+pin, 4)

    def test_read_gpio_powerup_direction(self):
        for pin in range(4):
            self.do_test_read_func_bit(self.mcp.gpio_read_powerup_direction, 4+pin, 3, pin)
            self.do_test_read_prop_bit("gpio{:d}_powerup_direction".format(pin), 4+pin, 3)

    def test_read_gpio_function(self):
        for pin in range(4):
            self.xb0_01[4+pin] = 0b00000010
            expected = getattr(mcp2221.enums, "GPIO{:d}Function".format(pin))(2)
            v = getattr(self.mcp, "gpio{:d}_read_function".format(pin))()
            self.assertEqual(v, expected)
            v = getattr(self.mcp, "gpio{:d}_function".format(pin))
            self.assertEqual(v, expected)


class TestWriteFlashGPSettings(MCPTestCase):
    def setUp(self):
        super().setUp()
        self.mcp._read_response = Mock()
        self.xb0_01 = bytearray(64)
        self.xb0_01[0:3] = [0xb0, 0, 4]
        self.mcp._read_response.return_value = self.xb0_01
        self.mcp.set_default_memory_target(MemoryType.Flash)

    def test_write_gpio_powerup_value(self):
        for pin in range(4):
            self.do_test_write_func_bit(self.mcp.gpio_write_powerup_value, 2+pin, 4, [pin, False], [pin, True])
            self.do_test_write_prop_bit("gpio{:d}_powerup_value".format(pin), 2+pin, 4)

    def test_write_gpio_powerup_direction(self):
        for pin in range(4):
            self.do_test_write_func_bit(self.mcp.gpio_write_powerup_direction, 2+pin, 3, [pin, False], [pin, True])
            self.do_test_write_prop_bit("gpio{:d}_powerup_direction".format(pin), 2+pin, 3)

    def test_write_gpio_function(self):
        for pin in range(4):
            value = getattr(mcp2221.enums, "GPIO{:d}Function".format(pin))(2)
            getattr(self.mcp, "gpio{:d}_write_function".format(pin))(value)
            self.assertEqual(self.mcp.dev.write.call_args[0][0][2+pin], 0b00000010)
            setattr(self.mcp, "gpio{:d}_function".format(pin), value)
            self.assertEqual(self.mcp.dev.write.call_args[0][0][2+pin], 0b00000010)










