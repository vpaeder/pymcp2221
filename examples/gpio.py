#!/usr/bin/python
'''This shows how to connect with a device and do some
basic operations with GPIO pins.
There's a 2nd example, gpio_powerup.py, that shows how
to set values in flash memory.
'''
from mcp2221 import MCP2221, find_devices
from mcp2221.enums import GPIO0Function, GPIODirection

# opens 1st device found
mcp = MCP2221(find_devices()[0])
# reads GPIO pin 0 function using property
# example output: GPIO0Function.GPIO
# Check enums GPIOxFunction to see what is available
# for each pin. To operate on pin 1, 2 or 3, use gpio1_...,
# gpio2_... or gpio3_... properties and methods.
print(mcp.gpio0_function)
# sets GPIO pin 0 function using property
mcp.gpio0_function = GPIO0Function.UartRxLed
# reads GPIO pin 0 function with class method
# should print: GPIOFunction.UartRxLed
print(mcp.gpio0_read_function())
# sets GPIO pin 0 function with class method
mcp.gpio0_write_function(GPIO0Function.GPIO)
# reads pin direction with property: input or output
# example output: GPIODirection.Output
print(mcp.gpio0_direction)
# sets pin direction using property
mcp.gpio0_direction = GPIODirection.Input
# reads pin direction with class method
# should print: GPIODirection.Input
print(mcp.gpio_read_direction(0))
# writes pin direction with class method
mcp.gpio_write_direction(0, GPIODirection.Output)
# reads pin value with property: True or False
print(mcp.gpio0_value)
# sets pin value with property
mcp.gpio0_value = True
# reads pin value with class method
# should print: True
print(mcp.gpio_read_value(0))
# writes pin value with class method
mcp.gpio_write_value(0, False)
