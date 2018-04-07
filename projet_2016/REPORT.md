# 3I025 - Projet 3

_Sources fournies dans le fichier 3I025-LOGLISCI-NASTURAS-03.tar.gz ci-joint, ou dans (le dépôt)[https://github.com/3201101/3I025/tree/master/Partie%203/app]._

L’objectif de ce projet a été de créer un algorithme capable d’apprendre tout seul comment gagner à un jeu consistant à peindre une plus grande surface de terrain que l'adversaire à l'aide de robots autonomes.

## Principe

Pour progresser, l'IA modifier aléatoirement chacun de ses paramètres selon une loi normale (gaussienne), et ce pour essayer d'améliorer sa _fitness_, la valeur qui mesure son efficacité. Celle-ci est simplement calculée en fonction du score de l'IA après chaque partie.

## Entrainement

    if fitness > bestFitness:
        bestFitness = fitness
        bestParams = params[:]
        sigma = min(max(0.1, sigma*2), 20)
        # ...
    else :
        sigma = max(2 ** (-1./4.) * sigma * (1  + math.sin(iteration / 2000)), 0.001 * (1 + math.sin(iteration / 2000)))

A chaque fois qu'une IA réalise un nouveau record, on conserve ses paramètres pour en faire un champion. On oppose alors ce champion à l'IA pendant les parties suivantes pour tenter d'obtenir un résultat encore meilleur. Enfin, on utilise une variable sigma qui pondérera les changements aléatoires de paramètres pour encourager les progrès et freiner les régressions. Cette variable est bornée, et même fonction de sinus en cas de régression, pour éviter de tout de même tomber dans des situations d'immobilisme où l'évolution s'arrête.

## Champions

Chaque nouvelle IA détentrice d'un record devient un champion. Ces champions servent à trouver d'encores meilleurs IA par comparaison. Mais en plus, chaque cinquième champion créé devient le nouvel adversaire de l'IA pour son entrainement.

    if fitness > bestFitness:
        # ...
        if enemisCpt % enemisMod == 0:
            setEnemisParams()

Cela permet de changer régulièrement l'adversaire de l'IA pour ne pas la laisser s'entraîner très longtemps contre un seul adversaire médiocre. Et on ne fait jouer que certains champions pour éviter d'optimiser l'IA contre elle-même uniquement.

## Protections

Pour améliorer encore la qualité de l'entrainement, on a ajouté une protection "anti-débile".

    while iteration != maxIterations:
        # ...
        if bestFitness * iteration / maxIterations / maxArena * outRatio > t:
            arena = maxArena - 1
            break

Cette ligne détecte les cas où une IA progresse trop lentement (selon un ratio arbitraire décidé avec la variable outRatio) afin d'éliminer rapidement une IA d'efficacité trop basse et passer à l'itération d'apprentissage suivante.