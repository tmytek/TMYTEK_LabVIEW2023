import argparse
import sys
from reg_tool import *
from jio_version import *
from myftdi.spi_gpio.ftdi_spi_sender import *

#header = [0xF0, 0x05]
header = [0xB5]
reg_addr = [0x00, 0x1E]
reg_data = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

def init_reg_table():
    """
    Init AWMF-0224 reg table format for check getting fields
    Format: 'addr' : (offset, size)
    """
    reg_addr_table[0x002] = {
                                'Description': "Mode_SEL, configures the mode of the hardware blocks for various signal paths",
                                'lshs_sel':
                                    {
                                        'offset': 0,
                                        'size': 1,
                                        'description': "Controls mixer: 0=Low Side LO, 1=High Side LO"
                                    },
                                'lo_src_sel':
                                    {
                                        'offset': 1,
                                        'size': 2,
                                        'description': "Selects the on-chip synthesizer, or an external source\r\n" +
                                                        "\t\t\t\t0: Internal Synthesizer is source, LO pin is unused\r\n" +
                                                        "\t\t\t\t1: Internal Synthesizer is source, and output on LO pin\r\n" +
                                                        "\t\t\t\t2: External LO is input on LO pin\r\n" +
                                                        "\t\t\t\t3: External LO is input, plus passthru to output (to feed to another IC"
                                    },
                                'lo_mult_sel':
                                    {
                                        'offset': 3,
                                        'size': 2,
                                        'description': "LO Frequency Multiplication: AWMF-0224: 0:x2, 1:x3 , 2:x4"
                                    },
                                'app_mode_def_ch2':
                                    {
                                        'offset': 5,
                                        'size': 3,
                                        'description': "Sets the Application Mode Definition for Channel 2 Up/Down Converter Block\r\n" +
                                                        "\t\t\t\t0 : Sleep, 1:Standby, 2: TDD, 3:TDD+FBRX, 4:LOFT Cal, 5:FDD, 6-7:Reserved"
                                    },
                                'app_mode_def_ch1':
                                    {
                                        'offset': 8,
                                        'size': 3,
                                        'description': "Sets the Application Mode Definition for Channel 1 Up/Down Converter Block\r\n" +
                                                        "\t\t\t\t0 : Sleep, 1:Standby, 2: TDD, 3:TDD+FBRX, 4:LOFT Cal, 5:FDD, 6-7:Reserved"
                                    },
                                'ic_mode':
                                    {
                                        'offset': 11,
                                        'size': 2,
                                        'description': "If ic_mode_ovrd_en=0: \r\n" +
                                                        "\t\t\t\t0:Sleep (RX_EN=1, TX_EN=1)\r\n" +
                                                        "\t\t\t\t1:Standby (RX_EN=0, TX_EN=0)\r\n" +
                                                        "\t\t\t\t2:Rx Mode (RX_EN=1,TX_EN=0)\r\n" +
                                                        "\t\t\t\t3:Tx Mode (RX_EN=0, TX_EN=1)\r\n" +
                                                        "\t\t\t\tIf ic_mode_ovrd_en=1: TX_EN, RX_EN pins are ignored"
                                    },
                                'ic_mode_ovrd_en':
                                    {
                                        'offset': 13,
                                        'size': 1,
                                        'description': "1 = enable software to change the current operating mode of the IC"
                                    }
                            }
    reg_addr_table[0x007] = {
                                'Description': "Configures LO hardware for best performance at a given band",
                                'lo_band_sel':
                                    {
                                        'offset': 10,
                                        'size': 10,
                                        'description': "Configures LO hardware for best performance at a given band\r\n" +
                                                        "\t\t\t\t0x3FF = 6   - 6.3 GHz\r\n" +
                                                        "\t\t\t\t0x3FB = 6.3 - 6.6 GHz\r\n" +
                                                        "\t\t\t\t0x35A = 6.6 - 7   GHz\r\n" +
                                                        "\t\t\t\t0x359 = 7   - 7.3 GHz\r\n" +
                                                        "\t\t\t\t0x356 = 7.3 - 7.7 GHz\r\n" +
                                                        "\t\t\t\t0x305 = 7.7 - 8.3 GHz\r\n" +
                                                        "\t\t\t\t0x200 = 8.3 - 8.6 GHz\r\n" +
                                                        "\t\t\t\t0x100 = 8.6 - 9   GHz"
                                    },
                            }
    reg_addr_table[0x01E] = {
                                'Description': "USER_ATT_TRX, 0.25dB/step",
                                'att_user_rx_ch1':
                                    {
                                        'offset': 0,
                                        'size': 8,
                                        'description': "Rx gain att step for CH1"
                                    },
                                'att_user_tx_ch1':
                                    {
                                        'offset': 8,
                                        'size': 8,
                                        'description': "Tx gain att step for CH1"
                                    },
                                'att_user_rx_ch2':
                                    {
                                        'offset': 16,
                                        'size': 8,
                                        'description': "Rx gain att step for CH2"
                                    },
                                'att_user_tx_ch2':
                                    {
                                        'offset': 24,
                                        'size': 8,
                                        'description': "Tx gain att step for CH2"
                                    },
                            }
    reg_addr_table[0x0300] = {
                                'Description': "Configuration and control signals for the on-chip PLL",
                                'pll_soft_rest':
                                    {
                                        'offset': 0,
                                        'size': 1,
                                        'description': "1=reset (self-clearing). \r\n" +
                                        "\t\t\t\tFor debug resets all programmable PLL registers and state machines to default value"
                                    },
                                'pll_en':
                                    {
                                        'offset': 1,
                                        'size': 2,
                                        'description': "Sets Power Mode of the PLL\r\n" +
                                                        "\t\t\t\t00 = Off (power-on default)\r\n" +
                                                        "\t\t\t\t01 = Warmup (go here for >5us after Off or Standby)\r\n" +
                                                        "\t\t\t\t10 = Standby (power saving nonoperational state)\r\n" +
                                                        "\t\t\t\t11 = On (PLL is active)"
                                    },
                                'vco_ct_en':
                                    {
                                        'offset': 3,
                                        'size': 1,
                                        'description': "Set to 1 to start coarse tuning operation. Self-clearing"
                                    },
                                'ct_linear_en':
                                    {
                                        'offset': 4,
                                        'size': 1,
                                        'description': "1 = enable linear (fine) tune hardwar"
                                    },
                                'ct_linear_auto_mode':
                                    {
                                        'offset': 5,
                                        'size': 1,
                                        'description': "1 = run linear (fine) tune automatically after coarse tune.\r\n" +
                                                        "\t\t\t\tNote ct_linear_en must be set to 1 to allow auto_mode"
                                    },
                                'pll_word_frac':
                                    {
                                        'offset': 8,
                                        'size': 24,
                                        'description': "Fractional part of PLL word. Divide by 2^24 to get fraction.\r\n" +
                                                        "\t\t\t\tNote this is before multiplication by lo_mult_sel[1:0].\r\n" +
                                                        "\t\t\t\tInternal namefracn_nfrac[23:0]"
                                    },
                                'pll_word_int':
                                    {
                                        'offset': 32,
                                        'size': 10,
                                        'description': "Integer part of PLL word. Note this is before multiplication by lo_mult_sel[1:0].\r\n" +
                                                        "\t\t\t\tInternal name fracn_nfrac[33:24]"
                                    },
                                'ref_div':
                                    {
                                        'offset': 44,
                                        'size': 3,
                                        'description': "Divides reference oscillator frequency Fref before it is applied to the PLL:\r\n" +
                                                        "\t\t\t\t1 = divide by 1\r\n" +
                                                        "\t\t\t\t2 = divide by 2\r\n" +
                                                        "\t\t\t\t4 = divide by 4\r\n"
                                    },
                            }
    reg_addr_table[0x0301] = {
                                'Description': "PLL Status",
                                'lpf_ld_out':
                                    {
                                        'offset': 3,
                                        'size': 2,
                                        'description': "1: lock"
                                    },
                                'ct_done':
                                    {
                                        'offset': 0,
                                        'size': 1,
                                        'description': "coarse tune done"
                                    }
                            }
    reg_addr_table[0x035] = {
                                'Description': "PDET_CTRL register",
                                'pdet_rst':
                                    {
                                        'offset': 0,
                                        'size': 1,
                                        'description': "1=Hold PDET Offset and Sample state machines for all PDETs in reset\r\n." +
                                                        "\t\t\t\tAlways write a 1 then a 0 to pdet_rst, after either:\r\n" +
                                                        "\t\t\t\tchanging one or more PDET configuration registers, or\r\n" +
                                                        "\t\t\t\texiting ic_mode==sleep, to cleanly resetthe PDET and ADC logic"
                                    },
                                'pdet_sw_trig':
                                    {
                                        'offset': 1,
                                        'size': 1,
                                        'description': "PDET Software Trigger: Only used if pdet_trig_cond=2."
                                    },
                                'pdet_trig_cond':
                                    {
                                        'offset': 2,
                                        'size': 3,
                                        'description': "Trigger conditions causing PDET acquisition:\r\n" +
                                                        "\t\t\t\t5: TX (IC enters Tx state)\r\n" +
                                                        "\t\t\t\t4: RX (IC enters Rx state)\r\n" +
                                                        "\t\t\t\t3: STRB (LDB/STRB active ex. at symbol boundary)\r\n" +
                                                        "\t\t\t\t2: SW_TRIG (pdet_sw_trig 0->1 transition) RECOMMENDED\r\n" +
                                                        "\t\t\t\t1: IMM (immediate trigger, loop continuously measuring PDETs)\r\n" +
                                                        "\t\t\t\t0: IDLE (no measurement)"
                                    }
                            }
    reg_addr_table[0x044] = {
                                'Description': "PDET_RD_CH2 register",
                                'rftx_pdet_ch2':
                                    {
                                        'offset': 24,
                                        'size': 8,
                                        'description': "Tx Power at output of internal PA (pin HPFE2)"
                                    },
                                'filt_pdet_ch2':
                                    {
                                        'offset': 40,
                                        'size': 8,
                                        'description': "Tx Power before external Filter and internal PA (pin RF2)"
                                    }
                            }
    reg_addr_table[0x045] = {
                                'Description': "PDET_RD_CH1 register",
                                'rftx_pdet_ch1':
                                    {
                                        'offset': 24,
                                        'size': 8,
                                        'description': "Tx Power at output of internal PA (pin HPFE1)"
                                    },
                                'filt_pdet_ch1':
                                    {
                                        'offset': 40,
                                        'size': 8,
                                        'description': "Tx Power before external Filter and internal PA (pin RF1)"
                                    }
                            }

