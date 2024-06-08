import numpy as np
import pandas as pd
import random

def gamemodeSelection():
    gamemodeSelected = input('Choose gamemode: dutch to english (de) or english to dutch (ed)?')
    while True:
        if gamemodeSelected not in ['de', 'ed']:
            gamemodeSelected = input('Try Again. Choose gamemode: dutch to english (de) or english to dutch (ed)?')
        else:
            break
    gamemodeChoices = {'ed': 0, 'de': 1}
    gamemode = gamemodeChoices[gamemodeSelected]
    return gamemode


def getRandomRow():
    df = pd.read_csv('DuolingoWords.csv')
    nRows = df.shape[0]
    randomN = random.randrange(0,nRows)
    randomRow = df.iloc[randomN]
    return randomRow