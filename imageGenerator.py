from PIL import Image

def tambahkanMahkota(croppedImage, posisiQueen, N, pathOutput):
    image = Image.fromarray(croppedImage[:, :, ::-1])

    lebar, tinggi = image.size
    sel_w = lebar // N
    sel_h = tinggi // N

    mahkotaGambar = Image.open("assets/crown.png").convert("RGBA")

    skala = 0.6
    w_baru = int(sel_w * skala)
    h_baru = int(sel_h * skala)

    mahkota = mahkotaGambar.resize((w_baru, h_baru), Image.LANCZOS)

    for baris in range(N):
        kolom = posisiQueen[baris]

        tengah_x = kolom * sel_w + sel_w // 2
        tengah_y = baris * sel_h + sel_h // 2

        x = tengah_x - w_baru // 2
        y = tengah_y - h_baru // 2

        image.paste(mahkota, (x, y), mahkota)
    
    image.save(pathOutput)