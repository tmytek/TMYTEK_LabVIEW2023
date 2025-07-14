import argparse
import sys
from reg_tool import *
from jio_version import *
from myftdi.spi_gpio.ftdi_spi_sender import *

en_list = [0,1,2,3]
dis_list = []
header_chain1 = [0xF0, 0x01]
header_chain2 = [0xF0, 0x02]
header_list = [header_chain1, header_chain2]

reg_addr_tx_v = [0x00, 0x03]
reg_addr_rx_v = [0x00, 0x04]
reg_addr_tx_h = [0x00, 0x22]
reg_addr_rx_h = [0x00, 0x23]
reg_addr_list = [reg_addr_tx_h, reg_addr_rx_h, reg_addr_tx_v, reg_addr_rx_v]

devA = None
devB = None

dis = 0
com = 15
ele = 0xFFFF

# Boresight phase step with cali phase offset
# For JIO V1.8
phase_chain1_ic4 = [0x16, 0x85, 0x46]
phase_chain1_ic3 = [0x1A, 0x69, 0xC7]
phase_chain1_ic2 = [0x1A, 0x8A, 0x46]
phase_chain1_ic1 = [0x02, 0x49, 0x41]
phase_chain2_ic4 = [0x1A, 0x9A, 0xC7]
phase_chain2_ic3 = [0x26, 0x8A, 0x49]
phase_chain2_ic2 = [0x2A, 0x9A, 0x89]
phase_chain2_ic1 = [0x1A, 0x69, 0x85]
phase_tx_v = [
    [phase_chain1_ic4, phase_chain1_ic3, phase_chain1_ic2, phase_chain1_ic1],
    [phase_chain2_ic4, phase_chain2_ic3, phase_chain2_ic2, phase_chain2_ic1]
]
phase_chain1_ic4 = [0x2F, 0x39, 0xCA]
phase_chain1_ic3 = [0x27, 0x2C, 0xCA]
phase_chain1_ic2 = [0x16, 0xBB, 0x05]
phase_chain1_ic1 = [0x02, 0x9A, 0x04]
phase_chain2_ic4 = [0x32, 0xAA, 0xD2]
phase_chain2_ic3 = [0x26, 0xBB, 0x0B]
phase_chain2_ic2 = [0x2E, 0xBB, 0x4C]
phase_chain2_ic1 = [0x26, 0xBA, 0xC9]
phase_rx_v = [
    [phase_chain1_ic4, phase_chain1_ic3, phase_chain1_ic2, phase_chain1_ic1],
    [phase_chain2_ic4, phase_chain2_ic3, phase_chain2_ic2, phase_chain2_ic1]
]
phase_chain1_ic4 = [0x0C, 0x58, 0xCF]
phase_chain1_ic3 = [0x10, 0x49, 0x25]
phase_chain1_ic2 = [0x18, 0x69, 0xA3]
phase_chain1_ic1 = [0x00, 0x08, 0xA6]
phase_chain2_ic4 = [0x10, 0x48, 0x65]
phase_chain2_ic3 = [0x18, 0x53, 0xA4]
phase_chain2_ic2 = [0x1C, 0x79, 0xEC]
phase_chain2_ic1 = [0x00, 0x28, 0xA3]
phase_tx_h = [
    [phase_chain1_ic4, phase_chain1_ic3, phase_chain1_ic2, phase_chain1_ic1],
    [phase_chain2_ic4, phase_chain2_ic3, phase_chain2_ic2, phase_chain2_ic1]
]
phase_chain1_ic4 = [0x28, 0x79, 0xD3]
phase_chain1_ic3 = [0x20, 0x7A, 0x6A]
phase_chain1_ic2 = [0x1C, 0x6A, 0x63]
phase_chain1_ic1 = [0x00, 0x38, 0xA7]
phase_chain2_ic4 = [0x20, 0x89, 0x27]
phase_chain2_ic3 = [0x24, 0x94, 0x68]
phase_chain2_ic2 = [0x24, 0xDA, 0xAE]
phase_chain2_ic1 = [0x0C, 0x6A, 0x68]
phase_rx_h = [
    [phase_chain1_ic4, phase_chain1_ic3, phase_chain1_ic2, phase_chain1_ic1],
    [phase_chain2_ic4, phase_chain2_ic3, phase_chain2_ic2, phase_chain2_ic1]
]

# For JIO V2.2
phase_ic_v22 = [0x02, 0x08, 0x00]
phase_v22 = [
    [phase_ic_v22 for ic in range(4)], # chain_1
    [phase_ic_v22 for ic in range(4)], # chain_2
]

phase_list= {
    1.8: [phase_tx_h, phase_rx_h, phase_tx_v, phase_rx_v],
    2.2: [phase_v22 for tr_hv in range(4)]
}

