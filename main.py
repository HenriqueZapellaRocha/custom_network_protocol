import time
from user_interface import protocol

name = input( "qual o nome que deseja usar? " )
protocol.start( name )

def mostrar_dispositivos():
    print("\n📡 Dispositivos Ativos:")
    registros = protocol.get_registers()
    if not registros:
        print("Nenhum dispositivo ativo.")
    else:
        for nome, (ip, port, ultimo_contato) in registros.items():
            print(f"- {nome} → {ip}:{port} (último contato há {round(time.time() - ultimo_contato, 1)}s)")

def enviar_mensagem():
    destino = input("Nome do destinatário (conforme registro): ")
    registros = protocol.get_registers()
    if destino not in registros:
        print("❌ Destinatário não encontrado.")
        return
    ip, port, _ = registros[destino]
    mensagem = input("Digite a mensagem a enviar: ")
    sucesso = protocol.talk(destino, mensagem)
    if sucesso:
        print("✅ Mensagem enviada com sucesso!")
    else:
        print("⚠️ Falha ao enviar a mensagem.")

def enviar_arquivo():
    name = input("Para quem enviar: ")
    file_name = input("Nome do arquivo: ")
    protocol.send_file( name, file_name )


def menu():
    while True:
        print("\n=== MENU ===")
        print("1. Ver dispositivos ativos")
        print("2. Enviar mensagem")
        print("3. Enviar arquivo")
        print("0. Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            mostrar_dispositivos()
        elif opcao == "2":
            enviar_mensagem()
        elif opcao == "0":
            print("Saindo.............")
            break
        elif opcao == "3":
            enviar_arquivo()
        else:
            print("Opção inválida.")

menu()
