from multiprocessing import Process
from serverBird import server
from clientRLBird import client


if __name__ == '__main__':
    s = Process(target=server)

    p1 = Process(target=client, args=(34,))
    p2 = Process(target=client, args=(33,))
    p3 = Process(target=client, args=(32,))

    s.start()
    p1.start()
    p2.start()
    p3.start()

    s.join()
    p1.join()
    p2.join()
    p3.join()
