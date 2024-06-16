from baseFunctions import *


#select gamemode
#extract random word from list with appropriate column (+ extract information about noun/adjective)
#ask to guess, remember the article
#answer check
#repeat

if __name__ == '__main__':
    nLives = 5

    gamemode = gamemodeSelection()
    print('Have fun! Type "stop" at any time to interrupt game')

    while nLives>0:
        randomRow = getRandomRow()
        guess = guessWordTranslation(randomRow, gamemode)
        if guess == 'stop':
            print('Thanks for playing!')
            break

        nLives = checkWordTranslation(guess, randomRow, gamemode, nLives)


