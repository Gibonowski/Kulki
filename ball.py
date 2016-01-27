# -*- coding: utf-8 -*-

class Ball(object):
    def __init__(self, position, color, render, scale = (1, 1 ,1)):
        self.model = loader.loadModel("ball")
        self.model.reparentTo(render)
        self.model.setColor(color)
        self.model.setPos(position)
        self.model.setScale(scale)
        self.color = color

    def resize(self, x, y,z):
        self.model.setScale(x, y, z)