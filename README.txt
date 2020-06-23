Hello!

GermBot is a basic Discord bot designed to help users practice their vocabulary.

This is more helpful for people learning the German language as vice-versa. This is due to the !German {WORD} command, which references duden.de for information on a specific word that may be used in chat. Maybe one day will a !English {WORD} command come into existence. 
###########################################################################################
As of now, there are 2 commands:
	
!German {WORD}

Prints information about a german word.  It is important to remember that Duden module is case-sensitive, i.e., 'tisch' will not return a result, but 'Tisch' will. Also, Duden does not typically include articles in their URLS.. 'Der Tisch' will not return a result.

!GermVocab {Verbs, Nouns, Adjectives, Custom} {Easy, Medium, Hard} {German, English}

Begins a vocab game with about 30 words being presented in either english or german.  Users have 3 lives.  It is recommended to use this only on not-so busy chat channels, as other users may become annoyed with all the message reminders if this is used in the main chat channel.  Our discord channel simply made a chat channel specifically for this bot. 

###########################################################################################

If you decide to run this from your own computer, which is probably the best idea, please download the repository, "https://github.com/Potatoconomy/GermBot", and run 'GermBot.py' with Python 3.7 from your command prompt that has a base directory of the GermBot folder.

For me, it looks like: 

(Anaconda Prompt):
(base) C:\Users\Patrick\Documents\PythonExercise\DiscordBot>python GermBot.py


Failing to have the correct base path on running will likely result in a file-not-found error, where os.getcwd() references the wrong base path to read in the vocabulary lists.

###########################################################################################
The following modules are required:
discord
numpy
duden
asyncio
dotenv
nest_asyncio
pandas
###########################################################################################
IMPORTANT:

To get the bot connected to your discord, please follow online instructions (https://realpython.com/how-to-make-a-discord-bot-python/)
on getting your Discord server Token and guild id. 

Replace my server Token and guild id in the file called .env (File can be opened with a notepad editor)
###########################################################################################



