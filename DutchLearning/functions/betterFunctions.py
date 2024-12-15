import numpy as np
import pandas as pd
import random

class RowForWord:
    def __init__(self):
        self.enword = None
        self.nlword = None
        self.gender = None
        self.count = None

class WordType:

    def __init__(self):
        self.isAdjective = None
        self.isHetWord = None

class Word:
    def __init__(self, source, weights):
        self.source = source
        self.weights = weights
        self.row = RowForWord()
        self.index = None
        self.type = WordType()

    def get_random_row(self):
        df = pd.read_csv(self.source)
        nRows = df.shape[0]
        randomN = random.choices(np.arange(nRows), self.weights, k=1)[0]
        randomRow = df.iloc[randomN]
        self.row.enword = randomRow['english']
        self.row.nlword = randomRow['dutch']
        self.row.gender = randomRow['gender']
        self.row.count = randomRow['count']
        self.index = randomN


    def get_word_type(self):
        if pd.isna(self.row.count):
            self.type.isAdjective = 1
        else:
            self.type.isAdjective = 0

        if self.row.gender == 'n' and self.row.count == 's':
            self.type.isHetWord = 1
        else:
            self.type.isHetWord = 0

    def get_correct_guess_ed(self):
        if self.type.isAdjective:
            correctGuess = self.row.nlword

        elif self.type.isHetWord:
            correctGuess = 'het ' + self.row.nlword

        else:
            correctGuess = 'de ' + self.row.nlword

        return correctGuess
    def get_correct_guess_de(self):
        correctGuess = self.row.enword

        return correctGuess
    def get_correct_guess(self, gamemode):

        if gamemode=='ed':
            correctGuess = self.get_correct_guess_ed()
        else:
            correctGuess = self.get_correct_guess_de()

        return correctGuess

    def check_word_translation(self, gamemode):
        stopGame = 0
        if gamemode == 'de':
            prompt = '"' + self.row.nlword + '" in english is: '
        else:
            word = self.row.enword
            if self.type.isAdjective:
                word = word + ' (' + self.row.gender + ')'
            else:
                word = '"the ' + word + '"'

            prompt = word + ' in dutch is: '

        guess = input(prompt)
        correctGuess = self.get_correct_guess(gamemode)

        if guess == correctGuess:
            deltaLives = 0
            deltaScore = 1
            self.weights[self.index] -= 1
            print('Correct!')

        elif guess == 'stop':
            stopGame = 1
            deltaLives = 0
            deltaScore = 0

        else:
            deltaLives = -1
            deltaScore = 0
            self.weights[self.index] += 1
            print('Wrong, the correct translation was:"' + correctGuess + '"')

        return deltaLives, deltaScore, stopGame


class DutchGame:
    def __init__(self):
        self.gamemode = None
        self.score = 0
        self.lives = 5
        self.weights = None
        self.stop = None

    def ask_gamemode(self):
        self.gamemode = input('Choose gamemode: dutch to english (de) or english to dutch (ed)?')

    def initialize_weights(self, source):
        df = pd.read_csv(source)
        nRows = df.shape[0]
        self.weights = np.ones(nRows) * 4

    def adjust_weights(self, weights):
        self.weights = weights

    def check_translation(self, word: Word):
        deltaLives, deltaScore, stopGame = word.check_word_translation(self.gamemode)
        self.lives = self.lives + deltaLives
        self.score = self.score + deltaScore
        self.stop = stopGame


#Taking words info and translation from internet
#Step 1: Find a list of most commonly used dutch words and randomly take one of them
#Step 2: Use dutch dictionary to find out the translation and its type
#Step 2a: go to the word page in dutch dictionary
#Step 2b: extract info like different translations of the word (all of them should be correct) and type
#ie noun (neuter or gendered as well), adjective, adverb