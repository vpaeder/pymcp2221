#!/usr/bin/python
'''This shows how to connect with a device and set GPIO
pin configuration in flash memory. The settings are then
remembered upon reboot.
There's a 2nd example, gpio.py, that shows how to set
run-time values and properties of GPIO pins.
'''
from mcp2221 import MCP2221, find_devices
from mcp2221.enums import GPIO0Function, GPIODirection, MemoryType

# opens 1st device found
mcp = MCP2221(find_devices()[0])
# sets target memory to flash memory
mcp.set_default_memory_target(MemoryType.Flash)
# It is also possible to pass the MemoryType argument to
# specific functions instead, like:
#    mcp.gpio0_write_function(GPIO0Function.GPIO, MemoryType.Flash)
# However, this variant is only possible with class method,
# not with property.
# reads GPIO pin 0 function using property
# example output: GPIO0Function.GPIO
# Note that this is exactly the same syntax as with runtime access,
# but since we have set the default memory target to flash, we
# read and write from/to flash by default.
print(mcp.gpio0_function)
# sets GPIO pin 0 function using property
mcp.gpio0_function = GPIO0Function.UartRxLed
# reads GPIO pin 0 function with class method
# should print: GPIOFunction.UartRxLed
print(mcp.gpio0_read_function())
# sets GPIO pin 0 function with class method
mcp.gpio0_write_function(GPIO0Function.GPIO)
# reads power-up pin direction with property: input or output
# example output: GPIODirection.Output
print(mcp.gpio0_powerup_direction)
# sets power-up pin direction using property
mcp.gpio0_powerup_direction = GPIODirection.Input
# reads power-up pin direction with class method
# should print: GPIODirection.Input
print(mcp.gpio_read_powerup_direction(0))
# writes power-up pin direction with class method
mcp.gpio_write_powerup_direction(0, GPIODirection.Output)
# reads power-up pin value with property: True or False
print(mcp.gpio0_powerup_value)
# sets power-up pin value with property
mcp.gpio0_powerup_value = True
# reads power-up pin value with class method
# should print: True
print(mcp.gpio_read_powerup_value(0))
# writes power-up pin value with class method
mcp.gpio_write_powerup_value(0, False)

# After disconnecting and reconnecting your device,
# GPIO pin 0 should be now set as output with value 0
