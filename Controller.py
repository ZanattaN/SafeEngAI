import cv2
import threading
import time


class Controller:
    def __init__(self, stream_id1=None, stream_id2=None):
        self.stream_id1 = stream_id1
        self.stream_id2 = stream_id2

        # Inicialização das câmeras
        self.cam1 = cv2.VideoCapture(self.stream_id1) if stream_id1 else None
        self.cam2 = cv2.VideoCapture(self.stream_id2, cv2.CAP_DSHOW) if stream_id2 else None

        # Configurações de performance
        for cam in [self.cam1, self.cam2]:
            if cam:
                cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                # Opcional: reduzir resolução no código se o MHDX permitir
                # cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                # cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self.frame1 = None
        self.frame2 = None
        self.running = True

        # Validação inicial
        if self.cam1 and not self.cam1.isOpened():
            print(f"Erro na conexão RTSP: Verifique usuário/senha no IP {self.stream_id1}")

        # Thread de captura otimizada
        threading.Thread(target=self.captura_loop, daemon=True).start()

    def captura_loop(self):
        while self.running:
            if self.cam1:
                # O grab() é mais rápido que o read() pois não decodifica o frame imediatamente
                if self.cam1.grab():
                    ret, frame = self.cam1.retrieve()
                    if ret:
                        self.frame1 = frame
                else:
                    # Tenta reconectar se a câmera cair (importante para segurança)
                    time.sleep(2)
                    self.cam1 = cv2.VideoCapture(self.stream_id1, cv2.CAP_FFMPEG)

            if self.cam2:
                ret2, f2 = self.cam2.read()
                if ret2:
                    self.frame2 = f2

            # Pequena pausa para não fritar a CPU (aprox 60 FPS)
            time.sleep(0.01)

    def ler_frames(self):
        # Retorna o frame mais atual disponível
        return self.frame1, self.frame2

    def liberar(self):
        self.running = False
        if self.cam1: self.cam1.release()
        if self.cam2: self.cam2.release()

    def iniciar(self):
        from View import View
        self.view = View(self)
        return self.view