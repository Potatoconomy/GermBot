# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 16:00:41 2020

@author: Patrick
"""

#Helpers#
import os
import xlrd
import csv
import pandas as pd

main = os.getcwd()

'''
pandas method is easier
'''
# def get_vocab_vocab(vocab):
#     '''
#     Gets user vocablist choice:  A1,A2,B1,B2,Custom
#     TODO: Make these json files
#     '''
    
#     vocab = []
#     fname = os.path.join(main,'VocabVocab','GermanCSV.csv')
#     xl_workbook = xlrd.open_workbook(fname)
    
#     # grab the first sheet by index 
#     # (sheets are zero-indexed)
#     xl_sheet = xl_workbook.sheet_by_index(0)
    
#     #iterating through rows and columns
#     num_cols = xl_sheet.ncols   # Number of columns
#     for row_idx in range(1, xl_sheet.nrows):    # Iterate through rows, 0th is title
#         col=0
#         row_info = {'English':None,'German':None,'Type':None,'Difficulty':None}
#         for col_idx in range(0, num_cols):  # Iterate through columns
#             cell_obj = xl_sheet.cell(row_idx, col_idx)  # Get cell object by row, col
#             if col_idx == 0:  row_info['German']     = cell_obj.value
#             if col_idx == 1:  row_info['English']    = cell_obj.value 
#             if col_idx == 2:  row_info['Type']       = cell_obj.value
#             if col_idx == 3:  row_info['Difficulty'] = cell_obj.value
        
#         #Fix entry syntax
#         row_info = {k.strip(): v.strip() for k, v in row_info.items()}
#         row_info = {k: v.split(',') for k, v in row_info.items()}
#         row_info = {k.strip(): [v[i].strip() for i in range(len(v))] for k, v in row_info.items()}
#         vocab.append(row_info)

#     return vocab



def get_vocab_vocab(vocab_diff, vocab_choice, n):
    fname = os.path.join(main,'VocabVocab','GermanCSV.csv')
    dfvocab = pd.read_csv(fname,encoding='latin-1') 
    for i in dfvocab.columns:
        dfvocab[i] = dfvocab[i].str.strip()
        
    diff = {'easy':   'E',
            'medium': 'M',
            'hard':   'H'}
    
    choice = {'verbs':      'V',
              'adjectives': 'A',
              'nouns':      'N',
              'custom':     'M'}   
    
    
    dfvocab = dfvocab.loc[dfvocab['Level']  == diff[vocab_diff.lower()]]
    dfvocab = dfvocab.loc[dfvocab['Type'] == choice[vocab_choice.lower()]]
    try:
        dfvocab = dfvocab.sample(n=n)
    except ValueError:
        dfvocab = dfvocab.sample(n=n, replace=True)
        
    return dfvocab



def get_synonym_vocab(vocab_diff, n):
    '''
    Gets user vocab from vocab_choices: Easy, Medium, Hard
    This is for the synonynm game
    '''
    fname = os.path.join(main,'VocabVocab','GermanCSV.csv')
    dfvocab = pd.read_csv(fname,encoding='latin-1') 
    for i in dfvocab.columns:
        dfvocab[i] = dfvocab[i].str.strip()
        
    diff = {'easy':   'E',
            'medium': 'M',
            'hard':   'H'}

    dfvocab = dfvocab.loc[dfvocab['Level']  == diff[vocab_diff.lower()]]

    try:
        dfvocab = dfvocab.sample(n=n)
    except ValueError:
        dfvocab = dfvocab.sample(n=n, replace=True)
        
    return dfvocab['German'].tolist()
    
    
# def get_synonym_vocab(choice):
    # '''
    # Gets user vocablist choice:  A1,A2,B1,B2,Custom
    # TODO: Make these csv files...
    # '''
    # if choice.upper()   == 'A1':     chosen = 'VocabA1.csv'
    # elif choice.upper() == 'A2':     chosen = 'VocabA2.csv'
    # elif choice.upper() == 'B1':     chosen = 'VocabB1.csv'
    # elif choice.upper() == 'B1':     chosen = 'VocabB2.csv'
    # elif choice.upper() == 'CUSTOM': chosen = 'VocabCustom.csv'
    # vocab = []

    # with open(os.path.join(main,'SynVocab',chosen)) as csvfile:
    #      vocabreader = csv.reader(csvfile, delimiter=',')
    #      for row in vocabreader:
    #         vocab.append(row[0])
    # return vocab

    