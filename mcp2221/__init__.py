"""A driver for the Microchip MCP2221/MCP2221A USB 2.0 to I2C/UART
protocol converters, together with helper functions and classes.

   Classes:
       MCP2221
   
   Functions:
       find_devices
   
   Submodules:
       enums
       exceptions
"""

__all__ = ['MCP2221', 'find_devices']

import os
import hid
import warnings

from .enums import *
from .exceptions import *

def find_devices(vendor_id:int = 1240, product_id:int = 221) -> list:
    """Finds HID devices with given vendor and product IDs,
    and returns a list of found descriptors.

    Parameters:
        vendor_id(int): the vendor ID to search for (default 1240)
        product_id(int): the product ID to search for (default 221)

    """
    return [dev for dev in hid.enumerate()
            if dev["vendor_id"]==vendor_id
            and dev["product_id"]==product_id]


class MCP2221():
    """A driver for the Microchip MCP2221/MCP2221A
    USB 2.0 to I2C/UART protocol converters
    
    Attributes:
        i2c_speed(int): I2C transfer speed in Hz
        default_memory_target(MemoryType): default memory target
        cdc_sn_enumeration_enable_flag(bool): CDC serial number enumeration enable flag
        led_idle_uart_rx_level(bool): UART RX LED idle signal level
        led_idle_uart_tx_level(bool): UART TX LED idle signal level
        led_idle_i2c_level(bool): I2C LED idle signal level
        suspend_mode_logic_level(bool): suspend mode signal level
        usb_configured_logic_level(bool): level of 'USB configured' signal
        security_option(SecurityOption): chip security option
        clock_output_frequency(ClockFrequency): clock output frequency
        clock_output_duty_cycle(ClockDutyCycle): clock output duty cycle
        usb_vid(int): USB vendor ID
        usb_pid(int): USB product ID
        usb_self_powered_attribute(bool): USB self-powered attribute
        usb_remote_wake_up_attribute(bool): USB remote wake-up attribute
        usb_current(int): USB current in enumeration phase, in mA
        usb_manufacturer_descriptor(str): USB manufacturer descriptor
        usb_product_descriptor(str): USB product descriptor
        usb_serial_number_descriptor(str): USB serial number descriptor
        chip_factory_serial_number(str): chip factory serial number
        password(str): flash access password (set only)
        interrupt_on_falling_edge(bool): interrupt on falling edge flag
        interrupt_on_rising_edge(bool): interrupt on rising edge flag
        interrupt_flag(bool): interrupt occurred flag
        gpio0_powerup_value(bool): GPIO pin 0 power-up value
        gpio1_powerup_value(bool): GPIO pin 1 power-up value
        gpio2_powerup_value(bool): GPIO pin 2 power-up value
        gpio3_powerup_value(bool): GPIO pin 3 power-up value
        gpio0_powerup_direction(GPIODirection): GPIO pin 0 power-up direction
        gpio1_powerup_direction(GPIODirection): GPIO pin 1 power-up direction
        gpio2_powerup_direction(GPIODirection): GPIO pin 2 power-up direction
        gpio3_powerup_direction(GPIODirection): GPIO pin 3 power-up direction
        gpio0_function(GPIO0Function): GPIO pin 0 function
        gpio1_function(GPIO1Function): GPIO pin 1 function
        gpio2_function(GPIO2Function): GPIO pin 2 function
        gpio3_function(GPIO3Function): GPIO pin 3 function
        gpio0_direction(GPIODirection): GPIO pin 0 direction
        gpio1_direction(GPIODirection): GPIO pin 1 direction
        gpio2_direction(GPIODirection): GPIO pin 2 direction
        gpio3_direction(GPIODirection): GPIO pin 3 direction
        gpio0_value(bool): GPIO pin 0 value
        gpio1_value(bool): GPIO pin 1 value
        gpio2_value(bool): GPIO pin 2 value
        gpio3_value(bool): GPIO pin 3 value
        adc_reference_voltage(ReferenceVoltageValue): ADC reference voltage settings
        adc_reference_source(ReferenceVoltageSource): ADC reference voltage source
        dac_reference_voltage(ReferenceVoltageValue): DAC reference voltage settings
        dac_reference_source(ReferenceVoltageSource): DAC reference voltage source
        dac_powerup_value(int): DAC power-up value
        adc0_value(int): ADC 0 value (read-only)
        adc1_value(int): ADC 1 value (read-only)
        adc2_value(int): ADC 2 value (read-only)
        dac_value(int): DAC value (write-only, 5 bit)
    
    Protected attributes:
        _opened(bool): True if associated device is opened, False otherwise
        _password(str): password string
        _mem_target(MemoryType): default memory target for data both in flash and SRAM

    """

    def __init__(self, dev_descriptor:dict=None, password:str = ""):
        """Class constructor.

        Parameters:
            dev_descriptor(dict): the device descriptor to open device from.
                                  Use find_devices to obtain one. (default None)
            password(str): 8 byte password to modify flash content (default "")

        Raises:
            IOException: if device was provided and device couldn't be opened.

        Note:
            If dev_descriptor is provided, device is opened automatically. If you
            don't want this to happen, provide no descriptor and use open() method
            at a later time.
        """
        self._opened = False
        self._password = password
        self._mem_target = MemoryType.SRAM
        if dev_descriptor != None:
            self.open(dev_descriptor)

    ################
    # HID commands #
    ################
    def open(self, dev_descriptor:dict) -> bool:
        """Opens device with given descriptor.

        Parameters:
            dev_descriptor(dict): the device descriptor to open device from.
                                  Use find_devices to obtain one.
        
        Returns:
            bool: True if device could be opened, False otherwise.
        
        Raises:
            IOException: if device couldn't be opened.
        """
        if self._opened == True: return False
        # create hidapi device instance
        self.dev = hid.device()
        try:
            self.dev.open_path(dev_descriptor["path"])
            self.dev.set_nonblocking(True)
            self._opened = True
        except (OSError, IOError):
            self._opened = False
            raise IOException("Can't open device. Check that the device descriptor exists and that you have access permissions.")
        # need to fix ADC state, which can return undefined values
        # in some configurations of pin functions
        pin_data = self._read_sram(SramDataSubcode.GPSettings)
        tmp_pin_data = [pin_data[0], 0x0, 0x0, 0x0]
        for n in [1,2,3]:
            # pin state must be treated differently when in input or output mode
            pin_function = pin_data[n] & 0x03
            if pin_function == 0 and pin_data[n] & 0x08: # GPIO input
                tmp_pin_data[n] |= 0x02 # set to ADC
            elif pin_function == 2: # ADC
                tmp_pin_data[n] |= 0x08 # set to GPIO input
            else:
                tmp_pin_data[n] = pin_data[n] # no change
        # apply temporary state, then original state
        self._write(0x60, 0, 0, 0, 0, 0, 0, 0x80, *tmp_pin_data)
        self._write(0x60, 0, 0, 0, 0, 0, 0, 0x80, *pin_data)
        return self._opened
    
    @property
    def opened(self) -> bool:
        """Tells if a device associated with this instance
        is currently opened.

        Returns:
            bool: True if a device is opened, False otherwise.
        """
        return self._opened
    
    def close(self):
        """Closes access to associated device.
        """
        if self._opened:
            self.dev.close()
            self._opened = False
    
    def _build_command(self, *args:bytes) -> bytearray:
        """Internal command. Builds a command string with given elements.

        Parameters:
            *args(bytes): a variable number of bytes to fill command string.

        Raises:
            InvalidParameterException: if more than 64 arguments are fed.

        Returns:
            bytearray: 64-byte command string.
        """
        if len(args)>64:
            InvalidParameterException("Too many command bytes.")
        cmd = bytearray(64)
        cmd[:len(args)] = args
        return cmd
    
    def _read_response(self, req_code:bytes) -> list:
        """Internal command. Reads response from device.

        Parameters:
            req_code(bytes): command code to request response for.

        Raises:
            FailedCommandException: if response is empty
            FailedCommandException: if reply code doesn't match
                                    with requested one
            FailedCommandException: if reply indicates failure
            IOException: if device is not opened

        Returns:
            list: device response as a list of bytes.
        """
        if self._opened:
            data = self.dev.read(64)
            if len(data) == 0:
                raise FailedCommandException("Empty response.")
            if data[0] != req_code:
                raise FailedCommandException("Command response code doesn't match.")
            if data[1] != 0x00:
                raise FailedCommandException("Command failed with code {:d}.".format(data[1]))
            return data
        else:
            raise IOException("Device not connected.")

    def _write(self, *args:bytes) -> list:
        """Internal command. Writes a command to device and requests response.
        
        Parameters:
            *args(bytes): a variable number of bytes to fill command string.
        
        Raises:
            IOException: if device is not opened

        Returns:
            list: device response as a list of bytes.
        """
        if self._opened:
            cmd = self._build_command(*args)
            if os.name == 'nt':
                # Windows HID requires additional prefix byte ReportID=0x00
                # https://stackoverflow.com/questions/22240591/confused-by-the-report-id-when-using-hidapi-through-usb
                # https://www.microchip.com/forums/m887066.aspx
                cmd.insert(0, 0x00)
            self.dev.write(cmd)
            self.dev.set_nonblocking(False)
            data = self._read_response(args[0])
            self.dev.set_nonblocking(True)
            return data
        else:
            raise IOException("Device not connected.")
        
    #############################
    # General support functions #
    #############################
    def __not(self, value:int) -> int:
        """Private command. An implementation of boolean 'not' on bytes.

        Parameters:
            value(int): the value to invert
        
        Returns:
            int: boolean 'not' of input value (~value).
        """
        v = [0 if b=='1' else 1 for b in reversed("{:08b}".format(value))]
        return sum([v[n] << n for n in range(8)])
    
    def __and(self, v1:int, v2:int) -> int:
        """Private command. An implementation of boolean 'and' on bytes.

        Parameters:
            v1(int): first operand
            v2(int): second operand
        
        Returns:
            int: boolean 'and' of inputs (v1 & v2).
        """
        return int.from_bytes([v1], "big") & int.from_bytes([v2], "big")
    
    def __or(self, v1:int, v2:int) -> int:
        """Private command. An implementation of boolean 'or' on bytes.

        Parameters:
            v1(int): first operand
            v2(int): second operand
        
        Returns:
            int: boolean 'or' of inputs (v1 | v2).
        """
        return int.from_bytes([v1], "big") | int.from_bytes([v2], "big")
    
    def __bits_to_byte(self, bits: 'list[bool]') -> int:
        """Private command. Converts a list of bits to a number (byte).

        Parameters:
            bits(list[bool]): list of bits values
        
        Returns:
            int: a value compiled from bit list.
        
        Note:
            Bit list is assumed to be little endian (LSB first).
        """
        return sum([bits[n]<<n for n in range(len(bits))])
    
    def __byte_to_bits(self, byte: int, length:int = 8) -> list:
        """Private command. Converts a byte to a list of bits of given length.

        Parameters:
            byte(int): value to convert
            length(int): number of bits of returned value (default 8)
        
        Returns:
            list[bool]: a list of booleans corresponding to byte bits.
        
        Note:
            Returned list is little endian (LSB first).
        """
        lst = list("{:08b}".format(byte))[::-1]
        return [True if lst[n]=='1' else False for n in range(length)]

    ######################################
    # Read/write flash and SRAM commands #
    ######################################
    def _read_flash(self, code: FlashDataSubcode) -> list:
        """Internal command. Reads data from flash memory.

        Parameters:
            code(FlashDataSubcode): flash register to read from

        Returns:
            list: flash register content in the form of a list of bytes
        """
        data = self._write(0xb0, code)
        len = data[2]
        return data[4:(4+len)]
    
    def _read_sram(self, code: SramDataSubcode) -> list:
        """Internal command. Reads data from SRAM.

        Parameters:
            code(SramDataSubcode): memory register to read from
        
        Returns:
            list: memory register content in the form of a list of bytes
        """
        data = self._write(0x61)
        if code == SramDataSubcode.ChipSettings:
            p0 = 4
            len = data[2]
        elif code == SramDataSubcode.GPSettings:
            p0 = data[2] + 4
            len = data[3]
        return data[p0:(p0+len)]
    
    def _write_sram(self, code:SramDataSubcode, byte:int, value:int) -> None:
        """Internal command. Writes one byte to a SRAM register.

        Parameters:
            code(SramDataSubcode): memory register to write to
            byte(int): index of byte to write
            value(int): value to write
        """
        gp_sram_set = self._read_sram(SramDataSubcode.GPSettings)
        # reads GPIO directions/values with command 0x51 and rearranges
        gp_set = self._write(0x51)[2:10]
        # read SRAM for alternate pin functions
        gp_sram_set = self._read_sram(SramDataSubcode.GPSettings)
        cmd = bytearray(64)
        cmd[0] = 0x60
        # set GPIO directions/values if these are relevant
        for n in range(4):
            if gp_set[2*n] <= 1:
                cmd[8+n] = (gp_set[2*n] << 4) + (gp_set[2*n+1] << 3)
            else:
                cmd[8+n] = gp_sram_set[n]
        
        if code == SramDataSubcode.ChipSettings:
            idx = 2 + byte
        elif code == SramDataSubcode.GPSettings:
            idx = 8 + byte
            cmd[7] = 0x80
        
        cmd[idx] = value
        self._write(*cmd)

    def __check_mem_access_parameters(self, byte:int, bits:'list[int]'):
        """Private command. Checks that given parameters are within bounds
        for memory access.

        Parameters:
            byte(int): index of targeted register byte
            bits(list[int]): a list of bits indices within targeted byte (0 to 7)
        
        Raises:
            InvalidParameterException: if byte index is below 0 or above 8
            InvalidParameterException: if one bit index is below 0 or above 7
        """
        if byte not in range(9):
            InvalidParameterException("Invalid byte index.")
        for bit in bits:
            if bit not in range(8):
                InvalidParameterException("Invalid bit index.")
        
    def _read_flash_byte(self, code:FlashDataSubcode, byte:int, bits:'list[int]') -> list:
        """Internal command. Reads some bits from a register byte in flash memory.

        Parameters:
            code(FlashDataSubcode): flash register to read from
            byte(int): index of byte to read from
            bits(list[int]): a list of bits indices to read
        
        Returns:
            list: the values of the requested bits in the form of a list.
        """
        self.__check_mem_access_parameters(byte, bits)
        ret = self._read_flash(code)
        return [bool((ret[byte]>>bit) & 0x01) for bit in bits]
    
    def _write_flash_byte(self, code:FlashDataSubcode, byte:int, bits:'list[int]', values:'list[bool]') -> None:
        """Internal command. Writes some bits to a register byte in flash memory.

        Parameters:
            code(FlashDataSubcode): flash register to write to
            byte(int): index of byte to write to
            bits(list[int]): a list of bits indices to write to
            values(list[bool]): a list of values to write
        """
        self.__check_mem_access_parameters(byte, bits)
        cmd = self._read_flash(code)
        for bit,value in zip(bits, values):
            cmd[byte] = self.__and(cmd[byte], self.__not(1<<bit))
            cmd[byte] = self.__or(cmd[byte], 1<<bit if value else 0)
        if code == FlashDataSubcode.ChipSettings:
            cmd += self._password.encode("utf-8")
        self._write(0xb1, code, *cmd)
    
    def _read_sram_byte(self, code:SramDataSubcode, byte:int, bits:'list[int]') -> list:
        """Internal command. Reads some bits from a register byte in SRAM.

        Parameters:
            code(FlashDataSubcode): memory register to read from
            byte(int): index of byte to read from
            bits(list[int]): a list of bits indices to read
        
        Returns:
            list: the values of the requested bits in the form of a list.
        """
        self.__check_mem_access_parameters(byte, bits)
        ret = self._read_sram(code)
        return [bool((ret[byte]>>bit) & 0x01) for bit in bits]
    
    def __get_mem_read_function(self, mem:MemoryType):
        """Private command. Gets appropriate memory access function.

        Parameters:
            mem(MemoryType): enum code for memory type (flash or SRAM)
        
        Returns:
            method: the appropriate function to read from requested memory.
        """
        if mem == None: mem = self._mem_target
        if mem == MemoryType.SRAM:
            return self._read_sram_byte
        elif mem == MemoryType.Flash:
            return self._read_flash_byte

    def get_default_memory_target(self) -> MemoryType:
        """Gets default memory target.

        Returns:
            MemoryType: enum code for memory type.
        """
        return self._mem_target

    def set_default_memory_target(self, mem:MemoryType) -> None:
        """Sets default memory target.

        Parameters:
            mem(MemoryType): enum code for memory type
        """
        self._mem_target = mem
    
    default_memory_target = property(get_default_memory_target, set_default_memory_target)

    #################
    # Chip settings #
    #################
    def read_cdc_sn_enumeration_enable(self) -> bool:
        """Reads CDC serial number enumeration enable bit from flash memory.

        Returns:
            bool: value of CDC serial number enumeration enable bit.
        """
        return self._read_flash_byte(FlashDataSubcode.ChipSettings, 0, [7])[0]
    
    def write_cdc_sn_enumeration_enable(self, value:bool) -> None:
        """Writes CDC serial number enumeration enable bit to flash memory.

        Parameters:
            value(bool): value to set
        """
        self._write_flash_byte(FlashDataSubcode.ChipSettings, 0, [7], [value])
    
    cdc_sn_enumeration_enable_flag = property(read_cdc_sn_enumeration_enable,
                                              write_cdc_sn_enumeration_enable)
    
    def read_led_idle_uart_rx_level(self) -> bool:
        """Reads idle level for UART RX LED signal. This is the value given
        to the UART RX LED signal when no RX transfer is ongoing.

        Returns:
            bool: value of UART RX LED idle signal level.
        """
        return self._read_flash_byte(FlashDataSubcode.ChipSettings, 0, [6])[0]

    def write_led_idle_uart_rx_level(self, value:bool) -> None:
        """Writes idle level for UART RX LED signal. This is the value given
        to the UART RX LED signal when no RX transfer is ongoing.

        Parameters:
            value(bool): value of UART RX LED idle signal level
        """
        self._write_flash_byte(FlashDataSubcode.ChipSettings, 0, [6], [value])
    
    led_idle_uart_rx_level = property(read_led_idle_uart_rx_level, write_led_idle_uart_rx_level)

    def read_led_idle_uart_tx_level(self) -> bool:
        """Reads idle level for UART TX LED signal. This is the value given
        to the UART TX LED signal when no TX transfer is ongoing.

        Returns:
            bool: value of UART TX LED idle signal level.
        """
        return self._read_flash_byte(FlashDataSubcode.ChipSettings, 0, [5])[0]

    def write_led_idle_uart_tx_level(self, value:bool) -> None:
        """Writes idle level for UART TX LED signal. This is the value given
        to the UART TX LED signal when no TX transfer is ongoing.

        Parameters:
            value(bool): value of UART TX LED idle signal level
        """
        self._write_flash_byte(FlashDataSubcode.ChipSettings, 0, [5], [value])

    led_idle_uart_tx_level = property(read_led_idle_uart_tx_level, write_led_idle_uart_tx_level)

    def read_led_idle_i2c_level(self) -> bool:
        """Reads idle level for I2C LED signal. This is the value given
        to the I2C LED signal when no I2C transfer is ongoing.

        Returns:
            bool: value of I2C LED idle signal level.
        """
        return self._read_flash_byte(FlashDataSubcode.ChipSettings, 0, [4])[0]

    def write_led_idle_i2c_level(self, value:bool) -> None:
        """Writes idle level for I2C LED signal. This is the value given
        to the I2C LED signal when no I2C transfer is ongoing.

        Parameters:
            value(bool): value of I2C LED idle signal level
        """
        self._write_flash_byte(FlashDataSubcode.ChipSettings, 0, [4], [value])

    led_idle_i2c_level = property(read_led_idle_i2c_level, write_led_idle_i2c_level)

    def read_suspend_mode_logic_level(self) -> bool:
        """Reads pin level for suspend mode signal. This is the value given
        to the suspend mode signal when chip is NOT in suspend mode.

        Returns:
            bool: value of suspend mode signal level.
        """
        return self._read_flash_byte(FlashDataSubcode.ChipSettings, 0, [3])[0]

    def write_suspend_mode_logic_level(self, value:bool) -> None:
        """Writes pin level for suspend mode signal. This is the value given
           to the suspend mode signal when chip is NOT in suspend mode.

        Parameters:
            value(bool): value of suspend mode signal level
        """
        self._write_flash_byte(FlashDataSubcode.ChipSettings, 0, [3], [value])
    
    suspend_mode_logic_level = property(read_suspend_mode_logic_level, write_suspend_mode_logic_level)

    def read_usb_configured_logic_level(self) -> bool:
        """Reads level for 'USB configured' signal. This is the value given
        when USB enumeration is complete.

        Returns:
            bool: level of 'USB configured' signal.
        """
        return self._read_flash_byte(FlashDataSubcode.ChipSettings, 0, [2])[0]

    def write_usb_configured_logic_level(self, value:bool) -> None:
        """Writes level for 'USB configured' signal. This is the value given
        when USB enumeration is complete.

        Parameters:
            value(bool): level of 'USB configured' signal
        """
        self._write_flash_byte(FlashDataSubcode.ChipSettings, 0, [2], [value])
    
    usb_configured_logic_level = property(read_usb_configured_logic_level, write_usb_configured_logic_level)

    def read_security_option(self) -> SecurityOption:
        """Reads chip security option.

        Returns:
            SecurityOption: enum code for security option.
        """
        ret = self._read_flash_byte(FlashDataSubcode.ChipSettings, 0, [0, 1])
        return SecurityOption(self.__bits_to_byte(ret))

    def write_security_option(self, value:SecurityOption) -> None:
        """Writes chip security option.
        !!!WARNING!!! If you choose SecurityOption.PermanentlyLocked,
        it will make your chip permanently read-only.

        Parameters:
            value(SecurityOption): enum code for security option
        """
        self._write_flash_byte(FlashDataSubcode.ChipSettings, 0, [0, 1], self.__byte_to_bits(value, 2))
    
    security_option = property(read_security_option, write_security_option)

    def read_clock_output_frequency(self, mem:MemoryType = None) -> ClockFrequency:
        """Reads clock output frequency. This is the frequency of clock output
        signal if directed to GPIO pin 1.

        Parameters:
            mem(MemoryType): memory to read from (default SRAM)

        Returns:
            ClockFrequency: enum code for clock output frequency.
        """
        fct = self.__get_mem_read_function(mem)
        ret = fct(FlashDataSubcode.ChipSettings, 1, [0, 1, 2])
        return ClockFrequency(self.__bits_to_byte(ret))

    def write_clock_output_frequency(self, value:ClockFrequency, mem:MemoryType = None) -> None:
        """Writes clock output frequency. This is the frequency of clock output
        signal if directed to GPIO pin 1. It doesn't change internal clock frequency.

        Parameters:
            value(ClockFrequency): enum code for clock output frequency
            mem(MemoryType): memory to write to (default SRAM)
        """
        if mem == None: mem = self._mem_target
        if mem == MemoryType.SRAM:
            init = self.__and(self._read_sram(SramDataSubcode.ChipSettings)[1], 0b00011000)
            self._write_sram(SramDataSubcode.ChipSettings, 0, value + 0x80 + init)
        elif mem == MemoryType.Flash:
            self._write_flash_byte(FlashDataSubcode.ChipSettings, 1, [0, 1, 2], self.__byte_to_bits(value, 3))

    clock_output_frequency = property(read_clock_output_frequency, write_clock_output_frequency)

    def read_clock_output_duty_cycle(self, mem:MemoryType = None) -> ClockDutyCycle:
        """Reads clock output duty cycle. This is the duty cycle of clock output
        signal if directed to GPIO pin 1.

        Parameters:
            mem(MemoryType): memory to read from (default SRAM)

        Returns:
            ClockDutyCycle: enum code for clock duty cycle.
        """
        fct = self.__get_mem_read_function(mem)
        ret = fct(FlashDataSubcode.ChipSettings, 1, [3, 4])
        return ClockDutyCycle(self.__bits_to_byte(ret))

    def write_clock_output_duty_cycle(self, value:ClockDutyCycle, mem:MemoryType = None) -> None:
        """Writes clock output duty cycle. This is the duty cycle of clock output
        signal if directed to GPIO pin 1.

        Parameters:
            value(ClockDutyCycle): enum code for clock duty cycle
            mem(MemoryType): memory to write to (default SRAM)
        """
        if mem == None: mem = self._mem_target
        if mem == MemoryType.SRAM:
            init = self.__and(self._read_sram(SramDataSubcode.ChipSettings)[1], 0b00000111)
            self._write_sram(SramDataSubcode.ChipSettings, 0, (value<<3) + 0x80 + init)
        elif mem == MemoryType.Flash:
            self._write_flash_byte(FlashDataSubcode.ChipSettings, 1, [3, 4], self.__byte_to_bits(value, 2))
    
    clock_output_duty_cycle = property(read_clock_output_duty_cycle, write_clock_output_duty_cycle)

    def read_usb_vid(self) -> int:
        """Reads USB vendor ID from flash memory.

        Returns:
            int: USB vendor ID.
        """
        ret = self._read_flash(FlashDataSubcode.ChipSettings)
        return ret[4] | (ret[5] << 8)
    
    def write_usb_vid(self, value:int) -> None:
        """Writes USB vendor ID to flash memory.

        Parameters:
            value(int): USB vendor ID
        """
        ret = self._read_flash(FlashDataSubcode.ChipSettings)
        ret[4] = value & 0xff
        ret[5] = value >> 8
        self._write(0xb1, FlashDataSubcode.ChipSettings, *ret)
    
    usb_vid = property(read_usb_vid, write_usb_vid)

    def read_usb_pid(self) -> int:
        """Reads USB product ID from flash memory.

        Returns:
            int: USB product ID.
        """
        ret = self._read_flash(FlashDataSubcode.ChipSettings)
        return ret[6] | (ret[7] << 8)
    
    def write_usb_pid(self, value:int) -> None:
        """Writes USB product ID to flash memory.

        Parameters:
            value(int): USB product ID
        """
        ret = self._read_flash(FlashDataSubcode.ChipSettings)
        ret[6] = value & 0xff
        ret[7] = value >> 8
        self._write(0xb1, FlashDataSubcode.ChipSettings, *ret)
    
    usb_pid = property(read_usb_pid, write_usb_pid)

    def read_usb_self_powered_attribute(self) -> bool:
        """Reads 'USB self-powered' attribute.

        Returns:
            bool: value of 'USB self-powered' attribute.
        """
        return self._read_flash_byte(FlashDataSubcode.ChipSettings, 8, [6])[0]
    
    def write_usb_self_powered_attribute(self, value:bool) -> None:
        """Writes 'USB self-powered' attribute.

        Parameters:
            value(bool): value of 'USB self-powered' attribute
        """
        self._write_flash_byte(FlashDataSubcode.ChipSettings, 8, [6], [value])
    
    usb_self_powered_attribute = property(read_usb_self_powered_attribute, write_usb_self_powered_attribute)

    def read_usb_remote_wake_up_attribute(self) -> bool:
        """Reads 'USB remote wake-up' attribute.

        Returns:
            bool: value of 'USB remote wake-up' attribute.
        """
        return self._read_flash_byte(FlashDataSubcode.ChipSettings, 8, [5])[0]
    
    def write_usb_remote_wake_up_attribute(self, value:bool) -> None:
        """Writes 'USB remote wake-up' attribute.

        Parameters:
            value(bool): value of 'USB remote wake-up' attribute
        """
        self._write_flash_byte(FlashDataSubcode.ChipSettings, 8, [5], [value])
    
    usb_remote_wake_up_attribute = property(read_usb_remote_wake_up_attribute, write_usb_remote_wake_up_attribute)

    def read_usb_current(self) -> int:
        """Reads USB current value for enumeration phase, in mA.

        Returns:
            int: value of USB current in enumeration phase, in mA.
        """
        return self._read_flash(FlashDataSubcode.ChipSettings)[9]*2
    
    def write_usb_current(self, value:int) -> None:
        """Writes USB current value for enumeration phase, in mA.

        Parameters:
            value(int): value of USB current in enumeration phase, in mA
        """
        ret = self._read_flash(FlashDataSubcode.ChipSettings)
        ret[9] = int(value/2)
        self._write(0xb1, FlashDataSubcode.ChipSettings, *ret)
    
    usb_current = property(read_usb_current, write_usb_current)

    ###################
    # USB descriptors #
    ###################
    def _write_usb_descriptor(self, code: FlashDataSubcode, value:str) -> None:
        """Internal command. Writes USB descriptor to flash memory.

        Parameters:
            code(FlashDataSubcode): enum code for USB descriptor register
            value(str): descriptor value
        
        Raises:
            InvalidParameterException: if code is not for a USB descriptor
            InvalidParameterException: if descriptor length exceeds 30 characters

        """
        if code not in [FlashDataSubcode.USBManufacturerDescriptorString,
                        FlashDataSubcode.USBProductDescriptorString,
                        FlashDataSubcode.USBSerialNumberDescriptorString]:
                            raise InvalidParameterException("Invalid descriptor code.")
        if len(value)>30:
            raise InvalidParameterException("Descriptor too long.")
        bval = value.encode("utf-16")
        self._write(0xb1, code, len(bval), 0x03, *bval)

    def read_usb_manufacturer_descriptor(self) -> str:
        """Reads USB manufacturer descriptor from flash memory.

        Returns:
            str: USB manufacturer descriptor string.
        """
        data = self._read_flash(FlashDataSubcode.USBManufacturerDescriptorString)
        if (len(data)<60):
            return bytes(data[:-2]).decode('utf-16')
        else:
            return bytes(data).decode('utf-16')
    
    def write_usb_manufacturer_descriptor(self, value:str) -> None:
        """Writes USB manufacturer descriptor to flash memory.

        Parameters:
            value(str): USB manufacturer descriptor string
        """
        self._write_usb_descriptor(FlashDataSubcode.USBManufacturerDescriptorString, value)

    usb_manufacturer_descriptor = property(read_usb_manufacturer_descriptor, write_usb_manufacturer_descriptor)

    def read_usb_product_descriptor(self) -> str:
        """Reads USB product descriptor from flash memory.

        Returns:
            str: USB product descriptor string.
        """
        data = self._read_flash(FlashDataSubcode.USBProductDescriptorString)
        if (len(data)<60):
            return bytes(data[:-2]).decode('utf-16')
        else:
            return bytes(data).decode('utf-16')

    def write_usb_product_descriptor(self, value:str) -> None:
        """Writes USB product descriptor to flash memory.

        Parameters:
            value(str): USB product descriptor string
        """
        self._write_usb_descriptor(FlashDataSubcode.USBProductDescriptorString, value)
    
    usb_product_descriptor = property(read_usb_product_descriptor, write_usb_product_descriptor)

    def read_usb_serial_number_descriptor(self) -> str:
        """Reads USB serial number descriptor from flash memory.

        Returns:
            str: USB serial number descriptor string.
        """
        data = self._read_flash(FlashDataSubcode.USBSerialNumberDescriptorString)
        if (len(data)<60):
            return bytes(data[:-2]).decode('utf-16')
        else:
            return bytes(data).decode('utf-16')

    def write_usb_serial_number_descriptor(self, value:str) -> None:
        """Writes USB serial number descriptor to flash memory.

        Parameters:
            value(str): USB serial number descriptor string
        """
        self._write_usb_descriptor(FlashDataSubcode.USBSerialNumberDescriptorString, value)
    
    usb_serial_number_descriptor = property(read_usb_serial_number_descriptor, write_usb_serial_number_descriptor)

    def read_chip_factory_serial_number(self) -> str:
        """Reads chip factory serial number from flash memory.

        Returns:
            str: USB chip factory serial number.
        """
        data = self._read_flash(FlashDataSubcode.ChipFactorySerialNumber)
        return bytes(data).decode("utf-8")
    
    def write_chip_factory_serial_number(self, value:str) -> None:
        """Writes chip factory serial number to flash memory.

        Parameters:
            value(str): chip factory serial number
        """
        if len(value)>60:
            raise InvalidParameterException("Serial number too long.")
        self._write(0xb1, FlashDataSubcode.ChipFactorySerialNumber, len(value), 0x03, *value.encode("utf-8"))

    chip_factory_serial_number = property(read_chip_factory_serial_number, write_chip_factory_serial_number)

    #########################
    # Flash access password #
    #########################
    def __check_password_validity(self, value:str):
        """Private command. Checks password string validity.

        Parameters:
            value(str): password string
        
        Raises:
            InvalidParameterException: if password is longer than 8 characters
        """
        if len(value)>8:
            raise InvalidParameterException("Password string too long.")

    def write_flash_access_password(self, value:str) -> None:
        """Writes flash memory access password. To activate password protection,
        set security option to SecurityOption.PasswordProtected.

        Parameters:
            value(str): password string (max. 8 characters)
        """
        self.__check_password_validity(value)
        self._password = value
        data = self._read_flash(FlashDataSubcode.ChipSettings) + bytearray(value.encode("utf-8"))
        self._write(0xb1, FlashDataSubcode.ChipSettings, *data)
    
    def unlock(self, value:str) -> None:
        """Tries to unlock flash memory with given password.

        Parameters:
            value(str): password string (max. 8 characters)
        """
        # tries to unlock with given password
        self._write(0xb2, 0x00, *value.encode("utf-8"))
        self._password = value
    
    password = property(None, unlock)

    #############
    # Interrupt #
    #############
    def read_interrupt_on_falling_edge(self, mem:MemoryType = None) -> bool:
        """Reads interrupt on falling edge flag. This tells the state of interrupt
        detection on falling edge.

        Parameters:
            mem(MemoryType): enum code for memory type (flash or SRAM)
        
        Returns:
            bool: value of interrupt on falling edge flag (True = active).
        """
        fct = self.__get_mem_read_function(mem)
        return fct(FlashDataSubcode.ChipSettings, 3, [6])[0]
    
    def write_interrupt_on_falling_edge(self, value:bool, mem:MemoryType = None) -> None:
        """Writes interrupt on falling edge flag. This sets the state of interrupt
        detection on falling edge.

        Parameters:
            value(bool): value of interrupt on falling edge flag (True = active)
            mem(MemoryType): enum code for memory type (flash or SRAM)
        """
        if mem == None: mem = self._mem_target
        if mem == MemoryType.SRAM:
            self._write_sram(SramDataSubcode.ChipSettings, 4, 0b10011000 if value else 0b10010000)
        elif mem == MemoryType.Flash:
            self._write_flash_byte(FlashDataSubcode.ChipSettings, 3, [6], [value])
    
    interrupt_on_falling_edge = property(read_interrupt_on_falling_edge, write_interrupt_on_falling_edge)

    def read_interrupt_on_rising_edge(self, mem:MemoryType = None) -> bool:
        """Reads interrupt on rising edge flag. This tells the state of interrupt
        detection on rising edge.

        Parameters:
            mem(MemoryType): enum code for memory type (flash or SRAM)
        
        Returns:
            bool: value of interrupt on rising edge flag (True = active).
        """
        fct = self.__get_mem_read_function(mem)
        return fct(FlashDataSubcode.ChipSettings, 3, [5])[0]
    
    def write_interrupt_on_rising_edge(self, value:bool, mem:MemoryType = None) -> None:
        """Writes interrupt on rising edge flag. This sets the state of interrupt
        detection on rising edge.

        Parameters:
            value(bool): value of interrupt on rising edge flag (True = active)
            mem(MemoryType): enum code for memory type (flash or SRAM)
        """
        if mem == None: mem = self._mem_target
        if mem == MemoryType.SRAM:
            self._write_sram(SramDataSubcode.ChipSettings, 4, 0b10000110 if value else 0b10000100)
        elif mem == MemoryType.Flash:
            self._write_flash_byte(FlashDataSubcode.ChipSettings, 3, [5], [value])
    
    interrupt_on_rising_edge = property(read_interrupt_on_rising_edge, write_interrupt_on_rising_edge)

    def read_interrupt_flag(self) -> bool:
        """Reads flag telling whether an interrupt occurred.

        Returns:
            bool: if True, an interrupt has occurred.
        """
        return bool(self._write(0x10)[24])
    
    interrupt_flag = property(read_interrupt_flag)
    
    def clear_interrupt_flag(self) -> None:
        """Clears the interrupt flag.
        """
        self._write_sram(SramDataSubcode.ChipSettings, 4, 0b10000001)

    #######################################
    # I2C configuration and data transfer #
    #######################################
    def i2c_cancel_transfer(self) -> I2CCancelTransferResponse:
        """Cancel pending I2C transfer.

        Returns:
            I2CCancelTransferResponse: response code returned by device.
        """
        data = self._write(0x10, 0x00, 0x10)
        return I2CCancelTransferResponse(data[2])
    
    def i2c_read_speed(self) -> int:
        """Read configured I2C speed.

        Returns:
            int: current I2C speed in Hz.
        """
        return 12000000//(self._write(0x10)[14]+3)

    def i2c_write_speed(self, speed: int) -> I2CSetSpeedResponse:
        """Write I2C speed to flash memory.

        Parameters:
            speed (int): I2C speed in Hz
        
        Returns:
            I2CSetSpeedResponse: response code returned by device.
        
        Raises:
            InvalidParameterException: if speed is out of range.
        """
        if speed<46333:
            raise InvalidParameterException("Speed too low (<46.33kHz)")
        elif speed>4000000:
            raise InvalidParameterException("Speed too high (>4MHz)")
        data = self._write(0x10, 0x00, 0x00, 0x20, 12000000 // speed - 3)
        return I2CSetSpeedResponse(data[3])
    
    i2c_speed = property(i2c_read_speed, i2c_write_speed)

    @property
    def i2c_requested_transfer_length(self) -> int:
        """Reads the number of bytes requested in the current I2C command.

        Returns:
            int: requested I2C transfer length.
        """
        data = self._write(0x10)[9:11]
        return data[0] + (data[1] << 8)
    
    @property
    def i2c_already_transferred_length(self) -> int:
        """Reads the number of bytes that have already been transferred
        in the current I2C command.

        Returns:
            int: amount of already transferred I2C bytes.
        """
        data = self._write(0x10)[11:13]
        return data[0] + (data[1] << 8)
    
    @property
    def i2c_internal_buffer_counter(self) -> int:
        """Reads the value of the I2C internal buffer counter.

        Returns:
            int: value of internal I2C buffer counter.
        """
        return self._write(0x10)[13]
    
    @property
    def i2c_slave_address(self) -> int:
        """Reads the I2C slave address being used.

        Returns:
            int: I2C slave address being used.
        """
        data = self._write(0x10)[16:18]
        return data[0] + (data[1] << 8)
    
    @property
    def i2c_scl_state(self) -> bool:
        """Reads the I2C clock (SCL) line state.

        Returns:
            bool: I2C clock line state.
        """
        return bool(self._write(0x10)[22])

    @property
    def i2c_sda_state(self) -> bool:
        """Reads the I2C data (SDA) line state.

        Returns:
            bool: I2C data line state.
        """
        return bool(self._write(0x10)[23])
    
    def i2c_has_pending_value(self) -> int:
        """Tells if I2C bus has pending data to be read.

        Returns:
            int: 0 for no, 1 for yes and 2 for irrelevant?.
        """
        return self._write(0x10)[25]

    def _check_i2c_parameters(self, address:int, length:int):
        """Internal command. Checks if given I2C parameters are valid.

        Parameters:
            address(int): 7-bit I2C slave address
            length(int): data string length (max. 65535 characters)
        
        Raises:
            InvalidParameterException: if address is larger than 7 bits
            InvalidParameterException: if string length exceeds 65535
        """
        if address > 0x7f:
            raise InvalidParameterException("Address too long.")
        if length > 0xffff:
            raise InvalidParameterException("Data string too long.")

    def i2c_write_data(self, address:int, data:bytearray, i2c_mode:I2CMode = I2CMode.Start) -> None:
        """Writes data to given I2C address.

        Parameters:
            address(int): 7-bit I2C slave address
            data(str): data string
            i2c_mode(I2CMode): enum code for I2C mode
        """
        dlen = len(data)
        self._check_i2c_parameters(address, dlen)
        rem_bytes = dlen
        while rem_bytes>0:
            chunk_len = min(rem_bytes, 60)
            chunk = data[dlen-rem_bytes:dlen-rem_bytes+chunk_len]
            while True:
                ret = self._write(i2c_mode, dlen & 0xff, dlen>>8, address<<1, *chunk)
                if ret[1] == 0: break
            rem_bytes -= chunk_len

    def i2c_read_data(self, address:int, length:int, i2c_mode:I2CMode = I2CMode.Start) -> bytearray:
        """Reads data from given I2C address.

        Parameters:
            address(int): 7-bit I2C slave address
            length(int): amount of data to read
            i2c_mode(I2CMode): enum code for I2C mode
        
        Returns:
            bytearray: data read from I2C slave.
        """
        self._check_i2c_parameters(address, length)
        if i2c_mode == I2CMode.NoStop:
            raise InvalidParameterException("I2C mode No Stop not available for read.")
        result = bytearray()
        while len(result)<length:
            while True:
                ret = self._write(i2c_mode+1, length & 0xff, length>>8, address<<1 | 0x01)
                if ret[1] == 0: break
            ret = self._write(0x40)
            if ret[1] == 0x41:
                raise FailedCommandException("Error reading from I2C slave.")
            if ret[3] == 0x7f:
                raise FailedCommandException("Error issued by I2C slave.")
            result += bytearray(ret[4:4+ret[3]])
        return result
    
    #################
    # GPIO settings #
    #################
    def __check_gpio_pin_index(self, pin:int):
        """Private command. Checks if GPIO pin index is valid.

        Parameters:
            pin(int): GPIO pin index
        
        Raises:
            InvalidParameterException: if pin index below 0 or above 3
        """
        if pin not in range(4):
            raise InvalidParameterException("Invalid pin index.")
    
    def gpio_read_powerup_value(self, gpio_num:int) -> bool:
        """Reads GPIO pin power-up value from flash memory.

        Parameters:
            gpio_num(int): GPIO pin index
        
        Returns:
            bool: pin power-up value.
        """
        self.__check_gpio_pin_index(gpio_num)
        return self._read_flash_byte(FlashDataSubcode.GPSettings, gpio_num, [4])[0]
    
    def gpio_write_powerup_value(self, gpio_num:int, value:bool) -> None:
        """Writes GPIO pin power-up value to flash memory.

        Parameters:
            gpio_num(int): GPIO pin index
            value(bool): pin power-up value
        """
        self.__check_gpio_pin_index(gpio_num)
        self._write_flash_byte(FlashDataSubcode.GPSettings, gpio_num, [4], [value])
    
    gpio0_powerup_value = property(lambda s: s.gpio_read_powerup_value(0), lambda s, v: s.gpio_write_powerup_value(0, v))
    gpio1_powerup_value = property(lambda s: s.gpio_read_powerup_value(1), lambda s, v: s.gpio_write_powerup_value(1, v))
    gpio2_powerup_value = property(lambda s: s.gpio_read_powerup_value(2), lambda s, v: s.gpio_write_powerup_value(2, v))
    gpio3_powerup_value = property(lambda s: s.gpio_read_powerup_value(3), lambda s, v: s.gpio_write_powerup_value(3, v))
    
    def gpio_read_powerup_direction(self, gpio_num:int) -> GPIODirection:
        """Reads GPIO pin power-up direction from flash memory.

        Parameters:
            gpio_num(int): GPIO pin index
        
        Returns:
            GPIODirection: pin power-up direction code.
        """
        self.__check_gpio_pin_index(gpio_num)
        return GPIODirection(self._read_flash_byte(FlashDataSubcode.GPSettings, gpio_num, [3])[0])
    
    def gpio_write_powerup_direction(self, gpio_num:int, value:GPIODirection) -> None:
        """Writes GPIO pin power-up direction to flash memory.

        Parameters:
            gpio_num(int): GPIO pin index
            value(GPIODirection): pin power-up direction code
        """
        self.__check_gpio_pin_index(gpio_num)
        if gpio_num == 0:
            self.gpio0_write_function(GPIO0Function.GPIO, MemoryType.Flash)
        elif gpio_num == 1:
            self.gpio1_write_function(GPIO1Function.GPIO, MemoryType.Flash)
        elif gpio_num == 2:
            self.gpio2_write_function(GPIO2Function.GPIO, MemoryType.Flash)
        elif gpio_num == 3:
            self.gpio3_write_function(GPIO3Function.GPIO, MemoryType.Flash)
        self._write_flash_byte(FlashDataSubcode.GPSettings, gpio_num, [3], [value])

    gpio0_powerup_direction = property(lambda s: s.gpio_read_powerup_direction(0), lambda s, v: s.gpio_write_powerup_direction(0, v))
    gpio1_powerup_direction = property(lambda s: s.gpio_read_powerup_direction(1), lambda s, v: s.gpio_write_powerup_direction(1, v))
    gpio2_powerup_direction = property(lambda s: s.gpio_read_powerup_direction(2), lambda s, v: s.gpio_write_powerup_direction(2, v))
    gpio3_powerup_direction = property(lambda s: s.gpio_read_powerup_direction(3), lambda s, v: s.gpio_write_powerup_direction(3, v))

    def _gpio_read_function(self, gpio_num:int, mem:MemoryType = None) -> list:
        """Internal command. Reads GPIO pin function.

        Parameters:
            gpio_num(int): GPIO pin index
            mem(MemoryType): enum code for memory type (flash or SRAM)
        
        Returns:
            list[bool]: bit list representing GPIO pin direction value.
        """
        self.__check_gpio_pin_index(gpio_num)
        if mem == None: mem = self._mem_target
        if mem == MemoryType.SRAM:
            return self._read_sram_byte(SramDataSubcode.GPSettings, gpio_num, [0, 1, 2])
        elif mem == MemoryType.Flash:
            return self._read_flash_byte(FlashDataSubcode.GPSettings, gpio_num, [0, 1, 2])
    
    def _gpio_write_function(self, gpio_num:int, value:int, mem:MemoryType = None) -> None:
        """Internal command. Writes GPIO pin function.

        Parameters:
            gpio_num(int): GPIO pin index
            value(int): enum code for GPIO pin function
            mem(MemoryType): enum code for memory type (flash or SRAM)
        """
        self.__check_gpio_pin_index(gpio_num)
        if mem == None: mem = self._mem_target
        if mem == MemoryType.SRAM:
            # we need to read SRAM for voltage reference settings, as they seem
            # to be erased when any GPIO function is changed
            vref_data = self._write(0x61)[6:8]
            # writing GPIO value/dir with 0x50 doesn't affect SRAM, so reading SRAM
            # with 0x61 doesn't tell the real value of GPIO pins unless pins are
            # assigned with 0x60; to avoid overwriting pin value/dir, we must get
            # data with 0x51
            init = self._write(0x51)[(2+2*gpio_num):(4+2*gpio_num)]
            if init[0] <= 1:
                value += (init[0]<<4) + (init[1]<<3)
            
            self._write_sram(SramDataSubcode.GPSettings, gpio_num, value)
            # rewrite voltage reference settings
            dac_vref = 0x80 | (vref_data[0] >> 5)
            adc_vref = 0x80 | ((vref_data[1] >> 2) & 0x07)
            self._write(0x60, 0, 0, dac_vref, 0, adc_vref)
        elif mem == MemoryType.Flash:
            self._write_flash_byte(FlashDataSubcode.GPSettings, gpio_num, [0, 1, 2], self.__byte_to_bits(value, 3))

    def gpio0_read_function(self, mem:MemoryType = None) -> GPIO0Function:
        """Reads GPIO pin 0 function.

        Parameters:
            mem(MemoryType): enum code for memory type (flash or SRAM)

        Returns:
            GPIO0Function: enum code for GPIO pin 0 function.
        """
        ret = self._gpio_read_function(0, mem)
        return GPIO0Function(self.__bits_to_byte(ret))
    
    def gpio0_write_function(self, value: GPIO0Function, mem:MemoryType = None) -> None:
        """Writes GPIO pin 0 function.

        Parameters:
            value(GPIO0Function): enum code for GPIO pin 0 function.
            mem(MemoryType): enum code for memory type (flash or SRAM)
        """
        self._gpio_write_function(0, value, mem)
    
    gpio0_function = property(gpio0_read_function, gpio0_write_function)

    def gpio1_read_function(self, mem:MemoryType = None) -> GPIO1Function:
        """Reads GPIO pin 1 function.

        Parameters:
            mem(MemoryType): enum code for memory type (flash or SRAM)

        Returns:
            GPIO1Function: enum code for GPIO pin 1 function.
        """
        ret = self._gpio_read_function(1, mem)
        return GPIO1Function(self.__bits_to_byte(ret))
    
    def gpio1_write_function(self, value: GPIO1Function, mem:MemoryType = None) -> None:
        """Writes GPIO pin 1 function.

        Parameters:
            value(GPIO1Function): enum code for GPIO pin 1 function.
            mem(MemoryType): enum code for memory type (flash or SRAM)
        """
        self._gpio_write_function(1, value, mem)

    gpio1_function = property(gpio1_read_function, gpio1_write_function)

    def gpio2_read_function(self, mem:MemoryType = None) -> GPIO2Function:
        """Reads GPIO pin 2 function.

        Parameters:
            mem(MemoryType): enum code for memory type (flash or SRAM)

        Returns:
            GPIO2Function: enum code for GPIO pin 2 function.
        """
        ret = self._gpio_read_function(2, mem)
        return GPIO2Function(self.__bits_to_byte(ret))
    
    def gpio2_write_function(self, value: GPIO2Function, mem:MemoryType = None) -> None:
        """Writes GPIO pin 2 function.

        Parameters:
            value(GPIO2Function): enum code for GPIO pin 2 function.
            mem(MemoryType): enum code for memory type (flash or SRAM)
        """
        self._gpio_write_function(2, value, mem)

    gpio2_function = property(gpio2_read_function, gpio2_write_function)

    def gpio3_read_function(self, mem:MemoryType = None) -> GPIO3Function:
        """Reads GPIO pin 3 function.

        Parameters:
            mem(MemoryType): enum code for memory type (flash or SRAM)

        Returns:
            GPIO3Function: enum code for GPIO pin 3 function.
        """
        ret = self._gpio_read_function(3, mem)
        return GPIO3Function(self.__bits_to_byte(ret))
    
    def gpio3_write_function(self, value: GPIO3Function, mem:MemoryType = None) -> None:
        """Writes GPIO pin 3 function.

        Parameters:
            value(GPIO3Function): enum code for GPIO pin 3 function.
            mem(MemoryType): enum code for memory type (flash or SRAM)
        """
        self._gpio_write_function(3, value, mem)

    gpio3_function = property(gpio3_read_function, gpio3_write_function)

    ###############
    # GPIO access #
    ###############
    def gpio_read_direction(self, pin:int) -> GPIODirection:
        """Reads GPIO pin direction.

        Parameters:
            pin(int): GPIO pin index
        
        Returns:
            GPIODirection: GPIO pin direction code.
        """
        self.__check_gpio_pin_index(pin)
        ret = self._write(0x51)
        return GPIODirection(ret[3 + pin*2])

    def gpio_write_direction(self, pin:int, mode:GPIODirection) -> None:
        """Writes GPIO pin direction.

        Parameters:
            pin(int): GPIO pin index
            mode(GPIODirection): GPIO pin direction code
        """
        self.__check_gpio_pin_index(pin)
        cmd = bytearray([0x50, 0x00])
        for n in range(4):
            cmd += bytearray([0x00, 0x00, 0x01 if pin == n else 0x00, mode if pin == n else 0x00])
        self._write(*cmd)
    
    gpio0_direction = property(lambda s: s.gpio_read_direction(0), lambda s, v: s.gpio_write_direction(0, v))
    gpio1_direction = property(lambda s: s.gpio_read_direction(1), lambda s, v: s.gpio_write_direction(1, v))
    gpio2_direction = property(lambda s: s.gpio_read_direction(2), lambda s, v: s.gpio_write_direction(2, v))
    gpio3_direction = property(lambda s: s.gpio_read_direction(3), lambda s, v: s.gpio_write_direction(3, v))
    
    def gpio_read_value(self, pin:int) -> bool:
        """Gets GPIO pin value.

        Parameters:
            pin(int): GPIO pin index
        
        Returns:
            bool: GPIO pin value.
        """
        self.__check_gpio_pin_index(pin)
        value = self._write(0x51)[2 + pin*2]
        if value == 0xee:
            warnings.warn("Pin not set for GPIO operation", InvalidReturnValueWarning)
        return bool(value)

    def gpio_write_value(self, pin:int, value:bool) -> None:
        """Sets GPIO pin direction.

        Parameters:
            pin(int): GPIO pin index
            value(bool): GPIO pin value
        """
        self.__check_gpio_pin_index(pin)
        cmd = bytearray([0x50, 0x00])
        for n in range(4):
            cmd += bytearray([0x01 if pin == n else 0x00, value if pin == n else 0x00, 0x00, 0x00])
        self._write(*cmd)

    gpio0_value = property(lambda s: s.gpio_read_value(0), lambda s, v: s.gpio_write_value(0, v))
    gpio1_value = property(lambda s: s.gpio_read_value(1), lambda s, v: s.gpio_write_value(1, v))
    gpio2_value = property(lambda s: s.gpio_read_value(2), lambda s, v: s.gpio_write_value(2, v))
    gpio3_value = property(lambda s: s.gpio_read_value(3), lambda s, v: s.gpio_write_value(3, v))

    ######################
    # ADC and DAC access #
    ######################
    def read_adc_reference_voltage(self, mem:MemoryType = None) -> ReferenceVoltageValue:
        """Reads ADC reference voltage settings.

        Parameters:
            mem(MemoryType): enum code for memory type (flash or SRAM)
        
        Returns:
            ReferenceVoltageValue: enum code for reference voltage settings.
        """
        fct = self.__get_mem_read_function(mem)
        ret = fct(FlashDataSubcode.ChipSettings, 3, [3, 4])
        return ReferenceVoltageValue(self.__bits_to_byte(ret))
    
    def write_adc_reference_voltage(self, value:ReferenceVoltageValue, mem:MemoryType = None) -> None:
        """Writes ADC reference voltage settings.

        Parameters:
            mem(MemoryType): enum code for memory type (flash or SRAM)
            ReferenceVoltageValue: enum code for reference voltage settings
        """
        if mem == None: mem = self._mem_target
        if mem == MemoryType.SRAM:
            # we keep bit 0 as it is reference flag and we don't want to modify it here
            init = self.__and(self._read_sram(SramDataSubcode.ChipSettings)[3]>>2, 0b00000001)
            # value must be on bits 1 and 2, bit 7 must be set to 1 to enable modification
            self._write_sram(SramDataSubcode.ChipSettings, 3, (value<<1) + 0x80 + init)
        elif mem == MemoryType.Flash:
            self._write_flash_byte(FlashDataSubcode.ChipSettings, 3, [3, 4], self.__byte_to_bits(value, 2))

    adc_reference_voltage = property(read_adc_reference_voltage, write_adc_reference_voltage)

    def read_adc_reference_source(self, mem:MemoryType = None) -> ReferenceVoltageSource:
        """Reads ADC reference flag.

        Parameters:
            mem(MemoryType): enum code for memory type (flash or SRAM)
        
        Returns:
            ReferenceVoltageSource: enum code for reference voltage source.
        """
        fct = self.__get_mem_read_function(mem)
        return ReferenceVoltageSource(fct(FlashDataSubcode.ChipSettings, 3, [2])[0])

    def write_adc_reference_source(self, value:ReferenceVoltageSource, mem:MemoryType = None) -> None:
        """Writes ADC reference flag.

        Parameters:
            value(ReferenceVoltageSource): enum code for reference voltage source
            mem(MemoryType): enum code for memory type (flash or SRAM)
        """
        if mem == None: mem = self._mem_target
        if mem == MemoryType.SRAM:
            init = self.__and(self._read_sram(SramDataSubcode.ChipSettings)[3] >> 2, 0b00000110)
            self._write_sram(SramDataSubcode.ChipSettings, 3, value + 0x80 + init)
        elif mem == MemoryType.Flash:
            self._write_flash_byte(FlashDataSubcode.ChipSettings, 3, [2], [value])
    
    adc_reference_source = property(read_adc_reference_source, write_adc_reference_source)

    def read_dac_reference_voltage(self, mem:MemoryType = None) -> ReferenceVoltageValue:
        """Reads DAC reference voltage settings.

        Parameters:
            mem(MemoryType): enum code for memory type (flash or SRAM)
        
        Returns:
            ReferenceVoltageValue: enum code for reference voltage settings.
        """
        fct = self.__get_mem_read_function(mem)
        ret = fct(FlashDataSubcode.ChipSettings, 2, [6, 7])
        return ReferenceVoltageValue(self.__bits_to_byte(ret))
    
    def write_dac_reference_voltage(self, value:ReferenceVoltageValue, mem:MemoryType = None) -> None:
        """Writes DAC reference voltage settings.

        Parameters:
            mem(MemoryType): enum code for memory type (flash or SRAM)
            ReferenceVoltageValue: enum code for reference voltage settings
        """
        if mem == None: mem = self._mem_target
        if mem == MemoryType.SRAM:
            init = self.__and(self._read_sram(SramDataSubcode.ChipSettings)[2]>>5, 0b00000001)
            self._write_sram(SramDataSubcode.ChipSettings, 1, (value<<1) + 0x80 + init)
        elif mem == MemoryType.Flash:
            self._write_flash_byte(FlashDataSubcode.ChipSettings, 2, [6, 7], self.__byte_to_bits(value, 2))

    dac_reference_voltage = property(read_dac_reference_voltage, write_dac_reference_voltage)

    def read_dac_reference_source(self, mem:MemoryType = None) -> ReferenceVoltageSource:
        """Reads DAC reference flag.

        Parameters:
            mem(MemoryType): enum code for memory type (flash or SRAM)
        
        Returns:
            ReferenceVoltageSource: enum code for reference voltage source.
        """
        fct = self.__get_mem_read_function(mem)
        return ReferenceVoltageSource(fct(FlashDataSubcode.ChipSettings, 2, [5])[0])

    def write_dac_reference_source(self, value:ReferenceVoltageSource, mem:MemoryType = None) -> None:
        """Writes DAC reference flag.

        Parameters:
            value(ReferenceVoltageSource): enum code for reference voltage source
            mem(MemoryType): enum code for memory type (flash or SRAM)
        """
        if mem == None: mem = self._mem_target
        if mem == MemoryType.SRAM:
            init = self.__and(self._read_sram(SramDataSubcode.ChipSettings)[2]>>5, 0b00000110)
            self._write_sram(SramDataSubcode.ChipSettings, 1, value + 0x80 + init)
        elif mem == MemoryType.Flash:
            self._write_flash_byte(FlashDataSubcode.ChipSettings, 2, [5], [value])
    
    dac_reference_source = property(read_dac_reference_source, write_dac_reference_source)

    def read_dac_powerup_value(self) -> int:
        """Reads DAC power-up value from flash memory.

        Returns:
            int: DAC power-up value.
        """
        ret = self._read_flash_byte(FlashDataSubcode.ChipSettings, 2, [0, 1, 2, 3, 4])
        return self.__bits_to_byte(ret)

    def write_dac_powerup_value(self, value:int) -> None:
        """Writes DAC power-up value to flash memory.

        Parameters:
            value(int): DAC power-up value
        """
        self._write_flash_byte(FlashDataSubcode.ChipSettings, 2, [0, 1, 2, 3 ,4], self.__byte_to_bits(value, 5))
    
    dac_powerup_value = property(read_dac_powerup_value, write_dac_powerup_value)

    def read_adc(self, idx:int) -> int:
        """Reads ADC value.

        Parameters:
            idx(int): ADC index
        
        Raises:
            InvalidParameterException: if ADC index is below 0 or above 2

        Returns:
            int: ADC value.
        """
        if idx not in [0, 1, 2]:
            InvalidParameterException("Invalid ADC index.")
        data = self._write(0x10)
        return data[50+idx*2] | (data[51+idx*2] << 8)
    
    adc0_value = property(lambda v : v.read_adc(0))
    adc1_value = property(lambda v : v.read_adc(1))
    adc2_value = property(lambda v : v.read_adc(2))

    def write_dac(self, value:int) -> None:
        """Writes DAC value.

        Parameters:
            value(int): DAC value (5 bit)
        """
        self._write_sram(SramDataSubcode.ChipSettings, 2, (value & 0x1f) + 0x80)

    dac_value = property(None, write_dac)

    #########
    # Other #
    #########
    def read_firmware_version(self) -> str:
        """Reads chip firmware version.

        Returns:
            str: chip firmware version string.
        """
        data = self._write(0x10)
        return bytearray(data[46:50]).decode("utf-8")
    
    firmware_version = property(read_firmware_version)

    def reset_chip(self) -> None:
        """Resets chip. After this, a new instance must be created,
        as the device descriptor will have changed.
        """
        try:
            # this should throw an OSError as chip disconnects
            self._write(0x70, 0xab, 0xcd, 0xef)
        except OSError:
            self.close()
