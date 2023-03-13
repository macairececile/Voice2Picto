import urllib.request
import json
import codecs
import os


def check_connection():
    """Function to check if there is an activated internet connection"""

    try:
        urllib.request.urlopen("http://google.com")
        return True
    except:
        return False


def clean_transcription(data):
    """Function to clean the transcription received from the ASR model"""

    result = json.loads(data)
    return result.get("partial", "")


def load_text_from_file(file_path):
    """Function to load a text file"""

    with codecs.open(file_path, encoding="utf-8") as f:
        text = f.read()

    f.close()
    return text


def digit_format(number):
    """Function to get a particular format for files"""

    if number < 10:
        return "000" + str(number)
    elif number < 100:
        return "00" + str(number)
    elif number < 1000:
        return "0" + str(number)
    elif number < 10000:
        return str(number)


def get_key_from_value(d, val):
    """Function to return the key by value"""

    keys = [k for k, v in d.items() if v == val]
    if keys:
        return keys[0]
    return None


def clear_tmp_files():
    """
    Function to clear files in the tmp repository
    """

    directory = "tmp"

    # Removing each file from the directory tmp
    for filename in os.listdir(directory):

        f = os.path.join(directory, filename)

        if os.path.isfile(f):
            os.remove(f)
