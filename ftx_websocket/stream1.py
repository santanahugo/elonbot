from multiprocessing import Process, Pipe
from ftx_websocket.mp1 import f
import time

if __name__ == '__main__':
    parent_conn, child_conn = Pipe()
    p = Process(target=f, args=(child_conn,))
    counter = 0
    p.start()
    while counter < 100:
        if counter % 2 == 0:
            print('Counter: ', counter)
            last = parent_conn.recv()
            print('Is float: ', isinstance(last,float))
            print('Msg: ', last)
            #print(last / 50)
        counter += 1
        #time.sleep(1)

    print(parent_conn.recv())   # prints "Hello"