def init_reg_table():
    """
    Init AWMF-0221 reg table format for check getting fields
    Format: 'addr' : (offset, size)
    """
    reg_addr_table[0x002] = {
                                'Description': "Mode",
                                'spi_tdbs_sel':
                                    {
                                        'offset': 1,
                                        'size': 1,
                                        'description': "TDBS Select (1=use TDBS memory values, 0=use BW values)"
                                    },
                                'spi_fbs_sel':
                                    {
                                        'offset': 2,
                                        'size': 1,
                                        'description': "FBS Phase Value Select (1=use FBS memory values, 0=use BW values)"
                                    },
                                'Zcal_init':
                                    {
                                        'offset': 3,
                                        'size': 1,
                                        'description': "Initiates Zcal features (1=enabled)"
                                    },
                                'spi_pdet_samp_trig':
                                    {
                                        'offset': 5,
                                        'size': 1,
                                        'description': "SPI controlled PDET Sampling Trigger"
                                    },
                                'sdo_polarity':
                                    {
                                        'offset': 6,
                                        'size': 1,
                                        'description': "SDO Clock Polarity. (0=drive SDO on falling SPI_CLK edge, 1=drive on rising edge)"
                                    },
                                # TODO: remain fields
                                'ic_mode_sel':
                                    {
                                        'offset': 15,
                                        'size': 3,
                                        'description': "IC Mode Select Word (0 = normal operation, 1= enables FBRx mode in Tx)"
                                    },
                                'spi_atc_sel':
                                    {
                                        'offset': 18,
                                        'size': 1,
                                        'description': "Set to 1 to enable automatic temperature compensation(ATC)"
                                    },
                                'rxip3_a':
                                    {
                                        'offset': 19,
                                        'size': 6,
                                        'description': "High Linearity Rx Mode Controls - A polarization"
                                    },
                                'rxip3_b':
                                    {
                                        'offset': 25,
                                        'size': 6,
                                        'description': "High Linearity Rx Mode Controls - B polarization"
                                    },
                                'telem_temp_units':
                                    {
                                        'offset': 33,
                                        'size': 1,
                                        'description': "Defines temperature format in TELEM registers (0=ADC codes, 1=signed deg C, 2’s complement)"
                                    },
                                'att_sharing_en':
                                    {
                                        'offset': 37,
                                        'size': 1,
                                        'description': "Enable sharing attenuation between common and element"
                                    },
                            }
    reg_addr_table[0x003] = {
                                'Description': "TX_A",
                                'tx_rf1_phase_a':
                                    {
                                        'offset': 0,
                                        'size': 6,
                                        'description': "Tx RF1 Phase-Shift step, 5.625deg/step"
                                    },
                                'tx_rf2_phase_a':
                                    {
                                        'offset': 6,
                                        'size': 6,
                                        'description': "Tx RF2 Phase-Shift step, 5.625deg/step"
                                    },
                                'tx_rf3_phase_a':
                                    {
                                        'offset': 12,
                                        'size': 6,
                                        'description': "Tx RF3 Phase-Shift step, 5.625deg/step"
                                    },
                                'tx_rf4_phase_a':
                                    {
                                        'offset': 18,
                                        'size': 6,
                                        'description': "Tx RF4 Phase-Shift step, 5.625deg/step"
                                    },
                                'tx_rf1_gain_a':
                                    {
                                        'offset': 24,
                                        'size': 4,
                                        'description': "Tx RF1 Attenuation, 0.5dB/step"
                                    },
                                'tx_rf2_gain_a':
                                    {
                                        'offset': 28,
                                        'size': 4,
                                        'description': "Tx RF2 Attenuation, 0.5dB/step"
                                    },
                                'tx_rf3_gain_a':
                                    {
                                        'offset': 32,
                                        'size': 4,
                                        'description': "Tx RF3 Attenuation, 0.5dB/step"
                                    },
                                'tx_rf4_gain_a':
                                    {
                                        'offset': 36,
                                        'size': 4,
                                        'description': "Tx RF4 Attenuation, 0.5dB/step"
                                    },
                                'tx_com_gain_a':
                                    {
                                        'offset': 40,
                                        'size': 4,
                                        'description': "Tx Common Arm Attenuation, 0.5dB/step"
                                    },
                                'tx_rf1_dis_a':
                                    {
                                        'offset': 44,
                                        'size': 1,
                                        'description': "Disable RF1A"
                                    },
                                'tx_rf2_dis_a':
                                    {
                                        'offset': 45,
                                        'size': 1,
                                        'description': "Disable RF2A"
                                    },
                                'tx_rf3_dis_a':
                                    {
                                        'offset': 46,
                                        'size': 1,
                                        'description': "Disable RF3A"
                                    },
                                'tx_rf4_dis_a':
                                    {
                                        'offset': 47,
                                        'size': 1,
                                        'description': "Disable RF4A"
                                    },
                            }
    reg_addr_table[0x004] = {
                                'Description': "RX_A",
                                'rx_rf1_phase_a':
                                    {
                                        'offset': 0,
                                        'size': 6,
                                        'description': "Rx RF1 Phase-Shift step, 5.625deg/step"
                                    },
                                'rx_rf2_phase_a':
                                    {
                                        'offset': 6,
                                        'size': 6,
                                        'description': "Rx RF2 Phase-Shift step, 5.625deg/step"
                                    },
                                'rx_rf3_phase_a':
                                    {
                                        'offset': 12,
                                        'size': 6,
                                        'description': "Rx RF3 Phase-Shift step, 5.625deg/step"
                                    },
                                'rx_rf4_phase_a':
                                    {
                                        'offset': 18,
                                        'size': 6,
                                        'description': "Rx RF4 Phase-Shift step, 5.625deg/step"
                                    },
                                'rx_rf1_gain_a':
                                    {
                                        'offset': 24,
                                        'size': 4,
                                        'description': "Rx RF1 Attenuation, 0.5dB/step"
                                    },
                                'rx_rf2_gain_a':
                                    {
                                        'offset': 28,
                                        'size': 4,
                                        'description': "Rx RF2 Attenuation, 0.5dB/step"
                                    },
                                'rx_rf3_gain_a':
                                    {
                                        'offset': 32,
                                        'size': 4,
                                        'description': "Rx RF3 Attenuation, 0.5dB/step"
                                    },
                                'rx_rf4_gain_a':
                                    {
                                        'offset': 36,
                                        'size': 4,
                                        'description': "Rx RF4 Attenuation, 0.5dB/step"
                                    },
                                'rx_com_gain_a':
                                    {
                                        'offset': 40,
                                        'size': 4,
                                        'description': "Rx Common Arm Attenuation, 0.5dB/step"
                                    },
                                'rx_rf1_dis_a':
                                    {
                                        'offset': 44,
                                        'size': 1,
                                        'description': "Disable RF1A"
                                    },
                                'rx_rf2_dis_a':
                                    {
                                        'offset': 45,
                                        'size': 1,
                                        'description': "Disable RF2A"
                                    },
                                'rx_rf3_dis_a':
                                    {
                                        'offset': 46,
                                        'size': 1,
                                        'description': "Disable RF3A"
                                    },
                                'rx_rf4_dis_a':
                                    {
                                        'offset': 47,
                                        'size': 1,
                                        'description': "Disable RF4A"
                                    },
                            }
    reg_addr_table[0x022] = {
                                'Description': "TX_B",
                                'tx_rf1_phase_b':
                                    {
                                        'offset': 0,
                                        'size': 6,
                                        'description': "Tx RF1 Phase-Shift step, 5.625deg/step"
                                    },
                                'tx_rf2_phase_b':
                                    {
                                        'offset': 6,
                                        'size': 6,
                                        'description': "Tx RF2 Phase-Shift step, 5.625deg/step"
                                    },
                                'tx_rf3_phase_b':
                                    {
                                        'offset': 12,
                                        'size': 6,
                                        'description': "Tx RF3 Phase-Shift step, 5.625deg/step"
                                    },
                                'tx_rf4_phase_b':
                                    {
                                        'offset': 18,
                                        'size': 6,
                                        'description': "Tx RF4 Phase-Shift step, 5.625deg/step"
                                    },
                                'tx_rf1_gain_b':
                                    {
                                        'offset': 24,
                                        'size': 4,
                                        'description': "Tx RF1 Attenuation, 0.5dB/step"
                                    },
                                'tx_rf2_gain_b':
                                    {
                                        'offset': 28,
                                        'size': 4,
                                        'description': "Tx RF2 Attenuation, 0.5dB/step"
                                    },
                                'tx_rf3_gain_b':
                                    {
                                        'offset': 32,
                                        'size': 4,
                                        'description': "Tx RF3 Attenuation, 0.5dB/step"
                                    },
                                'tx_rf4_gain_b':
                                    {
                                        'offset': 36,
                                        'size': 4,
                                        'description': "Tx RF4 Attenuation, 0.5dB/step"
                                    },
                                'tx_com_gain_b':
                                    {
                                        'offset': 40,
                                        'size': 4,
                                        'description': "Tx Common Arm Attenuation, 0.5dB/step"
                                    },
                                'tx_rf1_dis_b':
                                    {
                                        'offset': 44,
                                        'size': 1,
                                        'description': "Disable RF1A"
                                    },
                                'tx_rf2_dis_b':
                                    {
                                        'offset': 45,
                                        'size': 1,
                                        'description': "Disable RF2A"
                                    },
                                'tx_rf3_dis_b':
                                    {
                                        'offset': 46,
                                        'size': 1,
                                        'description': "Disable RF3A"
                                    },
                                'tx_rf4_dis_b':
                                    {
                                        'offset': 47,
                                        'size': 1,
                                        'description': "Disable RF4A"
                                    },
                            }
    reg_addr_table[0x023] = {
                                'Description': "RX_B",
                                'rx_rf1_phase_b':
                                    {
                                        'offset': 0,
                                        'size': 6,
                                        'description': "Rx RF1 Phase-Shift step, 5.625deg/step"
                                    },
                                'rx_rf2_phase_b':
                                    {
                                        'offset': 6,
                                        'size': 6,
                                        'description': "Rx RF2 Phase-Shift step, 5.625deg/step"
                                    },
                                'rx_rf3_phase_b':
                                    {
                                        'offset': 12,
                                        'size': 6,
                                        'description': "Rx RF3 Phase-Shift step, 5.625deg/step"
                                    },
                                'rx_rf4_phase_b':
                                    {
                                        'offset': 18,
                                        'size': 6,
                                        'description': "Rx RF4 Phase-Shift step, 5.625deg/step"
                                    },
                                'rx_rf1_gain_b':
                                    {
                                        'offset': 24,
                                        'size': 4,
                                        'description': "Rx RF1 Attenuation, 0.5dB/step"
                                    },
                                'rx_rf2_gain_b':
                                    {
                                        'offset': 28,
                                        'size': 4,
                                        'description': "Rx RF2 Attenuation, 0.5dB/step"
                                    },
                                'rx_rf3_gain_b':
                                    {
                                        'offset': 32,
                                        'size': 4,
                                        'description': "Rx RF3 Attenuation, 0.5dB/step"
                                    },
                                'rx_rf4_gain_b':
                                    {
                                        'offset': 36,
                                        'size': 4,
                                        'description': "Rx RF4 Attenuation, 0.5dB/step"
                                    },
                                'rx_com_gain_b':
                                    {
                                        'offset': 40,
                                        'size': 4,
                                        'description': "Rx Common Arm Attenuation, 0.5dB/step"
                                    },
                                'rx_rf1_dis_b':
                                    {
                                        'offset': 44,
                                        'size': 1,
                                        'description': "Disable RF1A"
                                    },
                                'rx_rf2_dis_b':
                                    {
                                        'offset': 45,
                                        'size': 1,
                                        'description': "Disable RF2A"
                                    },
                                'rx_rf3_dis_b':
                                    {
                                        'offset': 46,
                                        'size': 1,
                                        'description': "Disable RF3A"
                                    },
                                'rx_rf4_dis_b':
                                    {
                                        'offset': 47,
                                        'size': 1,
                                        'description': "Disable RF4A"
                                    },
                            }
    reg_addr_table[0x029] = {
                                'Description': "PDET Control",
                                'pdet_mask':
                                    {
                                        'offset': 0,
                                        'size': 4,
                                        'description': "Used to select which PDET outputs are sent to ADC for conversion.\r\n" +
                                                        "\t\t\t\t1=active 0=disabled. Both PDET ADC’s use mask.\r\n" +
                                                        "\t\t\t\tThe bits are in {element #, hv} ascending order ex. \r\n" +
                                                        "\t\t\t\tfor adc_el12: {2v,2h,1v,1h} and for adc_el34:{4v,4h,3v,3h}. \r\n" +
                                                        "\t\t\t\tThe lowest number/letter element is measured first"
                                    },
                                'pdet_ave_n':
                                    {
                                        'offset': 4,
                                        'size': 4,
                                        'description': "Exponent value “N” for digital averaging => 2^N\r\n" +
                                                        "\t\t\t\tIf pdet_ave_n=7 => 2^7 = 128 samples for averaging"
                                    },
                                'pdet_threshold':
                                    {
                                        'offset': 8,
                                        'size': 4,
                                        'description': "For rejecting ADC samples when there are gaps in the input waveform.\r\n" +
                                                        "\t\t\t\t(pdet_threshold*16 is the minimum ADC code that will count as a valid sample)"
                                    },
                                'pdet_wait_start':
                                    {
                                        'offset': 12,
                                        'size': 6,
                                        'description': "Additional wait time between TX_EN rising edge and first ADC sample being taken (LSB=2us)"
                                    },
                                'pdet_wait_sw':
                                    {
                                        'offset': 18,
                                        'size': 6,
                                        'description': "Programmable additional wait time between PDET mux change and first sample of PDET. Steps of 40ns"
                                    },
                                'pdet_cal_dac_int':
                                    {
                                        'offset': 24,
                                        'size': 1,
                                        'description': "Recommend set at 1. Setting of 1 will use internal cal coefficients. \r\n" +
                                                        "\t\t\t\tSetting of 0 will use cal coefficients generated during real-time calibration process"
                                    },
                                # 'pdet_cal_dac_wait':
                                #     {
                                #         'offset': 25,
                                #         'size': 6,
                                #         'description': ""
                                #     },
                                'pdet_rst':
                                    {
                                        'offset': 42,
                                        'size': 1,
                                        'description': "Reset PDET internal calibration and data acquisition. When set to 1, no data reported"
                                    },
                            }
    reg_addr_table[0x031] = {
                                'Description': "TELEM1",
                                'temp_sense':
                                    {
                                        'offset': 0,
                                        'size': 8,
                                        'description': "Temperature Sensor Output (see telem_temp_units)"
                                    },
                                'rf1_pdet_b':
                                    {
                                        'offset': 8,
                                        'size': 8,
                                        'description': "Quad 1 Power Detector Output B"
                                    },
                                'rf2_pdet_b':
                                    {
                                        'offset': 16,
                                        'size': 8,
                                        'description': "Quad 2 Power Detector Output B"
                                    },
                                'rf3_pdet_b':
                                    {
                                        'offset': 24,
                                        'size': 8,
                                        'description': "Quad 3 Power Detector Output B"
                                    },
                                'rf4_pdet_b':
                                    {
                                        'offset': 32,
                                        'size': 8,
                                        'description': "Quad 4 Power Detector Output B"
                                    },
                                'Pdet_status':
                                    {
                                        'offset': 40,
                                        'size': 6,
                                        'description': "PDET Status Codes : See PDET section for Status codes\r\n" +
                                                        "\t\t\t\t0: Data Ready - No Errors\r\n" +
                                                        "\t\t\t\t1: PDET measurement timeout occurred\r\n" +
                                                        "\t\t\t\t2: TX_EN=0 before measurement completed\r\n" +
                                                        "\t\t\t\t4: TX_EN=1 while internal calibration was initiated\r\n" +
                                                        "\t\t\t\t8: Ignore a 1 in this position if ZCal was run.\r\n" +
                                                        "\t\t\t\t16: Sampling sequence not complete"
                                    },
                                'Zcal_ready':
                                    {
                                        'offset': 46,
                                        'size': 1,
                                        'description': "ZCal Ready Flag: 0 = ZCal not ready ; 1 = ZCal initialization complete"
                                    },
                                'parity_error':
                                    {
                                        'offset': 47,
                                        'size': 1,
                                        'description': "0 = no parity error on previous received serial message.\r\n" +
                                                        "\t\t\t\t1 = parity error. Errors are only reported if parity_en==1"
                                    },
                            }
    reg_addr_table[0x032] = {
                                'Description': "TELEM2",
                                'temp_sense':
                                    {
                                        'offset': 0,
                                        'size': 8,
                                        'description': "Temperature Sensor Output (see telem_temp_units)"
                                    },
                                'rf1_pdet_a':
                                    {
                                        'offset': 8,
                                        'size': 8,
                                        'description': "Quad 1 Power Detector Output A"
                                    },
                                'rf2_pdet_a':
                                    {
                                        'offset': 16,
                                        'size': 8,
                                        'description': "Quad 2 Power Detector Output A"
                                    },
                                'rf3_pdet_a':
                                    {
                                        'offset': 24,
                                        'size': 8,
                                        'description': "Quad 3 Power Detector Output A"
                                    },
                                'rf4_pdet_a':
                                    {
                                        'offset': 32,
                                        'size': 8,
                                        'description': "Quad 4 Power Detector Output A"
                                    },
                                'Pdet_status':
                                    {
                                        'offset': 40,
                                        'size': 6,
                                        'description': "PDET Status Codes : See PDET section for Status codes\r\n" +
                                                        "\t\t\t\t0: Data Ready - No Errors\r\n" +
                                                        "\t\t\t\t1: PDET measurement timeout occurred\r\n" +
                                                        "\t\t\t\t2: TX_EN=0 before measurement completed\r\n" +
                                                        "\t\t\t\t4: TX_EN=1 while internal calibration was initiated\r\n" +
                                                        "\t\t\t\t8: Ignore a 1 in this position if ZCal was run.\r\n" +
                                                        "\t\t\t\t16: Sampling sequence not complete"
                                    },
                                'Zcal_ready':
                                    {
                                        'offset': 46,
                                        'size': 1,
                                        'description': "ZCal Ready Flag: 0 = ZCal not ready ; 1 = ZCal initialization complete"
                                    },
                                'parity_error':
                                    {
                                        'offset': 47,
                                        'size': 1,
                                        'description': "0 = no parity error on previous received serial message.\r\n" +
                                                        "\t\t\t\t1 = parity error. Errors are only reported if parity_en==1"
                                    },
                            }

