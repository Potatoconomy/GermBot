# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 11:21:56 2020

@author: Patrick
"""

'''
Vocab Game:
    :)
    Prompts user with a german or english word.
    User must input corresponding english or german response.
    
    Outline:
    
    User creates instance from GermBot.py
    User selects vocab choice from GermBot.py
        
        csv stored vocab:   col1: german words.  [toll, super, ausgezeichnet]
                            col2: english words. [great, super, awesome, fantastic, good]
                    
    If german to english is selected:
        User is shown: 'toll, super, ausgezeichnet'
        User input must be in: ['great', 'super', 'awesome', 'fantastic', 'good']
    If english to german is selected:
        User is shown: 'great, super, awesome, fantastic, good'
        User input must be in: ['toll', 'super', 'ausgezeichnet']
        
    if correct: yield next word, 
                score += 1
                word_count += 1
                
    if wrong:   lives -=1 
                show user remaining lives
                show correct answer. 
                    (maybe show example sentence from duden?!?) 
                yield next word
                word_count += 1

    When vocab list is ended or gameover (lives = 0) or word_count == 50:
        save user score using userID to a JSON file
        show user score.
        if possible: Print User's highest score for the corresponding vocab level.
            UserID1234567890 = {a1: 0/50,a2: 0/50, b1: 0/50, b2: 50}
        show user missed words and translations. (Maybe also example sentences using Duden)
        end game instance
        
    TODO: Plurality of correct answer(s)??
            Add spaces after comma separations in germancsv file
            Currently n = 30, hardcoded in.  Could easily be switched to user arg if desired.
                Locations:  helpers.py--> dfvocab.sample()
                            vocabulary.py--> lifecheck
        
        Rework out my CSV vocab sheet... German words could use more synonyms
    
'''
import os
cwd = os.getcwd()
# Dependencies
import numpy as np
import random
import duden
import discord
from discord.ext import commands
import nest_asyncio
import asyncio
nest_asyncio.apply()



class Vocabulary():
    
    def __init__(self, bot, ctx, info):
        self.bot = bot
        self.ctx = ctx
        self.score = 0
        self.lives = 3
        self.info = info
        self.author = info['author']
        self.vocab = info['vocab']
        self.vocab_direction = info['vocab_direction'].lower()
        print(f'self.vocab_direction:{self.vocab_direction}')
        self.vocab_choice = info['vocab_choice'].upper()
        self.i = 0
        self.wrong = []
        self.n = info['n']
        print(self.vocab)
        
    async def present_instructions(self):
        '''
        User Instructions
        '''
        if self.vocab_direction == 'english':
            await self.ctx.send('```Hello. Enter the correct translation for the shown word./nEnter "1" to move to next word.```')
        else: await self.ctx.send('```Hallo. Bitte geben sie die richtige Übersetzung ein./nTragen sie "1" ein um zu fortsetzen.```')
        
        
        
    async def present_vocab(self):
        '''
        Present vocab.... TODO: test out new helpers get_vocab() function
        '''        
        print('present_vocab')
        if self.vocab_direction =='german':
            await self.ctx.send(f'```{self.vocab["German"].iloc[self.i]}```')
        else:
            await self.ctx.send(f'```{self.vocab["English"].iloc[self.i]}```')
            
    
    async def get_answer(self):
        '''
        Get answer from user
        '''
        def check(message):
            ''' Only respond to ctx author '''
            return message.author == self.ctx.author
        
        def answer_fixer(answer):
            ''' Answers are bundled together as one str value.
            I change this to a list format for reduced errors in answer matching'''   
            answers = answer.split(sep=',')
            for c,i in enumerate(answers): 
                i = i.strip()
                if i.startswith('to '): 
                    i = i.replace('to ','')
                    i = i.strip()
                answers[c] = i
            print(answers)
            return answers
            
        
        if self.vocab_direction == 'german':
            correct_answer = answer_fixer(self.vocab['English'].iloc[self.i])
            correct_answer = [i.lower() for i in correct_answer]

            valid_message = False
            while valid_message == False:
                try:
                    message = await self.bot.wait_for('message', timeout=9.0, check=check)
                    if message.content.lower().startswith('to '): message.content = message.content.lower()[3:]
                    if message.content.lower().startswith('the '): message.content = message.content.lower()[4:]
                    print(message.content)
                    
                    if message.content.lower() == 'quit':
                        await self.ctx.send(f'```Spiel geendet! Ihr Endergebnis ist: {self.score}/{self.n}.```')
                        if len(self.wrong) == 3: await self.send(f'```Missed Answers:\n\t{self.wrong[0]/n/tself.wrong[1]/n/tself.wrong[2]}```')
                        if len(self.wrong) == 2: await self.ctx.send(f'```Missed Answers:\n\t{self.wrong[0]}\n\t{self.wrong[1]}```')
                        if len(self.wrong) == 1: await self.ctx.send(f'```Missed Answers:\n\t{self.wrong[0]}```')
                        if len(self.wrong) == 0: await self.ctx.send(f'```Nothing Missed! Sehr gut!```')
                        await self.ctx.send('```Bye Bye```')   #Would be nice to show score here. Worth the time investment though?
                        return False
                    
                    elif message.content == '1':
                        await self.ctx.send(f'The correct answers are:\n\t{correct_answer}')
                        self.wrong.append((self.vocab['English'].iloc[self.i],self.vocab['German'].iloc[self.i]))
                        self.lives -= 1
                        self.i += 1
                        valid_message = True
                    
                    if message.content.lower() not in correct_answer:  #Faster ways to do this, but it doesn't really matter here as the lists are short
                        message.content = ''
                        continue
                    
                    else:   #Correct answer!
                        self.score += 1
                        self.i += 1
                        valid_message = True
                        message = ''
                        
                except asyncio.TimeoutError:
                    await self.ctx.send(f'```Die richitige Antworten sind:\n\t{correct_answer}```')
                    self.wrong.append((self.vocab['German'].iloc[self.i],self.vocab['English'].iloc[self.i]))
                    self.lives -= 1
                    self.i += 1
                    valid_message = True
            
            ###Need to add the english direction as well!
        elif self.vocab_direction == 'english': 
            correct_answer = answer_fixer(self.vocab['German'].iloc[self.i])
            correct_answer = [i.lower() for i in correct_answer]
            valid_message = False
            print(f'correct: {correct_answer}')
            while valid_message == False:
                
                try:
                    message = await self.bot.wait_for('message', timeout=9.0, check=check)
                    
                    # if message.content.lower().startswith('to '): message.content = message.content.lower()[3:]
                    # if message.content.lower().startswith('the '): message.content = message.content.lower()[4:]

                    print(message.content.lower())
                    
                    if message.content.lower() == 'quit':
                        await self.ctx.send(f'```Game Over! Your final score is: {self.score}/{self.n}.```')
                        if len(self.wrong) == 3: await self.send(f'```Missed Answers:\n\t{self.wrong[0]/n/tself.wrong[1]/n/tself.wrong[2]}```')
                        if len(self.wrong) == 2: await self.ctx.send(f'```Missed Answers:\n\t{self.wrong[0]}\n\t{self.wrong[1]}```')
                        if len(self.wrong) == 1: await self.ctx.send(f'```Missed Answers:\n\t{self.wrong[0]}```')
                        if len(self.wrong) == 0: await self.ctx.send(f'```Nothing Missed! Sehr gut!```')
                        await ctx.send('```Bye Bye```')   
                        return False
                    
                    elif message.content == '1':
                        await self.ctx.send(f'```The correct answers are:\n\t{correct_answer}```')
                        self.wrong.append((self.vocab['English'].iloc[self.i],self.vocab['German'].iloc[self.i]))
                        self.lives -= 1
                        self.i += 1
                        valid_message = True
                        
                    if message.content.lower() not in correct_answer:
                        message.content = ''
                        continue
                    
                    else:   #Correct answer!
                        self.score += 1
                        self.i += 1
                        message = ''
                        valid_message = True
                        
                except asyncio.TimeoutError:
                    await self.ctx.send(f'```The correct answers are:\n\t{correct_answer}```')
                    self.wrong.append((self.vocab['English'].iloc[self.i],self.vocab['German'].iloc[self.i]))
                    self.lives -= 1
                    self.i += 1
                    valid_message = True
                
        return True            
                
    
    
    async def live_check(self):
        print('live_check')
        
        if self.lives == 0 or self.i == 30:  #30 is the # of words in a game.  Defined in helpers.py, get_vocab_vocab(), dfvocab.sample(n=50)
            
            if self.vocab_direction == 'german':
                await self.ctx.send(f'```Spiel geendet! Ihr Endergebnis ist: {self.score}/{self.n}.```')
            
            elif self.vocab_direction == 'english':
                await self.ctx.send(f'```Game Over! Your final score is: {self.score}/{self.n}.```')
            
            if len(self.wrong) == 3: await self.ctx.send(f'```Missed Answers:\n\t{self.wrong[0]}\n\t{self.wrong[1]}\n\t{self.wrong[2]}```')
            if len(self.wrong) == 2: await self.ctx.send(f'```Missed Answers:\n\t{self.wrong[0]}\n\t{self.wrong[1]}```')
            if len(self.wrong) == 1: await self.ctx.send(f'```Missed Answers:\n\t{self.wrong[0]}```')
            if len(self.wrong) == 0: await self.ctx.send(f'```Nothing Missed! Sehr gut!```')
            
            return False
        else: return True
            
        





























