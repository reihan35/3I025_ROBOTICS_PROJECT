#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# multirobot_teamwars.py
# Contact (ce fichier uniquement): nicolas.bredeche(at)upmc.fr
# Ce code utilise pySpriteWorld, développé par Yann Chevaleyre (U. Paris 13)
# 
# Description:
#   Template pour projet multi-robots "MULTIROBOT WARS"
#       But du jeu: posséder le maximum de cases!
#           Chaque joueur dispose de quatre robots
#           Le monde est divisé en 1024 cases (ie. 32x32 cases de 16x16 pixels)
#           Le jeu tourne pendant 4000 itérations
#           Une case "appartient" à la dernière équipe qui l'a visitée
#       Ce que vous avez le droit de faire:
#           Vous ne pouvez modifier que la méthode step(.) de la classe AgentTypeA
#           Les vitesses de translation et rotation maximales sont données par maxTranslationSpeed et maxRotationSpeed
#           La distance maximale autorisée des senseurs est maxSensorDistance
#       Recommandations:
#           Conservez intact multirobot_teamwars.py (travaillez sur une copie!)
#           Pour faire vos tests, vous pouvez aussi modifier (si vous le souhaitez) la méthode step() pour la classe AgentTypeB. Il ne sera pas possible de transmettre cette partie là lors de l'évaluation par contre.
#           La manière dont vous construirez votre fonction step(.) est libre. Par exemple:
#               code écrit à la main, code obtenu par un processus d'apprentissage ou d'optimisation préalable, etc.
#               comportements individuels, collectifs, parasites (p.ex: bloquer l'adversaire), etc.
#       Evaluation:
#           Soutenance devant machine (par binome, 15 min.) lors de la dernière séance de TP (matin et après-midi)
#               Vous devrez montrer votre résultat sur trois arènes inédites
#               Vous devrez mettre en évidence la réutilisation des concepts vus en cours
#               Vous devrez mettre en évidence les choix pragmatiques que vous avez du faire
#               Assurez vous que la simple copie de votre fonctions step(.) dans le fichier multirobots_teamwars.py suffit pour pouvoir le tester
#           Vous affronterez vos camarades
#               Au tableau: une matrice des combats a mettre a jour en fonction des victoires et défaites
#               Affrontement sur les trois arènes inédites
#               vous pouvez utiliser http://piratepad.net pour échanger votre fonction step(.))
#       Bon courage!
# 
# Dépendances:
#   Python 2.x
#   Matplotlib
#   Pygame
# 
# Historique: 
#   2016-03-28__23:23 - template pour 3i025 (IA&RO, UPMC, licence info)
#
# Aide: code utile
#   - Partie "variables globales"
#   - La méthode "step" de la classe Agent
#   - La fonction setupAgents (permet de placer les robots au début de la simulation)
#   - La fonction setupArena (permet de placer des obstacles au début de la simulation)
#   - il n'est pas conseillé de modifier les autres parties du code.
# 

import sys,os
cwd = os.getcwd()
sys.path.append(cwd.replace("app", "pySpriteWorld", 1))

from robosim import *
from random import random, shuffle, gauss
import time
import sys
import atexit
import math


'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''
'''  variables globales   '''
'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''

game = Game()
agents = []

arena = 0
maxArena = 3

nbAgents = 8 # doit être pair et inférieur a 32
maxSensorDistance = 30              # utilisé localement.
maxRotationSpeed = 5
maxTranslationSpeed = 1
SensorBelt = [-170,-80,-40,-20,+20,40,80,+170]  # angles en degres des senseurs

screen_width=512 #512,768,... -- multiples de 32  
screen_height=512 #512,768,... -- multiples de 32

maxIterations = 6000 # infinite: -1 #6000
maxGeneIteration = -1
showSensors = False
frameskip = 100   # 0: no-skip. >1: skip n-1 frames
verbose = True

def setOccupancyGrid():
    global occupancyGrid, screen_height, screen_width
    occupancyGrid = []
    for y in range(screen_height/16):
        l = []
        for x in range(screen_width/16):
            l.append("_")
        occupancyGrid.append(l)


