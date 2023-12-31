from cryptography.fernet import Fernet


def encrypt_image(image_bytes, key):
    cipher_suite = Fernet(key)
    cipher_image_bytes = cipher_suite.encrypt(image_bytes)
    return cipher_image_bytes


def decrypt_image(cipher_image_bytes, key):
    cipher_suite = Fernet(key)
    plain_image_bytes = cipher_suite.decrypt(cipher_image_bytes)
    return plain_image_bytes


def encrypt_text(text, key):
    cipher_suite = Fernet(key)
    cipher_text = cipher_suite.encrypt(text.encode('utf-8'))
    return cipher_text


def decrypt_text(cipher_text, key):
    cipher_suite = Fernet(key)
    plain_text = cipher_suite.decrypt(cipher_text).decode('utf-8')
    return plain_text


# Generate a key for encryption and decryption on the server
def generate_keys():
    server_key = Fernet.generate_key()
    with open('server_key.txt', 'wb') as key_file:
        key_file.write(server_key)


def read_keys(path_key='server_key.txt'):
    with open(path_key, 'rb') as key_file:
        server_key = key_file.read()
    return server_key
