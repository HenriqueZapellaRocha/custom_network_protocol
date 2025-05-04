import time
from user_interface import protocol

input("pressione enter para iniciar")
name = input( "qual o nome que deseja usar? " )
protocol.start( name )
print("\033[2J\033[H", end="")

print(r""""
 _  __   _       _                    _           
| |/_ | | |     | |                  | |          
| |_| | | | __ _| |__    _ __ ___  __| | ___  ___ 
| __| | | |/ _` | '_ \  | '__/ _ \/ _` |/ _ \/ __|
| |_| | | | (_| | |_) | | | |  __/ (_| |  __/\__ \
 \__|_| |_|\__,_|_.__/  |_|  \___|\__,_|\___||___/                                                                                                 
                 _                  _                        _                  _              _       
                | |                | |                      | |                (_)            | |      
 _ __  _ __ ___ | |_ ___   ___ ___ | | ___     ___ _   _ ___| |_ ___  _ __ ___  _ ______ _  __| | ___  
| '_ \| '__/ _ \| __/ _ \ / __/ _ \| |/ _ \   / __| | | / __| __/ _ \| '_ ` _ \| |_  / _` |/ _` |/ _ \ 
| |_) | | | (_) | || (_) | (_| (_) | | (_) | | (__| |_| \__ \ || (_) | | | | | | |/ / (_| | (_| | (_) |
| .__/|_|  \___/ \__\___/ \___\___/|_|\___/   \___|\__,_|___/\__\___/|_| |_| |_|_/___\__,_|\__,_|\___/ 
| |                                                                                                    
|_|                                                                                      
 _                 _____       _ _ _                               __      __                              
| |          _    / ____|     (_) | |                              \ \    / /                              
| |__  _   _(_)  | |  __ _   _ _| | |__   ___ _ __ _ __ ___   ___   \ \  / /_ _ ___  __ _ _   _  ___ ____  
| '_ \| | | |    | | |_ | | | | | | '_ \ / _ \ '__| '_ ` _ \ / _ \   \ \/ / _` / __|/ _` | | | |/ _ \_  /  
| |_) | |_| |_   | |__| | |_| | | | | | |  __/ |  | | | | | |  __/    \  / (_| \__ \ (_| | |_| |  __// / _ 
|_.__/ \__, (_)   \_____|\__,_|_|_|_| |_|\___|_|  |_| |_| |_|\___|     \/ \__,_|___/\__, |\__,_|\___/___( )
        __/ |                                                                          | |              |/ 
       |___/                                                                           |_|                 
 _    _                 _                    ______                _ _       
| |  | |               (_)                  |___  /               | | |      
| |__| | ___ _ __  _ __ _  __ _ _   _  ___     / / __ _ _ __   ___| | | __ _ 
|  __  |/ _ \ '_ \| '__| |/ _` | | | |/ _ \   / / / _` | '_ \ / _ \ | |/ _` |
| |  | |  __/ | | | |  | | (_| | |_| |  __/  / /_| (_| | |_) |  __/ | | (_| |
|_|  |_|\___|_| |_|_|  |_|\__, |\__,_|\___| /_____\__,_| .__/ \___|_|_|\__,_|
                             | |                       | |                   
                             |_|                       |_|                             
""")

def send_message():
    print( "\033[2J\033[H", end="" )
    destination = input( "\nNome do destinatário: " )
    registries = protocol.get_registers()
    if destination not in registries:
        print( "\n❌ Destinatário não encontrado." )
        return
    ip, port, _ = registries[destination]
    message = input( "Digite a mensagem a enviar: " )
    sucess = protocol.talk( destination, message )
    if sucess:
        print("✅ Mensagem enviada com sucesso!")
    else:
        print("⚠️ Falha ao enviar a mensagem.")
    input("pressione enter para voltar ao menu")

def send_file():
    print( "\033[2J\033[H", end="" )
    name = input( "Para quem enviar: " )
    file_name = input( "Nome do arquivo: " )
    file_name_receiver = input( "nome do arquivo para o receptor: " )
    protocol.send_file( name, file_name, file_name_receiver )
    input("pressione enter para voltar ao menu")

def alive_heartbeats() -> None:
    print("\033[2J\033[H", end="")
    print("DISPOSITIVOS ATIVOS:")
    registries = protocol.get_registers()
    if not registries:
        print("Nenhum dispositivo ativo.")
    else:
        for name, (ip, port, last_contact) in registries.items():
            print(f"- {name} → {ip}:{port} (último contato há { round(time.time() - last_contact, 1 )}s)" )

    input("pressione enter para voltar ao menu")
    menu()



def menu():
    while True:
        print("\n========== MENU ===========")
        print("1. Ver dispositivos ativos")
        print("2. Enviar mensagem")
        print("3. Enviar arquivo")
        print("0. Sair")
        print("\n\n========== MENSAGENS RECEBIDAS E LOGS ===========")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            alive_heartbeats()
        elif opcao == "2":
            send_message()
        elif opcao == "0":
            print("Saindo.............")
            break
        elif opcao == "3":
            send_file()
        else:
            print("Opção inválida.")

menu()