fic = "bestParams.txt"
ficBackup = "bestParamsBackup.txt"
nomFic = fic
def saveParamsIn(f, p):
    with open(f, "w") as fic:
        fic.write(repr(params))
    fic.close()
def getParamsIn(f):
    with open(f, "r") as fic:
        return eval(fic.read())
    fic.close()

enemisCpt = 0
enemisMod = 5

outRatio = 0.3
fitness = 0
bestFitness = - sys.maxint
sigma = 1

def saveParams() :
    saveParamsIn(nomFic, params)
    backupParams()
def setParams():
    global params
    params = getParamsIn(nomFic)
def backupParams():
    with open(ficBackup, "a") as fic:
        fic.write(repr(params)+'\n')
    fic.close()
def setEnemisParams():
    global enemisParams
    with open(ficBackup, "r") as fic:
        enemisParams = eval(fic.readlines()[-1])
    fic.close()
params = []
enemisParams = []
setParams()
setEnemisParams()
#params = [random()*2.-1 for x in range(2 + len(SensorBelt) * 2 * 3)] # [biais rotation, translation, parametre capteur mur, allié, enemie]
    
    
def algoGen():
    global fitness, bestFitness, sigma, bestParams, enemisCpt
    
    print "BEST FITNESS :" + str(bestFitness)
    print "FITNESS :" + str(fitness)
    if fitness > bestFitness:
        bestFitness = fitness
        bestParams = params[:]
        sigma = min(max(0.1, sigma*2), 20)
        if enemisCpt != 0:        
            saveParams()
        print "NEW SIGMA (better) : " + str(sigma)
        print bestParams
        if enemisCpt % enemisMod == 0:
            setEnemisParams()
        enemisCpt += 1
    else :
        print "NEW SIGMA (poor) : " + str(sigma)
        sigma = max(2 ** (-1./4.) * sigma * (1  + math.sin(iteration / 2000)), 0.001 * (1 + math.sin(iteration / 2000)))
    for i in range(len(SensorBelt)*2+2):
        params[i] = bestParams[i] + gauss(0,sigma)
    fitness = 0

'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''
'''  Agent "A"            '''
'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''

class AgentTypeA(object):
    
    agentIdCounter = 0 # use as static
    id = -1
    robot = -1
    agentType = "A"

    def __init__(self,robot):
        self.id = AgentTypeA.agentIdCounter
        AgentTypeA.agentIdCounter = AgentTypeA.agentIdCounter + 1
        #print "robot #", self.id, " -- init"
        self.robot = robot

    def getType(self):
        return self.agentType

    def getRobot(self):
        return self.robot

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-= JOUEUR A -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    teamname = "Equipe Alpha" # A modifier avec le nom de votre équipe

    def step(self):

        color( (0,255,0) )
        circle( *self.getRobot().get_centroid() , r = 22) # je dessine un rond bleu autour de ce robot

        #print "robot #", self.id, " -- step"

        p = self.robot

        # actions
        sensor_infos = sensors[p]

        def isEnemy(p):
            return agents[p].getType != self.agentType
        
        # calcul des sorties motrices en fonction des parametres
        j = 0
        translation = params[j] # biais 1
        j = j + 1
        rotation = params[j] # biais 2
        j = j + 1

        for i in range(len(SensorBelt)): # parametres pour la rotation
            dist = sensor_infos[i].dist_from_border
            if dist > maxSensorDistance:
                dist = maxSensorDistance # borne
            if sensor_infos[i].layer == 'joueur':
                if isEnemy(sensor_infos[i].sprite.numero):
                    translation += (1 - dist / maxSensorDistance) * params[j+4]
                    rotation += (1 - dist / maxSensorDistance) * params[j+5]
                else :
                    translation += (1 - dist / maxSensorDistance) * params[j+2]
                    rotation += (1 - dist / maxSensorDistance) * params[j+3]
            else:
                translation += (1 - dist / maxSensorDistance) * params[j]
                rotation += (1 - dist / maxSensorDistance) * params[j+1]
            j += 6

        if rotation > maxRotationSpeed:
            rotation = maxRotationSpeed
        elif rotation < -maxRotationSpeed:
            rotation = -maxRotationSpeed

        if translation > maxTranslationSpeed:
            translation = maxTranslationSpeed
        elif translation < -maxTranslationSpeed:
            translation = -maxTranslationSpeed

        p.rotate(rotation)   
        p.forward(translation)

        return

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=



