
def open_utf8_reading(filepath):
    return open(filepath, mode="r", encoding="utf-8")

def open_utf8_writing(filepath):
    return open(filepath, mode="w", encoding="utf-8", newline="\n")
