import customtkinter as ctk
import cv2
from PIL import Image
from threading import Thread, Lock
import queue
import time
import numpy as np  # Adicionado para o frame de teste
from IA import IA


class View(ctk.CTk):
    def __init__(self, controller):
        super().__init__()

        self.title("Sistema SAFEENGAI - Multi-Camera")
        self.geometry("1400x700")

        self.controller = controller

        # --- PASSO CRÍTICO: Inicialização e Warmup ---
        print("Inicializando IA e carregando modelos...")
        self.model = IA()

        # Fazemos um "warmup" (aquecimento) aqui no fluxo principal.
        # Isso força o Torch a carregar os pesos (.to(device)) antes do worker rodar.
        try:
            dummy_frame = np.zeros((320, 320, 3), dtype=np.uint8)
            self.model.processarDeteccao(dummy_frame)
            print("IA pronta para processamento.")
        except Exception as e:
            print(f"Aviso no Warmup: {e}")

        self.model_lock = Lock()
        # ---------------------------------------------

        self.fila1 = queue.Queue(maxsize=1)
        self.fila2 = queue.Queue(maxsize=1)

        self._setup_ui()

        # Inicia o worker apenas após a IA estar aquecida
        Thread(target=self.worker, daemon=True).start()
        self.update_loop()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.f_cam1 = ctk.CTkFrame(self)
        self.f_cam1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.label_cam1 = ctk.CTkLabel(self.f_cam1, text="Câmera 1 - Carregando...")
        self.label_cam1.pack(expand=True, fill="both")

        self.f_cam2 = ctk.CTkFrame(self)
        self.f_cam2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.label_cam2 = ctk.CTkLabel(self.f_cam2, text="Câmera 2 - Carregando...")
        self.label_cam2.pack(expand=True, fill="both")

    def worker(self):
        while True:
            try:
                # Puxa os frames do controller
                f1, f2 = self.controller.ler_frames()

                # Processa Câmera 1
                if f1 is not None:
                    with self.model_lock:
                        f1_proc = self.model.processarDeteccao(f1)
                    self._limpar_e_inserir(self.fila1, f1_proc)

                # Processa Câmera 2
                if f2 is not None:
                    with self.model_lock:
                        f2_proc = self.model.processarDeteccao(f2)
                    self._limpar_e_inserir(self.fila2, f2_proc)

                if f1 is None and f2 is None:
                    time.sleep(0.01)

            except Exception as e:
                # Evita que a thread morra se um frame falhar
                print(f"Erro no ciclo do worker: {e}")
                time.sleep(0.1)

    @staticmethod
    def _limpar_e_inserir(fila, frame):
        if not fila.empty():
            try:
                fila.get_nowait()
            except queue.Empty:
                pass
        fila.put(frame)

    def update_loop(self):
        if not self.fila1.empty():
            img1 = self.converter_para_tk(self.fila1.get())
            self.label_cam1.configure(image=img1, text="")
            self.label_cam1.image = img1

        if not self.fila2.empty():
            img2 = self.converter_para_tk(self.fila2.get())
            self.label_cam2.configure(image=img2, text="")
            self.label_cam2.image = img2

        self.after(15, self.update_loop)

    @staticmethod
    def converter_para_tk(frame):
        cv2_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(cv2_image)
        return ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(640, 480))