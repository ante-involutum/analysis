import re


def time_to_float(time_str):
    h, m, s = time_str.strip().split(":")
    return float(h) * 3600 + float(m) * 60 + float(s)


def msg_to_dict(msg):
    _ = msg.replace(" ", "")

    if 'summary' in _ and 'Avg' in _:
        values = re.compile(
            r"summary.(\d*)in(.*)=(.*)Avg:(\d*)Min:(\d*)Max:(\d*)Err:(\d*)(.*)"
        ).findall(_)[0]

        result = {
            'summary': float(values[0]),
            'duration_time': time_to_float(values[1]),
            'rps': float(values[2].replace("/s", "")),
            'avg': float(values[3]),
            'min': float(values[4]),
            'max': float(values[5]),
            'erro': float(values[6]),
        }
    else:
        result = {
            'summary': 0,
            'duration_time': 0,
            'rps': 0,
            'avg': 0,
            'min': 0,
            'max': 0,
            'erro': 0,
        }
    return result