def print_reg_fields(reg_addr, payload=None):
    if not reg_addr_table.get(reg_addr):
        print("Can not find this register")
        return

    print(f" ---- [{reg_addr:04X}] ----")
    for field_name, info in reg_addr_table[reg_addr].items():
        if field_name == 'Description' or payload is None:
            print(f"{field_name:<20}: {info}")
        else:
            value = Register48(payload).get_field(info['offset'], info['size'])
            print(f"{field_name:<20}: 0x{value:0X}({value}) -> {info['description']}")

def getBficConfig(addr, chain_number=None, print_config=True)->bool:
    ret_dict = {}
    chain_id_list = [1, 2]
    if chain_number is not None:
        chain_id_list = [chain_number]

    for i in range(len(header_list)):
        chain_id = i
        if not chain_id+1 in chain_id_list:
            continue
        # print(f"Chain-{chain_id+1}")

        # for each chain
        # RADDR
        raddr = 0x03D << 48 | addr & 0x3FF
        raddr = raddr << 60 | raddr
        raddr_bytes = raddr.to_bytes(15, 'big')
        pattern = bytearray(header_list[i]) + bytearray(raddr_bytes) + bytearray(raddr_bytes)
        spi_transfer(devA, devB, pattern)

        # SPARE
        spare = 0x001 << 48
        spare = spare << 60 | spare
        spare_bytes = spare.to_bytes(15, 'big')
        pattern = bytearray(header_list[i]) + bytearray(spare_bytes) + bytearray(spare_bytes)
        ret_bytes = spi_transfer(devA, devB, pattern)

        ret_dict[chain_id+1] = ret_bytes
        # formatted_recv_data = ' '.join(f'{byte:02X}' for byte in ret_bytes)
        # print(f"\t->: {formatted_recv_data}")

        ic_idx = 0
        shift_bytes = 15
        for half_chain in range(2):
            # Capture [2:17], [17:33]
            fetch_bytes = ret_bytes[2+shift_bytes*half_chain : 2+shift_bytes*(half_chain+1)]
            # print(fetch_bytes)
            half_payload = int.from_bytes(fetch_bytes, 'big')

            payload = (half_payload >> 60) & 0xFFFFFFFFFFFF
            print("[Addr:0x%04X][Chain_%d][IC_%d] Get Payload: 0x%06X" %(addr, chain_id+1, 4-ic_idx, payload))
            if print_config:
                print_reg_fields(addr, payload)
            ic_idx += 1

            payload = half_payload & 0xFFFFFFFFFFFF
            print("[Addr:0x%04X][Chain_%d][IC_%d] Get Payload: 0x%06X" %(addr, chain_id+1, 4-ic_idx, payload))
            if print_config:
                print_reg_fields(addr, payload)
            ic_idx += 1

    return ret_dict

