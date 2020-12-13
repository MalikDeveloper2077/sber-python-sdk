from binascii import unhexlify

from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA512


def verify_rsa_sha512_checksum(pubkey: str, data: bytes, checksum: str):
    """Verify your data and the callback checksum from SBER.

    Using asymmetric method: RSA SHA512 to encrypt the data
    https://securepayments.sberbank.ru/wiki/doku.php/integration:api:callback:start
    Returns:
        bool: verified or not

    """
    key = RSA.import_key(pubkey)
    signer = PKCS1_v1_5.new(key)
    digest = SHA512.new(data=data)
    return signer.verify(digest, unhexlify(checksum.lower()))


def get_callback_data(request_data: dict) -> str:
    """https://securepayments.sberbank.ru/wiki/doku.php/integration:api:callback:start
    Return data in format: mdOrder;6d7dd3386fe;operation;deposited;orderNumber;10747;status;1;
    """
    data_ignore_keys = ('checksum', 'sign_alias')
    GET_keys = sorted([key for key, val in request_data.items() if key not in data_ignore_keys])

    data = ''
    for key in GET_keys:
        data += f'{key};{request_data.get(key)};'

    return data
