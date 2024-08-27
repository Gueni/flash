<p align="center">
  <img  src="\Screenshots\espLogo.png.png"
</p>



----
![python3.x](https://img.shields.io/badge/python-3.x-brightgreen.svg)
[![Documentation Status](https://readthedocs.org/projects/ansicolortags/badge/?version=latest)](http://ansicolortags.readthedocs.io/?badge=latest)
[![GPLv3 license](https://img.shields.io/badge/License-GPLv3-blue.svg)](http://perso.crans.org/besson/LICENSE.html)
[![Open Source? Yes!](https://badgen.net/badge/Open%20Source%20%3F/Yes%21/blue?icon=github)](https://github.com/Naereen/badges/)

 

# ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico) Getting Started  
---
([flash 2.1](https://github.com/Gueni/flash/releases/tag/v2.1)) is a free software which allows the user to access, flash and erase the ESP32 and ESP8266 internal memory. Meanwhile , flash introduces the set of features mentioned in the sections below.

The software is divided into two major modes, production mode and advanced mode. The production mode is a simple user interface containing the minimum number of features allowing the operator to conduct the necessary flashing and or flash erasing procedures with minimum complexity and errors.The advanced mode on the other hand is more complex and sums up all the features and commands made possible with the esptool library but with an easier and more advanced user experience. 


#  ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico) Features  
---



### ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico) Serial Port  

The serial port is selected using the ComboBox Designated Serial Port, like COM1 (Windows). If no option is specified,esptool will enumerate all connected serial ports and try each one until it finds an Espressif device (ESP32 or ESP8266) connected. 
<p align="center">
  <img  src="\Screenshots\serialandbaud.png">
</p>

### ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico) Baud Rate  

The default baud rate is 115200bps. Different rates may be set using the Baud Rate ComboBox. This can speed up writing and reading flash operations.The baud rate is limited to 115200 when initial connection is established,higher speeds are only used for data transfers. Most hardware configurations will work with 230400, some with 460800, 921600 and/or 1500000 or higher.If you have connectivity problems then you can also set baud rates below 115200. You can also choose 74880, which is the usual baud rate used by the ESP8266 to output boot log information. 


### ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico) Flash Firmware/Bootloader  


Binary data (Multiple flash addresses and file)can be written to the ESP's flash chip. The chip selection is optional when writing to ESP flash, as it will be detected when it connects to the serial port.The offset (address) and file name are crucial for this operation.

The file names created by "ELF to Bin" include the flash offsets as part of the file name. For other types of images, consult your SDK documentation to determine the files to flash at which offsets.Numeric values passed as offset address can only
be specified in hex (ie 0x1000). 


### ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico) Setting Flash Mode and Size  

You may also need to specify flash mode and flash size, if you wish to override the defaults. 


### ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico) Compression  
By default, the serial transfered data is compressed by [esptool.py ](https://github.com/espressif/esptool) for better performance. 


### ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico) Read Flash Contents 

The Read flash feature allows reading back the contents of flash. for that you need to specify an address, a size, and a filename to dump the output to. 


### ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico) Erase Flash & erase region  



To erase the entire flash chip (all data replaced with 0xFF bytes) To erase a region of the flash, for example starting at an address (ie 0x20000)with a length (ie 0x4000 bytes) (16KB) The address and length must both be multiples of the SPI flash erase sector size. This is 0x1000 (4096) bytes for supported flash chips. 
<p align="center">
  <img  src="\Screenshots\memo.png">
</p>


### ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico) Convert ELF to Binary  

Converts an ELF file into the binary executable images which can be flashed and then booted into the chip. This command does not require a serial connection. 
<p align="center">
  <img  src="\Screenshots\settings.png">
</p>

### ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico) Output bin image details  

The image info outputs some information (load addresses, sizes, etc) about a .bin file. 


### ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico) Verify flash  

Allows you to verify that data in flash matches a local file. Additional verification is not usually needed. However, if you wish to perform a byte-by-byte verification of the flash contents then you can do so with this feature. 
<p align="center">
  <img  src="\Screenshots\advmod.png">
</p>

### ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico) Dump Memory  

Will dump a region from the chip's memory space to a file. 


### ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico) load RAM  

Allows the loading of an executable binary image directly into RAM, and then immediately executes the program contained within it.The binary image must only contain IRAM- and DRAM-resident segments. Any SPI flash mapped segments will not load correctly and the image will probably crash. The image info can be used to check the binary image contents. 


### ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico) Read / write Memory  

The read & write Memory allow reading and writing single words (4 bytes) of RAM. This can be used to "peek" and "poke" at registers. 


### ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico) Read flash status  

Intended for use when debugging hardware flash chip-related problems. It allows sending a RDSR, RDSR2 and/or RDSR3 command to the flash chip to read the status register contents. This can be used to check write protection status.
The bytes number determines how many status register bytes are read:

- bytes 1 sends the most common RDSR command (05h) and returns a single byte of status. 
- bytes 2 sends both RDSR (05h) and RDSR2 (35h), reads one byte of status from each, and returns a two byte status. 
- bytes 3 sends RDSR (05h), RDSR2 (35h), and RDSR3 (15h), reads one byte of status from each, and returns a 3 byte status. 


### ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico) Write flash status  

Intended for use when debugging hardware flash chip-related problems. It allows sending WRSR, WRSR2 and/or WRSR3 commands to the flash chip to write the status register contents. This can be used to clear write protection bits. The bytes option is similar to the corresponding option for read flash status and causes a mix of WRSR (01h), WRSR2 (31h), and WRSR3 (11h) commands to be sent to the chip. If bytes 2 is used then WRSR is sent first with a 16-bit argument and then with an 8-bit argument. Otherwise, each command is accompanied by 8-bits of the new status register value. 


### ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico) Chip Id 

Allows you to read a 4 byte ID which forms part of the MAC address.

### ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico) Secure Packaging  
This Option allows you to select firmware files you wish to work with more than once or in multiple enviroments then compress them inside a package with the extension .mtool along with the necessary settings and options for the flashing procedure in the production mode.
### ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico) Efuse Table  
The efuse tab introduced in flash makes it easier to display and burn any efuse without having to go through a long summary in a terminal. Also having as a simple security layer , a dialog that prevents you from making any unwanted burn operation, makes it safer than the traditional ways.
<p align="center">
  <img  src="\Screenshots\efusetab.png">
</p>

### ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico) Export Efuse  
You can now export the efuse table with all the values and states to an excel (xls) file.

# ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico) Dependencies  
---
flash uses a number of open source projects and libraries to work properly:

* [Python ]- https://www.python.org/
* [PyQt5] - https://pypi.org/project/PyQt5/
* [esptool] - https://github.com/espressif/esptool (@[espressif](https://github.com/espressif
)) (@[projectgus](https://github.com/projectgus/))    (@[themadinventor](https://github.com/themadinventor/))
# ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico) Download  
---
flash itself is open source with a [public repository][flash1.0] on GitHub.You can also download the LTS  ([release](https://github.com/Gueni/flash/releases/tag/v2.1)).

Or simply by cloning the repository to your machine : 

      git clone https://github.com/Gueni/flash.git

# ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico) Installation  
---
flash requires [Python 3](https://www.python.org/download/releases/3.0/) to run.

Install python 3 from https://www.python.org/download/releases/3.0/

Install PyQt5 from https://pypi.org/project/PyQt5/ 

        pip install pyqt5
        
# ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico) How to launch  

        python3 main.py
or simply download the latest release : ([Latest Release](https://github.com/Gueni/flash/releases/tag/v2.1))

# ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico) To do  

 - Optimize the Efuse feature.
 - Enhance UI/UX.
 - More Interactive Help Section.
 - Secure Boot Feature.
 - A dedicated Firmware merge library for ESP32.
 - more file type choices for efuse export.

# ![](https://github.com/Gueni/flash/blob/master/Theme/icons/GT.ico) Copyright and Licensing 
-----

Licensed under the GNU General Public License, Version 3.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at GNU.

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

###### [FAQ :Feel free to submit issues and enhancement requests.](https://github.com/Gueni/flash1.0/issues)



[//]:<These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO- >


   [flash1.0]: <https://github.com/Gueni/flash1.0/tree/1.0>
   [GNU]:<https://github.com/Gueni/flash1.0/releases>
  
