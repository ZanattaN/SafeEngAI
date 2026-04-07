from Controller import Controller

def main():
    # Definição das fontes
    # Use f-strings para garantir que as variáveis entrem limpas
    USER = "admin"
    PASS = "senha"
    IP = "192.168.80.102"  # O IP do MHDX que você achou

    url = f"rtsp://{USER}:{PASS}@{IP}:554/cam/realmonitor?channel=1&subtype=1"

    fonte_video1 = url
    fonte_video2 = 0 # Webcam local

    # O Controller deve receber as duas
    app_controller = Controller(fonte_video1, fonte_video2)

    # Inicia a View passando as fontes através do controller ou diretamente
    app_view = app_controller.iniciar()

    print("Sistema SAFEENGAI iniciado com sucesso.")
    app_view.mainloop()

if __name__ == "__main__":
    main()