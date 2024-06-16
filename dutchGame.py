from baseFunctions import *

if __name__ == '__main__':
    nLives = 5
    score = 0

    initialWeights = getInitialWeights()
    gamemode = gamemodeSelection()
    print('Have fun! Type "stop" at any time to interrupt game')

    while nLives>0:
        if score == 0:
            rowWeights = initialWeights

        randomRow, rowWeights = getRandomRow(rowWeights)
        guess = guessWordTranslation(randomRow, gamemode)
        if guess == 'stop':
            print('Thanks for playing!')
            break

        newLives = checkWordTranslation(guess, randomRow, gamemode, nLives)
        rowWeights = adjustWeights(rowWeights, randomRow, newLives-nLives)

        nlives = newLives
        if nLives == 0:
            print('You are out of lives. Game over')


