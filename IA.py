import math

import cv2
from ultralytics import YOLO


class IA:
    # Dentro da sua classe IA em IA.py
    def __init__(self):
        from ultralytics import YOLO
        self.model = YOLO("yolo26n.pt")

        # FORÇAR CARREGAMENTO: Isso evita o erro de NoneType nas threads
        # Fazemos uma predição vazia para garantir que o modelo saia do estado 'None'
        import numpy as np
        dummy_frame = np.zeros((320, 320, 3), dtype=np.uint8)
        self.model.predict(dummy_frame, imgsz=320, verbose=False)

    def verificar_toque_cabide(self, pontos_pessoa, frame):
        try:
            # No YOLO Pose: 9 é pulso esquerdo, 10 é pulso direito
            maos = [pontos_pessoa[9], pontos_pessoa[10]]
        except IndexError:
            return None

        for nome_zona, limites in self.zonas.items():# se as zonas com suas coordenadas estão dentro da proporção da câmera
            x_min, y_min, x_max, y_max = limites

            # Desenha a zona na tela para conferência
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (255, 255, 0), 1)#desenha o retângulo na pessoa
            cv2.putText(frame, nome_zona, (x_min, y_min - 5),#insere o texto acima do retangulo
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)

            for mao in maos:# se detectar pulso
                x_mao, y_mao = mao[0], mao[1]
                # Verifica colisão
                if x_min < x_mao < x_max and y_min < y_mao < y_max:
                    return nome_zona  # RETORNA o nome da zona para o alerta
        return None

    def processarDeteccao(self, frame):#processa detecção do frame
        #recebe resultado do track do frame
        resultados = self.model.predict(
            frame, imgsz=320, conf=0.4, verbose=False
        )
        for r in resultados:
            if r.keypoints is None or r.boxes.id is None:#se não estiver nos resultados pula o loop
                continue

            """
            r.keypoints.xy contém as coordenadas das articulações ela receberá
            o id que está em cada caixa do track e mandará para o id_pessoa
            
            """
            for i, pontos in enumerate(r.keypoints.xy):
                id_pessoa = int(r.boxes.id[i])

                # 1. Verifica interação com cabide usando a pose
                zona_tocada = self.verificar_toque_cabide(pontos, frame)

                # 2. Lógica de Suspeito (Parado)
                x1, y1, x2, y2 = map(int, r.boxes.xyxy[i])#recebe as coordenadas do suspeito
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2 #logica do deslocamento


                #logica do deslocamento aplicada no meotodo para verificar suspeito
                status_suspeito = self.atualizar_status_suspeito(id_pessoa, cx, cy)

                # 3. Desenhar alertas no frame
                cor = (0, 255, 0)  # Verde padrão

                if zona_tocada:
                    cor = (0, 0, 255)  # Vermelho
                    cv2.putText(frame, f"ALERTA: MEXENDO NO {zona_tocada.upper()}",
                                (x1, y1 - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, cor, 2)

                if status_suspeito:
                    cor = (0, 0, 255)
                    cv2.putText(frame, "SUSPEITO PARADO", (x1, y1 - 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, cor, 2)

                # Desenha a caixa e ID
                label = f'ID {id_pessoa}'
                cv2.rectangle(frame, (x1, y1), (x2, y2), cor, 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, cor, 2)

        return frame

    def atualizar_status_suspeito(self, id_pessoa, cx, cy):
        """Monitora se a pessoa está parada há muito tempo."""
        #Se a pessoa não estiver no array, então ela é adicionada
        if id_pessoa not in self.pessoas:
            self.pessoas[id_pessoa] = {"x": cx, "y": cy, "parado": 0}
            return False

        #distância euclidiana
        dist = math.sqrt((cx - self.pessoas[id_pessoa]["x"]) ** 2 + (cy - self.pessoas[id_pessoa]["y"]) ** 2)

        #se a distância for menor que 5 vai somando até o suspeito
        if dist < 5:
            self.pessoas[id_pessoa]["parado"] += 1
        else:
            self.pessoas[id_pessoa]["parado"] = 0
            self.pessoas[id_pessoa]["x"], self.pessoas[id_pessoa]["y"] = cx, cy

        return self.pessoas[id_pessoa]["parado"] > 60  # Retorna True se parado > 2 segundos aprox.