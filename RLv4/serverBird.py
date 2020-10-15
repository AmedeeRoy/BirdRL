import socket
from gameBird import Game
from paramBird import *
from _thread import start_new_thread
import pickle

def server():
    def threaded_client(conn, p):

        conn.send(str.encode(str(p)))
        game_count = 0
        while True:
            try:
                # Receive data from client
                data = conn.recv(4096).decode()
                if not data:
                    break
                else:
                    # look for specific commands from received data
                    if data == "left":
                        gg.listPlayer[p].moveLeft(gg.gameMap)
                    if data == "right":
                        gg.listPlayer[p].moveRight(gg.gameMap)
                    if data == "up":
                        gg.listPlayer[p].moveUp(gg.gameMap)
                    if data == "down":
                        gg.listPlayer[p].moveDown(gg.gameMap)
                    if data == "stay":
                        gg.listPlayer[p].moveStay(gg.gameMap)
                    if data == "dive":
                        gg.listPlayer[p].moveDive(gg.gameMap)
                    if data == "gameover":
                        gg.over[p] = True

                    # Reset Game when all players have finished
                    if np.prod(gg.over) == 1:
                        print('New Game')
                        game_count += 1
                        gg.reset()

                    if game_count == NB_GAMES:
                        gg.quit()

                    # send data back to clients
                    conn.sendall(pickle.dumps(gg))

            except:
                break

        # When user disconnects
        print("[DISCONNECT] Client Id:", p, "disconnected")
        conn.close()  # close connection

    # setup sockets
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 5555
    host = socket.gethostname()
    SERVER_IP = socket.gethostbyname(host)
    # SERVER_IP = "134.246.128.140"
    print(SERVER_IP)

    try:
        s.bind((SERVER_IP, port))
    except socket.error as e:
        str(e)

    s.listen(NB_PLAYER)
    print('Waiting for a connection, Server Started..')

    gg = Game()
    print(gg.gameMap.fishMap)

    p = 0
    while True:
        conn, addr = s.accept()
        print("Connected to:", addr)
        if p <= NB_PLAYER-1:
            start_new_thread(threaded_client, (conn, p))
            print('Player', p, 'joined!')
            p += 1


server()
