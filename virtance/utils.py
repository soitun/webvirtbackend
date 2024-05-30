from io import StringIO
from random import choice
from paramiko import RSAKey
from django.conf import settings
from cryptography.fernet import Fernet
from string import digits, ascii_letters
from base64 import b64encode, b64decode, urlsafe_b64decode


from .models import VirtanceError, VirtanceHistory


NOVNC_PASSWD_PREFIX = settings.NOVNC_PASSWD_PREFIX_LENGHT
NOVNC_PASSWD_SUFFIX = settings.NOVNC_PASSWD_SUFFIX_LENGHT


def is_valid_fernet_key(key):
    try:
        decoded_key = urlsafe_b64decode(key)
        return len(decoded_key) == 32
    except Exception:
        return False


def make_passwd(length=8):
    phrase = ""
    for _ in range(length):
        phrase += choice(f"{digits}{ascii_letters}")
    return phrase


def make_ssh_key():
    private_key = RSAKey.generate(bits=2048)
    private_key_string = StringIO()
    private_key.write_private_key(private_key_string)
    return private_key_string.getvalue()


def encrypt_data(data, key=None):
    if key and not is_valid_fernet_key(key):
        key = settings.ENCRYPTION_KEY
    cipher = Fernet(key.encode())
    encrypted_data = cipher.encrypt(data)
    encoded_encrypted_data = b64encode(encrypted_data).decode()
    return encoded_encrypted_data


def decrypt_data(data, key=None):
    if key and not is_valid_fernet_key(key):
        key = settings.ENCRYPTION_KEY
    cipher = Fernet(key.encode())
    decoded_encrypted_data = b64decode(data)
    decrypted_data = cipher.decrypt(decoded_encrypted_data)
    return decrypted_data.decode()


def make_vnc_hash(vnc_password, prefix_length=NOVNC_PASSWD_PREFIX, suffix_length=NOVNC_PASSWD_SUFFIX):
    return b64encode((f"{make_passwd(prefix_length)}{vnc_password}{make_passwd(suffix_length)}").encode())


def virtance_history(virtance_id, user_id, event, message=None):
    VirtanceHistory.objects.create(virtance_id=virtance_id, user_id=user_id, message=message, event=event)


def virtance_error(virtance_id, message, event=None):
    VirtanceError.objects.create(virtance_id=virtance_id, message=message, event=event)
