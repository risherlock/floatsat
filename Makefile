#########################
#  BASIC CONFIGURATION  #
#########################

# OS: Linux, Windows
OS = Linux

# Project name
TARGET = main

# Build path
BUILD_DIR = build

# Path to openocde for Linux
RULE_FILE = 60-openocd.rules
RULE_PATH = assets/$(RULE_FILE)
RULE_DEST = /etc/udev/rules.d/$(RULE_FILE)

# Will you debug?
DEBUG = 1

# C++ source files
CXX_SOURCES = \
libs/lsm9ds1/lsm9ds1.cpp \
$(main)

# C source files
C_SOURCES = \

# C/C++ include folders
C_INCLUDES =  \
-I"rodos/src/bare-metal/stm32f4/CMSIS/Device/ST/STM32F4xx/Include" \
-I"rodos/src/bare-metal/stm32f4/STM32F4xx_StdPeriph_Driver/inc"  \
-I"rodos/src/bare-metal/stm32f4/platform-parameter/discovery" \
-I"rodos/src/bare-metal/stm32f4/CMSIS/Include" \
-I"rodos/src/bare-metal/stm32f4/sdCard" \
-I"rodos/src/bare-metal/stm32f4/hal" \
-I"rodos/src/bare-metal/stm32f4" \
-I"rodos/src/bare-metal-generic" \
-I"rodos/src/independent/gateway" \
-I"rodos/support/support-libs" \
-I"rodos/src/independent" \
-I"rodos/default_usr_configs" \
-I"rodos/api/hal" \
-I"rodos/api" \
-I"libs/lsm9ds1"

# C/C++ defines
C_DEFS =  \
-DUSE_STM32_DISCOVERY \
-DSTM32F40_41xxx \
-DUART_DEBUG_IDX

# Asemply source files
ASM_SOURCES = \

# Asembly include files
ASM_INCLUDES = \

# Assembly defines
AS_DEFS = \

############################
#  ADVANCED CONFIGURATION  #
############################

# STM32 flags and toolchain
CPU = -mcpu=cortex-m4
FPU = -mfpu=fpv4-sp-d16
FLOAT-ABI = -mfloat-abi=soft
MCU = $(CPU) -mthumb $(FPU) $(FLOAT-ABI)
OPTIMIZE = -O0 -fmessage-length=0 -fsigned-char -ffunction-sections -fdata-sections
PREFIX = arm-none-eabi-

ifdef GCC_PATH
	CC = $(GCC_PATH)/$(PREFIX)gcc
	AS = $(GCC_PATH)/$(PREFIX)gcc -x assembler-with-cpp
	CP = $(GCC_PATH)/$(PREFIX)objcopy
	SZ = $(GCC_PATH)/$(PREFIX)size
	CXX = $(GCC_PATH)/arm-none-eabi-g++
else
	CC = $(PREFIX)gcc
	AS = $(PREFIX)gcc -x assembler-with-cpp
	CP = $(PREFIX)objcopy
	SZ = $(PREFIX)size
	CXX = arm-none-eabi-g++
endif

# Link script
LDSCRIPT = "rodos/src/bare-metal/stm32f4/scripts/stm32_flash.ld"

# Static libraries
LIBS = -lm -lrodos
LIBDIR = -L"rodos/build"

HEX = $(CP) -O ihex
BIN = $(CP) -O binary -S

ASFLAGS = $(MCU) $(AS_DEFS) $(ASM_INCLUDES) $(OPTIMIZE) -Wall -fdata-sections -ffunction-sections
CFLAGS = $(MCU) $(C_DEFS) $(C_INCLUDES) $(OPTIMIZE) -Wall -fdata-sections -ffunction-sections -fdebug-prefix-map="$(PWD)"=.

ifeq ($(DEBUG), 1)
	CFLAGS += -g -gdwarf-2
endif

