class Papan:
    def __init__(self, namaFile):
        self.namaFile = namaFile
        self.daftarBarisAsli = []
        self.matriksWarna = []
        self.pemetaanWarna = {}
        self.ukuran = 0

        self.bacaFile()
        self.validasiPapan()
        self.konversiKeAngka()
        self.validasiJumlahRegion()
        self.validasiKonektivitasRegion()

    def bacaFile(self):
        with open(self.namaFile, 'r') as file:
            baris = [baris.strip() for baris in file if baris.strip()]
        self.daftarBarisAsli = baris
    
    def validasiPapan(self):
        if not self.daftarBarisAsli:
            raise ValueError("File kosong (Tidak Valid)")
        
        self.ukuran = len(self.daftarBarisAsli)
        
        if self.ukuran > 26:
            raise ValueError("Ukuran papan maksimal adalah 26x26 (sesuai dengan jumlah huruf A-Z)")

        for baris in self.daftarBarisAsli:
            if len(baris) != self.ukuran:
                raise ValueError("Papan harus berbentuk persegi (N x N)")

            for huruf in baris:
                if not huruf.isalpha():
                    raise ValueError("Wilayah harus alfabet (A-Z). Input tidak valid!")
            
    def konversiKeAngka(self):
        idWarna = 0
        self.matriksWarna = []

        for baris in self.daftarBarisAsli:
            barisBaru = []
            for huruf in baris:
                if huruf not in self.pemetaanWarna:
                    self.pemetaanWarna[huruf] = idWarna
                    idWarna += 1
                barisBaru.append(self.pemetaanWarna[huruf])
            self.matriksWarna.append(barisBaru)

    def validasiJumlahRegion(self):
        jumlah_region = len(self.pemetaanWarna)
        if jumlah_region != self.ukuran:
            raise ValueError(f"Jumlah region ({jumlah_region}) harus sama dengan ukuran papan ({self.ukuran}x{self.ukuran}). Input tidak valid!")
    
    def validasiKonektivitasRegion(self):
        region_cells = {}
        for i in range(self.ukuran):
            for j in range(self.ukuran):
                region_id = self.matriksWarna[i][j]
                if region_id not in region_cells:
                    region_cells[region_id] = []
                region_cells[region_id].append((i, j))

        for region_id, cells in region_cells.items():
            if len(cells) == 0:
                continue

            visited = set()
            queue = [cells[0]]
            visited.add(cells[0])
            
            while queue:
                row, col = queue.pop(0)
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    new_row, new_col = row + dr, col + dc
                    if 0 <= new_row < self.ukuran and 0 <= new_col < self.ukuran:
                        if self.matriksWarna[new_row][new_col] == region_id:
                            if (new_row, new_col) not in visited:
                                visited.add((new_row, new_col))
                                queue.append((new_row, new_col))
            if len(visited) != len(cells):
                raise ValueError(
                    "Terdapat region yang tidak terhubung (terpecah menjadi beberapa bagian). "
                    "Setiap region harus membentuk satu kesatuan yang terhubung. Input tidak valid!"
                )
    
    def ambilMatriks(self):
        return self.matriksWarna

    def ambilUkuran(self):
        return self.ukuran

    def jumlahRegion(self):
        return len(self.pemetaanWarna) 