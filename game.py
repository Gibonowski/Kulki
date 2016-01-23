#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Michał Gibas

from direct.showbase.ShowBase import ShowBase
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from panda3d.core import AmbientLight, DirectionalLight, LightAttrib
from panda3d.core import TextNode
from panda3d.core import LPoint3, LVector3, BitMask32
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task
from pandac.PandaModules import WindowProperties
import sys
from random import randint
from ball import Ball

# Definicja kolorów
GREY = (.95, .95, .95, 1)
WHITE = (1, 1, 1, 1)
HIGHLIGHT = (0, 1, 1, 1)
PIECEBLACK = (.15, .15, .15, 1)
WORLD = (0.3, 0.3, 0.3, 1)
BALLS = [(.65, .65, .65, 1), (1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1), (1, 1, 0, 1), (1, 0, 1, 1), (0, 1, 1, 1)]


def PointAtZ(z, point, vec):
    return point + vec * ((z - point.getZ()) / vec.getZ())

# Funkcja do pozycjonowania płytek
def SquarePos(i):
    return LPoint3((i % 9) - 4, int(i // 9) - 4.5, 0)

# Funkcja generująca kolory dla płytek
def SquareColor(i):
    if (i%2):
        return GREY
    else:
        return WHITE


class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Ustawienia
        base.setBackgroundColor(WORLD)
        props = WindowProperties()
        props.setTitle('Kulki 3D')
        props.setSize(1366, 768)
        base.win.requestProperties(props)

        # Elementy 2D
        self.escapeEvent = OnscreenText(
            text="Punkty: " + str(self.points), parent=base.a2dTopLeft,
            style=1, fg=(1, 1, 1, 1), pos=(0.06, -0.1),
            align=TextNode.ALeft, scale = .05)
        self.mouse1Event = OnscreenText(
            text="Trolololo",
            parent=base.a2dTopLeft, align=TextNode.ALeft,
            style=1, fg=(1, 1, 1, 1), pos=(0.06, -0.16), scale=.05)

        # Klawisze
        self.accept('escape', sys.exit)
        self.accept('f2', self.showFPS)

        # Kamera i światło
        self.disableMouse()
        camera.setPosHpr(0, -12, 8, 0, -35, 0)
        self.setupLights()

        # Kolizja
        self.picker = CollisionTraverser()
        self.pq = CollisionHandlerQueue()
        self.pickerNode = CollisionNode('mouseRay')
        self.pickerNP = camera.attachNewNode(self.pickerNode)
        self.pickerNode.setFromCollideMask(BitMask32.bit(1))
        self.pickerRay = CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)
        self.picker.addCollider(self.pickerNP, self.pq)

        # Utworzenie planszy
        self.squareRoot = render.attachNewNode("squareRoot")

        # Plansza 9x9
        self.squares = [None for i in range(81)]
        for i in range(81):
            self.squares[i] = loader.loadModel("square")
            self.squares[i].reparentTo(self.squareRoot)
            self.squares[i].setPos(SquarePos(i))
            self.squares[i].setColor(SquareColor(i))
            self.squares[i].find("**/polygon").node().setIntoCollideMask(BitMask32.bit(1))
            self.squares[i].find("**/polygon").node().setTag('square', str(i))

        # Kulki
        self.balls = [None for i in range(81)]

        for i in range(81):
            self.empty.append(True)

        # Losowanie pierwszych 3 kulek
        for i in range(3):
            ok = False
            while(not ok):
                x = randint(0, 80)
                if self.empty[x]:
                    self.balls[x] = Ball(SquarePos(x), BALLS[randint(0, 6)], render)
                    self.empty[x] = False
                    ok = True

        # Zmienna do podświetlenia
        self.highlited = False

        # zaznaczone
        self.isSelected = False
        self.dragging = False

        # Start the task that handles the picking
        self.mouseTask = taskMgr.add(self.mouseTask, 'mouseTask')
        self.accept("mouse1", self.grabPiece)  # left-click grabs a piece
        self.accept("mouse1-up", self.releasePiece)  # releasing places it

    # To zmienie na animacje kulek
    def swapPieces(self, fr, to):
        temp = self.balls[fr]
        self.balls[fr] = self.balls[to]
        self.balls[to] = temp
        if self.balls[fr]:
            self.balls[fr].square = fr
            self.balls[fr].model.setPos(SquarePos(fr))
        if self.balls[to]:
            self.balls[to].square = to
            self.balls[to].model.setPos(SquarePos(to))

    # Task do podświetlania płytek
    def mouseTask(self, task):

        # Czyszczenie podświetlenia
        if self.highlited is not False and self.highlited is not self.selected:
            self.squares[self.highlited].setColor(SquareColor(self.highlited))
            self.highlited = False

        # Sprawdzenie czy myszka znajduje się w polu okna
        if self.mouseWatcherNode.hasMouse():
            # Pozycja myszki
            mpos = self.mouseWatcherNode.getMouse()

            self.pickerRay.setFromLens(self.camNode, mpos.getX(), mpos.getY())

            # Podnoszenie
            if self.dragging is not False:
                # Gets the point described by pickerRay.getOrigin(), which is relative to
                # camera, relative instead to render
                nearPoint = render.getRelativePoint(
                    camera, self.pickerRay.getOrigin())
                # Same thing with the direction of the ray
                nearVec = render.getRelativeVector(
                    camera, self.pickerRay.getDirection())
                self.balls[self.dragging].model.setPos(
                    PointAtZ(.5, nearPoint, nearVec))

            # Do the actual collision pass (Do it only on the squares for
            # efficiency purposes)
            self.picker.traverse(self.squareRoot)
            if self.pq.getNumEntries() > 0:
                # if we have hit something, sort the hits so that the closest
                # is first, and highlight that node
                self.pq.sortEntries()
                i = int(self.pq.getEntry(0).getIntoNode().getTag('square'))
                # Set the highlight on the picked square
                self.squares[i].setColor(HIGHLIGHT)
                self.highlited = i

        return Task.cont

    def grabPiece(self):
        # If a square is highlighted and it has a piece, set it to dragging
        # mode
        if self.highlited is not False and self.balls[self.highlited]:
            self.dragging = self.highlited
            if(not self.isSelected):
                self.squares[self.highlited].setColor(HIGHLIGHT)
                self.selected =  self.highlited
                self.isSelected = True

            # musze tu jakoś rozjebać odnaczanie
            else:
                self.squares[self.highlited].setColor(SquareColor(self.highlited))
                self.highlited = False
                self.isSelected = False

    def releasePiece(self):
        # Letting go of a piece. If we are not on a square, return it to its original
        # position. Otherwise, swap it with the piece in the new square
        # Make sure we really are dragging something
        if self.dragging is not False:
            # We have let go of the piece, but we are not on a square
            if self.highlited is False:
                self.pieces[self.dragging].obj.setPos(
                    SquarePos(self.dragging))
            else:
                # Otherwise, swap the pieces
                self.swapPieces(self.dragging, self.highlited)

        # We are no longer dragging anything
        self.dragging = False

    def setupLights(self):  # This function sets up some default lighting
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor((.8, .8, .8, 1))
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setDirection(LVector3(0, 45, -45))
        directionalLight.setColor((0.2, 0.2, 0.2, 1))
        render.setLight(render.attachNewNode(directionalLight))
        render.setLight(render.attachNewNode(ambientLight))

    def showFPS(self):
        base.setFrameRateMeter(self.fps)
        self.fps = not self.fps

    points = 0
    fps = True
    empty = []
    selected = None


# To wyladuje w main
demo = Game()
demo.run()
