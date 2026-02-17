import cv2
import numpy as np
from PIL import Image

def gambarKeMatriks(croppedImage, N):
    tinggi, lebar, _ = croppedImage.shape
    sel_h = tinggi // N
    sel_w = lebar // N

    gambarFix = croppedImage // 32 * 32

    warnaSel = []
    for i in range(N):
        baris = []
        for j in range(N):
            y1 = i * sel_h
            y2 = y1 + sel_h
            x1 = j * sel_w
            x2 = x1 + sel_w

            area = gambarFix[y1:y2, x1:x2]
            
            warnaTengah = np.median(area.reshape(-1, 3), axis=0)
            baris.append(warnaTengah)
        warnaSel.append(baris)
    
    warnaSel = np.array(warnaSel)

    matriks = [[-1 for _ in range(N)] for _ in range(N)]
    idWilayah = 0
    threshold = 40
    
    def cariAreaSama(i, j, idWilayah, warnaAcuan):
        stack = [(i, j)]
        
        while stack:
            ci, cj = stack.pop()
            if ci < 0 or ci >= N or cj < 0 or cj >= N:
                continue
            if matriks[ci][cj] != -1:
                continue

            perbedaanWarna = np.linalg.norm(warnaSel[ci][cj] - warnaAcuan)
            if perbedaanWarna > threshold:
                continue
            
            matriks[ci][cj] = idWilayah
            
            stack.append((ci-1, cj))
            stack.append((ci+1, cj))
            stack.append((ci, cj-1))
            stack.append((ci, cj+1))

    for i in range(N):
        for j in range(N):
            if matriks[i][j] == -1:
                cariAreaSama(i, j, idWilayah, warnaSel[i][j])
                idWilayah += 1
    
    return matriks

class ImageCropper:
    def __init__(self, lebarKanvas=450, tinggiKanvas=450):
        self.lebarKanvas = lebarKanvas
        self.tinggiKanvas = tinggiKanvas
        self.originalImageCv = None
        self.originalImagePil = None
        self.skala = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.lebarBaru = 0
        self.tinggiBaru = 0
    
    def loadImage(self, image_path):
        self.originalImageCv = cv2.imread(image_path)
        if self.originalImageCv is None:
            raise ValueError("Gambar tidak dapat dibaca")

        image_RGB = cv2.cvtColor(self.originalImageCv, cv2.COLOR_BGR2RGB)
        self.originalImagePil = Image.fromarray(image_RGB)

        lebarGambar, tinggiGambar = self.originalImagePil.size
        self.skala = min(self.lebarKanvas / lebarGambar, self.tinggiKanvas / tinggiGambar)
        self.lebarBaru = int(lebarGambar * self.skala)
        self.tinggiBaru = int(tinggiGambar * self.skala)
        
        self.offset_x = (self.lebarKanvas - self.lebarBaru) // 2
        self.offset_y = (self.tinggiKanvas - self.tinggiBaru) // 2

        perubahanUkuran = self.originalImagePil.resize((self.lebarBaru, self.tinggiBaru), Image.Resampling.LANCZOS)
        
        display_info = {
            'skala': self.skala,
            'offset_x': self.offset_x,
            'offset_y': self.offset_y,
            'display_width': self.lebarBaru,
            'display_height': self.tinggiBaru
        }
        
        return perubahanUkuran, self.originalImageCv, display_info
    
    def canvasToImageCoords(self, kanvas_x1, kanvas_y1, kanvas_x2, kanvas_y2):
        if self.originalImageCv is None:
            raise ValueError("Tidak ada gambar yang dimuat")
        if kanvas_x1 > kanvas_x2:
            kanvas_x1, kanvas_x2 = kanvas_x2, kanvas_x1
        if kanvas_y1 > kanvas_y2:
            kanvas_y1, kanvas_y2 = kanvas_y2, kanvas_y1

        original_x1 = int((kanvas_x1 - self.offset_x) / self.skala)
        original_y1 = int((kanvas_y1 - self.offset_y) / self.skala)
        original_x2 = int((kanvas_x2 - self.offset_x) / self.skala)
        original_y2 = int((kanvas_y2 - self.offset_y) / self.skala)

        tinggiGambar, lebarGambar = self.originalImageCv.shape[:2]
        original_x1 = max(0, min(original_x1, lebarGambar))
        original_y1 = max(0, min(original_y1, tinggiGambar))
        original_x2 = max(0, min(original_x2, lebarGambar))
        original_y2 = max(0, min(original_y2, tinggiGambar))
        
        return original_x1, original_y1, original_x2, original_y2
    
    def cropImage(self, x1, y1, x2, y2):
        if self.originalImageCv is None:
            raise ValueError("Tidak ada gambar yang dimuat")
        
        cropped = self.originalImageCv[y1:y2, x1:x2]
        
        if cropped.size == 0:
            raise ValueError("Area crop terlalu kecil")
        
        return cropped
    
    def processImage(self, cropped_image, N):
        if N > 26:
            raise ValueError("Ukuran N maksimal adalah 26 (sesuai dengan jumlah huruf A-Z)")
        
        matriks = gambarKeMatriks(cropped_image, N)

        unique_regions = set()
        for row in matriks:
            for region_id in row:
                unique_regions.add(region_id)
        
        jumlah_region = len(unique_regions)
        if jumlah_region != N:
            raise ValueError(f"Jumlah region yang terdeteksi ({jumlah_region}) harus sama dengan N ({N}). Input tidak valid!")
        
        regionColors = self.ekstrakWilayahWarna(cropped_image, N, matriks)
        huruf_awal = ord('A')
        hurufAsli = []

        for i in range(N):
            row = []
            for j in range(N):
                region_id = matriks[i][j]
                row.append(chr(huruf_awal + region_id))
            hurufAsli.append(row)
        
        return matriks, regionColors, hurufAsli
    
    def ekstrakWilayahWarna(self, croppedImage, N, matriks):
        tinggi, lebar = croppedImage.shape[:2]
        sel_h = tinggi // N
        sel_w = lebar // N
        gambarFix = croppedImage // 32 * 32
        warnaSel = []

        for i in range(N):
            baris = []
            for j in range(N):
                y1 = i * sel_h
                y2 = y1 + sel_h
                x1 = j * sel_w
                x2 = x1 + sel_w
                area = gambarFix[y1:y2, x1:x2]
                warnaTengah = np.median(area.reshape(-1, 3), axis=0)
                baris.append(warnaTengah)
            warnaSel.append(baris)
        warnaSel = np.array(warnaSel)
        regionColors = {}

        for i in range(N):
            for j in range(N):
                region_id = matriks[i][j]
                if region_id not in regionColors:
                    regionColors[region_id] = "#{:02x}{:02x}{:02x}".format(
                        int(warnaSel[i][j][2]),
                        int(warnaSel[i][j][1]),
                        int(warnaSel[i][j][0])
                    )
        return regionColors