def setBficBeam(dis:bool, pol:int, com:int, ele:int, en_ic_only=0, jio_ver=2.2)->bool:
    print(f"==== [JIO_V{jio_ver}] Set BFIC dis:{dis}, pol:{pol} with com:{com}, ele:{ele} ===")
    if dis:
        print(f"==== Set BFIC disable all ====")
        dis = 0xF
        en_list.clear()
        dis_list.extend([0,1,2,3])
    elif en_ic_only != 0:
        print(f"==== Set BFIC enable specific IC {en_ic_only} ====")
        if pol == 0:
            en_list.remove(2)
            en_list.remove(3)
        elif pol == 1:
            en_list.remove(0)
            en_list.remove(1)

        for type_id in en_list:
            # txh rxh txv rxv
            reg_addr_hex = int.from_bytes(reg_addr_list[type_id], 'big')
            reg_ic = (reg_addr_hex << 48 | dis << 44 | com << 40
                    | ele << 36 | ele << 32 | ele << 28 | ele << 24)
            reg_dis_ic = reg_addr_hex << 48 | 0xF << 44

            chain_id = int((en_ic_only-1)/4)
            header = header_list[chain_id]
            pattern = bytearray(header)

            phase_hex = int.from_bytes(phase_list[jio_ver][type_id][chain_id][(en_ic_only-1)%4], 'big')
            en_ic_only_in_chain = (en_ic_only-1) % 4 + 1
            if en_ic_only_in_chain == 1:
                reg_hex = reg_dis_ic
                reg_hex = reg_hex << 60 | reg_dis_ic
                reg_bytes = reg_hex.to_bytes(15, 'big')
                pattern += bytearray(reg_bytes)
                reg_hex = reg_dis_ic
                reg_hex = reg_hex << 60 | reg_ic | phase_hex
                reg_bytes = reg_hex.to_bytes(15, 'big')
                pattern += bytearray(reg_bytes)
                spi_transfer(devA, devB, pattern)
            elif en_ic_only_in_chain == 2:
                reg_hex = reg_dis_ic
                reg_hex = reg_hex << 60 | reg_dis_ic
                reg_bytes = reg_hex.to_bytes(15, 'big')
                pattern += bytearray(reg_bytes)
                reg_hex = reg_ic | phase_hex
                reg_hex = reg_hex << 60 | reg_dis_ic
                reg_bytes = reg_hex.to_bytes(15, 'big')
                pattern += bytearray(reg_bytes)
                spi_transfer(devA, devB, pattern)
            elif en_ic_only_in_chain == 3:
                reg_hex = reg_dis_ic
                reg_hex = reg_hex << 60 | reg_ic | phase_hex
                reg_bytes = reg_hex.to_bytes(15, 'big')
                pattern += bytearray(reg_bytes)
                reg_hex = reg_dis_ic
                reg_hex = reg_hex << 60 | reg_dis_ic
                reg_bytes = reg_hex.to_bytes(15, 'big')
                pattern += bytearray(reg_bytes)
                spi_transfer(devA, devB, pattern)
            elif en_ic_only_in_chain == 4:
                reg_hex = reg_ic | phase_hex
                reg_hex = reg_hex << 60 | reg_dis_ic
                reg_bytes = reg_hex.to_bytes(15, 'big')
                pattern += bytearray(reg_bytes)
                reg_hex = reg_dis_ic
                reg_hex = reg_hex << 60 | reg_dis_ic
                reg_bytes = reg_hex.to_bytes(15, 'big')
                pattern += bytearray(reg_bytes)
                spi_transfer(devA, devB, pattern)
        return True
    else:
        if pol == 0:
            en_list.remove(2)
            dis_list.append(2)
            en_list.remove(3)
            dis_list.append(3)
        elif pol == 1:
            en_list.remove(0)
            dis_list.append(0)
            en_list.remove(1)
            dis_list.append(1)

    for type_id in en_list:
        # txh rxh txv rxv
        reg_addr_hex = int.from_bytes(reg_addr_list[type_id], 'big')
        print("En 0x%03X(%d)" %(reg_addr_hex, reg_addr_hex))
        reg_ic = (reg_addr_hex << 48 | dis << 44 | com << 40
                | ele << 36 | ele << 32 | ele << 28 | ele << 24)

        for chain_id in range(len(header_list)):
            # for each chain
            header = header_list[chain_id]
            pattern = bytearray(header)
            for ic_pair in range(2):
                phase_hex = int.from_bytes(phase_list[jio_ver][type_id][chain_id][ic_pair*2], 'big')
                reg_hex = reg_ic | phase_hex

                phase_hex = int.from_bytes(phase_list[jio_ver][type_id][chain_id][ic_pair*2+1], 'big')
                reg_hex = reg_hex << 60 | reg_ic | phase_hex

                reg_bytes = reg_hex.to_bytes(15, 'big')
                pattern += bytearray(reg_bytes)
            spi_transfer(devA, devB, pattern)

    for type_id in dis_list:
        # txh rxh txv rxv
        dis = 0xF
        reg_addr_hex = int.from_bytes(reg_addr_list[type_id], 'big')
        print("Dis 0x%03X(%d)" %(reg_addr_hex, reg_addr_hex))
        reg_ic = (reg_addr_hex << 48 | dis << 44)

        for chain_id in range(len(header_list)):
            # for each chain
            header = header_list[chain_id]
            pattern = bytearray(header)
            for ic_pair in range(2):
                reg_hex = reg_ic << 60 | reg_ic

                reg_bytes = reg_hex.to_bytes(15, 'big')
                pattern += bytearray(reg_bytes)
            spi_transfer(devA, devB, pattern)
    return True

