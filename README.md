# FloatSat

Software templates for *FloatSat Praktikum* at *Julius-Maximilians-Universität Würzburg*.

The purpose of these instructions is to help you get started with RODOS on both Windows and Linux for FloatSat. This work is carried out at the *FloatSat lab* under the supervision of Atheel Redah and Muhammad Faisal.

## Table of contents

1. [Setting up for STM32 programming.](#setting-up-for-stm32-programming)
    - [Linux](#linux)
    - [Windows](#windows)
1. [First project: Hello blinky](#first-project-hello-blinky)
1. [Basic RODOS examples](#basic-rodos-examples)
1. [How to setup a new project?](#how-to-setup-a-new-project)
1. [Debugging](#debugging)
1. [Python middleware for ground station](#python-middleware-for-ground-station)
1. [Caution!](#caution)
1. [Contact](#contact)

## Setting up for STM32 programming

We need following tools/software for embedded software development for FloatSat.

1. A tool with command terminal to write the C++ software  like VSCode.
2. GNU Arm Embedded Toolchain for cross-compilation.
3. Make and CMake to automate compile and flash process.
4. A software for flash & debug like OpenOCD.
5. Serial terminal for virtual port like Arduino IDE (serial terminal), Hterm, PuTTY etc.
6. Git for automatic clone and installation of [RODOS](https://gitlab.com/rodos) by [Makefile](Makefile).

Following sections guides you through the installation of these dependencies on your computer for [Linux](#linux) and [Windows](#windows).

### Linux

Followings are the commands to install above mentioned softwares. Before any of that, please make sure to update your system with the command ```sudo apt upgrade``` and ```sudo apt update```.

1. VS Code: ```sudo snap install code```
2. GNU Toolchain: ```sudo apt-get install gcc-arm-none-eabi gdb-multiarch```
3. OpenOCD:
```
git clone https://github.com/openocd-org/openocd.git
cd openocd
./bootstrap
./configure
make
sudo make install
```
4. HTerm: https://www.der-hammer.info/pages/terminal.html

### Windows

Following are the links to Windows installer for the different dependencies.

1. VS Code: https://code.visualstudio.com/docs/?dv=win64user
2. GNU Toolchain [win32.exe]: https://developer.arm.com/downloads/-/gnu-rm
3. Make installer: https://gnuwin32.sourceforge.net/downlinks/make.php
4. CMake [Windows x64 Installer] : https://cmake.org/download/
5. OpenOCD: https://gnutoolchains.com/arm-eabi/openocd/
6. HTerm: https://www.der-hammer.info/pages/terminal.html
7. Git: https://git-scm.com/downloads/win

**Note:** For both Linux and Windows, make sure that the installation in successful simply by checking the version of software in command prompt.

1. Make: ```make --version```
2. CMake: ```cmake --version```
3. Toolchain: ```arm-none-eabi-gcc --version```
4. OpenOCD: ```openocd --version```
5. Git: ```git --version```

**Note:** For Windows, if the installation is successful but the version check fails, please add the software's ```bin``` directory to the global PATH environment variable. For example: ```C:\Program Files\GnuWin32\bin``` for ```make```.

## First project: Hello blinky

Now that everything is setup, we are ready to flash our first software; ```hello_blinky.cpp```. Please follow following steps.

1. Clone or download the [repository](https://github.com/risherlock/FloatSat).
2. Open the folder ```FloatSat``` from VSCode via ```File - Open Folder``` on the toolbar.
3. Select your operating system on ```Makefile``` by setting ```OS``` variable. Only Linux and Windows is supported as of now.
4. Open the terminal of the VSCode with ```View - Terminal``` on the toolbar.
5. Clone and compile RODOS using the command: ```make rodos```
6. Compile an example with command: ```make main=hello_blinky.cpp```
7. Compile and flash example with command: ```make flash main=hello_blinky.cpp```
8. Enjoy the serenity of blinking LEDs!

[Here](https://youtu.be/kRnWll_0JtY) is a video demonstrating the example.

## Basic RODOS examples

Official RODOS repository contains a whole bunch of examples which can be found [here](https://gitlab.com/rodos/rodos/-/tree/master/tutorials). However, we have selected some basic examples to help you get started with RODOS for FloatSat.

1. [hello_blinky.cpp](hello_blinky.cpp) - Flashes four LEDs onboard the Discovery board.
3. [hello_world.cpp](hello_world.cpp) - Continuously prints ```Hello World!\n```  via UART port.
4. [hello_topic.cpp](hello_topic.cpp) - Inter-thread communication between two threads using a topic. Transmitter thread publishes the topic with increment of values every 5 seconds and the receiver thread subscribes to the topic once a second.
5. [hello_debug](hello_debug.cpp) - Computes the Fibonacci sequence but does not print any output. The goal is to track the values of the variables using onboard STLINK debugger with OpenOCD.

**Note:** ```PRINTF``` will not work if you do not do [this](#virtual-com-port-configuration).

[Here](https://youtu.be/kRnWll_0JtY) is a video demonstrating the ```hello_blinky.cpp``` and ```hello_world.cpp```.

## How to setup a new project?

Allow me to make a deduction, if I may? I know what you are thinking right now: *so far, these instructions have only shown us how to run a single example file. What if I need to add different header and .cpp files? How do I create a project with my own folder structure?*

I’m glad you asked! Here is a solution using the following imaginary folder structure.

```
|.
├── libs
│   ├── devices
│   │   ├── imu.h
│   │   ├── imu.cpp
│   │   ├── encoder.h
│   │   └── encoder.cpp
│   └── algorithms
│       ├── pid.h
│       └── pid.cpp
│       └── ekf.h
│       └── ekf.cpp
```

All you need to do is add the path of directory that contains ```.h``` files under ```C_INCLUDES``` and all the ```.cpp``` files under ```CXX_SOURCES``` in [Makefile](Makefile). The configuration for above imaginary scenario would look something like this.

```Makefile
CXX_SOURCES = \
libs/devices/imu.cpp \
libs/devices/encoder.cpp \
libs/algorithms/pid.cpp \
libs/algorithms/ekf.cpp

C_INCLUDES =  \
-I"rodos/api" \
-I"libs/devices" \
-I"libs/algorithm"
```

**Note:** It should be noted that have just included ```-I"rodos/api" \``` and ignored other directories inside ```rodos``` in ```C_INCLUDES``` just to save space. Please do not remove others from your Makefile.

**Note:** ```$(main)``` under ```CXX_SOURCES``` is the reason why we could compile the specific example using command ```make main=hello_blinky.cpp```. This can be removed altogether when setting up your project in which case the commands simplifies to

1. Compilation: ```make```
2. Compilation and flash: ```make flash```

## Debugging

We will be using an extension called [Cortex Debug](https://github.com/Marus/cortex-debug) in order to facilitate debugging.

Go to the ```Extensions``` on the vertical bar at the left hand side of the VSCode and search for ```Cortex-Debug``` by [marus25](https://github.com/Marus). Flash the software and press ```F5``` to start debugging.

Please watch this [video](https://youtu.be/FC7BE-yrDFg) for the demonstration of debugging.

### Python middleware for ground station

RODOS has [Python middleware ](rodos/support/support-programs/middleware-python) that allows communication between Python on computer and RODOS on STM32 using gateways such as UART (using bluetooth module) or UDP (using WiFi module). [This pdf](rodos/support/support-programs/middleware-python/readme.pdf) has instruction on how to install the middleware. There are some [examples](rodos/support/support-programs/middleware-python/examples/) on the RODOS repository, but again, we have included software to get started. It should be a good starting point to develop ground station.

1. [hello_python.cpp](hello_python.cpp) - Publishes data using RODOS topic via UART gateway (with bluetooth module) to Python. It also receives three axis sensor data from Python middleware and prints it on virtual COM port.
2. [python_rxtx.py](python_rxtx.py) - Receives topic published by RODOS and transmits the data by packing it into ```struct``` that is understood by RODOS.

<p align="center">
  <img src="docs/20241001_174229.jpg" width="350">
</p>

Figure: Setup to test communication with Python middleware. The middleware communicates with RODOS using bluetooth module connected to ```UART_IDX2``` (Tx: PD5 and Rx: PD6).

## Caution!

### Virtual COM port configuration

In the Discovery boards provided in the lab, virtual COM ports have been enabled by connecting PD8 and PD9 (UART3) to the STLINK. You may notice a pair of fine enameled wires on your board or in the figure above. The virtual COM port allows us to print messages using the UART protocol via the STLINK USB port onboard the STM32, without the need for any USB-TTL modules.

However, RODOS configures UART2 by default. Therefore we should configure the appropriate UART port by uncommenting the corresponding ```UART_DEBUG``` in ```platform-parameter.h``` for the target device. For Discovery board, [this](rodos/src/bare-metal/stm32f4/platform-parameter/discovery/platform-parameter.h) is the file.

```C
#define UART_DEBUG UART_IDX3, GPIO_056, GPIO_057
```

Do not forget to recompile RODOS with ```make rodos``` after the configuration.

### Links not working

There are various links in this README that directs to files and folders inside the repository of RODOS. They will only work once you clone the repository using ```make rodos``` or simply ```git clone https://gitlab.com/rodos/rodos.git```.

## Contact

If you find any issues with the content of this repository (such as dead hyperlinks) or would like to make improvements, please feel free to either create a GitHub issue or submit a pull request. I highly encourage you to reach out if you need any assistance or guidance on RODOS, or for any other questions related to firmware development for FloatSat. My email is metrictensor221b@gmail.com.

<div align="right">
  - Rishav
</div>

<div align="center">
  Happy coding!
</div>
