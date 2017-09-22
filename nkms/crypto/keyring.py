import sha3
from nacl.utils import random
from nkms.crypto.keypairs import SigningKeypair, EncryptingKeypair
from nkms.crypto import (default_algorithm, pre_from_algorithm,
                         symmetric_from_algorithm)


class KeyRing(object):
    def __init__(self, sig_privkey=None, enc_privkey=None):
        """
        Initializes a KeyRing object. Uses the private keys to initialize
        their respective objects, if provided. If not, it will generate new
        keypairs.

        :param bytes sig_privkey: Private key in bytes of ECDSA signing keypair
        :param bytes enc_privkey: Private key in bytes of encrypting keypair
        """
        self.sig_keypair = SigningKeypair(sig_privkey)
        self.enc_keypair = EncryptingKeypair(enc_privkey)
        self.pre = pre_from_algorithm(default_algorithm)

    @property
    def sig_pubkey(self):
        return self.sig_keypair.pub_key

    @property
    def sig_privkey(self):
        return self.sig_keypair.priv_key

    @property
    def enc_pubkey(self):
        return self.enc_keypair.pub_key

    @property
    def enc_privkey(self):
        return self.enc_keypair.priv_key

    def sign(self, message):
        """
        Signs a message and returns a signature with the keccak hash.

        :param bytes message: Message to sign in bytes

        :rtype: bytestring
        :return: Signature of message
        """
        msg_digest = sha3.keccak_256(message).digest()
        return self.sig_keypair.sign(msg_digest)

    def verify(self, message, signature, pubkey=None):
        """
        Verifies a signature.

        :param bytes message: Message to check signature for
        :param bytes signature: Signature to validate
        :param bytes pubkey: Pubkey to validate signature with
                             Default is the sig_keypair's pub_key

        :rtype: Boolean
        :return: Is the message signature valid or not?
        """
        if not pubkey:
            pubkey = self.sig_keypair.pub_key
        msg_digest = sha3.keccak_256(message).digest()
        return self.sig_keypair.verify(msg_digest, signature, pubkey=pubkey)

    def encrypt(self, plaintext, pubkey=None):
        """
        Encrypts the plaintext provided.

        :param bytes plaintext: Plaintext to encrypt w/ EncryptingKeypair
        :param bytes pubkey: Pubkey to encrypt for

        :rtype: bytes
        :return: Ciphertext of plaintext
        """
        if not pubkey:
            pubkey = self.enc_keypair.pub_key
        return self.enc_keypair.encrypt(plaintext, pubkey=pubkey)

    def decrypt(self, ciphertext):
        """
        Decrypts the ciphertext provided.

        :param bytes ciphertext: Ciphertext to decrypt w/ EncryptingKeypair

        :rtype: bytes
        :return: Plaintext of Encrypted ciphertext
        """
        return self.enc_keypair.decrypt(ciphertext)

    def secure_random(self, length):
        """
        Generates a bytestring from a secure random source for keys, etc.

        :params int length: Length of the bytestring to generate.

        :rtype: bytes
        :return: Secure random generated bytestring of <length> bytes
        """
        return random(length)

    def derive_path_key(self, path, is_pub=True):
        """
        Derives a key for the specific path.

        :param bytes path: Path to generate the key for
        :param bool is_pub: Is the derived key a public key?

        :rtype: bytes
        :return: Derived key
        """
        key = sha3.keccak_256(self.enc_privkey + path).digest()
        return self.pre.priv2pub(key) if is_pub else key
