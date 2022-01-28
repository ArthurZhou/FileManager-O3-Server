#!/usr/bin/env python
# -*- coding=utf-8 -*-


"""
file: service.py
socket service
"""

import os
import socket
import threading
import _thread
import time
import sys


true = str(os.path.exists('./config.txt'))
if true == 'False':
    # first time
    from setup import setup
    setup()
else:
    pass

with open('config.txt', 'r') as f:
    line = f.readlines()
    # get server ip
    way = line[0].replace('\n', '')
    port2 = line[1].replace('\n', '')
    f.close()
conac = 0


def start():
    try:
        global conn, lo, s
        ti = time.strftime("%Y-%m-%d %H:%M:%S")
        lo = open(os.getcwd() + '/log/' + ti + '.log', 'w')
        os.chdir(way)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # avoid (socket.error: [Error 98] Address already in use) error
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        host_name = socket.gethostname()
        host = socket.gethostbyname(host_name)
        port = int(port2)
        print('Server opened on:', host, ':', port2, '\nType "stop" to stop it.')
        lo.write('\n\n' + ti + 'Server opened on:' + host + ':' + port2)
        s.bind((host, int(port)))
        s.listen(10)
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    print('Waiting connections...')

    def wait():
        st = input()
        while st != 'stop':
            st = input()
        else:
            stop()

    _thread.start_new_thread(wait, ())

    while 1:
        global addr
        connf, addrf = s.accept()
        t = threading.Thread(target=deal, args=(connf, addrf))
        t.start()
        if conac == 1:
            s.close()


def signup(conn, addr):
    try:
        time.sleep(0.1)
        uids = conn.recv(1024).decode('utf-8')
        if not uids:
            signup(conn, addr)
        else:
            print('{0} sign up as {1}'.format(addr, uids))
            lo.write('\n{0} sign up as {1}'.format(addr, uids))
            kf = open('key.lock', 'a+')
            os.chdir(way)
            os.mkdir(uids)
            kf.write(uids + '\n')
            kf.close()
            time.sleep(0.1)
            conn.send('ready!'.encode('utf-8'))
            print('{0} account ready: {1}'.format(addr, uids))
            lo.write('\n{0} account ready: {1}'.format(addr, uids))
            sys.exit(0)
    except FileExistsError:
        conn.send('ex!'.encode('utf-8'))
        print('{0} account already in used: {1}'.format(addr, uids))
        lo.write('\n{0} account already in used: {1}'.format(addr, uids))
        signup(conn, addr)


def ex(conn, addr):
    while 1:
        try:
            lo.flush()
            data = conn.recv(1024).decode('utf-8')
            # services
            if data == '>getfilelist<':
                print('{0} client:get file list {1}'.format(addr, os.getcwd()))
                lo.write('\n{0} client:get file list {1}'.format(addr, os.getcwd()))
                time.sleep(0.1)
                conn.send(os.getcwd().encode('utf-8'))
                inCld = os.listdir(os.getcwd())
                conn.send(str(inCld).encode('utf-8'))
            if data == '>open<':
                openf(conn=conn, addr=addr)
            if data == '>back<':
                way2 = os.path.abspath(os.path.join(os.getcwd(), ".."))
                if way2 != way:
                    os.chdir(way2)
                    print('{0} client:back to {1}'.format(addr, os.getcwd()))
                    lo.write('\n{0} client:back to {1}'.format(addr, os.getcwd()))
                    ex(conn=conn, addr=addr)
                else:
                    pass
            if data == '>up<':
                uploadf(conn=conn, addr=addr)

            if data == '>down<':
                downloadf(conn=conn, addr=addr)

            if data == '>delt<':
                deltf(conn=conn, addr=addr)

            if data == '>quit<' or not data:
                if data == '>quit<':
                    print('{0} connection close'.format(addr))
                    lo.write('\n{0} connection close'.format(addr))
                if not data:
                    print('{0} connection close by accident'.format(addr))
                    lo.write('\n{0} connection close by accident'.format(addr))
                conn.close()
                os.chdir(way)
                sys.exit(0)
        except:
            pass


def deal(connf, addrf):
    print('Accept new connection from {0}'.format(addrf))
    lo.write('\nAccept new connection from {0}'.format(addrf))
    login(connf, addrf)


