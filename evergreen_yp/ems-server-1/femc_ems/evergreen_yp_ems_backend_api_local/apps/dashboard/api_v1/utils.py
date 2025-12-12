def modbus_type(event_type):
    if event_type == 'A':
        start_address = 6001  # 開關機
    elif event_type == 'B':
        start_address = 6003  # 手動關離網模式
    elif event_type == 'C':
        start_address = 6004  # 主動孤島
    else:
        raise NotImplementedError
    return start_address
