import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pymcp2221",
    version="1.0.9",
    author="Vincent Paeder",
    author_email="python@paeder.fi",
    description="Python driver for the Microchip MCP2221/MCP2221A USB 2.0 to I2C/UART protocol converters.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=['MCP2221', 'MCP2221A', 'Microchip'],
    url="https://github.com/vpaeder/pymcp2221",
    project_urls={
        "Bug Tracker": "https://github.com/vpaeder/pymcp2221/issues",
    },
    packages=setuptools.find_packages(),
    install_requires=['hidapi'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Communications",
        "Topic :: System :: Hardware :: Hardware Drivers",
        "Topic :: System :: Hardware :: Universal Serial Bus (USB)",
        "Topic :: System :: Hardware :: Universal Serial Bus (USB) :: Human Interface Device (HID)"
    ],
    python_requires='>=3.2',
)
