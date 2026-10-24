from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.exceptions import InvalidSignature
import os


KEY_FOLDER = "keys"

PRIVATE_KEY_FILE = os.path.join(
    KEY_FOLDER,
    "private_key.pem"
)

PUBLIC_KEY_FILE = os.path.join(
    KEY_FOLDER,
    "public_key.pem"
)


def generate_keys():

    os.makedirs(KEY_FOLDER, exist_ok=True)

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    public_key = private_key.public_key()

    with open(PRIVATE_KEY_FILE, "wb") as file:

        file.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    with open(PUBLIC_KEY_FILE, "wb") as file:

        file.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )


def load_private_key():

    with open(PRIVATE_KEY_FILE, "rb") as file:

        return serialization.load_pem_private_key(
            file.read(),
            password=None
        )


def load_public_key():

    with open(PUBLIC_KEY_FILE, "rb") as file:

        return serialization.load_pem_public_key(
            file.read()
        )


def sign_data(data):

    private_key = load_private_key()

    signature = private_key.sign(

        data.encode("utf-8"),

        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),

        hashes.SHA256()
    )

    return signature


def verify_signature(data, signature):

    public_key = load_public_key()

    try:

        public_key.verify(

            signature,

            data.encode("utf-8"),

            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),

            hashes.SHA256()
        )

        return True

    except InvalidSignature:

        return False