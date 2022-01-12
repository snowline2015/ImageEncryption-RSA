import random
import numpy as np
from PIL import Image
import cv2


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


def RSA_key_generation(length=2):
    p = q = 0
    while p == 0 or q == 0:
        temp = random.randint(0, 10 ** length)
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


def power(a,d,n):
    ans = 1
    while d != 0:
        if d % 2 == 1:
            ans = ((ans % n)*(a % n)) % n
        a = ((a % n) * (a % n)) % n
        d >>= 1
    return ans


def encrypt_image(img_path, E, N):
    img = cv2.imread(img_path, cv2.IMREAD_COLOR)
    row, col = img.shape[0], img.shape[1]
    enc = [[0 for x in range(3000)] for y in range(3000)]

    for i in range(0, row):
        for j in range(0, col):
            r, g, b = img[i, j]
            C1 = power(r, E, N)
            C2 = power(g, E, N)
            C3 = power(b, E, N)
            enc[i][j] = [C1, C2, C3]
            C1 = C1 % 256
            C2 = C2 % 256
            C3 = C3 % 256
            img[i, j] = [C1, C2, C3]
    # cv2.imshow("image", img)
    # cv2.waitKey(0)
    return img, img.shape, enc


def decrypt_image(img_shape, enc, D, N):
    row, col = img_shape[0], img_shape[1]
    img = np.empty((row, col, 3))
    for i in range(0, row):
        for j in range(0, col):
            r, g, b = enc[i][j]
            M1 = power(r, D, N)
            M2 = power(g, D, N)
            M3 = power(b, D, N)
            img[i, j] = [M1, M2, M3]
    img = img.astype(np.uint8)
    # cv2.imshow("image", img)
    # cv2.waitKey(0)
    return img


# e, n, d = RSA_key_generation()
# print("\nPublic key (e, n):")
# print("\te = ", e)
# print("\tn = ", n)
# print("\nPrivate key (d, n):")
# print("\td = ", d)
# print("\tn = ", n)



