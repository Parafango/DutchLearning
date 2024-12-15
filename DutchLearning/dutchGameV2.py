from DutchLearning.functions.betterFunctions import *

source = 'DuolingoWords.csv'

if __name__ == '__main__':

    theGame = DutchGame()
    theGame.ask_gamemode()
    theGame.initialize_weights(source)
    print('Have fun! Type "stop" at any time to interrupt game')

    while theGame.lives>0:
        theWord = Word(source, theGame.weights)
        theWord.get_random_row()
        theWord.get_word_type()
        theGame.check_translation(theWord)
        theGame.adjust_weights(theWord.weights)

        if theGame.stop:
            print(f'Final score: {theGame.score}\n')
            print('Thanks for playing!')
            break

        if theGame.lives == 0:
            print(f'You are out of lives.\nFinal score: {theGame.score}\n Game over')


