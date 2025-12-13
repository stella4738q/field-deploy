def convert_to_uint_16(value):
    if value == -1:
        return 65535
    elif value < 0:
        return 65536 + value
    else:
        return value


def power_cal(current_soc, target_soc, total_charge_hour, total_power):
    power = (current_soc - target_soc)/100*total_power/total_charge_hour
    return power


def lc_set_power(client, value):
    value = int(round(value * 10, 0))
    if value >= 0:
        sign = 0
    else:
        value = convert_to_uint_16(value)
        sign = convert_to_uint_16(-1)
    client.write_multiple_registers(10126, [value, sign])

