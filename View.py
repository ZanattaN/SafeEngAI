import customtkinter as ctk
import cv2
from PIL import Image
from threading import Thread
import queue

from Controller import Controller
from IA import IA


class View(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema SAFEENGAI")
        self.geometry("1400x700")

        # Inicialização dos Modelos e Controllers
        self.model = IA()

        # Configuração Câmera 1
        self.controller1 = Controller(
            "rtsp://admin:Tijolonanuca007@192.168.0.8:554/cam/realmonitor?channel=1&subtype=0", 0
        )
        self.fila1 = queue.Queue(maxsize=1)

        # Configuração Câmera 2 (Ajuste a URL/ID conforme necessário)
        self.controller2 = Controller(
            "rtsp://admin:Tijolonanuca007@192.168.0.8:554/cam/realmonitor?channel=2&subtype=0", 1
        )
        self.fila2 = queue.Queue(maxsize=1)

        self._setup_ui()

        # Inicia as Threads de processamento
        Thread(target=self.worker, args=(self.controller1, self.fila1), daemon=True).start()
        Thread(target=self.worker, args=(self.controller2, self.fila2), daemon=True).start()

        self.update_loop()

    def _setup_ui(self):
        """Organiza a interface em colunas para as duas câmeras"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Label Câmera 1
        self.label_cam1 = ctk.CTkLabel(self, text="Câmera 1 - Carregando...")
        self.label_cam1.grid(row=0, column=0, padx=10, pady=10)

        # Label Câmera 2
        self.label_cam2 = ctk.CTkLabel(self, text="Câmera 2 - Carregando...")
        self.label_cam2.grid(row=0, column=1, padx=10, pady=10)

    def worker(self, controller, fila):
        """Worker genérico que aceita o controller e a fila específica"""
        while True:
            frame = controller.ler_frame()

            if frame is None:
                continue

            # Processamento de IA
            frame = self.model.processarDeteccao(frame)

            # Lógica de atualização da fila
            if not fila.empty():
                try:
                    fila.get_nowait()
                except queue.Empty:
                    pass

            fila.put(frame)

    def update_loop(self):
        """Atualiza os frames na interface para ambas as câmeras"""
        # Atualiza Cam 1
        if not self.fila1.empty():
            frame1 = self.fila1.get()
            img1 = self.converter_para_tk(frame1)
            self.label_cam1.configure(image=img1, text="")
            self.label_cam1.image = img1

        # Atualiza Cam 2
        if not self.fila2.empty():
            frame2 = self.fila2.get()
            img2 = self.converter_para_tk(frame2)
            self.label_cam2.configure(image=img2, text="")
            self.label_cam2.image = img2

        self.after(15, self.update_loop)

    @staticmethod
    def converter_para_tk(frame):
        cv2_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(cv2_image)
        # Reduzi o tamanho para (640x480) para caberem lado a lado melhor
        return ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(640, 480))