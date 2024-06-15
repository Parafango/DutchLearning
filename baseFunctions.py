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

def getWordType(row):
    if pd.isna(row['count']):
        isAdjective = 1
    else:
        isAdjective = 0
    return isAdjective

def getWordArticle(row):
    isHetWord = 0
    if row['gender'] == 'n' and row['count'] == 's':
        isHetWord = 1

    return isHetWord

def guessWordTranslation(row, gamemode):
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

def getCorrectGuess(row, gamemode):
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


def checkWordTranslation(guess, row, gamemode):
    correctGuess = getCorrectGuess(row, gamemode)
    if guess == correctGuess:
        print('Correct!')
    else:
        print('Wrong, the correct translation was:"' + correctGuess + '"')

