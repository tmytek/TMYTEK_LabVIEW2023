import argparse
from enum import Enum, auto, Flag
import ft4222
from ft4222.SPI import Cpha, Cpol
from ft4222.SPIMaster import Mode, Clock, SlaveSelect

import ft4222.GPIO as GPIO
import json
from pathlib import Path

"""
FT4222 SPI data transfer as a submodule
"""
def version():
    return "1.0.2"

class RWType(Flag):
    WRITE_ONLY = 1
    WRITE_READ = 2
    WRITE_TWICE_READ = WRITE_ONLY | WRITE_READ

def initialize_ft4222(LDB_en=False):
    """
    Initialize FT4222

    Args:
        LDB_en (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: devA and devB
    """
    try:
        devA = None
        devB = None

        nbDev = ft4222.createDeviceInfoList()
        if nbDev == 0:
            raise Exception("Empty device info, please check FTDI connected or cable is workable for data transmission")
        for i in range(nbDev):
            info = ft4222.getDeviceInfoDetail(i, False)
            desc = info['description'].decode().strip()
            print(f"Scanned: {i} -> {desc}")

            if "A" in desc or "UDM0620" in desc:
                #print("Attempting to open 'FT4222 A' device...")
                devA = ft4222.openByDescription(desc)#'FT4222 A'
                #print("'FT4222 A' device opened")
                print("Initializing SPI master device...")
                # Sys clock: CLK_60 = 60MHz, then SPI clock = 60/8 = 7.5MHz
                # print(devA.getClock())
                devA.spiMaster_Init(Mode.SINGLE, Clock.DIV_8, Cpol.IDLE_LOW, Cpha.CLK_LEADING, SlaveSelect.SS0)
                devA.setTimeouts(500, 500)
                print("SPI master device initialized")
            elif "B" in desc:
                #print("Attempting to open 'FT4222 B' device...")
                devB = ft4222.openByDescription(desc)
                #print("'FT4222 B' device opened")

        if LDB_en:
            print("Initializing GPIO(LDB pin) ...")
            # GPIO 0, 1 can not control gpio, maybe due to occupied by i2C
            # real pin 0~3 are 4th~7th from JP4.
            devB.gpio_Init(gpio0=GPIO.Dir.OUTPUT,
                           gpio1=GPIO.Dir.OUTPUT,
                           gpio2=GPIO.Dir.OUTPUT,
                           gpio3=GPIO.Dir.OUTPUT)
            print("GPIO initialization complete")

        return devA, devB
    except Exception as e:
        print(f"Error during FT4222 initialization: {e}")
        return None, None

def spi_transfer(devA, devB, data, rw_type=RWType.WRITE_TWICE_READ, LDB_en=False):
    """
    SPI data transfer (read/write mode, supports custom read length)

    Args:
        devA (_type_): _description_
        devB (_type_): _description_
        data (_type_): _description_
        LDB_en (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    # Print the SPI data to be sent
    formatted_data = ' '.join(f'{byte:02X}' for byte in data)
    print(f"SPI_W: {formatted_data}")
    try:
        # Ensure the input data is of type bytes
        if not isinstance(data, (bytes, bytearray)):
            data = bytes(data)

        # SPI transfer (write-only)
        if rw_type.__contains__(RWType.WRITE_ONLY):
            devA.spiMaster_SingleWrite(data, True)

        # SPI transfer (write and read simultaneously)
        recv_data_2 = bytearray(len(data))
        if rw_type.__contains__(RWType.WRITE_READ):
            recv_data_2 = devA.spiMaster_SingleReadWrite(data, True)

            # Print the received data in hexadecimal format after the second transfer
            formatted_recv_data = ' '.join(f'{byte:02X}' for byte in recv_data_2)
            print(f"SPI_R: {formatted_recv_data}")

        if LDB_en:
            devB.gpio_Write(GPIO.Port.P0, False)
            devB.gpio_Write(GPIO.Port.P0, True)

        # Return the received data from the second transfer
        return recv_data_2

    except Exception as e:
        print(f"Error during SPI transfer: {e}")
        return None

# Close FT4222
def close_ft4222(devA, devB):
    try:
        if devA:
            devA.close()
        if devB:
            devB.close()
        print("FT4222 devices successfully closed")
    except Exception as e:
        print(f"Error closing FT4222: {e}")

def cmd_prompt(devA, devB, fs, LDB_en=False):
    """
    CMD Prompt interface, reads commands from JSON

    Args:
        devA (_type_): _description_
        devB (_type_): _description_
        LDB_en (_type_): _description_
        fs (_type_): _description_
    """
    if isinstance(fs, (bytes, bytearray)):
        spi_transfer(devA, devB, fs, LDB_en)
        return

    commands = {}
    extension = "".join(Path(fs).suffixes)
    print(extension)
    if extension == ".json":
        # Read the command configuration file with UTF-8 encoding
        with open(fs, 'r', encoding='utf-8') as f:
            commands = json.load(f)['commands']
    elif extension == ".bin":
        with open(fs, 'rb') as f:
            data_to_send = f.read()
        spi_transfer(devA, devB, data_to_send, LDB_en)
        close_ft4222(devA, devB)
        return

    while True:
        print("\nCommand options:")
        for i, (cmd_name, cmd_info) in enumerate(commands.items(), 1):
            print(f"{i}. {cmd_info['description']}")

        print(f"{len(commands) + 1}. Exit program")

        cmd = input("Please enter command number: ").strip()

        # Validate if the input is a valid command
        if cmd.isdigit():
            cmd_index = int(cmd)
            if 1 <= cmd_index <= len(commands):
                # Select the corresponding command based on input
                cmd_name = list(commands.keys())[cmd_index - 1]
                cmd_info = commands[cmd_name]

                # Convert the hexadecimal string to bytes
                data_to_send = bytes(int(byte, 16) for byte in cmd_info['data'])

                # Call SPI transfer function and read the specified length of data
                spi_transfer(devA, devB, data_to_send, LDB_en)

            elif cmd_index == len(commands) + 1:
                print("Exiting program...")
                close_ft4222(devA, devB)
                break
            else:
                print("Invalid command, please try again.")
        else:
            print("Invalid input, please enter a number.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ldb", help="LDB enable", type=bool, default=False)
    parser.add_argument("--file", help="File path, support bin/json", type=str, default="commands.json")
    parser.add_argument("--ver", help="Get the version", action='version', version='%(prog)s: v'+version())
    args = parser.parse_args()

    try:
        # Initialize FT4222 devices
        devA, devB = initialize_ft4222(args.ldb)

        if devA and devB:
            # Start command line prompt
            cmd_prompt(devA, devB, args.file, args.ldb)
        else:
            print("Unable to initialize FT4222 devices, exiting program.")

    except Exception as e:
        print(f"Error occurred: {e}")

    # input("Press Enter to exit...")
