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
listOfCategories = []

def xmlToList(str):
        tree = et.fromstring(data)        
        #user_list = [(ch.tag, ch.text) for e in tree.findall('user') for ch in e.getchildren()]
        #print user_list
        user_list = []
        movie_list = []
        users = tree.findall('user')
        i=0
        for user in users:
           print i
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
           categories = ''

           if tv != 'N/A':
              split_tv = tv.split(',')
              for singleTv in split_tv:
                #i=12 should be categorized
                '''
                if singleTv.lower()=='king of the hill':
                   print i
                '''
		# check if tv in list of TV shows
		tv_categories = showIsCategorized(singleTv) 
                if tv_categories != []:
		    movies = movies+ ',' + tv
                    categories=categories.join(tv_categories)
                    #categories=categories.join(',')
                    categories=categories + ','

           if movie != 'N/A':
              split_movie = movie.split(',')
              #if movie in list of shows
              for singleMovie in split_movie:
		movie_categories = showIsCategorized(singleMovie) 
		if movie_categories != []: 
		    movies = movies + ',' +  movie
                    categories=categories.join(movie_categories)
                    categories = categories + ','
           
           tokens = [token for token in tokens if token != 'N/A']
       
           if movies !='':
	     user_dict['tokens']=tokens 
	     user_dict['movies']= movies
             user_dict['categories']=categories
             movie_list.append(movies)
	     user_list.append(user_dict)
                       
           i+=1
        
        return user_list, movie_list

def movieCategoryMatrix(user_list):

    users_movie_categories = []
    for user in user_list:
	singleUser_movie_categories = [0]*len(listOfCategories)     
        for category in user['categories'].split(','): 
            try:
	      index = listOfCategories.index(category) 
	      singleUser_movie_categories[index]=1
            except IndexError:
              # do nothing
              pass
            except ValueError:
              pass
        users_movie_categories.append(singleUser_movie_categories)

    return users_movie_categories

def showIsCategorized(tvOrMovie):
  categories = [movie['category'] for movie in movieCategory_list if similarity(movie['name'].lower(), tvOrMovie.lower()) >0.7]
  return categories 

def similarity(string1, string2):
  len1 = float(len(string1))
  len2 = float(len(string2))
  lensum = len1 + len2
  levdist = float(nltk.edit_distance(string1, string2))
  similarityMetric = ((lensum - levdist) / lensum)
  return similarityMetric 
     
def tokenizeList(list):
        tokenized_user = []
        tokenizer = PunktWordTokenizer()
        #for user in list:
              
def makeMovieListFromXls(file):
    wb = open_workbook('shows_all.xls') 
    movie_categories = []   
    #load movies from excel spreadsheet
    for s in wb.sheets():
        for row in range(s.nrows):
	      movies = {} 
	      name=s.cell(row,0).value.encode('ascii','ignore')
	      category=s.cell(row,1).value.encode('ascii','ignore')
	      movies['name']=name
	      movies['category']=category
	      movie_categories.append(movies)         
       
    return movie_categories

def findWithImdb(movie):
        return 'action,romance'

if __name__ == "__main__":

        #profiles = open("aggregate_data.xml", "r+")
        #profiles  = open("friendData.xml", "r+")
        profiles  = open("friendData_small.xml", "r+")

        #read list of movie categories & put them in a list
        categories_file= "categories.txt"
        global listOfCategories 

	for line in open( categories_file, "r+" ).readlines():
	  for value in line.split():
            listOfCategories.append(value) 

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
       
        #have a matrix of categories 1, if the user likes the category 
        category_matrix = movieCategoryMatrix(user_list)
        
        #Write movie category matrix to output file 
        category_matrix_file = open("category_matrix.txt", "w+")
        for item in category_matrix:  
            print >> category_matrix_file, item
        category_matrix_file.close()
