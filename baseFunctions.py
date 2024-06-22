import numpy
import pandas as pd
import numpy as np
import random

import pandas.core.series


def gamemodeSelection() -> int:
    gamemodeSelected = input('Choose gamemode: dutch to english (de) or english to dutch (ed)?')
    while True:
        if gamemodeSelected not in ['de', 'ed']:
            gamemodeSelected = input('Try Again. Choose gamemode: dutch to english (de) or english to dutch (ed)?')
        else:
            break
    gamemodeChoices = {'ed': 0, 'de': 1}
    gamemode = gamemodeChoices[gamemodeSelected]
    return gamemode

def getInitialWeights() -> numpy.ndarray:
    df = pd.read_csv('DuolingoWords.csv')
    nRows = df.shape[0]
    initialWeights = np.ones(nRows) * 4
    return initialWeights

def adjustWeights(rowWeights: numpy.ndarray, randomRow: pandas.core.series.Series, delta: int) -> np.ndarray:
    df = pd.read_csv('DuolingoWords.csv')
    randomN = df.index[(df['english']==randomRow['english']) & (df['gender']==randomRow['gender'])].tolist()
    if delta == 0:
        rowWeights[randomN] = rowWeights[randomN] - 1
    else:
        rowWeights[randomN] = rowWeights[randomN] + 1

    return rowWeights

def getRandomRow(rowWeights: numpy.ndarray) -> (pd.core.series.Series, np.ndarray):
    df = pd.read_csv('DuolingoWords.csv')
    nRows = df.shape[0]
    randomN = random.choices(np.arange(nRows), rowWeights, k=1)[0]
    randomRow = df.iloc[randomN]
    return randomRow, rowWeights

def getWordType(row: pd.core.series.Series) -> int:
    if pd.isna(row['count']):
        isAdjective = 1
    else:
        isAdjective = 0
    return isAdjective

def getWordArticle(row: pd.core.series.Series) -> int:
    isHetWord = 0
    if row['gender'] == 'n' and row['count'] == 's':
        isHetWord = 1

    return isHetWord

def guessWordTranslation(row: pd.core.series.Series, gamemode: int) -> str:
    isAdjective = getWordType(row)
    if gamemode:
        prompt = '"' + row['dutch'] + '" in english is: '
    else:
        word = row['english']
        if isAdjective:
            word = word + ' (' + row['gender'] + ')'
        else:
            word = '"the ' + word + '"'

        prompt = word + ' in dutch is: '

    guess = input(prompt)
    return guess

def getCorrectGuess(row: pd.core.series.Series, gamemode: int) -> str:
    isAdjective = getWordType(row)
    gamemodeToDestinationColumnMapper = {0: 'dutch', 1: 'english'}
    correctGuess = row[gamemodeToDestinationColumnMapper[gamemode]]

    if not (isAdjective or gamemode):
        isHetWord = getWordArticle(row)
        if isHetWord:
            correctGuess = 'het ' + correctGuess
        else:
            correctGuess = 'de ' + correctGuess

    return correctGuess


def checkWordTranslation(guess: str, row: pd.core.series.Series, gamemode: int, nLives: int, score: int) -> (int, int):
    correctGuess = getCorrectGuess(row, gamemode)
    if guess == correctGuess:
        print('Correct!')
        score = score + 1
    else:
        print('Wrong, the correct translation was:"' + correctGuess + '"')
        nLives = nLives - 1

    return nLives, score
