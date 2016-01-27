#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Michał Gibas
#         Paweł Wilkaniec
#         Marek Wyrostek

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

        # Zmienne
        self.points = 0
        self.fps = True
        self.selected = None
        self.counter = 81
        self.koniec = False

        # Elementy 2D
        self.PointsText = OnscreenText(
            text="Punkty: " + str(self.points), parent=base.a2dTopLeft,
            style=1, fg=(1, 1, 1, 1), pos=(0.06, -0.1),
            align=TextNode.ALeft, scale = .05)
        self.newGameText = OnscreenText(
            text="N - Nowa Gra",
            parent=base.a2dTopLeft, align=TextNode.ALeft,
            style=1, fg=(1, 1, 1, 1), pos=(0.06, -0.16), scale=.05)

        # Klawisze
        self.accept('escape', sys.exit)
        self.accept('f2', self.showFPS)
        self.accept('n', self.newGame)

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
        self.empty = []

        for i in range(81):
            self.empty.append(True)

        # Losowanie pierwszych 3 kulek
        for i in range(3):
            self.randBall()

        # Zmienna do podświetlenia
        self.highlited = False

        # Zaznaczone
        self.isSelected = False
        self.dragging = False

        # Włączenie tasku do podświetlania pól
        self.mouseTask = taskMgr.add(self.mouseTask, 'mouseTask')
        self.accept("mouse1", self.LBMevent)

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

            # Podświetlanie
            self.picker.traverse(self.squareRoot)
            if self.pq.getNumEntries() > 0:
                self.pq.sortEntries()
                i = int(self.pq.getEntry(0).getIntoNode().getTag('square'))
                # Ustawienie koloru podświetlenia
                self.squares[i].setColor(HIGHLIGHT)
                self.highlited = i

        return Task.cont

    def LBMevent(self):
        if self.highlited is not False and self.balls[self.highlited]:
            # Jeśli nic nie zaznaczone to zaznacz
            if not self.isSelected:
                self.selected =  self.highlited
                self.isSelected = True

            # Zmiana zaznaczenia na inną kulkę
            elif self.isSelected and self.selected is not self.highlited:
                self.squares[self.selected].setColor(SquareColor(self.selected))
                self.selected = self.highlited

            # Jeśli zaznaczone
            else:
                # Odznaczanie
                if self.highlited == self.selected:
                    self.squares[self.highlited].setColor(SquareColor(self.highlited))

                    self.highlited = False
                    self.isSelected = False
                    self.selected = None

        # Przemieszczenie kulki
        else:
            if self.isSelected and self.empty[self.highlited]:
                #self.checkWay(self.selected, self.highlited)
                self.empty[self.selected] = True
                self.empty[self.highlited] = False
                self.squares[self.selected].setColor(SquareColor(self.selected))
                self.balls[self.selected].model.setPos(SquarePos(self.highlited))
                self.balls[self.highlited] = self.balls[self.selected]
                self.balls[self.selected] = None
                self.isSelected = False
                self.selected = None

                # Sprawdzanie kulek
                if(not self.checkColors()):
                    # Losowanie kulki po wykonanym ruchu
                    for i in range(3):
                        if self.counter > 0:
                            self.randBall()
                        else:
                            break
                    if self.counter == 0:
                        self.gameOver = OnscreenText(
                            text="Koniec Gry!",
                            align=TextNode.ACenter,
                            style=1, fg=(1, 1, 1, 1), scale=.3)
                        self.koniec = True

    # Losowanie piłek
    def randBall(self):
        ok = False
        # Losuj pole aż będzie puste
        while(not ok):
            x = randint(0, 80)
            if self.empty[x]:
                self.balls[x] = Ball(SquarePos(x), BALLS[randint(0, 6)], render)
                self.empty[x] = False
                ok = True
        self.counter -= 1

    def checkColors(self):
        value = False
        toDelete = []
        firstBall = False
        lenght = 0
        for i in range(81):
            # Sprawdzanie w poziomie

            # Jeśli kolumna mniejsza od 4
            # to sprawdzaj na prawo
            if i % 9 < 4:
                for j in range(i, 81):
                    if not self.empty[j]:
                        if not firstBall:
                            firstBall = self.balls[j].color
                            toDelete.append(j)
                            lenght += 1
                        else:
                            if self.balls[j].color == firstBall:
                                toDelete.append(j)
                                lenght += 1
                    else:
                        if lenght > 4:
                            value = True
                            self.points += (lenght - 4) ** 2
                            self.PointsText.destroy()
                            self.PointsText = OnscreenText(
                                text="Punkty: " + str(self.points), parent=base.a2dTopLeft,
                                style=1, fg=(1, 1, 1, 1), pos=(0.06, -0.1),
                                align=TextNode.ALeft, scale = .05)
                            for i in range(lenght):
                                self.balls[toDelete[i]].model.removeNode()
                                self.balls[i] = None
                                self.empty[i] = True
                                self.counter += 1
                        for x in toDelete:
                            toDelete.pop()
                        firstBall = False
                        lenght = 0
                        break

            return value

            '''# Sprawdzaj w prawo i lewo
            elif i % 9 == 4:
                #sprawdz w lewo i w prawo
            # Sprawdzaj na lewo
            else:
                #sprawdzanie na lewo

            # Sprawdzanie w pionie
            # Jeśli wiersz mniejszy od 4
            # to sprawdzaj do góry
            if i / 9 < 4:
                #sprawdzanie w górę
            # Sprawdzaj w górę i w dół
            if i / 9 == 4:
                #góra i dół
            # Sprawdzaj w dół
            else:
                #sprawdzanie w dół

            # Sprawdzanie po skosie'''

            #print '-----'



    # Sprawdzanie drogi
    def checkWay(self, start, finish):
        startColumn =  start % 9
        startRow = start / 9
        finishColumn = finish % 9
        finishRow = finish / 9
        directionX = finishColumn - startColumn
        directionY =  finishRow - startRow

        way = []
        current = start
        while(True):
            if directionX > 0:
                if self.empty[current+1] == True:
                    current = current +1
                    way.append(current+1)
            break

    # Ustawienie oświetlenia
    def setupLights(self):
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

    # Zacznij od nowa / wyzeruj wszystko
    def newGame(self):
        for i in range(81):
            if not self.empty[i]:
                self.balls[i].model.removeNode()
                self.balls[i] = None
                self.empty[i] = True

        if self.koniec:
            self.gameOver.destroy()

        self.PointsText.destroy()
        self.PointsText = OnscreenText(
                                text="Punkty: " + str(self.points), parent=base.a2dTopLeft,
                                style=1, fg=(1, 1, 1, 1), pos=(0.06, -0.1),
                                align=TextNode.ALeft, scale = .05)

        self.koniec = False
        self.points = 0
        self.selected = None
        self.counter = 81

        for i in range(3):
            self.randBall()


gra = Game()
gra.run()
