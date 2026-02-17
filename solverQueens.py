import time

class SolverQueens:
    def __init__(self, matriksWarna, hurufAsli, ukuran, live_k=0, aktifkanOptimasi=False, metodeSolusi="backtracking", callback=None):
        self.papanWarna = matriksWarna
        self.hurufAsli = hurufAsli
        self.ukuran = ukuran
        self.posisiQueen = [-1] * ukuran
        self.kolomDipakai = [False] * ukuran
        jumlahRegion = self.jumlahRegion()
        self.regionDipakai = [False] * jumlahRegion
        self.jumlahIterasi = 0
        self.live_k = live_k
        self.aktifkanOptimasi = aktifkanOptimasi
        self.metodeSolusi = metodeSolusi.lower()
        self.solusiDitemukan = False
        self.callback = callback
        self.log_callback = None

    def jumlahRegion(self):
        semuaRegion = set()
        for baris in self.papanWarna:
            for nilai in baris:
                semuaRegion.add(nilai)
        return len(semuaRegion)
    
    def mulai(self):
        waktuMulai = time.perf_counter()
        
        if self.metodeSolusi == "brute_force":
            hasil = self.bruteForce()
        else:
            hasil = self.backtracking(0)
        
        waktuSelesai = time.perf_counter()
        durasi = (waktuSelesai - waktuMulai) * 1_000_000

        return hasil, self.jumlahIterasi, durasi
    
    def membuatSemuaKombinasi(self):
        kombinasi = [0] * self.ukuran
        
        while True:
            yield tuple(kombinasi)
            memuat = 1
            for i in range(self.ukuran - 1, -1, -1):
                if memuat:
                    kombinasi[i] += 1
                    if kombinasi[i] >= self.ukuran:
                        kombinasi[i] = 0
                    else:
                        memuat = 0
                        break
            if memuat:
                break
    
    def bruteForce(self):
        for kombinasi in self.membuatSemuaKombinasi():
            self.jumlahIterasi += 1
            if self.log_callback and self.live_k > 0 and self.jumlahIterasi % self.live_k == 0:
                self.posisiQueen = list(kombinasi)
                self.log_callback(list(self.posisiQueen), self.jumlahIterasi)
            if self.live_k > 0 and self.jumlahIterasi % self.live_k == 0:
                self.posisiQueen = list(kombinasi)
                if self.callback:
                    self.callback(list(self.posisiQueen), self.jumlahIterasi)
            if self.aktifkanOptimasi:
                if self.cekDenganOptimasi(kombinasi):
                    self.posisiQueen = list(kombinasi)
                    self.solusiDitemukan = True
                    if self.log_callback:
                        self.log_callback(list(self.posisiQueen), self.jumlahIterasi)
                    return True
            else:
                if self.cekTanpaOptimasi(kombinasi):
                    self.posisiQueen = list(kombinasi)
                    self.solusiDitemukan = True
                    if self.log_callback:
                        self.log_callback(list(self.posisiQueen), self.jumlahIterasi)
                    return True
        
        return False
    
    def cekTanpaOptimasi(self, kombinasi):
        validKolom = True
        validRegion = True
        validTetangga = True

        if len(set(kombinasi)) != self.ukuran:
            validKolom = False

        regionDipakai = set()
        for baris, kolom in enumerate(kombinasi):
            region = self.papanWarna[baris][kolom]
            if region in regionDipakai:
                validRegion = False
            regionDipakai.add(region)

        for baris in range(self.ukuran):
            kolom = kombinasi[baris]
            for barisLain in range(baris + 1, self.ukuran):
                kolomLain = kombinasi[barisLain]
                if abs(baris - barisLain) <= 1 and abs(kolom - kolomLain) <= 1:
                    validTetangga = False

        return validKolom and validRegion and validTetangga
    
    def cekDenganOptimasi(self, kombinasi):
        if len(set(kombinasi)) != self.ukuran:
            return False

        regionDipakai = set()
        for baris, kolom in enumerate(kombinasi):
            region = self.papanWarna[baris][kolom]
            if region in regionDipakai:
                return False
            regionDipakai.add(region)

        for baris in range(self.ukuran):
            kolom = kombinasi[baris]
            for barisLain in range(baris + 1, self.ukuran):
                kolomLain = kombinasi[barisLain]
                if abs(baris - barisLain) <= 1 and abs(kolom - kolomLain) <= 1:
                    return False
        
        return True
    
    def backtracking(self, baris):
        if baris == self.ukuran:
            self.solusiDitemukan = True
            if self.log_callback:
                self.log_callback(list(self.posisiQueen), self.jumlahIterasi)
            return True
        
        for kolom in range(self.ukuran):
            self.jumlahIterasi += 1
            if self.log_callback and self.live_k > 0 and self.jumlahIterasi % self.live_k == 0:
                self.log_callback(list(self.posisiQueen), self.jumlahIterasi)
            if self.live_k > 0 and self.jumlahIterasi % self.live_k == 0:
                if self.callback:
                    self.callback(list(self.posisiQueen), self.jumlahIterasi)
            if self.aktifkanOptimasi:
                if self.kolomDipakai[kolom]:
                    continue
                regionSaatIni = self.papanWarna[baris][kolom]
                if self.regionDipakai[regionSaatIni]:
                    continue
                if self.adaKonflikBertetangga(baris, kolom):
                    continue

            regionSaatIni = self.papanWarna[baris][kolom]
            self.posisiQueen[baris] = kolom
            self.kolomDipakai[kolom] = True
            self.regionDipakai[regionSaatIni] = True

            if not self.aktifkanOptimasi:
                if not self.cekPenempatanValid(baris):
                    self.posisiQueen[baris] = -1
                    self.kolomDipakai[kolom] = False
                    self.regionDipakai[regionSaatIni] = False
                    continue
            if self.backtracking(baris + 1):
                return True

            self.posisiQueen[baris] = -1
            self.kolomDipakai[kolom] = False
            self.regionDipakai[regionSaatIni] = False

        return False
    
    def cekPenempatanValid(self, barisTerakhir):
        kolomSet = set()
        regionSet = set()
        
        for baris in range(barisTerakhir + 1):
            kolom = self.posisiQueen[baris]
            if kolom in kolomSet:
                return False
            kolomSet.add(kolom)

            region = self.papanWarna[baris][kolom]
            if region in regionSet:
                return False
            regionSet.add(region)

            for barisLain in range(baris):
                kolomLain = self.posisiQueen[barisLain]
                if abs(baris - barisLain) <= 1 and abs(kolom - kolomLain) <= 1:
                    return False
        
        return True
    
    def adaKonflikBertetangga(self, baris, kolom):
        for barisSebelum in range(baris):
            kolomSebelum = self.posisiQueen[barisSebelum]
            if kolomSebelum != -1:
                if abs(baris - barisSebelum) <= 1 and abs(kolom - kolomSebelum) <= 1:
                    return True
        return False