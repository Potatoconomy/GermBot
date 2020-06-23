# -*- coding: utf-8 -*-
"""
Created on Wed Jun  3 12:20:34 2020

@author: Patrick
"""
#Make sure current working directory is the folder before DiscordBot
import os
cwd = os.getcwd()
# Dependencies
import numpy as np
# import random
import duden
import discord
from dotenv import load_dotenv
import nest_asyncio
import asyncio
nest_asyncio.apply()
# from discord.ext import commands
load_dotenv()
from discord.ext.commands import Bot
# import csv
from datetime import datetime
#Other Discord Bot files
# import synonyms
import vocabulary
from helpers import get_vocab_vocab #get_synonym_vocab

'''
TODO:
    Short:  
        Make proper vocab lists.
        Create a vocab english-german game (also german english)
        Turn this into a bot class and create a main.py file  --- ehhh
        Get quit to work during vocab choice questions
        Fix the !help command
            
    Long Term Goal:  
        Data tracking by user?
        Multiple instances?
        "Next word" prints as well when at end of game. -- easy fix
    
    I need to figure out how data_storage like that works for other users of discord.
    
    TODO: 
        Connection issues:
            discord.ext.commands.errors.CommandInvokeError: Command raised an exception: ClientOSError: [WinError 10054] An existing connection was forcibly closed by the remote host
            
        Entering a message resets the wait_for('message',timeout=9,check=check) timer. 
        
        Fix the help message displays!!! *--Most important--*
    

'''
#%%
user_synonym_instance = False
user_vocab_instance = False
player = 0


def fix_meaning_overview(duden_object_def):
    '''
    Duden module does not include examples.
    This creates def_ex which is tuple of (definition,example).
    Note that most words have multiple definitions.  
    1 example is included for each definition
    
    TODO: 
        Some words have no examples.
        Some words have only 1 def no examples. -- this function doesn't account for this.
            Resolved in German() func. via hard coding
    '''
    new_list = []
    def_ex = []
    for major in duden_object_def[0]:
        if type(major) != list: major = [major] #some are str, some are list
        for minor in major:  #definitions are grouped by relative closeness
            new_list.append(minor)
        
    for c,(maj_,min_) in enumerate(zip(new_list,duden_object_def[1])):
        def_ex.append((maj_,min_[0]))
        
    return def_ex


TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD')
BOT_PREFIX = {"!","?"}

bot = Bot(command_prefix=BOT_PREFIX,
          case_insensitive = True)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    
    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
    
    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')
    
    
@bot.event
async def on_message(message):
    '''
    Read messages and process commands.
    '''
    global player
    
    if message.author == bot.user:
        return
    
    await bot.process_commands(message)

   


@bot.command(help = '```Provides information about a German word (case sensitive).\n\tUSAGE: !German [german_word]```')
async def German(ctx, word: str):
    '''
    prints information on discord about a specific german word.
    TODO: implement duden's "search" module for words with no "get" URL.
    '''
    
    duden_obj = duden.get(word)

    if duden_obj == None:
        duden_obj = duden.search(word)
        if len(duden_obj) == 0: 
            await ctx.send(f'```{word} is not in Duden, ya goof.\n\tPlease remember that duden is case sensitive.```')
            return 
        else:
            duden_obj = duden_obj[0]
        
    def_ex = fix_meaning_overview(duden_obj.meaning_overview)

    #prioritize more common definitions/exs
    #do not want to overwhelm users and show entire duden page
    prob = np.arange(len(def_ex),0,-1)
    probz = [i/sum(prob) for i in prob]
    try:
        def_,ex_ = def_ex[np.random.choice(np.arange(0,len(def_ex)), p=probz)]   
    except ValueError:
        await ctx.send(f'```Incomplete Duden entry.\n\tBedeutung: {duden_obj.meaning_overview[0]}```')
        print(def_ex)
        return
    await ctx.send(f'```Word: {word}\n\tWortart: {duden_obj.part_of_speech}\n\tBedeutung: {def_}\n\tBeispiel: {ex_}```')