def setBficChannel(chain, ic, channel, tr_mode, pol, dis=0, com=0, ele=0, phase=0, keep=True, jio_ver=2.2):
    print(f"==== [JIO_V{jio_ver}] Set BFIC chain:{chain}, ic:{ic}, channel:{channel}, tr_mode:{tr_mode}, pol:{pol} with dis:{dis}, com:{com}, ele:{ele}, phase:{phase} ===")

    # Generate basic pattern header from chain,
    out_pattern = bytearray(header_list[chain-1])

    # Generate basic address hex from tr_mode, pol
    type_id =  pol*2 + tr_mode
    reg_addr_hex = int.from_bytes(reg_addr_list[type_id], 'big')

    if keep:
        # Read origin reg
        ret_dict = getBficConfig(reg_addr_hex, chain, False)
        # print(ret_dict)

        # Test with dummy payload
        dummy = False
        if dummy:
            print("Dummy data")
            dis_ori = 0xF
            com_ori = 0xD
            ele_ori = 0xA
            reg_ic = (1 << 48 | dis_ori << 44 | com_ori << 40
                    | ele_ori << 36 | ele_ori << 32 | ele_ori << 28 | ele_ori << 24)
            reg_hex = reg_ic << 60 | reg_ic | 0
            reg_bytes = reg_hex.to_bytes(15, 'big')
            ret_dict = {chain: bytearray([0x00, 0x00]) + bytearray(reg_bytes) + bytearray(reg_bytes)}

        # Override new field of reg
        for ret_bytes in ret_dict.values():
            shift_bytes = 15
            for half_chain in range(2):
                # Capture [2:17], [17:33] for IC 4,3 and IC 2,1
                fetch_bytes = ret_bytes[2+shift_bytes*half_chain : 2+shift_bytes*(half_chain+1)]
                # print(fetch_bytes)
                half_payload = int.from_bytes(fetch_bytes, 'big')

                # Enable assigned channel in the assigned IC
                ic_current = (1-half_chain)*2 + (ic-1)%2 + 1
                # print(f"IC: {ic_current}")
                if ic_current == ic:
                    print(f"Target IC: {ic}")
                    if ic % 2 > 0:
                        payload = half_payload & 0xFFFFFFFFFFFF
                    else:
                        payload = (half_payload >> 60) & 0xFFFFFFFFFFFF
                    # print("[Addr:0x%04X][Chain_%d][IC_%d] Get Payload: 0x%06X" %(reg_addr_hex, chain, ic, payload))

                    en_hex = Register48(payload).set_field(dis, 44+channel-1, 1)
                    en_hex = Register48(en_hex).set_field(com, 40, 4)
                    (start_bit, size) = get_reg_fields(reg_addr_hex, 'rf'+str(channel)+'_gain')
                    en_hex = Register48(en_hex).set_field(ele, start_bit, size)
                    (start_bit, size) = get_reg_fields(reg_addr_hex, 'rf'+str(channel)+'_phase')
                    en_hex = Register48(en_hex).set_field(phase, start_bit, size)
                    print("[Addr:0x%04X][Chain_%d][IC_%d] Set Payload: 0x%06X" %(reg_addr_hex, chain, ic, en_hex))

                    en_hex |= (reg_addr_hex << 48)

                    # Only focus the target IC/channel to write, other ICs not assign reg addr to skip written
                    if ic % 2 > 0:
                        # IC 1 or 3
                        reg_hex = en_hex
                    else:
                        # IC 2 or 4
                        reg_hex = en_hex << 60
                else:
                    # print("not change")
                    reg_hex = 0

                reg_bytes = reg_hex.to_bytes(15, 'big')
                out_pattern += bytearray(reg_bytes)
    else:
        # Every time to write a new pattern

        dis = 0xF
        print("Control Reg: 0x%03X(%d)" %(reg_addr_hex, reg_addr_hex))

        # Default disable
        reg_ic_default = (reg_addr_hex << 48 | dis << 44)
        for half_chain in range(2):
            # IC 4,3 and IC 2,1

            # Enable assigned channel in the assigned IC
            ic_current = (1-half_chain)*2 + (ic-1)%2 +1
            print(f"Current IC: {ic_current}")
            if ic_current == ic:
                en_bit = dis ^ (1 << (channel-1))
                en_hex = Register48(0).set_field(en_bit, 44, 4)
                en_hex = Register48(en_hex).set_field(com, 40, 4)
                (start_bit, size) = get_reg_fields(reg_addr_hex, 'rf'+str(channel)+'_gain')
                en_hex = Register48(en_hex).set_field(ele, start_bit, size)
                (start_bit, size) = get_reg_fields(reg_addr_hex, 'rf'+str(channel)+'_phase')
                en_hex = Register48(en_hex).set_field(phase, start_bit, size)

                if ic % 2 > 0:
                    # IC 1 or 3
                    reg_hex = reg_ic_default << 60 | (reg_addr_hex << 48 | en_hex)
                else:
                    # IC 2 or 4
                    reg_hex = (reg_addr_hex << 48 | en_hex) << 60 | reg_ic_default
            else:
                # print("dis")
                reg_hex = reg_ic_default << 60 | reg_ic_default

            reg_bytes = reg_hex.to_bytes(15, 'big')
            out_pattern += bytearray(reg_bytes)

    spi_transfer(devA, devB, out_pattern)

