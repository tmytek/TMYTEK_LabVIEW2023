import argparse

reg_addr_table = {}

class Register48:
    def __init__(self, reg_payload):
        self._reg_payload = reg_payload

    def set_field(self, value, offset, size):
        """設置指定欄位的值"""
        mask = (1 << size) - 1
        self._reg_payload &= ~(mask << offset)
        self._reg_payload |= (value & mask) << offset
        return self._reg_payload

    def get_field(self, offset, size):
        """獲取指定欄位的值"""
        mask = (1 << size) - 1
        return (self._reg_payload >> offset) & mask

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

def get_reg_fields(reg_addr, key_field_name):
    """
    Search key field name to return start

    Args:
        reg_addr (_type_)      : register address
        key_field_name (_type_): Field name to search

    Returns:
        tuple: (start_bit, size)
    """
    if not reg_addr_table.get(reg_addr):
        print("Can not find this register")
        return False

    for field_name, info in reg_addr_table[reg_addr].items():
        if field_name.lower().__contains__(key_field_name):
            return (info['offset'], info['size'])

    return False

def hex_int_type(value):
    try:
        ret = 0
        if value.startswith("0x"):
            ret = int(value, 16)
        else:
            ret = int(value)
        print("\'%s\' -> hex(int): 0x%03X(%d)" %(value, ret, ret))
        return ret
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid hex value: {value}")
