import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
from datetime import datetime
from PIL import Image, ImageTk
from papan import Papan
from solverQueens import SolverQueens
from imageParser import ImageCropper

class GUIQueens:  
    def __init__(self, root):
        self.root = root
        self.root.title("Visualisasi Penyelesaian N-Queens ---> Dika Pramudya Nugraha (13524132)")
        self.root.geometry("1800x750")
        self.root.resizable(True, True)
        self.ukuran = 0
        self.papan = None
        self.solver = None
        self.matriks = None
        self.hurufAsli = None
        self.solving = False
        self.modeTxt = False
        self.imageCropper = ImageCropper(lebarKanvas=450, tinggiKanvas=450)
        self.modeCrop = False
        self.cropStartX = None
        self.cropStartY = None
        self.cropRect = None
        self.gambarTampil = None
        self.regionColors = {}
        self.riwayatIterasi = []
        self.counterLog = 0
        self.crownImage = None
        self.fotoMahkotaInput = {}
        self.fotoMahkotaOutput = {}
        try:
            mahkota_path = os.path.join(os.path.dirname(__file__), "assets", "crown.png")
            self.crownImage = Image.open(mahkota_path)
        except Exception as e:
            pass

        self.colors = [
            "#FFB6C1", "#87CEEB", "#98FB98", "#FFD700", "#DDA0DD",
            "#F0E68C", "#FFE4B5", "#E0BBE4", "#FFDAB9", "#B0E0E6",
            "#FAFAD2", "#D8BFD8", "#F5DEB3", "#C1FFC1", "#FFE4E1"
        ]

        self.createScrollableFrame()
        self.buildUI()

    def createScrollableFrame(self):
        self.mainCanvas = tk.Canvas(self.root, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.mainCanvas.yview)
        self.scrollableFrame = tk.Frame(self.mainCanvas)

        self.scrollableFrame.bind(
            "<Configure>",
            lambda e: self.mainCanvas.configure(scrollregion=self.mainCanvas.bbox("all"))
        )
        
        self.mainCanvas.create_window((0, 0), window=self.scrollableFrame, anchor="nw")
        self.mainCanvas.configure(yscrollcommand=scrollbar.set)
        self.mainCanvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.mainCanvas.bind_all("<MouseWheel>", self.on_mousewheel)
    
    def on_mousewheel(self, event):
        self.mainCanvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def buildUI(self):
        frameAtas = tk.Frame(self.scrollableFrame)
        frameAtas.pack(pady=10)

        tk.Button(frameAtas, text="Load TXT", command=self.loadTxt, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(frameAtas, text="Load Image", command=self.loadImage, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(frameAtas, text="Start", command=self.startSolver, width=12, bg="#90EE90").pack(side=tk.LEFT, padx=5)
        tk.Button(frameAtas, text="Reset", command=self.resetBoard, width=12, bg="#FFB6C1").pack(side=tk.LEFT, padx=5)

        pengaturanFrame = tk.Frame(self.scrollableFrame)
        pengaturanFrame.pack(pady=5)

        tk.Label(pengaturanFrame, text="Live update (k):").pack(side=tk.LEFT)
        self.inputLive = tk.Entry(pengaturanFrame, width=8)
        self.inputLive.insert(0, "100")
        self.inputLive.pack(side=tk.LEFT, padx=5)
        self.opsiOptimasi = tk.BooleanVar(value=True)
        tk.Checkbutton(pengaturanFrame, text="Optimasi", variable=self.opsiOptimasi).pack(side=tk.LEFT, padx=10)
        tk.Label(pengaturanFrame, text="Mode:").pack(side=tk.LEFT, padx=5)
        self.pilihanMode = tk.StringVar(value="backtracking")
        tk.Radiobutton(pengaturanFrame, text="Backtracking", variable=self.pilihanMode, value="backtracking").pack(side=tk.LEFT)
        tk.Radiobutton(pengaturanFrame, text="Brute Force", variable=self.pilihanMode, value="brute_force").pack(side=tk.LEFT)

        frameUtama = tk.Frame(self.scrollableFrame)
        frameUtama.pack(pady=10)

        frameKiri = tk.Frame(frameUtama)
        frameKiri.pack(side=tk.LEFT, padx=10)
        
        tk.Label(frameKiri, text="INPUT BOARD", font=("Arial", 12, "bold"), anchor="center").pack()
        self.canvasLeft = tk.Canvas(frameKiri, width=450, height=450, bg="white", 
                                     highlightthickness=2, highlightbackground="blue")
        self.canvasLeft.pack(pady=5)
        self.frameCropControls = tk.Frame(frameKiri)
        tk.Label(self.frameCropControls, text="N (Grid Size):").pack(side=tk.LEFT, padx=5)
        self.inputUkuran = tk.Entry(self.frameCropControls, width=8)
        self.inputUkuran.pack(side=tk.LEFT, padx=5)
        tk.Button(self.frameCropControls, text="Confirm Crop", command=self.confirmCrop, 
                 bg="#90EE90").pack(side=tk.LEFT, padx=5)
        
        frameKanan = tk.Frame(frameUtama)
        frameKanan.pack(side=tk.LEFT, padx=10)
        
        tk.Label(frameKanan, text="OUTPUT BOARD (Live Update)", font=("Arial", 12, "bold"), anchor="center").pack()
        self.canvasRight = tk.Canvas(frameKanan, width=450, height=450, bg="#f0f0f0", 
                                      highlightthickness=2, highlightbackground="green")
        self.canvasRight.pack(pady=5)
        
        frameLog = tk.Frame(frameUtama)
        frameLog.pack(side=tk.LEFT, padx=10)
        
        tk.Label(frameLog, text="ITERATION LOG (History)", font=("Arial", 12, "bold"), anchor="center").pack()
        logContainer = tk.Frame(frameLog, width=450, height=450, bg="white",
                               highlightthickness=2, highlightbackground="orange")
        logContainer.pack(pady=5)
        logContainer.pack_propagate(False)
        
        self.logScrollbar = tk.Scrollbar(logContainer)
        self.logScrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.textLog = tk.Text(logContainer, wrap=tk.WORD, 
                              yscrollcommand=self.logScrollbar.set,
                              font=("Courier New", 9),
                              bg="#f9f9f9", fg="#333333",
                              state='disabled')
        self.textLog.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.logScrollbar.config(command=self.textLog.yview)

        self.labelInfo = tk.Label(self.scrollableFrame, text="Belum ada file dimuat", font=("Arial", 10), anchor="center")
        self.labelInfo.pack(pady=5)
        
        self.labelProgress = tk.Label(self.scrollableFrame, text="", font=("Arial", 9), fg="blue", anchor="center")
        self.labelProgress.pack()

        self.frameSimpan = tk.Frame(self.scrollableFrame, bg="#ffffcc", relief=tk.RAISED, borderwidth=2)
        self.labelSaveQuestion = tk.Label(self.frameSimpan, text="✅ Solusi ditemukan! Apakah Anda ingin menyimpan solusi?", 
                                          font=("Arial", 10, "bold"), bg="#ffffcc", fg="#006400", anchor="center")
        self.labelSaveQuestion.pack(pady=8)
        
        frameTombolSimpan = tk.Frame(self.frameSimpan, bg="#ffffcc")
        frameTombolSimpan.pack(pady=5)
        
        self.btnSaveYa = tk.Button(frameTombolSimpan, text="Ya, Simpan", width=15, bg="#90EE90", 
                                   font=("Arial", 10, "bold"), cursor="hand2")
        self.btnSaveYa.pack(side=tk.LEFT, padx=10)
        
        self.btnSaveTidak = tk.Button(frameTombolSimpan, text="Tidak", width=15, bg="#FFB6C1", 
                                      font=("Arial", 10, "bold"), cursor="hand2")
        self.btnSaveTidak.pack(side=tk.LEFT, padx=10)

        tk.Label(self.scrollableFrame, text="", height=1).pack()

        self.canvasLeft.bind("<ButtonPress-1>", self.onCropStart)
        self.canvasLeft.bind("<B1-Motion>", self.onCropDrag)
        self.canvasLeft.bind("<ButtonRelease-1>", self.onCropEnd)

    def loadTxt(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not path:
            return

        try:
            self.modeCrop = False
            self.frameCropControls.pack_forget()
            
            self.papan = Papan(path)
            self.ukuran = self.papan.ambilUkuran()
            self.matriks = self.papan.ambilMatriks()
            self.hurufAsli = [[char for char in row] for row in self.papan.daftarBarisAsli]
            self.modeTxt = True
            
            self.drawBoard(self.canvasLeft, showQueens=False)
            self.canvasRight.delete("all")
            self.labelInfo.config(text=f"✓ TXT Loaded | Ukuran: {self.ukuran}x{self.ukuran}")
            self.labelProgress.config(text="")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def loadImage(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if not path:
            return
        try:
            resized, cv_image, display_info = self.imageCropper.loadImage(path)
            self.gambarTampil = ImageTk.PhotoImage(resized)
            self.canvasLeft.delete("all")
            self.canvasLeft.create_image(225, 225, image=self.gambarTampil)
            self.modeCrop = True
            self.frameCropControls.pack(pady=5)
            self.labelInfo.config(text="Gambar telah dimuat. Seret (drag) untuk memilih area pemotongan gambar, masukkan N, lalu klik Confirm Crop.")
            self.labelProgress.config(text="")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def onCropStart(self, event):
        if not self.modeCrop:
            return
        self.cropStartX = event.x
        self.cropStartY = event.y
        if self.cropRect:
            self.canvasLeft.delete(self.cropRect)
    
    def onCropDrag(self, event):
        if not self.modeCrop or self.cropStartX is None:
            return
        if self.cropRect:
            self.canvasLeft.delete(self.cropRect)
        self.cropRect = self.canvasLeft.create_rectangle(
            self.cropStartX, self.cropStartY, event.x, event.y,
            outline="red", width=3
        )
    
    def onCropEnd(self, event):
        if not self.modeCrop:
            return
    
    def confirmCrop(self):
        if not self.modeCrop or self.imageCropper.originalImageCv is None:
            messagebox.showwarning("Warning", "Load image terlebih dahulu!")
            return
        
        if self.cropRect is None:
            messagebox.showwarning("Warning", "Pilih area crop terlebih dahulu!")
            return
        try:
            N = int(self.inputUkuran.get())
            if N <= 0:
                raise ValueError("N harus positif")
            if N > 26:
                raise ValueError("N maksimal adalah 26 (sesuai dengan jumlah huruf A-Z)")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return
        try:
            coords = self.canvasLeft.coords(self.cropRect)
            canvas_x1, canvas_y1, canvas_x2, canvas_y2 = coords

            orig_x1, orig_y1, orig_x2, orig_y2 = self.imageCropper.canvasToImageCoords(
                canvas_x1, canvas_y1, canvas_x2, canvas_y2
            )

            cropped = self.imageCropper.cropImage(orig_x1, orig_y1, orig_x2, orig_y2)

            self.matriks, self.regionColors, self.hurufAsli = self.imageCropper.processImage(cropped, N)
            self.ukuran = N
            self.modeTxt = False
            self.drawBoard(self.canvasLeft, showQueens=False)
            self.canvasRight.delete("all")
            self.modeCrop = False
            self.frameCropControls.pack_forget()
            self.labelInfo.config(text=f"✓ Image Cropped & Processed | Ukuran: {N}x{N}")
            self.labelProgress.config(text="")
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memproses crop: {str(e)}")

    def drawBoard(self, canvas, showQueens=False, queenPositions=None):
        canvas.delete("all")
        if self.ukuran == 0:
            return

        cell = 450 // self.ukuran

        if canvas == self.canvasLeft:
            crownCache = self.fotoMahkotaInput
        else:
            crownCache = self.fotoMahkotaOutput

        if self.modeTxt:
            for i in range(self.ukuran):
                for j in range(self.ukuran):
                    x1 = j * cell
                    y1 = i * cell
                    x2 = x1 + cell
                    y2 = y1 + cell

                    canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="white", width=1)
                    
                    if showQueens and queenPositions and i < len(queenPositions) and queenPositions[i] == j:
                        display_char = "#"
                        color = "red"
                        font_size = max(14, cell//2)
                    else:
                        display_char = self.hurufAsli[i][j] if self.hurufAsli else ""
                        color = "black"
                        font_size = max(10, cell//3)
                    
                    canvas.create_text(x1 + cell//2, y1 + cell//2, 
                                      text=display_char, 
                                      font=("Courier New", font_size, "bold"),
                                      fill=color)
        else:
            for i in range(self.ukuran):
                for j in range(self.ukuran):
                    x1 = j * cell
                    y1 = i * cell
                    x2 = x1 + cell
                    y2 = y1 + cell

                    region_id = self.matriks[i][j]
                    if self.regionColors and region_id in self.regionColors:
                        color = self.regionColors[region_id]
                    else:
                        color = self.colors[region_id % len(self.colors)]
                    
                    canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=color, width=1)
                    
                    if self.hurufAsli:
                        label = self.hurufAsli[i][j]
                        canvas.create_text(x1 + cell//2, y1 + cell//2, 
                                          text=label, 
                                          font=("Arial", max(8, cell//4)),
                                          fill="gray")

            if showQueens and queenPositions:
                for i in range(len(queenPositions)):
                    kol = queenPositions[i]
                    if kol != -1:
                        x = kol * cell + cell // 2
                        y = i * cell + cell // 2
                        
                        if self.crownImage:
                            crown_size = int(cell * 0.8)
                            
                            if crown_size not in crownCache:
                                crown_rgba = self.crownImage.convert('RGBA')
                                resized = crown_rgba.resize((crown_size, crown_size), Image.Resampling.LANCZOS)
                                crownCache[crown_size] = ImageTk.PhotoImage(resized)
                            
                            canvas.create_image(x, y, 
                                              image=crownCache[crown_size],
                                              tags="queen")
                        else:
                            canvas.create_text(x, y, text="♛",
                                             font=("Arial", max(12, cell//2)),
                                             fill="darkred",
                                             tags="queen")
    
    def updateLiveVisual(self, positions, iterasi):
        self.root.after(0, lambda: self.updateUI(positions, iterasi))
    
    def updateUI(self, positions, iterasi):
        self.drawBoard(self.canvasRight, showQueens=True, queenPositions=positions)
        self.labelProgress.config(text=f"Solving... Iterasi: {iterasi:,}")
        
        self.tambahLogIterasi(positions, iterasi)
    
    def tambahLogIterasi(self, positions, iterasi):
        log_entry = f"Iterasi ke-{iterasi:,}\n"
        
        if self.modeTxt:
            for i in range(self.ukuran):
                row = ""
                for j in range(self.ukuran):
                    if positions[i] == j:
                        row += "# "
                    else:
                        row += self.hurufAsli[i][j] + " "
                log_entry += row.strip() + "\n"
        else:
            for i in range(self.ukuran):
                row = ""
                for j in range(self.ukuran):
                    if positions[i] == j:
                        row += "# "
                    else:
                        row += self.hurufAsli[i][j] + " "
                log_entry += row.strip() + "\n"
        
        log_entry += "-" * 30 + "\n"

        self.textLog.config(state='normal')
        self.textLog.insert(tk.END, log_entry)

        lines = int(self.textLog.index('end-1c').split('.')[0])
        max_lines = 500 * (self.ukuran + 2)
        if lines > max_lines:
            self.textLog.delete('1.0', f'{lines - max_lines}.0')
        
        self.textLog.config(state='disabled')
        self.textLog.see(tk.END)
    
    def bersihkanLog(self):
        self.textLog.config(state='normal')
        self.textLog.delete('1.0', tk.END)
        self.textLog.config(state='disabled')
        self.riwayatIterasi = []
    
    def logIterasi(self, positions, iterasi):
        self.root.after(0, lambda: self.logIterationUI(positions, iterasi))
    
    def logIterationUI(self, positions, iterasi):
        self.tambahLogIterasi(positions, iterasi)

    def startSolver(self):
        if self.matriks is None:
            messagebox.showwarning("Warning", "Load file terlebih dahulu!")
            return
        
        if self.solving:
            messagebox.showwarning("Warning", "Solver sedang berjalan!")
            return

        try:
            live_k = int(self.inputLive.get())
        except:
            live_k = 0

        self.solving = True
        self.labelInfo.config(text="Memulai solver...")
        self.labelProgress.config(text="")
        self.frameSimpan.pack_forget()
        self.bersihkanLog() 
        
        self.solver = SolverQueens(
            matriksWarna=self.matriks,
            hurufAsli=self.hurufAsli,
            ukuran=self.ukuran,
            live_k=live_k,
            aktifkanOptimasi=self.opsiOptimasi.get(),
            metodeSolusi=self.pilihanMode.get(),
            callback=self.updateLiveVisual if live_k > 0 else None
        )

        self.solver.log_callback = self.logIterasi

        thread = threading.Thread(target=self.jalankanSOlver, daemon=True)
        thread.start()

    def jalankanSOlver(self):
        try:
            hasil, total, durasi = self.solver.mulai()
            waktu_ms = durasi / 1000

            if hasil:
                self.root.after(0, lambda: self.drawBoard(self.canvasRight, showQueens=True, 
                                                         queenPositions=self.solver.posisiQueen))
                self.root.after(0, lambda: self.labelInfo.config(
                    text=f"✅ Solusi ditemukan! | Waktu Pencarian: {waktu_ms:.3f} ms | Iterasi: {total:,}"
                ))
                self.root.after(0, lambda: self.labelProgress.config(text=""))
                self.root.after(100, lambda: self.tampilkanPromptSimpan(waktu_ms, total))
            else:
                self.root.after(0, lambda: self.canvasRight.delete("all"))
                self.root.after(0, lambda: self.labelInfo.config(
                    text=f"❌ Tidak ada solusi | Waktu Pencarian: {waktu_ms:.3f} ms | Iterasi: {total:,}"
                ))
                self.root.after(0, lambda: self.labelProgress.config(text=""))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Solver error: {str(e)}"))
        finally:
            self.solving = False

    def tampilkanPromptSimpan(self, waktu_ms, iterasi):
        self.btnSaveYa.config(command=lambda: self.onSaveYes(waktu_ms, iterasi))
        self.btnSaveTidak.config(command=self.onSaveNo)
        self.frameSimpan.pack(pady=10, padx=20, fill=tk.X)
        self.root.after(200, lambda: self.mainCanvas.yview_moveto(1.0))
    
    def onSaveYes(self, waktu_ms, iterasi):
        self.frameSimpan.pack_forget()
        self.simpanSolusi(waktu_ms, iterasi)
    
    def onSaveNo(self):
        self.frameSimpan.pack_forget()
    
    def simpanSolusi(self, waktu_ms, iterasi):
        if self.modeTxt:
            self.simpanSolusiTxt(waktu_ms, iterasi)
        else:
            self.simpanSolusiGambar(waktu_ms, iterasi)
    
    def simpanSolusiTxt(self, waktu_ms, iterasi):
        default_name = f"solution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            initialfile=default_name
        )
        
        if not filepath:
            return
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 50 + "\n")
                f.write("N-QUEENS SOLVER - SOLUTION\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Ukuran Grid: {self.ukuran}x{self.ukuran}\n")
                f.write(f"Mode: {'Backtracking' if self.solver.metodeSolusi == 'backtracking' else 'Brute Force'}\n")
                f.write(f"Optimasi: {'Ya' if self.solver.aktifkanOptimasi else 'Tidak'}\n")
                f.write(f"Waktu Eksekusi: {waktu_ms:.3f} ms\n")
                f.write(f"Jumlah Iterasi: {iterasi:,}\n")
                f.write(f"Tanggal: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("SOLUSI:\n")
                f.write("-" * 50 + "\n\n")
                
                for i in range(self.ukuran):
                    row = ""
                    for j in range(self.ukuran):
                        if self.solver.posisiQueen[i] == j:
                            row += "# "
                        else:
                            row += self.hurufAsli[i][j] + " "
                    f.write(row.strip() + "\n")
                
                f.write("\n" + "-" * 50 + "\n")
                
                f.write("\nPOSISI QUEEN (Baris, Kolom):\n")
                for i in range(self.ukuran):
                    f.write(f"Baris {i+1}: Kolom {self.solver.posisiQueen[i]+1}\n")
            
            messagebox.showinfo("Sukses", f"Solusi berhasil disimpan ke:\n{filepath}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan file:\n{str(e)}")
    
    def simpanSolusiGambar(self, waktu_ms, iterasi):
        default_name = f"solution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")],
            initialfile=default_name
        )
        
        if not filepath:
            return
        
        try:
            from PIL import Image as PILImage, ImageDraw, ImageFont
            img_size = 450
            img = PILImage.new('RGB', (img_size, img_size), 'white')
            draw = ImageDraw.Draw(img)
            
            cell = img_size // self.ukuran

            if self.modeTxt:
                for i in range(self.ukuran):
                    for j in range(self.ukuran):
                        x1 = j * cell
                        y1 = i * cell
                        x2 = x1 + cell
                        y2 = y1 + cell

                        draw.rectangle([x1, y1, x2, y2], outline='black', fill='white', width=1)

                        if self.solver.posisiQueen[i] == j:
                            display_char = "#"
                            color = "red"
                            font_size = max(14, cell//2)
                        else:
                            display_char = self.hurufAsli[i][j] if self.hurufAsli else ""
                            color = "black"
                            font_size = max(10, cell//3)
                        
                        try:
                            font = ImageFont.truetype("cour.ttf", font_size)
                        except:
                            font = ImageFont.load_default()

                        bbox = draw.textbbox((0, 0), display_char, font=font)
                        text_width = bbox[2] - bbox[0]
                        text_height = bbox[3] - bbox[1]
                        text_x = x1 + (cell - text_width) // 2
                        text_y = y1 + (cell - text_height) // 2
                        
                        draw.text((text_x, text_y), display_char, fill=color, font=font)
            else:
                for i in range(self.ukuran):
                    for j in range(self.ukuran):
                        x1 = j * cell
                        y1 = i * cell
                        x2 = x1 + cell
                        y2 = y1 + cell

                        region_id = self.matriks[i][j]
                        if self.regionColors and region_id in self.regionColors:
                            color = self.regionColors[region_id]
                        else:
                            color = self.colors[region_id % len(self.colors)]

                        draw.rectangle([x1, y1, x2, y2], outline='black', fill=color, width=1)

                        if self.hurufAsli:
                            label = self.hurufAsli[i][j]
                            font_size = max(8, cell//4)
                            try:
                                font = ImageFont.truetype("arial.ttf", font_size)
                            except:
                                font = ImageFont.load_default()
                            
                            bbox = draw.textbbox((0, 0), label, font=font)
                            text_width = bbox[2] - bbox[0]
                            text_height = bbox[3] - bbox[1]
                            text_x = x1 + (cell - text_width) // 2
                            text_y = y1 + (cell - text_height) // 2
                            
                            draw.text((text_x, text_y), label, fill='gray', font=font)
                
                for i in range(len(self.solver.posisiQueen)):
                    kol = self.solver.posisiQueen[i]
                    if kol != -1:
                        x = kol * cell + cell // 2
                        y = i * cell + cell // 2

                        if self.crownImage:
                            crown_size = int(cell * 0.8)
                            crown_rgba = self.crownImage.convert('RGBA')
                            crown_resized = crown_rgba.resize((crown_size, crown_size), Image.Resampling.LANCZOS)

                            crown_x = x - crown_size // 2
                            crown_y = y - crown_size // 2

                            img.paste(crown_resized, (crown_x, crown_y), crown_resized)
                        else:
                            queen_char = "♛"
                            font_size = max(12, cell//2)
                            try:
                                font = ImageFont.truetype("arial.ttf", font_size)
                            except:
                                font = ImageFont.load_default()
                            
                            bbox = draw.textbbox((0, 0), queen_char, font=font)
                            text_width = bbox[2] - bbox[0]
                            text_height = bbox[3] - bbox[1]
                            text_x = x - text_width // 2
                            text_y = y - text_height // 2
                            
                            draw.text((text_x, text_y), queen_char, fill='darkred', font=font)

            img.save(filepath, 'PNG')
            
            messagebox.showinfo("Sukses", f"Solusi berhasil disimpan ke:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan gambar:\n{str(e)}")

    def resetBoard(self):
        if self.matriks is not None:
            self.canvasLeft.delete("all")
            self.canvasRight.delete("all") 
            self.frameSimpan.pack_forget()
            self.bersihkanLog()
            self.labelInfo.config(text=f"Board direset | Ukuran: {self.ukuran}x{self.ukuran}")
            self.labelProgress.config(text="")
        else:
            self.canvasLeft.delete("all")
            self.canvasRight.delete("all")
            self.frameSimpan.pack_forget()
            self.bersihkanLog()
            self.labelInfo.config(text="Belum ada file dimuat")
            self.labelProgress.config(text="")

if __name__ == "__main__":
    root = tk.Tk()
    app = GUIQueens(root)
    root.mainloop()
