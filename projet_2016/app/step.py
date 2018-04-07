def step(self):

        color( (0,255,0) )
        circle( *self.getRobot().get_centroid() , r = 22) # je dessine un rond bleu autour de ce robot

        #print "robot #", self.id, " -- step"

        p = self.robot
        
        #params = [7.768477026858286, 0.19808033076339562, -3.276666110149957, 158.2300381012713, 4.973785132986818, 168.89033837709565, -1.1890910121721885, 181.3019038907149, -0.7288753340776037, 75.70922042927258, -4.117614838147645, 78.80310331635602, 9.475288403760853, 79.20991258608966, 0.652314697990763, 45.79310481916451, -7.289982358746094, 32.900016319270236, 1.0, 40.0, 1.0, 20.0, 1.0, 20.0, 1.0, 20.0, 1.0, -20.0, 1.0, -20.0, 1.0, -20.0, 1.0, -40.0, 1.0, -40.0, 1.0, -40.0, 1.0, -80.0, 1.0, -80.0, 1.0, -80.0, 1.0, -170.0, 1.0, -170.0, 1.0, -170.0]
	params = [23.118374831751687, -0.3650536516354801, -2.995461122681323, 166.65086280291163, 8.520056350269282, 173.02226057763048, -7.184313407807772, 173.57276371303658, 1.9963953074938825, 88.35124901891274, -4.992124921370944, 71.46822797263835, 9.88913576327111, 75.0562888730577, 14.143233760832363, 37.03238333420831, -5.000570096269627, 33.68123354442115, 1.0, 40.0, 1.0, 20.0, 1.0, 20.0, 1.0, 20.0, 1.0, -20.0, 1.0, -20.0, 1.0, -20.0, 1.0, -40.0, 1.0, -40.0, 1.0, -40.0, 1.0, -80.0, 1.0, -80.0, 1.0, -80.0, 1.0, -170.0, 1.0, -170.0, 1.0, -170.0]

        
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
