def get_settings(settings, key):
    df = settings[settings['key'] == key]
    if df.empty:
        return None
    return df.iloc[0]['value']
