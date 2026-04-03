from Controller import Controller

def main():
    # 1. Instancia o Controller (passando o ID da câmera ou link RTSP)
    # 0 é a webcam padrão, ou use a sua string RTSP
    fonte_video = "rtsp://admin:Tijolonanuca007@192.168.0.8:554/cam/realmonitor?channel=1&subtype=0"
    app_controller = Controller(fonte_video)

    # 2. Chama o método iniciar.
    # Internamente, ele importa a View e a devolve para o main.
    app_view = app_controller.iniciar()

    # 3. Inicia o loop da interface gráfica
    print("Sistema SAFEENGAI iniciado com sucesso.")
    app_view.mainloop()

if __name__ == "__main__":
    main()