# gzdl.py

Command Line Downloader for Motorola/Freescale/NXP MC68HC908GZ60

## Terminology

## Terminology

### Monitor loader

Monitor loader is a PC side software which can update program memory of an
empty (virgin) microcontroller.
Disadvantages are it needs special hardware interface and it is slow.
My one is available
[here](https://github.com/butyi/gzml.py/) in Python language, or
[here](https://github.com/butyi/gzml.c/) in C language.
I propose the Python one.

### Bootloader

Bootloader is software embedded in the microcontroller, which can receive data
from a hardware interface and write it into its own program memory.
This software needs to be programmed into the microcontroller only once by a
monitor loader. 
My one is available 
[here](https://github.com/butyi/gzbl/).

### Downloader

Downloader is PC side software. The communication partner of Bootloader.
It can send the pre-compiled software (or any other data) to data to
microcontroller through the supported hardware interface.
My one is available
[here](https://github.com/butyi/gzdl.py/) in Python language, or
[here](https://github.com/butyi/gzdl.c/) in C language.
I propose the Python one.

### Application

Application is the real software for the main purpose. It is easier if you
start your application software from an application template.
Application template is a sample software which initializes and uses almost
all modules of microcontroller for some basic purpose. You can download into
uC and it already works and does something. You just need to modify it for your 
purpose. 
My one is available 
[here](https://github.com/butyi/gzat/).

## What is this?

This is the Downloader for GZ series microcontroller.

I have written the same in C [See here](https://github.com/butyi/gzdl.c/), which works only on Linux. 
But this Python one works on any platform (Windows, Linux, OS X).

## Hardware

To be HW interface easy and cheap, buy TTL USB-Serial interface from China.
I use FT232RL FTDI USB to TTL Serial Adapter Module for communication. This is supported by both Linux and Windows 10.
With this you do not need voltage level converter (MAX232) on microcontroller side hardware, you just need some cable and that's it.

More details about hardware is [here.](https://github.com/butyi/gzml.py/)

## How get use gzdl.py?

The software was developed on my Ubuntu Linux 18.04 LTS.
- Open a terminal
- First check out files into a folder `git init` , `git clone https://github.com/butyi/gzdl.py.git`.
- You maybe need to add your user to group of RS232 device in case of permission denied. In my case `sudo gpasswd --add ${USER} dialout`. After this command, you need to log out and in to effect the change.
- You maybe need to install some Python modules. See my comments around imports in file `gzdl.py`.
- Give executable flag `chmod +x gzdl.py`

## How to use gzdl.py?
`./gzdl.py -h`

Print out help about version, command line options, tipical usages. 

`./gzdl.py -b 57600 -t`

Open a serial terminal with defined baud rate.

`./gzdl.py -b 57600 -f ~/prg.s19 -m`

Download file prg.s19 from home folder with defined baud rate and memory mirror file `gzdl.mem` will be created.

`./gzdl.py -b 57600 -f ~/prg.s19 -m -t`

Same as before but after successfull download it remains in terminal mode.

Note: on Windows you do not need the first `./` characters.

## Further Development

If you only improve PC (client) side features, just 
- Edit gzdl.py 
- Enjoy it.

Some improvements need to be implemented on both PC (client) side and uC (server) side software. Feel free to do it.

## Baud rate

Baud rate depends on the bootloader. Download is only possible if defined baud rate is same as implemented in the bootloader.
Refer bootloader code [here](https://github.com/butyi/gzbl/).

## Supported interfaces

- Motherboard mounted ttyS0
- USB Serial interface ttyUSB0 
  ( E.g. [FT231XS](https://www.ftdichip.com/Support/Documents/DataSheets/Cables/DS_Chipi-X.pdf) and
    [ATEN UC232A1](https://www.aten.com/global/en/products/usb-&-thunderbolt/usb-converters/uc232a1/) ) 

## Supported Operation Systems

I have tested download and terminal on both Linux (Ubuntu 18.04.4 LTS) and Windows 10.
I could not test on OS X because I don't have.

## License

This is free. You can do anything you want with it.
While I am using Linux, I've got so many support from free projects, now I am happy if I can help for the community.

### Keywords

Motorola, Freescale, NXP, MC68HC908GZ60, 68HC908GZ60, HC908GZ60, MC908GZ60, 908GZ60, HC908GZ48, HC908GZ32, HC908GZ16, HC908GZ, 908GZ

###### 2020 Janos Bencsik