def getUdicConfig(addr, debug=True)->bool:
    # RADDR
    raddr = 0x009 << 48 | addr & 0x3FF
    raddr_bytes = raddr.to_bytes(8, 'big')
    pattern = bytearray(header) + bytearray(raddr_bytes)
    spi_transfer(devA, devB, pattern)

    # SPARE
    spare = 0x001 << 48
    spare_bytes = spare.to_bytes(8, 'big')
    pattern = bytearray(header) + bytearray(spare_bytes)
    ret_bytes = spi_transfer(devA, devB, pattern)

    payload = ((int.from_bytes(ret_bytes, 'big') >> 4) & 0xFFFFFFFFFFFF)
    if debug:
        print("[Addr:0x%04X] Payload: 0x%06X" %(addr, payload))
        print_reg_fields(addr, payload)
    return payload

def setUdicGeneralConfig(addr, payload):
    print(f"==== Set UDIC Reg:{addr}, Payload:{payload} ====")

    reg = addr << 48 | payload
    reg_bytes = reg.to_bytes(8, 'big')
    pattern = bytearray(header)+bytearray(reg_bytes)
    spi_transfer(devA, devB, pattern)

def setUdicGeneralConfig(addr, value, start_bit, end_bit):
    print(f"==== Set UDIC Reg:{addr}, Value:{value} ====")

    # Get original payload
    payload = getUdicConfig(addr, False)

    reg = addr << 48 | Register48(payload).set_field(value, start_bit, end_bit-start_bit+1)
    reg_bytes = reg.to_bytes(8, 'big')
    pattern = bytearray(header)+bytearray(reg_bytes)
    spi_transfer(devA, devB, pattern)

    # Get modified payload
    payload = getUdicConfig(addr, True)

