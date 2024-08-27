<p align="center">
  <img  src="\Screenshots\espLogo.png.png"
</p>



----
![python3.x](https://img.shields.io/badge/python-3.x-brightgreen.svg) ![python2.x](https://img.shields.io/badge/python-2.x-yellow.svg) /github/v/release/:user/:repo

 

# Getting Started  ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico)
---
flash is a free software which allows the user to access, flash and erase the ESP32 and ESP8266 internal memory. Meanwhile , flash introduces the set of features mentioned in the sections below.

The software is divided into two major modes, production mode and advanced mode. The production mode is a simple user interface containing the minimum number of features allowing the operator to conduct the necessary flashing and or flash erasing procedures with minimum complexity and errors.The advanced mode on the other hand is more complex and sums up all the features and commands made possible with the esptool library but with an easier and more advanced user experience. 


  
# Table of contents  ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico)
---
- [Features](#features)
  - [Serial Port](#Serial-Port)
  - [Baud Rate](#Baud-Rate)
  - [Flash Firmware Bootloader](#Flash-Firmware-Bootloader)
  - [Setting Flash Mode and Size](#Setting-Flash-Mode-and-Size)
  - [Compression](#Compression)
  - [Read Flash Contents](#Read-Flash-Contents)
  - [Erase Flash & erase region](#Erase-Flash-&-erase-region)
  - [Convert ELF to Binary](#Convert-ELF-to-Binary)
  - [Output bin image details](#Output-bin-image-details)
  - [Verify flash](#Verify-flash)
  - [Dump Memory](#Dump-Memory)
  - [load RAM](#load-RAM)
  - [Read / write Memory](#Read-/-write-Memory)
  - [Read flash status](#Read-flash-status)
  - [Write flash status](#Write-flash-status)
  - [Chip Id](#Chip-Id)
  - [Secure Packaging](#Secure-Packaging)
  - [Efuse Table](#Efuse-Table)
  - [Export Efuse](#Export-Efuse)
  - [Login/Password Change](#Login/Password-Change)
- [Dependencies](#Dependencies)
- [Download](#Download)
- [Installation](#Installation)
- [To do](#To-do)
- [Licensing](#Licensing)




#  Features  ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico)
---



### Serial Port  ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico)

The serial port is selected using the ComboBox Designated Serial Port, like COM1 (Windows). If no option is specified,esptool will enumerate all connected serial ports and try each one until it finds an Espressif device (ESP32 or ESP8266) connected. 
<p align="center">
  <img  src="\Screenshots\serialandbaud.png">
</p>

### Baud Rate  ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico)

The default baud rate is 115200bps. Different rates may be set using the Baud Rate ComboBox. This can speed up writing and reading flash operations.The baud rate is limited to 115200 when initial connection is established,higher speeds are only used for data transfers. Most hardware configurations will work with 230400, some with 460800, 921600 and/or 1500000 or higher.If you have connectivity problems then you can also set baud rates below 115200. You can also choose 74880, which is the usual baud rate used by the ESP8266 to output boot log information. 


### Flash Firmware/Bootloader  ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico)


Binary data (Multiple flash addresses and file)can be written to the ESP's flash chip. The chip selection is optional when writing to ESP flash, as it will be detected when it connects to the serial port.The offset (address) and file name are crucial for this operation.

The file names created by "ELF to Bin" include the flash offsets as part of the file name. For other types of images, consult your SDK documentation to determine the files to flash at which offsets.Numeric values passed as offset address can only
be specified in hex (ie 0x1000). 


### Setting Flash Mode and Size  ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico)

You may also need to specify flash mode and flash size, if you wish to override the defaults. 


### Compression  ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico)

By default, the serial transfered data is compressed by [esptool.py ](https://github.com/espressif/esptool) for better performance. 


### Read Flash Contents  ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico)

The Read flash feature allows reading back the contents of flash. for that you need to specify an address, a size, and a filename to dump the output to. 


### Erase Flash & erase region  ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico)



To erase the entire flash chip (all data replaced with 0xFF bytes) To erase a region of the flash, for example starting at an address (ie 0x20000)with a length (ie 0x4000 bytes) (16KB) The address and length must both be multiples of the SPI flash erase sector size. This is 0x1000 (4096) bytes for supported flash chips. 
<p align="center">
  <img  src="\Screenshots\memo.png">
</p>


### Convert ELF to Binary  ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico)

Converts an ELF file into the binary executable images which can be flashed and then booted into the chip. This command does not require a serial connection. 
<p align="center">
  <img  src="\Screenshots\settings.png">
</p>

### Output bin image details  ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico)

The image info outputs some information (load addresses, sizes, etc) about a .bin file. 


### Verify flash  ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico)

Allows you to verify that data in flash matches a local file. Additional verification is not usually needed. However, if you wish to perform a byte-by-byte verification of the flash contents then you can do so with this feature. 
<p align="center">
  <img  src="\Screenshots\advmod.png">
</p>

### Dump Memory  ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico)

Will dump a region from the chip's memory space to a file. 


### load RAM  ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico)

Allows the loading of an executable binary image directly into RAM, and then immediately executes the program contained within it.The binary image must only contain IRAM- and DRAM-resident segments. Any SPI flash mapped segments will not load correctly and the image will probably crash. The image info can be used to check the binary image contents. 


### Read / write Memory  ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico)

The read & write Memory allow reading and writing single words (4 bytes) of RAM. This can be used to "peek" and "poke" at registers. 


### Read flash status  ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico)

Intended for use when debugging hardware flash chip-related problems. It allows sending a RDSR, RDSR2 and/or RDSR3 command to the flash chip to read the status register contents. This can be used to check write protection status.
The bytes number determines how many status register bytes are read:

- bytes 1 sends the most common RDSR command (05h) and returns a single byte of status. 
- bytes 2 sends both RDSR (05h) and RDSR2 (35h), reads one byte of status from each, and returns a two byte status. 
- bytes 3 sends RDSR (05h), RDSR2 (35h), and RDSR3 (15h), reads one byte of status from each, and returns a 3 byte status. 


### Write flash status  ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico)

Intended for use when debugging hardware flash chip-related problems. It allows sending WRSR, WRSR2 and/or WRSR3 commands to the flash chip to write the status register contents. This can be used to clear write protection bits. The bytes option is similar to the corresponding option for read flash status and causes a mix of WRSR (01h), WRSR2 (31h), and WRSR3 (11h) commands to be sent to the chip. If bytes 2 is used then WRSR is sent first with a 16-bit argument and then with an 8-bit argument. Otherwise, each command is accompanied by 8-bits of the new status register value. 


### Chip Id  ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico)

Allows you to read a 4 byte ID which forms part of the MAC address.

### Secure Packaging  ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico)
This Option allows you to select firmware files you wish to work with more than once or in multiple enviroments then compress them inside a package with the extension .mtool along with the necessary settings and options for the flashing procedure in the production mode.
### Efuse Table  ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico)
The efuse tab introduced in flash makes it easier to display and burn any efuse without having to go through a long summary in a terminal. Also having as a simple security layer , a dialog that prevents you from making any unwanted burn operation, makes it safer than the traditional ways.
<p align="center">
  <img  src="\Screenshots\efusetab.png">
</p>

### Export Efuse  ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico)
You can now export the efuse table with all the values and states to an excel (xls) file.

# Dependencies  ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico)
---
flash uses a number of open source projects and libraries to work properly:

* [Python ]- https://www.python.org/
* [PyQt5] - https://pypi.org/project/PyQt5/
* [esptool] - https://github.com/espressif/esptool (@[espressif](https://github.com/espressif
)) (@[projectgus](https://github.com/projectgus/))    (@[themadinventor](https://github.com/themadinventor/))
# Download  ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico)
---
flash itself is open source with a [public repository][flash1.0] on GitHub.You can also download the first release from the [this link ](https://github.com/Gueni/flash1.0/releases).

Or simply by cloning the repository to your machine : 

      git clone https://github.com/Gueni/flash1.0.git

# Installation  ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico)
---
flash requires [Python 3](https://www.python.org/download/releases/3.0/) to run.

Install python 3 from https://www.python.org/download/releases/3.0/

Install PyQt5 from https://pypi.org/project/PyQt5/ 

        pip install pyqt5
        
# How to launch  ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico)

        python3 main.py
or simply download the latest release : [![GitHub release](https://img.shields.io/github/release/johnDoe/Library.svg)](https://github.com/Gueni/flash/releases/latest)

# To do  ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico)
----

 - Optimize the Efuse feature.
 - Enhance UI/UX.
 - More Interactive Help Section.
 - Secure Boot Feature.
 - A dedicated Firmware merge library for ESP32.
 - more file type choices for efuse export.

# Copyright and Licensing  ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico)
-----

   Copyright 2019 by [Mohamed Gueni](https://github.com/Gueni)

    Licensed under the GNU General Public License License, Version 2.0
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at GNU .

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

###### [FAQ :Feel free to submit issues and enhancement requests.](https://github.com/Gueni/flash1.0/issues)



[//]:<These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO- >


   [flash1.0]: <https://github.com/Gueni/flash1.0/tree/1.0>
   [GNU]:<https://github.com/Gueni/flash1.0/releases>
  
