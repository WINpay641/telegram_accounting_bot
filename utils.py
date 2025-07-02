import re

def parse_amount(text):
    try:
        match = re.search(r"[-+]?\d+(\.\d+)?", text)
        return float(match.group()) if match else None
    except:
        return None
