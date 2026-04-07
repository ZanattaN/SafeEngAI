import customtkinter as ctk
import cv2
from PIL import Image
from threading import Thread, Lock
import queue
import time
import numpy as np
from IA import IA


class View(ctk.CTk):
    def __init__(self, controller):
        super().__init__()

        self.title("Sistema SAFEENGAI - Monitoramento Inteligente")
        self.geometry("1300x750")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.controller = controller

        # Inicialização Segura da IA
        print("Carregando Modelos de Visão Computacional...")
        self.ia = IA()
        self.model_lock = Lock()

        # Filas de frames (tamanho 1 para garantir sempre o frame mais recente = menos delay)
        self.fila1 = queue.Queue(maxsize=1)
        self.fila2 = queue.Queue(maxsize=1)

        self._setup_ui()

        # Thread de processamento (Worker)
        self.running = True
        self.thread_worker = Thread(target=self.worker, daemon=True)
        self.thread_worker.start()

        # Loop de atualização da interface
        self.update_loop()

    def _setup_ui(self):
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Container Câmera 1
        self.f_cam1 = ctk.CTkFrame(self)
        self.f_cam1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.label_cam1 = ctk.CTkLabel(self.f_cam1, text="Conectando ao DVR Intelbras...", font=("Arial", 16))
        self.label_cam1.pack(expand=True, fill="both")

        # Container Câmera 2
        self.f_cam2 = ctk.CTkFrame(self)
        self.f_cam2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.label_cam2 = ctk.CTkLabel(self.f_cam2, text="Câmera 2 - Local", font=("Arial", 16))
        self.label_cam2.pack(expand=True, fill="both")

    def worker(self):
        """Thread que processa a IA sem travar a interface visual"""
        while self.running:
            try:
                f1, f2 = self.controller.ler_frames()

                # Processa Câmera 1 (MHDX)
                if f1 is not None:
                    with self.model_lock:
                        # Agora usando a lógica corrigida da IA
                        f1_proc = self.ia.processarDeteccao(f1)
                    self._atualizar_fila(self.fila1, f1_proc)

                # Processa Câmera 2 (Webcam/Local)
                if f2 is not None:
                    with self.model_lock:
                        f2_proc = self.ia.processarDeteccao(f2)
                    self._atualizar_fila(self.fila2, f2_proc)

                if f1 is None and f2 is None:
                    time.sleep(0.02)  # Evita consumo excessivo de CPU

            except Exception as e:
                print(f"Erro no Worker: {e}")
                time.sleep(0.1)

    def _atualizar_fila(self, fila, frame):
        """Garante que a fila tenha apenas o frame mais novo para evitar lag"""
        if fila.full():
            try:
                fila.get_nowait()
            except queue.Empty:
                pass
        fila.put(frame)

    def update_loop(self):
        """Loop principal do CustomTkinter (Main Thread)"""
        if not self.fila1.empty():
            frame = self.fila1.get()
            img1 = self.converter_para_tk(frame)
            self.label_cam1.configure(image=img1, text="")
            self.label_cam1.image = img1

        if not self.fila2.empty():
            frame = self.fila2.get()
            img2 = self.converter_para_tk(frame)
            self.label_cam2.configure(image=img2, text="")
            self.label_cam2.image = img2

        if self.running:
            self.after(10, self.update_loop)

    def converter_para_tk(self, frame):
        # Redimensiona para caber na UI sem esticar
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(frame_rgb)
        return ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(600, 450))

    def on_closing(self):
        self.running = False
        self.controller.liberar()
        self.destroy()