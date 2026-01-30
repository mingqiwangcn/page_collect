import os
import json

def write_text_sync(out_file, text):
    """
     Append a line of text to a file synchronously
    """
    with open(out_file, "a", encoding="utf-8") as f_o:
        f_o.write(text + "\n")

def read_json(file_path):
    """
     Load and a JSON file from disk
    """
    with open(file_path) as f:
        return json.load(f)
