from baseFunctions import *


if __name__ == '__main__':
    nLives = 5
    score = 0

    rowWeights = getInitialWeights()
    gamemode = gamemodeSelection()
    print('Have fun! Type "stop" at any time to interrupt game')

    while nLives>0:
        randomRow, rowWeights = getRandomRow(rowWeights)
        guess = guessWordTranslation(randomRow, gamemode)
        if guess == 'stop':
            print('Thanks for playing!')
            break

        newLives, score = checkWordTranslation(guess, randomRow, gamemode, nLives, score)
        rowWeights = adjustWeights(rowWeights, randomRow, newLives-nLives)

        nLives = newLives
        if nLives == 0:
            print(f'You are out of lives.\nFinal score: {score}\n Game over')