@bot.command(help='```Creates a vocab game! \n\tUSAGE: !GermVocab\n\t[Verbs, Nouns, Adjectives, Custom]\n\t[Easy, Medium, Hard]\n\t[German, English]```')
async def GermVocab(ctx, vocab_choice='$$$!!!$$$', vocab_diff='$$$!!!$$$', vocab_direction='$$$!!!$$$'):
    '''
    Create an instance of vocabulary game.
    Interacts with vocabulary.py to ask users the translations of words
    Words come from my custom csv files.  May make them json files one day.
    
    TODO:
        Create Instance with user
        ensure only one user at a time
        prompt user for english to german or vice versa
        load vocab dicts
        present user with vocab
        get answer from user
        right/wrong
        scoring/lives
    '''

    global user_vocab_instance
    n=30  #How many words are in the game.  Must also be altered in helpers.py if changed
    
    if ctx.author == bot.user:
        return
    
    
    async def runthrough_vocab(ctx):
        '''
        Primary runthrough of the game.
        '''
        alive = True
        
        while alive:    
            await user_game.present_vocab()
            alive = await user_game.get_answer()
            alive = await user_game.live_check()
        
        return False
    
    
    '''
    GAME INITIATION AND OPTION SETTINGS
    
    There are better ways to deal with the *args but discord processes them differently than Python,
    which is why the *args are defined in a weird way. 
    '''
    
    if user_vocab_instance == False:
        user_vocab_instance = True
        
        await ctx.send(f'```Initiating a game with: {ctx.author}.\nPlease provide the correct translation\nType "Quit" to quit.```')
        print(f'vocabchoice: {vocab_choice},{type(vocab_choice)}')
        
        #######################################################################
        ############################Get vocab choice###########################
        #######################################################################
        
        if vocab_choice != '$$$!!!$$$':
            if vocab_choice.lower() in ['verbs','nouns','adjectives','custom']:
                pass
            else: vocab_choice = '$$$!!!$$$'
            
        if vocab_choice == '$$$!!!$$$':
            await ctx.send(f'```Please choose a vocab type: Verbs, Nouns, Adjectives, Custom```')
            valid_message = False
            
            while valid_message == False:
                try:
                    
                    def check(message):
                        if message.author == ctx.author:
                            if message.content.lower() in ['verbs','nouns','adjectives','custom']:
                                return True
                            
                    message = await bot.wait_for('message', timeout=60.0, check=check)
                    # vocab = get_vocab_vocab(message.content.lower())
                    vocab_choice = message.content.lower()
                    valid_message = True
                    
                except asyncio.TimeoutError:
                    await ctx.send('👎')
                    user_synonym_instance = False
                    return False
                
        #######################################################################
        #########################Get vocab list################################
        #######################################################################
                
        if vocab_diff != '$$$!!!$$$':
            if vocab_diff.lower() in ['easy','medium','hard']:
               pass         # vocab = get_vocab_vocab(vocab_diff.lower())
        else: vocab_diff = '$$$!!!$$$'

        if vocab_diff == '$$$!!!$$$':
            await ctx.send(f'```Please choose a vocab level: Easy, Medium, Hard```')
            valid_message = False
            
            while valid_message == False:
                try:
                    def check(message):
                        if message.author == ctx.author:
                            if message.content.lower() in ['easy','medium','hard']:
                                return True
                    message = await bot.wait_for('message', timeout=60.0, check=check)
                    # vocab = get_vocab_vocab()
                    vocab_diff = message.content.lower()
                    valid_message = True
                except asyncio.TimeoutError:
                    await ctx.send('👎')
                    user_synonym_instance = False
                    return False
        
        #######################################################################
        ##########################Get vocab_direction list#####################
        #######################################################################
                
        if vocab_direction != '$$$!!!$$$':
            if vocab_direction.lower() in ['german','english']:
                pass
            
            else: 
                vocab_direction = '$$$!!!$$$'
            
        if vocab_direction == '$$$!!!$$$':
            await ctx.send(f'```Please choose the language to be presented:\n\tGerman\n\tEnglish```')
            valid_message = False
            
            while valid_message == False:
                try:
                    
                    def check(message):
                        if message.author == ctx.author:
                            if message.content.lower() in ['german','english']:
                                return True
                            
                    message = await bot.wait_for('message', timeout=60.0, check=check)
                    vocab_direction = message.content.lower()
                    valid_message = True
                    
                except asyncio.TimeoutError:
                    await ctx.send('👎')
                    user_synonym_instance = False
                    return False
        
        vocab = get_vocab_vocab(vocab_diff, vocab_choice, n)
        #######################################################################
        #######################################################################
        #######################################################################

        '''
        CREATE INSTANCE
        '''
                
        
        user_game = vocabulary.Vocabulary(bot, ctx,
                                          {'author':          ctx.author,
                                           'start_time':      datetime.now(),
                                           'vocab':           vocab,
                                           'vocab_direction': vocab_direction,
                                           'vocab_choice':    vocab_choice,
                                           'n':               n})
        
        while user_vocab_instance == True:
            user_vocab_instance = await runthrough_vocab(ctx)
    
        #######################################################################
        #######################################################################
        #######################################################################

