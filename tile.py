# -*- coding: utf-8 -*-

class Tile:
    def __init__(self, file, color, position, render):
        self.model = loader.loadModel(file)
        self.model.reparentTo(render)
        self.model.setColor(color)
        self.model.setPos(position)
        self.position = position

    def getPos(self):
        return self.position

    def getStatus(self):
        return self.isFree

    def setStatus(self, status):
        self.isFree = status

    isFree = True;