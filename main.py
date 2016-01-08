#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Michał Gibas

from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from pandac.PandaModules import WindowProperties

import sys
from tile import Tile

#definicja kolorów
WORLD = (0.1, 0.1, 0.8, 1)
WHITE = (1, 1, 1, 1)

class Kulki(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        #ustawienia
        base.setBackgroundColor(WORLD)
        props = WindowProperties()
        props.setTitle('Kulki 3D')
        props.setFullscreen(1)
        base.win.requestProperties(props)

        #klawisze
        self.accept('escape', sys.exit)
        self.accept('f2', self.showFPS)

        #elementy 2d
        self.punkty = OnscreenText(text="Punkty: " + str(self.punkty),
                                  style=1, fg=(1, 1, 1, 1), shadow=(0, 0, 0, 1),
                                  pos=(1.1, .85), scale = .07)


        #obiekty
        for i in range(9):
            for j in range(9):
                self.plytki.append(Tile("square.egg", WHITE, (i-4+i*.04, (j-4+j*.04)*-1, 0), self.render))


        self.pilka = self.loader.loadModel("ball.egg")
        self.pilka.reparentTo(self.render)
        self.pilka.setColor(1, 0, 0)
        self.pilka.setPos(self.plytki[41].getPos()[0], self.plytki[41].getPos()[0]-0.2, 0.2)

        #kamera
        self.disableMouse()
        self.camera.setPos(0,-14, 15)
        self.camera.setHpr(0, -44, 0)

    def showFPS(self):
        base.setFrameRateMeter(self.fps)
        self.fps = not self.fps


    plytki = []
    punkty = 0
    fps = True


gra = Kulki()
gra.run()