bot.run(TOKEN)

'''
Synonyms Game is a little dumb.  I thought that the synonyms provided by Duden would be good, but they aren't.
Luckily, I wrote Synonyms first, so most of the poor coding practices with discord's API are found in the Synonyms module, as opposed to the VocabGame/German.
This can kinda run, but the user playing of the program is honestly not conducive to learning, so it is being dropped.
'''
# @bot.command(help = '```Context clue game. Provides 3 clues to an unknown word.\n\tUSAGE: !GermSynonyms\n\t[Easy, Medium, Hard]```')
# async def GermSynonyms(ctx, vocab_choice='$$$!!!$$$'):
#     '''
#     Create instance of Synoyms game.
#     Ensures only 1 class can run at a time.
    
#     TODO:
#         Ask what vocab to use
#         Ensure 1 instantiation actually works
#         Ensure game responds only to player
#         Create game
#     '''
#     n=12
#     global user_synonym_instance
#     if ctx.author == bot.user:
#         return
    
#     """ Initiate Game """
#     '''
#     #Only allow one instance at a time.  
#     TODO: 
#         Ensure only one instance at a time.
#         Make sure function at end turns user_synonym_instance false again for repeated play
#     '''
#     async def runthrough_synonym(ctx):
#         syns = user_game.present_synonyms()
#         print(1)
#         right_answer = user_game.duden_obj.name
#         print(2)
#         wrong_objects = user_game.synonym_check()
#         print(user_game.duden_obj,'\n',syns)
#         await ctx.send(f'```Context Clues: \n\t{syns[0]}\n\t{syns[1]}\n\t{syns[2]}\n```')
#         print(f'wrong_objects: {wrong_objects}')
#         answer_list = [wrong_objects[0].name,
#                        wrong_objects[1].name,
#                        wrong_objects[2].name,
#                        right_answer]
        
#         np.random.shuffle(answer_list)
#         letter_answer = answer_list.index(right_answer)
#         ans_dict = {'a':0,'b':1,'c':2,'d':3}
#         print(f'letter_answer: {letter_answer}')
#         print(f'\n\nanswer_list: {answer_list}')
#         await ctx.send(f'```\tA.{answer_list[0]}\n\tB.{answer_list[1]}\n\tC.{answer_list[2]}\n\tD.{answer_list[3]}\n```')
        
#         ####
#         def check(message):
#             return message.author == ctx.author
        
#         valid_message = False
#         while valid_message == False:
#             try:
#                 message = await bot.wait_for('message', timeout=60.0, check=check)
#                 if message.content.lower() == 'quit':
#                     await ctx.send('```Bye Bye```')   #Would be nice to show score here. Worth the time investment though?
#                     return False
#                 if message.content.lower() not in ans_dict.keys():
#                     message.content = ''
#                     pass
#                 else: valid_message = True
#             except asyncio.TimeoutError:
#                 await ctx.send('```👎\nTimeout (60 seconds)```')
#                 return False
        