def setBficGeneralConfig(addr, value, start_bit, size):
    print(f"==== Set BFIC Reg: {addr:0X}, Value: {value} at bit: {start_bit} ====")

    ret_dict = getBficConfig(addr)
    # print(ret_dict)

    print(f"\r\n==== Modify BFIC Reg ====\r\n")
    for chain_num, ret_bytes in ret_dict.items():
        out_pattern = bytearray(header_list[chain_num-1])

        ic_idx = 0
        shift_bytes = 15
        for half_chain in range(2):
            # Capture [2:18], [17:33]
            fetch_bytes = ret_bytes[2+shift_bytes*half_chain : 2+shift_bytes*(half_chain+1)]
            # print(fetch_bytes)
            half_payload = int.from_bytes(fetch_bytes, 'big')

            # IC:4 or IC:2
            payload = (half_payload >> 60) & 0xFFFFFFFFFFFF
            reg_hex = addr << 48 | Register48(payload).set_field(value, start_bit, size)
            print("[Addr:0x%04X][Chain_%d][IC_%d] Set Payload: 0x%06X" %(addr, chain_num, 4-ic_idx, reg_hex & 0xFFFFFFFFFFFF))
            ic_idx += 1
            print_reg_fields(addr, reg_hex & 0xFFFFFFFFFFFF)

            # IC:3 or IC:1
            payload = half_payload & 0xFFFFFFFFFFFF
            reg_hex = reg_hex << 60 | addr << 48 | Register48(payload).set_field(value, start_bit, size)
            print("[Addr:0x%04X][Chain_%d][IC_%d] Set Payload: 0x%06X" %(addr, chain_num, 4-ic_idx, reg_hex & 0xFFFFFFFFFFFF))
            ic_idx += 1
            print_reg_fields(addr, reg_hex & 0xFFFFFFFFFFFF)

            # combine a 15 byte
            reg_bytes = reg_hex.to_bytes(15, 'big')
            out_pattern += bytearray(reg_bytes)

        spi_transfer(devA, devB, out_pattern)

