#!/usr/bin/python
# coding: utf-8

#
#  Takes and XML document and outputs 2 documents, one with list of tokens and one with list of 
#  another one with list of numbers representing each token for a user  
#

from xml.dom import minidom
from xml.dom.minidom import parseString
from xml.sax.saxutils import escape		
import xml.etree.cElementTree as et
import nltk
from nltk.tokenize import PunktWordTokenizer
from xlrd import open_workbook

movieCategory_list = []

def xmlToList(str):
        tree = et.fromstring(data)        
        #user_list = [(ch.tag, ch.text) for e in tree.findall('user') for ch in e.getchildren()]
        #print user_list
        user_list = []
        movie_list = []
        users = tree.findall('user')
        i=0
        for user in users:
           #print i
	   user_dict = {}
           user_attributes = [(ch.tag, ch.text)for ch in user.getchildren()]    
           fields= [att[0] for att in user_attributes]
           tokens= [att[1] for att in user_attributes] 

           tv_index = fields.index('tv')
           del(fields[tv_index])
           movie_index = fields.index('movies')
           tv= tokens[tv_index]
           del(tokens[tv_index])
           movie=tokens[movie_index]
           del(tokens[movie_index])

           movies = ''

           if tv != 'N/A':
              split_tv = tv.split(',')
              for singleTv in split_tv:
                #i=12 should be categorized
                '''
                if singleTv.lower()=='king of the hill':
                   print i
                '''
		# check if tv in list of TV shows
		if showIsCategorized(singleTv): 
		  movies = movies+ ',' + tv
           if movie != 'N/A':
              split_movie = movie.split(',')
              #if movie in list of shows
              for singleMovie in split_movie:
		if showIsCategorized(singleMovie): 
		  movies = movies +',' +  movie
           
           tokens = [token for token in tokens if token != 'N/A']
       
           if movies !='':
	     user_dict['tokens']=tokens 
	     user_dict['movies']= movies
             movie_list.append(movies)
	     user_list.append(user_dict)
           
           i+=1
        
        return user_list, movie_list

def showIsCategorized(tvOrMovie):
   categories = [movie['category'] for movie in movieCategory_list if movie['name'].lower() == tvOrMovie.lower()]
   return categories !=[]
     
def tokenizeList(list):
        tokenized_user = []
        tokenizer = PunktWordTokenizer()
        #for user in list:
              
'''
def categorizeMovie(movie_list, workBook):
       
        movie_categories = []   
        #load movies from excel spreadsheet
        for s in wb.sheets():
            for row in range(s.nrows):
	      movies = {} 
	      movies['name']=s.cell(row,0).value 
	      movies['category']=s.cell(row,1).value
	      movie_categories.append(movies)         
        
        for movies in movie_list:
                 split_movies =movies.split(',') 
                 for singleMovie in split_movies: 
		   categories = [movie['category'] for movie in movies if movie['name'].lower()== singleMovie.lower()] 
                   if categories is nil or categories =='':
                     categories = findWithImdb(singleMovie.lower())
                     single_user_categories.append(categories) 
                     user_categories.append(single_user_categories)
'''

def makeMovieListFromXls(file):
    wb = open_workbook('shows_all.xls') 
    movie_categories = []   
    #load movies from excel spreadsheet
    for s in wb.sheets():
        for row in range(s.nrows):
	      movies = {} 
	      movies['name']=s.cell(row,0).value.encode('ascii','ignore')
	      movies['category']=s.cell(row,1).value.encode('ascii','ignore')
	      movie_categories.append(movies)         
       
    return movie_categories

def findWithImdb(movie):
        return 'action,romance'

if __name__ == "__main__":

        #profiles = open("aggregate_data.xml", "r+")
        profiles  = open("friendData.xml", "r+")
        categories= open("categories.txt", "r+")
        #open excel spreadsheet of movies and movie categories
        xlsFile = 'shows_all.xls'
        
        #convert to string
        data = profiles.read()
        profiles.close()

        global movieCategory_list
        movieCategory_list=makeMovieListFromXls(xlsFile)

        user_list,movie_list = xmlToList(data)
        #categorizeMovie(movie_list, wb) 
        user_list_tokenized = tokenizeList(user_list)  
        
        
        

