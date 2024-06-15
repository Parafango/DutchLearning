from baseFunctions import *


#select gamemode
#extract random word from list with appropriate column (+ extract information about noun/adjective)
#ask to guess, remember the article
#answer check
#repeat

if __name__ == '__main__':
    gamemode = gamemodeSelection()
    randomRow = getRandomRow()
    guess = guessWordTranslation(randomRow, gamemode)
    checkWordTranslation(guess, randomRow, gamemode)


