import os
import sys


def setup():
    print('Hi!Welcome to FileManager-Server(Alpha-0.10.0)\n'
          'Before using,you must accept our licence.(GPL-3.0)\n'
          'Click here to view:https://github.com/ArthurZhou/FileManager/blob/main/LICENSE')
    acc = input('Type "accept" here to accept our licence:')
    if acc == 'accept':
        sf = open('config.txt', 'a+')
        sf.write(os.getcwd() + '/file\n')
        port = input('Which port do you want the server open on:')
        sf.write(port)
        print("Your server setup successfully!Run 'main.py' to use it!")
    else:
        sys.exit(0)
