import math
import cv2
import numpy as np
from ultralytics import YOLO


class IA:
    def __init__(self):
        # Carrega o modelo de pose (essencial para detectar pulsos)
        self.model = YOLO("yolov8n.pt")

        # Inicializa o dicionário de rastreamento de comportamentos
        self.pessoas = {}

        # Define as zonas de interesse (ajuste as coordenadas conforme a posição da sua câmera)
        self.zonas = {
            "Cabide_A": (100, 100, 300, 400),
            "Prateleira_B": (400, 100, 600, 400),
            "CAIXA": (360, 170, 600, 530)
        }

        # Warmup

        dummy = np.zeros((320, 320, 3), dtype=np.uint8)
        self.model.track(dummy, imgsz=320, verbose=False, persist=True)

    def verificar_toque_cabide(self, pontos_pessoa, frame):
        """Verifica se os pulsos da pessoa colidem com as zonas definidas."""
        try:
            # No YOLO Pose: índice 9 é pulso esquerdo, 10 é pulso direito
            # Usamos .tolist() ou garantimos que estamos acessando os valores numéricos
            maos = []
            if len(pontos_pessoa) > 10:
                maos = [pontos_pessoa[9], pontos_pessoa[10]]
            else:
                return None
        except (IndexError, TypeError):
            return None

        for nome_zona, limites in self.zonas.items():
            x_min, y_min, x_max, y_max = limites

            # Desenha a zona visualmente para conferência no monitor
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (255, 255, 0), 1)
            cv2.putText(frame, nome_zona, (x_min, y_min - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)

            for mao in maos:
                x_mao, y_mao = mao[0], mao[1]
                # Verifica se a coordenada da mão está dentro do retângulo da zona
                if x_min < x_mao < x_max and y_min < y_mao < y_max:
                    return nome_zona
        return None

    def processarDeteccao(self, frame):
        resultados = self.model.track(frame, imgsz=640, conf=0.2, verbose=False, persist=True)

        for r in resultados:
            # Se não houver caixas ou IDs, pula
            if r.boxes is None or r.boxes.id is None:
                continue

            # Pegamos os dados como arrays numpy para facilitar o acesso
            ids = r.boxes.id.cpu().numpy().astype(int)
            boxes = r.boxes.xyxy.cpu().numpy()

            # Keypoints de pose (se houver)
            keypoints = r.keypoints.xy.cpu().numpy() if r.keypoints is not None else None

            for i in range(len(ids)):
                id_pessoa = ids[i]
                x1, y1, x2, y2 = map(int, boxes[i])
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

                # 1. Lógica do Caixa (Ignorar alerta de parado aqui)
                x_min, y_min, x_max, y_max = self.zonas.get("CAIXA", (0, 0, 0, 0))
                no_caixa = x_min < cx < x_max and y_min < cy < y_max

                # 2. Verificação de Toque (Pose)
                zona_tocada = None
                if keypoints is not None and i < len(keypoints):
                    zona_tocada = self.verificar_toque_cabide(keypoints[i], frame)

                # 3. Status Suspeito (Só se NÃO estiver no caixa)
                status_suspeito = False
                if not no_caixa:
                    status_suspeito = self.atualizar_status_suspeito(id_pessoa, cx, cy)

                # --- Desenho dos Alertas ---
                cor = (0, 255, 0)
                if no_caixa:
                    cv2.putText(frame, "ATENDIMENTO", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
                elif status_suspeito or zona_tocada:
                    cor = (0, 0, 255)
                    msg = "SUSPEITO" if status_suspeito else f"TOQUE: {zona_tocada}"
                    cv2.putText(frame, msg, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, cor, 2)

                cv2.rectangle(frame, (x1, y1), (x2, y2), cor, 2)
                cv2.putText(frame, f"ID {id_pessoa}", (x1, y2 + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, cor, 1)

        return frame

    def atualizar_status_suspeito(self, id_pessoa, cx, cy):
        """Calcula se a pessoa se moveu menos que 5 pixels em 60 frames (~2 segundos)."""
        if id_pessoa not in self.pessoas:
            self.pessoas[id_pessoa] = {"x": cx, "y": cy, "parado": 0}
            return False

        # Cálculo da distância entre a posição anterior e a atual
        dist = math.sqrt((cx - self.pessoas[id_pessoa]["x"]) ** 2 +
                         (cy - self.pessoas[id_pessoa]["y"]) ** 2)

        # Se a distância for insignificante, incrementa o contador de "parado"
        if dist < 5:
            self.pessoas[id_pessoa]["parado"] += 1
        else:
            # Se a pessoa se moveu, reseta o cronômetro e atualiza a posição
            self.pessoas[id_pessoa]["parado"] = 0
            self.pessoas[id_pessoa]["x"], self.pessoas[id_pessoa]["y"] = cx, cy

        # 60 frames a 30 FPS equivalem a 2 segundos parado
        return self.pessoas[id_pessoa]["parado"] > 60