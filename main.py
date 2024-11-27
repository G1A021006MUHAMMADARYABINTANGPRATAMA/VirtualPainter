import HandTrackingModule as htm
import cv2
import numpy as np
import os
import time

# Folder untuk gambar header
folder = "Header"
video = cv2.VideoCapture(0)
list_files = os.listdir(folder)  # Ambil daftar file dari folder Header
overlayList = []
video.set(3, 1280)  # Set lebar frame kamera
video.set(4, 720)   # Set tinggi frame kamera

# Memuat gambar dari folder Header
for i in list_files:
    image = cv2.imread(f"{folder}/{i}")
    overlayList.append(image)

header = overlayList[0]  # Default header pertama
detector = htm.handDetector(detectionCon=0.85, maxHands=1)
drawColor = (255, 0, 255)  # Warna default (ungu)
eraserThickness = 50
delay_start = None
shape = 'freestyle'  # Bentuk default
imgcanvas = np.zeros((720,1280,3), np.uint8)
xp, yp = 0, 0  # Inisialisasi variabel xp dan yp

# Mengaktifkan kamera
while True:
    success, img = video.read()
    img = cv2.flip(img, 1)  # Membalik frame secara horizontal
    img = detector.findHands(img)  # Mendeteksi tangan
    pos, bbox = detector.findPosition(img)  # Ambil posisi landmark dan bounding box

    # Validasi apakah landmark 8 (ujung jari telunjuk) tersedia
    if pos and len(pos) > 12:
        x1, y1 = pos[8][1:]  # Landmark ID 8 (ujung jari telunjuk)
        xm, ym = pos[12][1:]  # Landmark ID 12 (ujung jari tengah)
        up = detector.fingersUp()  # Deteksi jari yang diangkat
        xt,yt = pos[4][1:]
        dist = int((((yt-y1)**2)+((xt-x1)**2))**0.5)

        # Logika untuk memilih warna atau bentuk
        if up[1] and up[2]:  # Jari telunjuk dan tengah terangkat
            if y1 < 120:  # Area menu atas
                if 250 < x1 < 450:
                    header = overlayList[0]
                    drawColor = (255, 0, 255)
                elif 550 < x1 < 750:
                    header = overlayList[1]
                    drawColor = (255, 0, 0)
                elif 800 < x1 < 950:
                    header = overlayList[2]
                    drawColor = (0, 255, 0)
                elif 1050 < x1 < 1200:
                    header = overlayList[5]
                    drawColor = (0, 0, 0)

            elif 120 <= y1 < 210:  # Area pemilihan bentuk
                if x1 < 250:
                    header = overlayList[9]

                elif 250 < x1 < 450 and drawColor == (255, 0, 255):
                    header = overlayList[0]
                    shape = 'freestyle'
                elif 550 < x1 < 750 and drawColor == (255, 0, 255):
                    header = overlayList[6]
                    shape = 'circle'
                elif 800 < x1 < 950 and drawColor == (255, 0, 255):
                    header = overlayList[7]
                    shape = 'rectangle'
                elif 1050 < x1 < 1200 and drawColor == (255, 0, 255):
                    header = overlayList[8]
                    shape = 'ellipse'
                elif 250 < x1 < 450 and drawColor == (255, 0, 0):
                    header = overlayList[10]
                    shape = 'freestyle'
                elif 550 < x1 < 750 and drawColor == (255, 0, 0):
                    header = overlayList[11]
                    shape = 'circle'
                elif 800 < x1 < 950 and drawColor == (255, 0, 0):
                    header = overlayList[12]
                    shape = 'rectangle'
                elif 1050 < x1 < 1200 and drawColor == (255, 0, 0):
                    header = overlayList[13]
                    shape = 'ellipse'
                elif 250 < x1 < 450 and drawColor == (0, 255, 0):
                    header = overlayList[1]
                    shape = 'freestyle'
                elif 550 < x1 < 750 and drawColor == (0, 255, 0):
                    header = overlayList[2]
                    shape = 'circle'
                elif 800 < x1 < 950 and drawColor == (0, 255, 0):
                    header = overlayList[3]
                    shape = 'rectangle'
                elif 1050 < x1 < 1200 and drawColor == (0, 255, 0):
                    header = overlayList[4]
                    shape = 'ellipse'
        
        cv2.circle(img,(x1,y1),30,drawColor,cv2.FILLED)
        
        if up[1] and up[2] == False :
            if xp == 0 and yp == 0 :
                xp, yp = x1, y1
            if drawColor == (0,0,0) :
                if up[1] and up[4] :
                    eraserThickness = dist
                cv2.circle(img,(x1,y1),eraserThickness,drawColor, cv2.FILLED)
                cv2.circle(imgcanvas,(x1,y1),eraserThickness,drawColor, cv2.FILLED)
            else :
                if shape == "freestyle" :
                    cv2.line(imgcanvas, (xp, yp), (x1, y1), drawColor, 10)
                elif shape == "circle" :
                    if xp != 0 and yp != 0:  # Jika titik pusat lingkaran diketahui
                        radius = int(((x1 - xt)**2 + (y1 - yt)**2)**0.5)  
                        cv2.circle(img,(x1,y1),dist,drawColor, 2)
                        if up[4]==1 :
                            if delay_start is None:  # Mulai delay jika belum dimulai
                                delay_start = time.time()
                            elif time.time() - delay_start > 1.5:  # Jika lebih dari 1 detik
                                cv2.circle(imgcanvas,(x1,y1),dist,drawColor, 2)
                                xp, yp = 0, 0  # Reset koordinat
                                delay_start = None  # Reset delay
                    else:
                        delay_start = None 

                elif shape == "rectangle":  # Menggambar persegi panjang
                    if xp != 0 and yp != 0:  # Jika titik awal sudah ditentukan
                        cv2.rectangle(img, (xt, yt), (x1, y1), drawColor, 2)  # Pratinjau
                        if up[4] == 1:  # Jika jari kelingking diangkat, permanenkan
                            if delay_start is None:  # Mulai delay jika belum dimulai
                                delay_start = time.time()
                            elif time.time() - delay_start > 1.5:  # Jika lebih dari 1 detik
                                cv2.rectangle(imgcanvas, (xt, yt), (x1, y1), drawColor, 2)  # Gambar permanen
                                xp, yp = 0, 0  # Reset koordinat
                                delay_start = None  # Reset delay
                    else:
                        delay_start = None  # Reset delay jika jari kelingking tidak diangkat

                elif shape == "ellipse":  # Menggambar elips
                    if xp != 0 and yp != 0:  # Jika titik pusat ellipse diketahui
                        axis_major = abs(x1 - xt)  # Sumbu panjang
                        axis_minor = abs(y1 - yt)  # Sumbu pendek
                        cv2.ellipse(img, (xt, yt), (axis_major, axis_minor), 0, 0, 360, drawColor, 2)  # Pratinjau
                        if up[4] == 1:  # Jika jari kelingking diangkat, permanenkan
                            if delay_start is None:  # Mulai delay jika belum dimulai
                                delay_start = time.time()
                            elif time.time() - delay_start > 1.5:  # Jika lebih dari 1 detik
                                cv2.ellipse(imgcanvas, (xt, yt), (axis_major, axis_minor), 0, 0, 360, drawColor, 2)  # Gambar permanen
                                xp, yp = 0, 0  # Reset koordinat
                                delay_start = None  # Reset delay
                    else:
                        delay_start = None  # Reset delay jika jari kelingking tidak diangkat

        xp, yp = x1, y1

    # Menambahkan header ke frame
    img[0:210, 0:1280] = header

    img_gray = cv2.cvtColor(imgcanvas,cv2.COLOR_BGR2GRAY)
    _,imginv = cv2.threshold(img_gray,50,255,cv2.THRESH_BINARY_INV)
    imginv = cv2.cvtColor(imginv, cv2.COLOR_GRAY2BGR)
    img = cv2.bitwise_and(img, imginv)
    img = cv2.bitwise_or(img, imgcanvas)

    # Tampilkan frame
    cv2.imshow("Virtual Painter (No Mirror)", img)

    # Keluar jika tombol 'q' ditekan
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Melepaskan kamera dan menutup semua jendela
video.release()

cv2.destroyAllWindows()
