import customtkinter as ctk
import cv2
from PIL import Image
import queue           # Gerencia as filas de frames
from threading import Thread # Gerencia o processamento paralelo
from IA import IA
from Controller import Controller


class View(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema SAFEENGAI")
        self.geometry("1400x600")

        self.controller = Controller(0)
        self.model = IA()

        self.fila = queue.Queue(maxsize=1)

        self._setup_ui()

        Thread(target=self.worker, daemon=True).start()

        self.update_loop()

    # No arquivo View.py
    def worker(self):
        while True:
            frame = self.controller.ler_frame()

            if frame is None:
                continue

            # CORREÇÃO AQUI: Mude 'processar' para 'processarDeteccao'
            frame = self.model.processarDeteccao(frame)

            if not self.fila.empty():
                self.fila.get()

            self.fila.put(frame)

    def update_loop(self):
        if not self.fila.empty():
            frame = self.fila.get()

            img = self.converter_para_tk(frame)
            self.label_cam1.configure(image=img)
            self.label_cam1.image = img

        self.after(10, self.update_loop)

    def _setup_ui(self):
        self.label_cam1 = ctk.CTkLabel(self, text="")
        self.label_cam1.pack()

    @staticmethod
    def converter_para_tk(frame):
        cv2_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(cv2_image)
        return ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(600, 400))