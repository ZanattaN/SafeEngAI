import cv2
import queue



class Controller:
    def __init__(self, stream_id):
        self.cam = cv2.VideoCapture(stream_id)
        self.stream_id = stream_id

        if not self.cam.isOpened():
            print("Erro ao abrir câmera")

    def iniciar(self):
        from View import View  # Import local para evitar erro circular
        self.view = View()
        return self.view

    def ler_frame(self):
        ret, frame = self.cam.read()
        if not ret:
            return None
        return frame

    def liberar(self):
        self.cam.release()

    def worker_ia(self, camera_controller, fila_saida, ia_instance):
        while True:
            # CORREÇÃO: Usar o método ler_frame() que você definiu no Controller
            frame_raw = camera_controller.ler_frame()

            if frame_raw is not None:
                # Processa a IA em uma cópia para evitar conflitos de memória
                frame_processado = ia_instance.processarDeteccao(frame_raw.copy())

                # Gerenciamento da fila (mantém apenas o frame mais recente)
                if fila_saida.full():
                    try:
                        fila_saida.get_nowait()
                    except:  # Importante: certifique-se de que 'queue' foi importado
                        pass

                fila_saida.put(frame_processado)

    def update_loop(self):
        try:
            # Tenta pegar o frame da fila sem esperar (get_nowait)
            # CORREÇÃO: Verifique se o nome é self.fila ou self.fila_cam1
            frame1 = self.fila.get_nowait()

            # Converte para o formato que o CustomTkinter entende
            img_tk1 = self.converter_para_tk(frame1)

            # Atualiza o Label da interface
            self.label_cam1.configure(image=img_tk1, text='')

            # Mantém a referência da imagem (se não o Python apaga da memória)
            self.label_cam1.image = img_tk1

        except queue.Empty:
            # Se a fila estiver vazia, não faz nada e tenta de novo no próximo ciclo
            pass
        except Exception as e:
            print(f"Erro no loop de atualização: {e}")

        # Agenda a próxima execução para daqui a 10 milissegundos
        self.after(10, self.update_loop)







        
