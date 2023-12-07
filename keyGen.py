import logging

from Crypto.Hash import keccak
import random
from string import digits,ascii_lowercase,ascii_uppercase
alph = digits+ascii_uppercase+ascii_lowercase
logging.basicConfig(level=logging.INFO)


def generateKeys(n: int) -> [str]:# - hashes
    hl = []; kl = []
    for i in range(n):
        val = "".join([alph[random.randint(0,26+26+9)] for x in range(256)])
        hash = getHash(val)
        hl.append(hash)
        kl.append(str(i) + "|   " + val + "\n")
    with open("keys.txt", "a") as f: f.writelines(kl); f.close()
    logging.log(20,"Key(s) has(have) been saved to txt and passed to worker")
    return hl


def getHash(key):
    return keccak.new(digest_bits=256).update(key.encode("utf-8")).hexdigest() # -> str - hash