'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''
'''  Agent "B"            '''
'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''

class AgentTypeB(object):
    
    agentIdCounter = 0 # use as static
    id = -1
    robot = -1

    agentType = "B"

    def __init__(self,robot):
        self.id = AgentTypeB.agentIdCounter
        AgentTypeB.agentIdCounter = AgentTypeB.agentIdCounter + 1
        #print "robot #", self.id, " -- init"
        self.robot = robot

    def getType(self):
        return self.agentType

    def getRobot(self):
        return self.robot


    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-= JOUEUR B -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    teamname = "Equipe Test" # A modifier avec le nom de votre équipe

    def step(self):

        color( (0,0,255) )
        circle( *self.getRobot().get_centroid() , r = 22) # je dessine un rond bleu autour de ce robot

        #print "robot #", self.id, " -- step"

        p = self.robot        
        
        # actions
        sensor_infos = sensors[p]

        def isEnemy(p):
            return agents[p].getType != self.agentType
        
        # calcul des sorties motrices en fonction des parametres
        j = 0
        translation = enemisParams[j] # biais 1
        j = j + 1
        rotation = enemisParams[j] # biais 2
        j = j + 1

        for i in range(len(SensorBelt)): # parametres pour la rotation
            dist = sensor_infos[i].dist_from_border
            if dist > maxSensorDistance:
                dist = maxSensorDistance # borne
            if sensor_infos[i].layer == 'joueur':
                if isEnemy(sensor_infos[i].sprite.numero):
                    translation += (1 - dist / maxSensorDistance) * enemisParams[j+4]
                    rotation += (1 - dist / maxSensorDistance) * enemisParams[j+5]
                else :
                    translation += (1 - dist / maxSensorDistance) * enemisParams[j+2]
                    rotation += (1 - dist / maxSensorDistance) * enemisParams[j+3]
            else:
                translation += (1 - dist / maxSensorDistance) * enemisParams[j]
                rotation += (1 - dist / maxSensorDistance) * enemisParams[j+1]
            j += 6

        if rotation > maxRotationSpeed:
            rotation = maxRotationSpeed
        elif rotation < -maxRotationSpeed:
            rotation = -maxRotationSpeed

        if translation > maxTranslationSpeed:
            translation = maxTranslationSpeed
        elif translation < -maxTranslationSpeed:
            translation = -maxTranslationSpeed

        p.rotate(rotation)   
        p.forward(translation)

        return

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=



'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''
'''  Fonctions init/step  '''
'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''


def setupAgents():
    global screen_width, screen_height, nbAgents, agents, game

    # Make agents

    nbAgentsTypeA = nbAgentsTypeB = nbAgents / 2
    nbAgentsCreated = 0

    for i in range(nbAgentsTypeA):
        p = game.add_players( (16 , 200+32*i) , None , tiled=False)
        p.oriente( 0 )
        p.numero = nbAgentsCreated
        nbAgentsCreated = nbAgentsCreated + 1
        agents.append(AgentTypeA(p))

    for i in range(nbAgentsTypeB):
        p = game.add_players( (486 , 200+32*i) , None , tiled=False)
        p.oriente( 180 )
        p.numero = nbAgentsCreated
        nbAgentsCreated = nbAgentsCreated + 1
        agents.append(AgentTypeB(p))

    game.mainiteration()



def setupArena0():
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

def setupArena1():
    return

def setupArena2():
    for i in range(0,8):
        addObstacle(row=i,col=7)
    for i in range(8,16):
        addObstacle(row=i,col=8)

