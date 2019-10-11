<p align="center">
  <img  src="/icons/espLogo.png">
</p>


----


# Getting Started
---
MicroTool is a free software which allows the user to access, flash and erase the ESP32 and ESP8266 internal memory. Meanwhile , MicroTool introduces the set of features mentioned in the sections below.

The software is divided into two major modes, production mode and advanced mode. The production mode is a simple user interface containing the minimum number of features allowing the operator to conduct the necessary flashing and or flash erasing procedures with minimum complexity and errors.The advanced mode on the other hand is more complex and sums up all the features and commands made possible with the esptool library but with an easier and more advanced user experience. 

  - Production Mode.
  - Advanced Mode.
  
# Table of contents
---
- [Features](#features)
  - [Serial Port](#Serial-Port)
  - [Baud Rate](#Baud-Rate)
  - [Flash Firmware/Bootloader](#Flash-Firmware/Bootloader)
  - [Setting Flash Mode and Size](#Setting-Flash-Mode-and-Size)
  - [Compression](#Compression)
  - [Read Flash Contents](#Read-Flash-Contents)
  - [Erase Flash & erase region](#Erase-Flash:-&-erase-region)
  - [Convert ELF to Binary](#Convert-ELF-to-Binary)
  - [Output bin image details: image info](#Output-bin-image-details:-image-info)
  - [Verify flash](#Verify-flash)
  - [Dump Memory](#Dump-Memory)
  - [load RAM](#load-RAM)
  - [Read / write Memory](#Read-/-write-Memory)
  - [Read flash status](#Read-flash-status)
  - [Write flash status](#Write-flash-status)
  - [Chip Id](#Chip-Id)
- [New Features](#new-features)
  - [Secure Packaging](#Secure-Packaging)
  - [Efuse Table](#Efuse-Table)
  - [Export Efuse](#Export-Efuse)
  - [Login/Password Change](#Login/Password-Change)
- [Dependencies](#Dependencies)
- [Download](#Download)
- [Installation](#Installation)
- [To do](#To do)
- [Contributing](#contributing)
- [License](#License)

#  Features
---

### Serial Port

The serial port is selected using the ComboBox Designated Serial Port, like COM1 (Windows). If no option is specified,esptool will enumerate all connected serial ports and try each one until it finds an Espressif device (ESP32 or ESP8266) connected. 


### Baud Rate

The default baud rate is 115200bps. Different rates may be set using the Baud Rate ComboBox. This can speed up writing and reading flash operations.The baud rate is limited to 115200 when initial connection is established,higher speeds are only used for data transfers. Most hardware configurations will work with 230400, some with 460800, 921600 and/or 1500000 or higher.If you have connectivity problems then you can also set baud rates below 115200. You can also choose 74880, which is the usual baud rate used by the ESP8266 to output boot log information. 


### Flash Firmware/Bootloader

Binary data (Multiple flash addresses and file)can be written to the ESP's flash chip. The chip selection is optional when writing to ESP flash, as it will be detected when it connects to the serial port.The offset (address) and file name are crucial for this operation.

The file names created by "ELF to Bin" include the flash offsets as part of the file name. For other types of images, consult your SDK documentation to determine the files to flash at which offsets.Numeric values passed as offset address can only
be specified in hex (ie 0x1000). 


### Setting Flash Mode and Size

You may also need to specify flash mode and flash size, if you wish to override the defaults. 


### Compression

By default, the serial transfered data is compressed by esptool.py for better performance. 


### Read Flash Contents

The Read flash feature allows reading back the contents of flash. for that you need to specify an address, a size, and a filename to dump the output to. 


### Erase Flash & erase region

To erase the entire flash chip (all data replaced with 0xFF bytes) To erase a region of the flash, for example starting at an address (ie:0x20000)with a length (ie 0x4000 bytes) (16KB) The address and length must both be multiples of the SPI flash erase sector size. This is 0x1000 (4096) bytes for supported flash chips. 


### Convert ELF to Binary

Converts an ELF file into the binary executable images which can be flashed and then booted into the chip. This command does not require a serial connection. 


### Output bin image details: image info

The image info outputs some information (load addresses, sizes, etc) about a .bin file. 


### Verify flash

Allows you to verify that data in flash matches a local file. Additional verification is not usually needed. However, if you wish to perform a byte-by-byte verification of the flash contents then you can do so with this feature. 


### Dump Memory

Will dump a region from the chip's memory space to a file. 


### load RAM

Allows the loading of an executable binary image directly into RAM, and then immediately executes the program contained within it.The binary image must only contain IRAM- and DRAM-resident segments. Any SPI flash mapped segments will not load correctly and the image will probably crash. The image info can be used to check the binary image contents. 


### Read / write Memory

The read & write Memory allow reading and writing single words (4 bytes) of RAM. This can be used to "peek" and "poke" at registers. 


### Read flash status

Intended for use when debugging hardware flash chip-related problems. It allows sending a RDSR, RDSR2 and/or RDSR3 command to the flash chip to read the status register contents. This can be used to check write protection status.
The bytes number determines how many status register bytes are read:

- bytes 1 sends the most common RDSR command (05h) and returns a single byte of status. 
- bytes 2 sends both RDSR (05h) and RDSR2 (35h), reads one byte of status from each, and returns a two byte status. 
- bytes 3 sends RDSR (05h), RDSR2 (35h), and RDSR3 (15h), reads one byte of status from each, and returns a 3 byte status. 


### Write flash status

Intended for use when debugging hardware flash chip-related problems. It allows sending WRSR, WRSR2 and/or WRSR3 commands to the flash chip to write the status register contents. This can be used to clear write protection bits. The bytes option is similar to the corresponding option for read flash status and causes a mix of WRSR (01h), WRSR2 (31h), and WRSR3 (11h) commands to be sent to the chip. If bytes 2 is used then WRSR is sent first with a 16-bit argument and then with an 8-bit argument. Otherwise, each command is accompanied by 8-bits of the new status register value. 


### Chip Id

Allows you to read a 4 byte ID which forms part of the MAC address.
# New Features 
---
### Secure Packaging
### Efuse Table
### Export Efuse
### Login/Password Change 

---

# Dependencies
---
MicroTool uses a number of open source projects and libraries to work properly:

* [Python] - HTML enhanced for web apps!
* [PyQt5] - awesome web-based text editor
* [esptool] - evented I/O for the backend
* [esptool] - fast node.js network app framework [@tjholowaychuk] 
* [Gulp] - the streaming build system
* [Breakdance](http://breakdance.io) - HTML to Markdown converter
* [jQuery] - duh
# Download
---
MicroTool itself is open source with a [public repository][MicroTool1.0] on GitHub.You can also download the first release from the [this link ](https://github.com/Gueni/MicroTool1.0/releases).

# Installation
---
Microtool requires [Python 3](https://www.python.org/download/releases/3.0/) to run.

Install python 3 from https://www.python.org/download/releases/3.0/





# To do
----

 - Integrate all features in local terminal without having to type all attributes.
 - Optimize the Efuse feature.
 - Enhance UI/UX.
 - More Interactive Help Section.
 

# Contributing
----

# License
-----

    Copyright 2019 by Mohamed Gueni

    Licensed under the GNU General Public License License, Version 2.0
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at GNU .

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.


[//]:<These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO- >


   [MicroTool1.0]: <https://github.com/Gueni/MicroTool1.0/tree/1.0>
   [GNU]:<https://github.com/Gueni/MicroTool1.0/releases>
  