def setUdicAttConfig(att_tx, att_rx):
    print(f"==== Set UDIC ATT_Tx:{att_tx}, ATT_Rx:{att_rx} ====")
    # CH2
    reg_data[2] = att_tx
    reg_data[3] = att_rx
    # CH1
    reg_data[4] = att_tx
    reg_data[5] = att_rx
    pattern = bytearray(header)+bytearray(reg_addr)+bytearray(reg_data)
    spi_transfer(devA, devB, pattern)

def setUdicPdet(pdet_rst:bool, pdet_trig:bool, pdet_cond:int)->bool:
    print(f"==== Pdet config: pdet_rst:{pdet_rst}, pdet_trig:{pdet_trig}, pdet_cond:{pdet_cond} ====")

    addr = 0x035
    if pdet_rst is not None:
        ret = get_reg_fields(addr, 'pdet_rst')
        if not ret:
            return
        (start_bit, size) = ret
        setUdicGeneralConfig(addr, pdet_rst, start_bit, size)

    if pdet_trig is not None:
        ret = get_reg_fields(addr, 'pdet_sw_trig')
        if not ret:
            return
        (start_bit, size) = ret
        setUdicGeneralConfig(addr, pdet_trig, start_bit, size)

    if pdet_cond is not None:
        ret = get_reg_fields(addr, 'pdet_trig_cond')
        if not ret:
            return
        (start_bit, size) = ret
        setUdicGeneralConfig(addr, pdet_cond, start_bit, size)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    mode_group = parser.add_argument_group(title="PDET Control cmds")
    mode_group.add_argument("--pdet", help="Set PDET, trigger must from 0 to 1", type=int)
    mode_group.add_argument("--pdet_rst", help="Set PDET reset from 1 to 0", type=int)
    mode_group.add_argument("--pdet_cond", help="Set PDET trigger condition", type=int)

    control_group = parser.add_argument_group(title="Control cmds")
    control_group.add_argument("--att_tx", help="Tx att gain step(0-255), default:0x22", type=hex_int_type, default=0x22)
    control_group.add_argument("--att_rx", help="Rx att gain step(0-255), default:0x24", type=hex_int_type, default=0x24)
    parser.add_argument("--ver", action='store_true', help="Get the version")#, action='version', version='%(prog)s: v'+jio_ver())
    parser.add_argument("--get", help="Get reg info with for the assigned reg", type=hex_int_type)
    args = parser.parse_args()

    print((args.pdet_rst is not None
                or args.pdet is not None
                or args.pdet_cond is not None))

    # 如果沒有提供任何參數，顯示 --help 的內容
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    init_reg_table()

    devA, devB = initialize_ft4222()

    if devA:
        if args.ver is not None and args.ver is True:
            print(jio_ver(devA, devB))
        elif args.get is not None:
            getUdicConfig(args.get)
        elif (args.pdet_rst is not None
                or args.pdet is not None
                or args.pdet_cond is not None):
            setUdicPdet(args.pdet_rst, args.pdet, args.pdet_cond)
        else:
            setUdicAttConfig(args.att_tx, args.att_rx)

    close_ft4222(devA, devB)