def stepWorld():

    efface()
        
    # chaque agent se met à jour. L'ordre de mise à jour change à chaque fois (permet d'éviter des effets d'ordre).
    shuffledIndexes = [i for i in range(len(agents))]
    shuffle(shuffledIndexes)     # erreur sur macosx
    for i in range(len(agents)):
        agents[shuffledIndexes[i]].step()
        # met à jour la grille d'occupation
        coord = agents[shuffledIndexes[i]].getRobot().get_centroid()
        occupancyGrid[int(coord[0])/16][int(coord[1])/16] = agents[shuffledIndexes[i]].getType() # first come, first served
    return

def reInitAgents():
    global agents
    
    j = 0
    k = 0
    for i in agents:
        if i.agentType == 'A':
            i.robot.x = 16
            i.robot.y = 200+32 * j
            i.robot.oriente(0)
            j +=1
        else:
            i.robot.x = 486
            i.robot.y = 200+32 * k
            i.robot.oriente(180)
            k +=1

def setupArena():
    global arena
    
    game.del_all_sprites('obstacle')
    
    if arena == 0:
        setupArena0()
    elif arena == 1:
        setupArena1()
    else:
        setupArena2()
    
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

def displayOccupancyGrid():
    global iteration
    nbA = nbB = nothing = 0

    for y in range(screen_height/16):
        for x in range(screen_width/16):
            sys.stdout.write(occupancyGrid[x][y])
            if occupancyGrid[x][y] == "A":
                nbA = nbA+1
            elif occupancyGrid[x][y] == "B":
                nbB = nbB+1
            else:
                nothing = nothing + 1
        sys.stdout.write('\n')

    sys.stdout.write('Time left: '+str(maxIterations-iteration)+'\n')
    sys.stdout.write('Summary: \n')
    sys.stdout.write('\tType A: ')
    sys.stdout.write(str(nbA))
    sys.stdout.write('\n')
    sys.stdout.write('\tType B: ')
    sys.stdout.write(str(nbB))
    sys.stdout.write('\n')
    sys.stdout.write('\tFree  : ')
    sys.stdout.write(str(nothing))
    sys.stdout.write('\n')
    sys.stdout.flush() 

    return nbA,nbB,nothing

def onExit(): 
    
    ret = displayOccupancyGrid()
    print "\n\n=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-="
    if ret[0] > ret[1]:
        print "Robots type A (\"" + str(AgentTypeA.teamname) + "\") wins!"
    elif ret[0] < ret[1]:
        print "Robots type B (\"" + str(AgentTypeB.teamname) + "\") wins!"
    else: 
        print "Nobody wins!"
    print "=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n"
    print "\n[Simulation::stop]"
    
    return ret


'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''
'''  Main loop            '''
'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''

#try:
setOccupancyGrid()
init('vide3',MyTurtle,screen_width,screen_height) # display is re-dimensioned, turtle acts as a template to create new players/robots
game.auto_refresh = False # display will be updated only if game.mainiteration() is called
game.frameskip = frameskip
atexit.register(onExit)
setupArena()
setupAgents()
game.mainiteration()

geneIteration = 0
while geneIteration != maxGeneIteration :

    iteration = 0
    while iteration != maxIterations:
        # c'est plus rapide d'appeler cette fonction une fois pour toute car elle doit recalculer le masque de collision,
        # ce qui est lourd....
        sensors = throw_rays_for_many_players(game, game.layers['joueur'], SensorBelt, max_radius = maxSensorDistance+game.player.diametre_robot(), show_rays=showSensors)
        stepWorld()
        if iteration % 200 == 0:
            t = displayOccupancyGrid()[0]
            if bestFitness * iteration / maxIterations / maxArena * outRatio > t:
                arena = maxArena - 1
                break
        game.mainiteration()
        iteration = iteration + 1
        
    ret = onExit()
    if ret[0] > ret[1]:
        fitness += 2 * ret[0]
    elif ret[0] < ret[1]:
        fitness += ret[0] // 2
    else :
        fitness += ret[0]
  
    if arena == maxArena - 1:
        algoGen()    
        geneIteration += 1
    
    reInitAgents()
    arena = (arena + 1) % maxArena
    setupArena()
    setOccupancyGrid()
    game.mainiteration()
        
        
#except SystemExit as e:
    #onExit()
    #except ValueError as e:
    #    exit()
