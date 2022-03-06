#!/usr/bin/python
'''This shows how to configure and use the DAC.
'''
from mcp2221 import MCP2221, find_devices
from mcp2221.enums import ReferenceVoltageSource, ReferenceVoltageValue, GPIO2Function, GPIO3Function

# opens 1st device found
mcp = MCP2221(find_devices()[0])
# reads DAC voltage reference source using property
print(mcp.dac_reference_source)
# this tells if the DAC uses VDD or the internal
# reference as a voltage reference; if the later
# is true, then we may want to read the internal
# voltage reference value that way (with property):
print(mcp.dac_reference_voltage)
# sets the DAC reference source and voltage reference
# using properties; note that setting voltage reference voltage
# when reference source is Vdd is useless, but it can be done
mcp.dac_reference_source = ReferenceVoltageSource.Vdd
mcp.dac_reference_voltage = ReferenceVoltageValue.Voltage2_048V
# reads adc voltage reference source and value with class methods
print(mcp.read_dac_reference_source())
print(mcp.read_dac_reference_voltage())
# writes adc voltage reference source and value with class methods
mcp.write_dac_reference_source(ReferenceVoltageSource.Internal)
mcp.write_dac_reference_voltage(ReferenceVoltageValue.Voltage1_024V)
# reads DAC power-up value using property
print(mcp.dac_powerup_value)
# writes DAC power-up value using property
mcp.dac_powerup_value = 10
# reads DAC power-up value using class method
print(mcp.read_dac_powerup_value())
# writes DAC power-up value using class method
mcp.write_dac_powerup_value(0)
# DAC can be routed to GPIO pin 2 or 3 with:
#     mcp.gpio2_function = GPIO2Function.DAC1
# or
#     mcp.gpio3_function = GPIO3Function.DAC2
#
# writes DAC value using property
mcp.dac_value = 5
# writes DAC value using class method
mcp.write_dac(10)
