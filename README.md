# pymcp2221

This is a python driver for the Microchip MCP2221/MCP2221A USB 2.0 to I2C/UART protocol converters
([manufacturer's page](https://www.microchip.com/en-us/product/MCP2221A)).

First and foremost, there are python packages for the same chip available [here](https://github.com/nonNoise/PyMCP2221A) and [here](https://github.com/pilotak/python-mcp2221). If you use them and are satisfied, you probably won't find improvements in my package. If you're missing some features however, my code is meant to expose every chip feature described in the datasheet in a systematic manner, for python 3.2+.

## Implemented features

- Status/Set Parameters (0x10) - ok
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

Every feature marked *ok* is implemented, but some of them, like I2C, haven't been tested in real conditions.

## Requirements

- [hidapi](https://pypi.org/project/hidapi)

## Setup

From command line, use:

```bash
python setup.py install
```

or for Linux/OSX:

```bash
sudo python setup.py install
```

On Linux, to access your devices without root privileges, you need to set specific udev rules, as explained in [hidapi documentation](https://github.com/trezor/cython-hidapi#udev-rules).

## Examples

See [examples](examples) folder.

## Tests

The [tests](tests) folder contains unit tests for most of the aspects of this package. To run them, use:

```bash
python -m unittest
```

## API

You can find docs in the [docs](docs) folder (generated from python docstrings). Alternatively, you can rely on python docstrings

1) either from the command line, use pydoc:

```bash
pydoc mcp2221
```

2) or from within python:

```python
import mcp2221; help(mcp2221)
```
