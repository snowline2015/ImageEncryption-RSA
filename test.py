import cv2
import numpy as np
import matplotlib.pyplot as plt


E, N, D = 6073, 6557, 4297


my_img = cv2.imread('test.jpg', cv2.IMREAD_COLOR)
# cv2.imshow("", my_img)
# cv2.waitKey(0)

# plt.imshow(my_img, cmap="gray")

def power(a,d,n):
  ans=1
  while d!=0:
    if d%2==1:
      ans=((ans%n)*(a%n))%n
    a=((a%n)*(a%n))%n
    d>>=1
  return ans

row,col=my_img.shape[0],my_img.shape[1]
enc = [[0 for x in range(3000)] for y in range(3000)]


for i in range(0,row):
  for j in range(0,col):
    r,g,b=my_img[i,j]
    C1=power(r,E,N)
    C2=power(g,E,N)
    C3=power(b,E,N)
    enc[i][j]=[C1,C2,C3]
    C1=C1%256
    C2=C2%256
    C3=C3%256
    my_img[i,j]=[C1,C2,C3]

cv2.imshow("", my_img)
cv2.waitKey(0)


for i in range(0,row):
  for j in range(0,col):
    r,g,b=enc[i][j]
    M1=power(r,D,N)
    M2=power(g,D,N)
    M3=power(b,D,N)
    my_img[i,j]=[M1,M2,M3]

cv2.imshow("", my_img)
cv2.waitKey(0)

# f = open("haha.txt", "r")
# print(f.read()[:10000])