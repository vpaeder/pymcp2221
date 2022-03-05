# pymcp2221
A python driver for the Microchip MCP2221/MCP2221A USB 2.0 to I2C/UART protocol converters

First and foremost, there is already a python package for the same chip available [here](https://github.com/nonNoise/PyMCP2221A). If you use it and are satisfied with it, you probably won't find improvements in my package. If you're missing some features however, my code is meant to expose every chip feature described in the datasheet in a systematic manner, for python 3.3+.

This code is currently in alpha stage. I'm writing unittests and will likely find remaining bugs. Some properties and methods may also change name.

##### Implemented features
- Status/Set Parameters (0x10) - ok, except I2C line monitoring (bytes 22 and 23)
- Read Flash Data (0xB0) - ok
- Write Flash Data (0xB1) - ok
- Send Flash Access Password (0xB2) - ok
- I2C Write Data (0x90) - ok
- I2C Write Data Repeated Start (0x92) - ok
- I2C Write Data No Stop (0x94) - ok
- I2C Read Data (0x91/0x40) - ok
- I2C Read Data Repeated Start (0x93/0x40) - ok
- Set GPIO Output Values (0x50) - ok
- Get GPIO Values (0x51) - ok
- Set SRAM Settings (0x60) - ok, except GPIO directions/values through SRAM (duplicate with 0x50)
- Get SRAM Settings (0x61) - ok, except GPIO directions/values through SRAM (duplicate with 0x51)
- Reset Chip (0x70) - ok

Every feature marked *ok* is implemented but not thoroughly tested at this point.

# Requirements
- [hidapi](https://pypi.org/project/hidapi)

# Setup
... not written yet ...

# Examples
... not written yet ...

# API
I'll format docs in a neat way at some point. In the meantime you can rely on python docstrings, which are rather complete already.

Two ways to do that:
1) from the command line, use pydoc:
    ` $ pydoc mcp2221`
2) from within python:
    ` >>> import mcp2221; help(mcp2221)`