#         def meaning_reducer(dobj):
#             '''
#             Chooses 1st meaning in duden_obj.meaning_overview[0]
#             '''

#             def recursive_meaning(meaning):
#                 while isinstance(meaning, list):
#                     meaning = recursive_meaning(meaning[0])
#                 return meaning
            
#             def recursive_example(example):
#                 while isinstance(example, list):
#                     example = recursive_example(example[0])
#                 return example
            
#             meaning = recursive_meaning(dobj.meaning_overview[0])
#             if len(meaning) >= 1000: meaning = meaning[0:100] + '...'  ###2000 word limit for Discord
            
#             example = recursive_example(dobj.meaning_overview[1])
#             if len(example) >= 1000: example = example[0:100] + '...'  ###2000 word limit for Discord
#             return meaning,example

            
#         if ans_dict[message.content.lower()] == letter_answer: 
#             user_synonym_instance,score,dobj = user_game.answer_handling(correct=True)
#             definition, example = meaning_reducer(dobj)
#             # print(definition)
#             await ctx.send(f'```Correct!\n{dobj.name}: {definition}\n\nBeispiel: {example}\n\nNext word:```')  
        
#         else:
#             user_synonym_instance,score,dobj = user_game.answer_handling(correct=False)
#             definition, example = meaning_reducer(dobj)
#             # print(definition)
#             await ctx.send(f'```Wrong!\nCorrect Answer: {dobj.name}: {definition}\n\nBeispiel: {example}\n\nNext word:```')
            
#         if user_synonym_instance == False:
#             await ctx.send(f'```final score: {score}/{len(vocab)}```')
#             return False
#         return user_synonym_instance    
        
#     if user_synonym_instance == False:
#         user_synonym_instance = True
#         await ctx.send(f'```Initiating a game with: {ctx.author}.\nChoose a letter answer [a,b,c,d]\nType "Quit" to quit.\nChoose the word that is most related to the context clues.\n\nCurrently talking to Duden.```')
#         print(f'vocabchoice: {vocab_choice},{type(vocab_choice)}')
        
#         ###
#         #Get vocab list
#         '''
#         Originally used a better default vocab_choice arg, but discord processes these weirdly.
#         So I am resorting to this crude method, as a superior method is not worth the time investment.
#         '''
        
#         async def get_vocab_choice(): 
#             await ctx.send(f'```Please choose a vocab level: Easy, Medium, Hard```')
#             valid_message = False
            
#             while valid_message == False:
#                 try:
#                     def check(message):
#                         if message.author == ctx.author:
#                             if message.content.lower() in ['easy','medium','hard']:
#                                 return True
#                     message = await bot.wait_for('message', timeout=60.0, check=check)
#                     vocab = get_synonym_vocab(message.content.lower(), n)
#                     valid_message = True
#                 except asyncio.TimeoutError:
#                     await ctx.send('👎')
#                     user_synonym_instance = False
                
#                 return vocab
                
#         if vocab_choice != '$$$!!!$$$':
            
#             if vocab_choice.lower() in ['easy','medium','hard']:
#                 vocab = get_synonym_vocab(vocab_choice.lower(), n)
                
#             else: 
#                 vocab_choice = '$$$!!!$$$'
#                 vocab = await get_vocab_choice()
            
#         elif vocab_choice == '$$$!!!$$$':
#             vocab = await get_vocab_choice()

#         user_game = synonyms.Synonyms({'author':    ctx.author,
#                                        'start_time':datetime.now(),
#                                        'vocab':     vocab,
#                                        'size':      n        #Size cant be larger than population of vocab!
#                                         })
        
#         while user_synonym_instance == True:
#             user_synonym_instance = await runthrough_synonym(ctx)

    