CFLAGS += -MMD -MP -MF"$(@:%.o=%.d)"
CXXFLAGS=$(CFLAGS)
CXXFLAGS+=-fno-rtti -fno-exceptions
CXXFLAGS+=-std=c++11
CXXFLAGS+=-U__STRICT_ANSI__
LDFLAGS = $(MCU) -specs=nano.specs -T$(LDSCRIPT) -nostartfiles -nodefaultlibs -nostdlib -Xlinker --gc-sections \
$(LIBDIR) $(LIBS) -Wl,-Map=$(BUILD_DIR)/$(TARGET).map,--cref -Wl,--gc-sections

#######################
#  CROSS COMPILATION  #
#######################

# Default action
all: clean $(BUILD_DIR)/$(TARGET).elf $(BUILD_DIR)/$(TARGET).hex $(BUILD_DIR)/$(TARGET).bin

# List of C, ASM, and C++ objects
OBJECTS = $(addprefix $(BUILD_DIR)/,$(notdir $(C_SOURCES:.c=.o)))
vpath %.c $(sort $(dir $(C_SOURCES)))
OBJECTS += $(addprefix $(BUILD_DIR)/,$(notdir $(ASM_SOURCES:.s=.o)))
vpath %.s $(sort $(dir $(ASM_SOURCES)))
OBJECTS += $(addprefix $(BUILD_DIR)/,$(notdir $(CXX_SOURCES:.cpp=.o)))
vpath %.cpp $(sort $(dir $(CXX_SOURCES)))

$(BUILD_DIR)/%.o: %.c Makefile | $(BUILD_DIR)
	$(CC) -c $(CFLAGS) -Wa,-a,-ad,-alms=$(BUILD_DIR)/$(notdir $(<:.c=.lst)) $< -o $@

$(BUILD_DIR)/%.o: %.s Makefile | $(BUILD_DIR)
	$(AS) -c $(CFLAGS) $< -o $@

$(BUILD_DIR)/%.o: %.cpp Makefile | $(BUILD_DIR)
	$(CXX) -c $(CXXFLAGS) -Wa,-a,-ad,-alms=$(BUILD_DIR)/$(notdir $(<:.cpp=.lst)) $< -o $@

$(BUILD_DIR)/$(TARGET).elf: $(OBJECTS) Makefile
	$(CXX) $(OBJECTS) $(LDFLAGS) -o $@
	$(SZ) $@

$(BUILD_DIR)/%.hex: $(BUILD_DIR)/%.elf | $(BUILD_DIR)
	$(HEX) $< $@

$(BUILD_DIR)/%.bin: $(BUILD_DIR)/%.elf | $(BUILD_DIR)
	$(BIN) $< $@

$(BUILD_DIR):
	mkdir $@

#######################
#  UTILITY FUNCTIONS  #
#######################

# Linux
ifeq ($(OS), Linux)
clean:
	rm -r $(BUILD_DIR) || true

rodos: clean
	git clone https://gitlab.com/rodos/rodos.git rodos || true
	rm -r rodos/build/CMakeFiles || true
	rm -r rodos/build/test-suite || true
	rm rodos/build/* || true
	cmake -Srodos -Brodos/build -DCMAKE_TOOLCHAIN_FILE=cmake/port/discovery.cmake
	make -C rodos/build

udev:
	sudo cp $(RULE_PATH) $(RULE_DEST)
	sudo chmod 644 $(RULE_DEST)
	sudo udevadm control --reload
	sudo udevadm trigger
endif

# Windows
ifeq ($(OS), Windows)
clean:
	if exist $(BUILD_DIR) rmdir /s/q $(BUILD_DIR)

rodos: clean
	if not exist "rodos" git clone https://gitlab.com/rodos/rodos.git
	if exist "rodos/build" rmdir /s/q "rodos/build"
	cmake -Srodos -Brodos/build -G "MinGW Makefiles" -DCMAKE_TOOLCHAIN_FILE=cmake/port/discovery.cmake
	make -C rodos/build
endif

flash: all
	openocd -f interface/stlink.cfg -f target/stm32f4x.cfg -c "program $(BUILD_DIR)/$(TARGET).hex verify reset exit"
