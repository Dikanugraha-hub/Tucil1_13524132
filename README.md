# Tugas Kecil 1 IF2211 Strategi Algoritma
## Implementasi Algoritma Brute Force pada Permasalahan Permainan Queens LinkedIn

---

## General Information

Program ini merupakan implementasi solusi untuk permasalahan **N-Queens** yang terinspirasi dari permainan Queens di LinkedIn. Program menggunakan algoritma **Brute Force** dan **Backtracking** (sebagai pilihan lain supaya tidak terlalu exhaustive search) N×N dengan constraint region (warna) tertentu.

Program dilengkapi dengan **Graphical User Interface (GUI)** yang memungkinkan pengguna untuk:
- Memuat konfigurasi puzzle dari file TXT atau gambar
- Memilih algoritma solving (Brute Force murni atau backtracking dengan optimasi atau tanpa optimasi)
- Memvisualisasikan proses pencarian solusi secara real-time
- Menyimpan solusi dalam format TXT atau PNG

**Constraint:**
- Setiap baris harus memiliki tepat 1 ratu
- Setiap kolom harus memiliki tepat 1 ratu
- Setiap region (warna) harus memiliki tepat 1 ratu

---

## Technology Used

- **Python 3.x** - Bahasa pemrograman utama
- **Tkinter** - Library untuk GUI
- **PIL (Pillow)** - Library untuk image processing dan manipulation
- **Threading** - Untuk menjalankan solver secara asynchronous agar GUI tetap responsif

---

## Contributor

| **NIM**  | **Nama**              |
|:--------:|:---------------------:|
| 13524132 | Dika Pramudya Nugraha |

---

## Project Structure

```
Tucil_1/
│
├── assets/
│   └── crown.png                
│
├── doc/                          
│   ├── laporan
|
├── output/                     
│  
├── testcases/
│   ├── images/                  
│   └── txt/                      
│
├── imageGenerator.py           
├── imageParser.py                
├── papan.py                      
├── solverQueens.py               
├── main_gui.py                   
└── README.md            
```

---

## How to Run GUI

### Prerequisites
Pastikan Python 3.x sudah terinstall di sistem Anda. Install dependencies yang diperlukan:

```bash
pip install pillow
```

### Running the Program

1. **Clone atau download repository ini**

2. **Navigasi ke direktori proyek**

3. **Jalankan program GUI**
   - Windows
      ```bash
      python main_gui.py
      ```
   - Linux
      ```bash
      python3 main_gui.py
      ```

### Using the GUI

1. **Load Input:**
   - Klik **"Load TXT"** untuk memuat file puzzle format TXT
   - Klik **"Load Image"** untuk memuat gambar puzzle, lalu crop area yang diinginkan dan tentukan ukuran grid (N)

2. **Configure Solver:**
   - **Live update (k):** Interval update visualisasi (misal: 100 = update setiap 100 iterasi)
   - **Optimasi:** Centang untuk mengaktifkan optimasi pada algoritma
   - **Mode:** Pilih antara "Backtracking" atau "Brute Force"

3. **Start Solving:**
   - Klik **"Start"** untuk memulai pencarian solusi
   - Lihat proses solving di **OUTPUT BOARD** dan log iterasi di **ITERATION LOG**

4. **Save Solution:**
   - Setelah solusi ditemukan, pilih **"Ya, Simpan"** untuk menyimpan hasil
   - Pilih format TXT atau PNG sesuai kebutuhan

5. **Reset:**
   - Klik **"Reset"** untuk membersihkan board dan memulai dari awal

---

## Additional Notes

### Input Format (TXT)
File TXT harus memiliki format sebagai berikut:
```
AAAA
BBBB
CCCC
DDDD
```
matriks region yang direpresentasikan dengan huruf (A-Z)

### Algorithm Details

**Brute Force:**
- Mencoba semua kemungkinan kombinasi penempatan queen
- Kompleksitas: O(N^N)
- Cocok untuk N kecil (N ≤ 8)

**Backtracking:**
- Menggunakan pruning untuk menghindari pencarian yang tidak perlu
- Kompleksitas lebih baik dari Brute Force
- Dapat dioptimasi dengan constraint checking lebih awal

### Performance Tips
- Untuk N besar (N > 10), gunakan mode Backtracking dengan Optimasi
- Atur live update (k) lebih besar untuk mempercepat proses solving
- Untuk N > 26, program akan membatasi input karena keterbatasan representasi region (A-Z)

### Known Limitations
- Maksimal ukuran grid: 26×26 (sesuai jumlah huruf A-Z)
- Untuk N yang sangat besar, waktu komputasi bisa sangat lama pada mode Brute Force
- Gambar input harus memiliki region yang jelas dan berbeda warna

---

**© 2026 - Tugas Kecil 1 IF2211 Strategi Algoritma**
