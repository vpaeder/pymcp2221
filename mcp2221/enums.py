"""Enums for MCP2221 driver."""

__all__ = ["ClockDutyCycle", "ReferenceVoltageValue", "GPIO0Function", "GPIO1Function",
           "GPIO2Function", "GPIO3Function", "I2CCancelTransferResponse", "I2CSetSpeedResponse",
           "FlashDataSubcode", "SramDataSubcode", "I2CMode", "GPIODirection",
           "SecurityOption", "MemoryType", "ClockFrequency", "ReferenceVoltageSource"]

import enum

class ClockDutyCycle(enum.IntEnum):
    """Clock output duty cycle. This is the duty cycle
    of the clock signal when output to GPIO 1. Values are in percent.
    """
    Percent_0 = 0x00
    Percent_25 = 0x01
    Percent_50 = 0x02
    Percent_75 = 0x03

class ReferenceVoltageValue(enum.IntEnum):
    """Voltage reference for ADCs or DAC. Values are in V (replace underscore
    with dot, e.g. 1_024V => 1.024V).
    """
    VoltageOff = 0x00
    Voltage1_024V = 0x01
    Voltage2_048V = 0x02
    Voltage4_096V = 0x03

class ClockFrequency(enum.IntEnum):
    """Clock output frequency. This is the frequency
    of the clock signal when output to GPIO 1.
    """
    Clock_24MHz = 0x01
    Clock_12MHz = 0x02
    Clock_6MHz = 0x03
    Clock_3MHz = 0x04
    Clock_1_5MHz = 0x05
    Clock_750kHz = 0x06
    Clock_375kHz = 0x07

class GPIO0Function(enum.IntEnum):
    """Functions for GPIO pin 0. These are:
        GPIO: normal GPIO operation
        USBSuspendState: indicates if chip is in suspend state
        UartRxLed: activity signal for UART RX
    """
    GPIO = 0x00
    USBSuspendState = 0x01
    UartRxLed = 0x02

class GPIO1Function(enum.IntEnum):
    """Functions for GPIO pin 1. These are:
        GPIO: normal GPIO operation
        ClockOutput: clock output
        ADC1: input for ADC1
        UartTxLed: activity signal for UART TX
        Interrupt: input for interrupt trigger
    """
    GPIO = 0x00
    ClockOutput = 0x01
    ADC1 = 0x02
    UartTxLed = 0x03
    Interrupt = 0x04

class GPIO2Function(enum.IntEnum):
    """Functions for GPIO pin 2. These are:
        GPIO: normal GPIO operation
        USBConfigured: indicates if USB connection is configured
        ADC2: input for ADC2
        DAC1: output for DAC
    """
    GPIO = 0x00
    USBConfigured = 0x01
    ADC2 = 0x02
    DAC1 = 0x03

class GPIO3Function(enum.IntEnum):
    """Functions for GPIO pin 3. These are:
        GPIO: normal GPIO operation
        I2CLed: activity signal for I2C
        ADC3: input for ADC3
        DAC2: output for DAC
    """
    GPIO = 0x00
    I2CLed = 0x01
    ADC3 = 0x02
    DAC2 = 0x03

class I2CCancelTransferResponse(enum.IntEnum):
    """Response for I2C cancel transfer command. These are:
        NoOp: not in the right state to do anything
        MarkedForCancellation: transfer is marked for cancellation
        InIdleMode: I2C bus is already in idle state
    """
    NoOp = 0x00
    MarkedForCancellation = 0x10
    InIdleMode = 0x11

class I2CSetSpeedResponse(enum.IntEnum):
    """Response for I2C set speed command. These are:
        NoOp: not in the right state to do anything
        SpeedConsidered: chip acknowledged request
        SpeedNotSet: chip rejected request
    """
    NoOp = 0x00
    SpeedConsidered = 0x20
    SpeedNotSet = 0x21


class FlashDataSubcode(enum.IntEnum):
    """Codes for access to flash memory registers:
        ChipSettings: general chip settings
        GPSettings: GPIO settings
        USBManufacturerDescriptorString: USB manufacturer descriptor
        USBProductDescriptorString: USB product descriptor
        USBSerialNumberDescriptorString: USB serial number descriptor
        ChipFactorySerialNumber: chip serial number
    """
    ChipSettings = 0x00
    GPSettings = 0x01
    USBManufacturerDescriptorString = 0x02
    USBProductDescriptorString = 0x03
    USBSerialNumberDescriptorString = 0x04
    ChipFactorySerialNumber = 0x05

class SramDataSubcode(enum.IntEnum):
    """Codes for access to SRAM registers:
        ChipSettings: general chip settings
        GPSettings: GPIO settings
    """
    ChipSettings = 0x00
    GPSettings = 0x01

class I2CMode(enum.IntEnum):
    """I2C data transfer modes.
    These are defined in the I2C protocol.
    """
    Start = 0x90
    RepeatedStart = 0x92
    NoStop = 0x94

class GPIODirection(enum.IntEnum):
    """GPIO direction values."""
    Output = 0x00
    Input = 0x01
    NotSet = 0xef

class SecurityOption(enum.IntEnum):
    """Chip security options."""
    Unsecured = 0x00
    PasswordProtected = 0x01
    PermanentlyLocked = 0x02

class MemoryType(enum.IntEnum):
    """Memory type. This tells which memory should be accessed
    for values present in both SRAM and flash.
    """
    SRAM = 0x00
    Flash = 0x01

class ReferenceVoltageSource(enum.IntEnum):
    """Voltage reference source for ADCs and DAC."""
    Vdd = 0x00
    Internal = 0x01
