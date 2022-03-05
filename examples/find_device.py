#!/usr/bin/python
'''This is an example showing how to discover connected devices.
If you have an appropriate device connected, this example will
produce an output like this:

    [{'path': b'...path_to_device...', 'vendor_id': 1240,
    'product_id': 221, 'serial_number': '', 'release_number': 256,
    'manufacturer_string': 'ˇMicrochip Technology Inc.',
    'product_string': 'MCP2221 USB-I2C/UART Combo',
    'usage_page': 65280, 'usage': 1, 'interface_number': 2}]

This is a list of device descriptors (here with one device) that
can be used to initialize a MCP2221 class instance.

The arguments vendor_id and product_id are for USB vendor ID and
product ID, namely. Vendor IDs are obtained from usb.org against
a fee. The one for Microchip is 1240, and they decided to assign
product ID 221 to their chip (hence the default values).
This said, we can get to the HID bit. The chip communicates with
the host through the USB-HID protocol. We use the hidapi wrapper
for python, which provides a function to enumerate all connected
devices. The function 'find_devices' filters relevant devices. 
'''

from mcp2221 import find_devices

print(find_devices(vendor_id=1240, product_id=221))