#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import Ice

class Client(Ice.Application):
    def __init__(self):
        print('El cliente se ha iniciado con éxito\n')

sys.exit(Client().main(sys.argv))
