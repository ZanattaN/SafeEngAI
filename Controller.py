import cv2
import threading


class Controller:
    def __init__(self, stream_id1=None, stream_id2=None):
        # Câmera 1 (sempre tenta)
        self.cam1 = cv2.VideoCapture(stream_id1, cv2.CAP_FFMPEG) if stream_id1 is not None else None

        # Câmera 2
        self.cam2 = cv2.VideoCapture(stream_id2) if stream_id2 is not None else None

        # Câmera 3
        #self.cam3 = cv2.VideoCapture(stream_id3, cv2.CAP_FFMPEG) if stream_id3 is not None else None

        # Reduz delay
        if self.cam1:
            self.cam1.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        if self.cam2:
            self.cam2.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        # if self.cam3:
        #     self.cam3.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        # Frames
        self.frame1 = None
        self.frame2 = None
        # self.frame3 = None

        # Validação
        if self.cam1 and not self.cam1.isOpened():
            print("Erro na câmera 1")

        if self.cam2 and not self.cam2.isOpened():
            print("Erro na câmera 2")

        # if self.cam3 and not self.cam3.isOpened():
        #     print("Erro na câmera 3")

        threading.Thread(target=self.captura_loop, daemon=True).start()

    def captura_loop(self):
        while True:
            # Cam 1
            if self.cam1:
                ret1, f1 = self.cam1.read()
                if ret1:
                    self.frame1 = f1

            # Cam 2
            if self.cam2:
                ret2, f2 = self.cam2.read()
                if ret2:
                    self.frame2 = f2

            # Cam 3
            # if self.cam3:
            #     ret3, f3 = self.cam3.read()
            #     if ret3:
            #         self.frame3 = f3

    def ler_frames(self):
        return self.frame1, self.frame2 #self.frame3

    # compatibilidade com código antigo
    def ler_frame(self):
        return self.frame1

    def liberar(self):
        if self.cam1:
            self.cam1.release()
        if self.cam2:
            self.cam2.release()
        # if self.cam3:
        #     self.cam3.release()

    def iniciar(self):
        from View import View
        self.view = View()
        return self.view