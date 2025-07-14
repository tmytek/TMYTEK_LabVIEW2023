from myftdi.spi_gpio.ftdi_spi_sender import *

def jio_ver(devA, devB):
    return f"FTDI: v{ftdi_ver()}, FPGA: v{fpga_ver(devA, devB)}"

def ftdi_ver():
    return "1.3.7"

def fpga_ver(devA, devB):
    cmd_bytes = [0xFF, 0x00]
    pattern = bytearray(cmd_bytes)
    spi_transfer(devA, devB, pattern, RWType.WRITE_ONLY)

    # SPARE
    res_size = 4
    spare_bytes = [ 0xFF for i in range(res_size)]
    pattern = bytearray(spare_bytes)
    ver_bytes = spi_transfer(devA, devB, pattern, RWType.WRITE_READ)

    ver_list = [ str(ver_bytes[i]) for i in range(res_size)]
    return '.'.join(ver_list)