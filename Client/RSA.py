import random
import cv2
from copy import deepcopy


def bezout(a, b, x2=1, x1=0, y2=0, y1=1):
    if a < b:
        a, b = b, a
    if b == 0:
        d, x, y = a, 1, 0
        return d, x, y
    while b:
        q = a//b
        r = a % b
        x, y = x2-q*x1, y2-q*y1
        x2, x1 = x1, x
        y2, y1 = y1, y
        a, b = b, r
    return a, x2, y2


def is_prime(n):
    if n != int(n):
        return False
    n = int(n)
    # Miller-Rabin test for prime
    if n == 0 or n == 1 or n == 4 or n == 6 or n == 8 or n == 9:
        return False
    if n == 2 or n == 3 or n == 5 or n == 7:
        return True
    s = 0
    d = n - 1
    while d % 2 == 0:
        d >>= 1
        s += 1
    assert (2 ** s * d == n - 1)

    def trial_composite(a):
        if pow(a, d, n) == 1:
            return False
        for i in range(s):
            if pow(a, 2 ** i * d, n) == n - 1:
                return False
        return True

    for i in range(8):  # number of trials
        a = random.randrange(2, n)
        if trial_composite(a):
            return False

    return True


def RSA_key_generation():
    p = q = 0
    while p == 0 or q == 0:
        temp = random.randint(0, 10 ** 10)      # Could be 10 ** 128 -> 1024 bits
        if is_prime(temp):
            if p == 0:
                p = temp
            elif len(str(p)) == len(str(temp)):
                q = temp
    n = p*q
    euler = (p-1)*(q-1)
    e = random.randint(2, euler)
    while bezout(e, euler)[0] != 1:
        e = random.randint(2, euler)
    d = bezout(e, euler)[2] % euler
    return e, n, d


def encrypt_image(img, e, n):
    enc = [[0 for x in range(3000)] for y in range(3000)]
    for i in range(100, 700):
        for j in range(100, 1000):
            r, g, b = img[i, j]
            C1 = pow(r, e, n)
            C2 = pow(g, e, n)
            C3 = pow(b, e, n)
            enc[i][j] = [C1, C2, C3]
            C1 = C1 % 256
            C2 = C2 % 256
            C3 = C3 % 256
            img[i, j] = [C1, C2, C3]
    return img


def decrypt_image(encrypted_img, d, n):
    for i in range(100, 700):
        for j in range(100, 1000):
            r, g, b = encrypted_img[i][j]
            M1 = pow(r, d, n)
            M2 = pow(g, d, n)
            M3 = pow(b, d, n)
            encrypted_img[i, j] = [M1, M2, M3]
    return encrypted_img


# e, n, d = RSA_key_generation()
# print("\nPublic key (e, n):")
# print("\te = ", e)
# print("\tn = ", n)
# print("\nPrivate key (d, n):")
# print("\td = ", d)
# print("\tn = ", n)



