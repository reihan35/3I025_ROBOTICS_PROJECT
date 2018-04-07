#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# multirobot.py
# Contact (ce fichier uniquement): nicolas.bredeche(at)upmc.fr
# 
# Description:
#   Template pour simulation mono- et multi-robots type khepera/e-puck/thymio
#   Ce code utilise pySpriteWorld, dÃ©veloppÃ© par Yann Chevaleyre (U. Paris 13)
# 
# DÃ©pendances:
#   Python 2.x
#   Matplotlib
#   Pygame
# 
# Historique: 
#   2016-03-28__23:23 - template pour 3i025 (IA&RO, UPMC, licence info)
#
# Aide: code utile
#   - Partie "variables globales"
#   - La mÃ©thode "step" de la classe Agent
#   - La fonction setupAgents (permet de placer les robots au dÃ©but de la simulation)
#   - La fonction setupArena (permet de placer des obstacles au dÃ©but de la simulation)
#   - il n'est pas conseillÃ© de modifier les autres parties du code.
# 

import sys,os
cwd = os.getcwd()
sys.path.append(cwd.replace("app", "pySpriteWorld", 1))

from robosim import *
import math
from random import random, shuffle, gauss
import time
import sys
import atexit
from itertools import count


'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''
'''  Aide                 '''
'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''

#game.setMaxTranslationSpeed(3) # entre -3 et 3
# size of arena: 
#   screenw,screenh = taille_terrain()
#   OU: screen_width,screen_height

'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''
'''  variables globales   '''
'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''

game = Game()

agents = []
screen_width=512 #512,768,... -- multiples de 32  
screen_height=512 #512,768,... -- multiples de 32
nbAgents = 1

maxSensorDistance = 30              # utilisÃ© localement.
maxRotationSpeed = 5
maxTranslationSpeed = 3
SensorBelt = [-170,-80,-40,-20,+20,40,80,+170]  # angles en degres des senseurs

maxIterations = -1 # infinite: -1

showSensors = False
frameskip = 0   # 0: no-skip. >1: skip n-1 frames
verbose = True

'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''
'''  Classe Agent/Robot   '''
'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''

class Agent(object):
    
    agentIdCounter = 0 # use as static
    id = -1
    robot = -1
    name = "Equipe Alpha" # A modifier avec le nom de votre Ã©quipe
    params = []

    def __init__(self,robot):
        self.id = Agent.agentIdCounter
        Agent.agentIdCounter = Agent.agentIdCounter + 1
        #print "robot #", self.id, " -- init"
        self.robot = robot

    def getRobot(self):
        return self.robot

    def step(self):

        #print "robot #", self.id, " -- step"
        p = self.robot
        sensor_infos = sensors[p]


        self.params = [0.21051756848051448, -0.11135408851060026, 0.20360584821789537, -0.20548803001164853, 0.2186973467500787, 0.22196257459680846, 0.21065947550485253, -0.22557303830338843, -0.08570901189806411, -0.24536128718198927, 0.22996000995376809, -0.2245294545010238, 0.19597579377128824, 0.21347215686912868, 0.2143933572792422, -0.15248150354537204, -0.1520667883613749, -0.22202059815691266]
       
        
        # calcul des sorties motrices en fonction des parametres
        j = 0
        translation = self.params[j] # biais 1
        j = j + 1
        rotation = self.params[j] # biais 2
        j = j + 1
        minDist = maxSensorDistance
        for i in range(len(SensorBelt)): # parametres pour la rotation
            dist = sensor_infos[i].dist_from_border
            if dist > maxSensorDistance:
                dist = maxSensorDistance # borne
            if dist < minDist:  # Recuperation de la valeur minimale
                minDist = dist
            translation += dist * self.params[j]
            rotation += dist * self.params[j]
            j = j + 1

        if rotation > maxRotationSpeed:
            rotation = maxRotationSpeed
        elif rotation < -maxRotationSpeed:
            rotation = -maxRotationSpeed

        if translation > maxTranslationSpeed:
            translation = maxTranslationSpeed
        elif translation < maxTranslationSpeed:
            translation = -maxTranslationSpeed

        p.rotate(rotation)   
        p.forward(translation) 

        return


'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''
'''  Fonctions init/step  '''
'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''

def setupAgents():
    global screen_width, screen_height, nbAgents, agents, game

    # Make agents
    nbAgentsCreated = 0
    for i in range(nbAgents):
        while True:
            p = -1
            while p == -1: # p renvoi -1 s'il n'est pas possible de placer le robot ici (obstacle)
                p = game.add_players( (random()*screen_width , random()*screen_height) , None , tiled=False)
            if p:
                p.oriente( random()*360 )
                p.numero = nbAgentsCreated
                nbAgentsCreated = nbAgentsCreated + 1
                agents.append(Agent(p))
                break
    game.mainiteration()


def setupArena():
    for i in range(6,13):
        addObstacle(row=3,col=i)
    for i in range(3,10):
        addObstacle(row=12,col=i)
    addObstacle(row=4,col=12)
    addObstacle(row=5,col=12)
    addObstacle(row=6,col=12)
    addObstacle(row=11,col=3)
    addObstacle(row=10,col=3)
    addObstacle(row=9,col=3)



def stepWorld():
    # chaque agent se met Ã  jour. L'ordre de mise Ã  jour change Ã  chaque fois (permet d'Ã©viter des effets d'ordre).
    shuffledIndexes = [i for i in range(len(agents))]
    shuffle(shuffledIndexes)     ### TODO: erreur sur macosx
    for i in range(len(agents)):
        agents[shuffledIndexes[i]].step()
    return


'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''
'''  Fonctions internes   '''
'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''

def addObstacle(row,col):
    # le sprite situe colone 13, ligne 0 sur le spritesheet
    game.add_new_sprite('obstacle',tileid=(0,13),xy=(col,row),tiled=True)

class MyTurtle(Turtle): # also: limit robot speed through this derived class
    maxRotationSpeed = maxRotationSpeed # 10, 10000, etc.
    def rotate(self,a):
        mx = MyTurtle.maxRotationSpeed
        Turtle.rotate(self, max(-mx,min(a,mx)))

def onExit():
    print "\n[Terminated]"

'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''
'''  Main loop            '''
'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''

init('vide3',MyTurtle,screen_width,screen_height) # display is re-dimensioned, turtle acts as a template to create new players/robots
game.auto_refresh = False # display will be updated only if game.mainiteration() is called
game.frameskip = frameskip
atexit.register(onExit)

setupArena()
setupAgents()
game.mainiteration()

iteration = 0
while iteration != maxIterations:
    # c'est plus rapide d'appeler cette fonction une fois pour toute car elle doit recalculer le masque de collision,
    # ce qui est lourd....
    sensors = throw_rays_for_many_players(game,game.layers['joueur'],SensorBelt,max_radius = maxSensorDistance+game.player.diametre_robot() , show_rays=showSensors)
    stepWorld()
    game.mainiteration()
    iteration = iteration + 1