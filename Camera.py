import cv2

class Camera:
    def __init__(self, stream_id=0):
        """
        Inicializa o status cam para None e zero
        """
        self.stream_id = stream_id
        self.cam = None
        self.frame = None

    def iniciar_camera(self):
        """
        Câmera recebe id e define as proporções

        """
        self.cam = cv2.VideoCapture(self.stream_id)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
        self.cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        return self.cam

    def obter_resolucao(self):
        """
        camera recebe a variável de instância sobre altura e largura e retorna tupla

        """
        largura = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        altura = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return largura, altura

    def lerFrame(self):
        """
        retorno booleano e frame do metodo
        """
        ret, frame = self.cam.read()
        return ret, frame

    def gravarframe(self, out, frame):
        """""
        gravar o frame
        """
        out.write(frame)

    def exibir_frame(self, frame):
        """
        frame com resize da tela
        mostra a janela do frame

        """
        frame = cv2.resize(frame, (800, 600))
        cv2.imshow("Camera", frame)

    def tecla_pressionada(self, atalho='q'):
        """
        atalho para a tela pressionada
        """
        return cv2.waitKey(1) == ord(atalho)

    def fechar_camera(self):
        """
        fecha a camera fechado todas as janelas
        """
        self.cam.release()
        cv2.destroyAllWindows()

    def iniciar_gravacao(self):
        """
        Obtém o tamanho do frame
        Define que tipo de arquivo é
        Retorna a saída do video
        """

        largura, altura = self.obter_resolucao()
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (largura, altura))
        return out

    def melhorarFrame(self, frame):
        """
        melhora a qualidade do frame
        """

        frame = cv2.resize(frame, (640, 640))
        frame = cv2.convertScaleAbs(frame, alpha=1.3, beta=30)
        return frame


