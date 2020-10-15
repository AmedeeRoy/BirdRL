from multiprocessing import Process
from serverBird import server
from clientRLBird import client


if __name__ == '__main__':
    s = Process(target=server)

    p1 = Process(target=client, args=(1,))
    p2 = Process(target=client, args=(2,))
    p3 = Process(target=client, args=(3,))

    s.start()
    p1.start()
    p2.start()
    p3.start()

    s.join()
    p1.join()
    p2.join()
    p3.join()