def setBficMode(zcal:bool, pdet_trig:bool, atc:bool, rxip3:int)->bool:
    print(f"==== Mode config: zcal:{zcal}, pdet:{pdet_trig}, rxip3:{rxip3} ====")

    addr = 0x002
    if zcal is not None:
        ret = get_reg_fields(addr, 'zcal')
        if not ret:
            return
        (start_bit, size) = ret
        setBficGeneralConfig(addr, zcal, start_bit, size)

    if pdet_trig is not None:
        ret = get_reg_fields(addr, 'pdet')
        if not ret:
            return
        (start_bit, size) = ret
        setBficGeneralConfig(addr, pdet_trig, start_bit, size)

    if atc is not None:
        ret = get_reg_fields(addr, 'atc')
        if not ret:
            return
        (start_bit, size) = ret
        setBficGeneralConfig(addr, atc, start_bit, size)

    if rxip3 is not None:
        ret = get_reg_fields(addr, 'rxip3_a')
        if not ret:
            return
        (start_bit, size) = ret
        setBficGeneralConfig(addr, rxip3, start_bit, size)
        setBficGeneralConfig(addr, rxip3, start_bit+size, size)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    mode_group = parser.add_argument_group(title="Mode Control cmds")
    mode_group.add_argument("--zcal", help="Enable Zcal", type=int)
    mode_group.add_argument("--pdet", help="Set PDET, trigger must from 0 to 1", type=int)
    mode_group.add_argument("--atc", help="Enable ATC", type=int)
    mode_group.add_argument("--rxip3", help="Set att of RXIP3(0-63)", type=int)

    control_group = parser.add_argument_group(title="Beam Control cmds")
    control_group.add_argument("--jio_hw_ver", help="Jio HW version, default:2.2", type=float, default=2.2)
    control_group.add_argument("--dis", help="Disable all ICs", type=bool, default=False)
    control_group.add_argument("--ic", help="Enable specific ICs(1-8), Please disable all ICs in the previous cmd", type=int)
    control_group.add_argument("--pol", help="Polorization(0:H,1:V,2:H+V), default:2", type=int, default=2)
    control_group.add_argument("--com", help="T/R att com gain step(0-15), default:15", type=int, default=15)
    control_group.add_argument("--ele", help="T/R att ele gain step(0-15), default:15", type=int, default=15)

    channel_group = parser.add_argument_group('channel')
    channel_group.add_argument('--channel', action='store_true', help='channel config')
    channel_group.add_argument('_chain', type=int, nargs='?', help='daisy-chain number(1-2)')
    channel_group.add_argument('_ic', type=int, nargs='?', help='BFIC(1-4) in the daisy-chain')
    channel_group.add_argument('_channel', type=int, nargs='?', help='Channel(1-4) in the BFIC')
    channel_group.add_argument("_tr", help="T/R mode(0:T, 1:R), default:0", type=int, nargs='?', default=0)
    channel_group.add_argument("_pol", help="Polorization(0:H, 1:V), default:0", type=int, nargs='?', default=0)
    channel_group.add_argument("_dis", help="Disable channel(0:enable, 1:disable, default:0", type=int, nargs='?', default=0)
    channel_group.add_argument("_com", help="att com gain step(0-15), default:0", type=int, nargs='?', default=0)
    channel_group.add_argument("_ele", help="att ele gain step(0-15), default:0", type=int, nargs='?', default=0)
    channel_group.add_argument("_phase", help="T/R att ele gain step(0-63), default:0", type=int, nargs='?', default=0)

    parser.add_argument("--ver", action='store_true', help="Get the version")#, action='version', version='%(prog)s: v'+jio_ver())
    parser.add_argument("--get", help="Get reg info with for the assigned reg", type=hex_int_type)
    args = parser.parse_args()

    # 如果沒有提供任何參數，顯示 --help 的內容
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    # print(args.zcal, args.pdet, args.atc)
    # print(any([args.zcal, args.pdet, args.atc]))

    init_reg_table()

    devA, devB = initialize_ft4222()
    if devA:
        if args.ver is not None and args.ver is True:
            print(jio_ver(devA, devB))
        elif args.get is not None:
            getBficConfig(args.get)
        elif any([args.zcal, args.pdet, args.atc, args.rxip3]):
            setBficMode(args.zcal, args.pdet, args.atc, args.rxip3)
        elif args.ic is not None and 1 <= args.ic <= 8:
            setBficBeam(args.dis, args.pol, args.com, args.ele, args.ic, args.jio_hw_ver)
        elif args.channel:
            if not args._chain or not args._ic or not args._channel:
                parser.error("--channel requires chain,ic and channel")
            setBficChannel(args._chain, args._ic, args._channel, args._tr, args._pol, args._dis, args._com, args._ele, args._phase)
        elif any([args.dis, args.pol, args.com, args.ele]) is not None:
            setBficBeam(args.dis, args.pol, args.com, args.ele, 0, args.jio_hw_ver)

    close_ft4222(devA, devB)