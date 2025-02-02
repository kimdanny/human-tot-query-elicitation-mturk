import base64


def encode(filename):
    # Encode the filename to Base64
    encoded_filename = base64.b64encode(filename.encode("utf-8")).decode("utf-8")
    return encoded_filename


def decode(encoded_filename):
    # Decode the Base64-encoded filename
    decoded_filename = base64.b64decode(encoded_filename).decode("utf-8")
    return decoded_filename