def login(connf, addrf):
    global uida
    os.chdir('..')
    kf = open('key.lock', 'r')
    oldkeys = kf.read()
    kf.close()
    os.chdir(way)
    time.sleep(0.2)
    uida = connf.recv(1024).decode('utf-8')
    if uida == '>setup<':
        signup(connf, addrf)
    keys = oldkeys.split('\n')
    print(keys)
    ch = list.count(keys, str(uida))
    time.sleep(0.2)
    if not uida:
        connf.close()
        print('{0} connection close'.format(addrf))
        lo.write('\n{0} connection close'.format(addrf))
        pass
    else:
        if ch >= 1:
            if str(os.path.exists(uida)) == 'True':
                print('{0} logged in as {1}'.format(addrf, uida))
                lo.write('\n{0} logged in as {1}'.format(addrf, uida))
                connf.send('True'.encode('utf-8'))
                os.chdir(uida)
                ex(conn=connf, addr=addrf)
            else:
                pass
        else:
            print('{0} wrong username or password'.format(addrf))
            lo.write('\n{0} wrong username or password'.format(addrf))
            connf.send('False'.encode('utf-8'))
            login(connf, addrf)


def openf(conn, addr):
    # get file name
    opFl = conn.recv(1024).decode('utf-8')

    # is it a file or a directory?
    dof = os.path.isdir(opFl)
    fod = os.path.isfile(opFl)

    if str(dof) == 'False' and str(fod) == 'True':  # it is a file
        conn.send('file'.encode('utf-8'))
        time.sleep(0.5)
        with open(opFl, 'r') as f:
            inc = f.read()
            # if the file is empty,the client won`t receive it
            if inc == '':
                inc = ' '  # add a space to empty file
            print('{0} client:open file {1}'.format(addr, opFl))
            lo.write('\n{0} client:open file {1}'.format(addr, opFl))
            conn.send(str(inc).encode('utf-8'))
            f.close()

    if str(fod) == 'False' and str(dof) == 'True':  # it is a folder
        conn.send('fold'.encode('utf-8'))
        os.chdir(opFl)
        print('{0} client:open folder {1}'.format(addr, opFl))
        lo.write('\n{0} client:open folder {1}'.format(addr, opFl))
        ex(conn=conn, addr=addr)


def deltf(conn, addr):
    deFl = conn.recv(1024).decode('utf-8')
    os.remove(deFl)
    print('{0} client:delete file {1}'.format(addr, deFl))
    lo.write('\n{0} client:delete file {1}'.format(addr, deFl))
    ex(conn, addr)


def uploadf(conn, addr):
    time.sleep(0.1)
    fof = conn.recv(1024).decode('utf-8')
    if fof == '>œ<':
        pass
    if fof == 'file':
        time.sleep(0.1)
        upFl = conn.recv(1024).decode('utf-8')
        f = open(upFl, 'w')
        print('{0} client:uploading file {1}'.format(addr, upFl))
        lo.write('\n{0} client:uploading file {1}'.format(addr, upFl))
        f.write(conn.recv(1024).decode('utf-8'))
        f.close()
        print('{0} client:finish uploading file {1}'.format(addr, upFl))
        lo.write('\n{0} client:finish uploading file {1}'.format(addr, upFl))
    ex(conn, addr)


def downloadf(conn, addr):
    doFl = conn.recv(1024).decode('utf-8')
    doFl = os.getcwd() + '/' + doFl

    dof = os.path.isdir(doFl)
    fod = os.path.isfile(doFl)
    if str(dof) == 'False' and str(fod) == 'True':
        time.sleep(0.1)
        conn.send('file'.encode('utf-8'))
        print('{0} client:downloading file {1}'.format(addr, doFl))
        lo.write('\n{0} client:downloading file {1}'.format(addr, doFl))
        with open(doFl, 'rb')as f:  # open and send real file
            time.sleep(0.1)
            conn.send(f.read())
            f.close()
        print('{0} client:finish downloading file {1}'.format(addr, doFl))
        lo.write('\n{0} client:finish downloading file {1}'.format(addr, doFl))


def stop():
    global conac
    conac = conac + 1
    print('Logging out...')
    try:
        s.shutdown(2)
        conn.close()
    except:
        pass
    print('Saving sessions...')
    lo.write('\nServer stop at ' + time.strftime("%Y-%m-%d %H:%M:%S"))
    lo.close()
    print('Done!You can kill the process now.')


if __name__ == '__main__':
    #try:
        start()
    #except:
        #pass
