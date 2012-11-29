#!/usr/bin/python
# coding: utf-8
#
#  Takes and XML document and outputs 2 documents, one with list of tokens and one with list of 
#  another one with list of numbers representing each token for a user  

from xml.dom import minidom
from xml.dom.minidom import parseString
from xml.sax.saxutils import escape		
import xml.etree.cElementTree as et
import nltk
import nltk.data
#from nltk.tokenize import PunktWordTokenizer
from nltk.tokenize import regexp_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from xlrd import open_workbook
import time
import string
import bisect

#some globals
stemmer   = PorterStemmer()
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
english_stops = set(stopwords.words('english'))
movieCategory_list = []
movie_names = []
movieCategory_list_tokenized = []
listOfCategories = []

def xmlToList(xmlData):
        tree = et.fromstring(xmlData)        
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

           movies = [] 
           categories = [] 

           if tv != 'N/A':
              split_tv = tv.split(',')
              #tokenize show names (remove stop words, punctuation and stem words)
              #split_tv_tokenized = tokenizeList(split_tv)
              for singleTv in split_tv:
		# check if tv in list of TV shows
		#tv_categories = showIsCategorized(singleTv)
                singleTv = singleTv.encode('ascii', 'ignore').lstrip().lower().translate(None,string.punctuation)
		tv_categories = showIsCategorized(singleTv)
                if tv_categories != []:
                    movies.append(singleTv)
                    categories.extend(tv_categories)

           if movie != 'N/A':
              split_movie = movie.split(',')
              #split_movie_tokenized = tokenizeList(split_movie)
              #if movie in list of shows
              for singleMovie in split_movie:
		#movie_categories = showIsCategorized(singleMovie) 
                singleMovie = singleMovie.encode('ascii', 'ignore').lstrip().lower().translate(None,string.punctuation) 
		movie_categories = showIsCategorized(singleMovie)
		if movie_categories != []: 
                    movies.append(singleMovie)
                    categories.extend(movie_categories) 
  
           if movies !=[]:
	     tokens = [token for token in tokens if token != 'N/A']
	     tokenized_token = tokenizeList(tokens)
	     user_dict['tokens']= tokenized_token
	     user_dict['movies']= movies
             user_dict['categories']=categories
             movie_list.append(movies)
	     user_list.append(user_dict)
           else: 
             #remove xml entry because it is not useful 
             tree.remove(user)
           i+=1
        
        #write new cleaned XML to file
        cleanXMLFile = open("cleanProfiles.xml","w+")
        cleanXML=et.tostring(tree)
        cleanXMLFile.write(cleanXML)
        cleanXMLFile.close()
        
        return user_list, movie_list

def movieCategoryMatrix(user_list):
    users_movie_categories = []
    for user in user_list:
	singleUser_movie_categories =[0]*len(listOfCategories)     
        for category in user['categories']: 
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
  start = time.clock()
  #categories = [movie['category'] for movie in '''movieCategory_list'''movieCategory_list_tokenized if similarity(movie['name'].lower(), tvOrMovie.lower()) >0.7]
  # categories = [movie['category'] for movie in movieCategory_list_tokenized if movie['name'].lower()==tvOrMovie.lower()]
  #categories = [movie['category'] for movie in movieCategory_list if movie['name']==tvOrMovie]
  categories = []
  name_index = bisect.bisect(movie_names,tvOrMovie)
  if name_index != len(movie_names) and movie_names[name_index-1]==tvOrMovie: 
      categories = movieCategory_list[name_index-1]['category'] 
  
  elapsed = time.clock()-start
  #print elapsed
  return categories 

def similarity(string1, string2):
    len1 = float(len(string1))
    len2 = float(len(string2))
    lensum = len1 + len2
    levdist = float(nltk.edit_distance(string1, string2))
    similarityMetric = ((lensum - levdist) / lensum)
    return similarityMetric 
     
def tokenizeList(tokenList):
      #remove stop words, punctuation & stem words to create tokens out of phrases and names
      tokenized_list = []
      
      for item in tokenList:
         tokenized = regexp_tokenize(item.lower(), "[\w']+")
         filtered = [word for word in tokenized if word not in english_stops] 
         stemmed  = [stemmer.stem(word).encode('ascii', 'ignore') for word in filtered]   
         stemmed  = [word for word in stemmed if word !='']
	 tokenized_list.extend(stemmed)

      return tokenized_list
              
def makeMovieListFromXls(file):
    wb = open_workbook('shows_all.xls') 
    movie_categories = []   
    categories = []

    #load movies from excel spreadsheet
    for s in wb.sheets():
        for row in range(s.nrows):
	      movies = {} 
	      name=s.cell(row,0).value.encode('ascii','ignore')
	      category=s.cell(row,1).value.encode('ascii','ignore')
	      movies['name']=name.lstrip().lower().translate(None,string.punctuation) 
              category = [category.lstrip() for category in category.lower().split(',')]
	      movies['category']=category
              categories.extend(category)
	      movie_categories.append(movies)         

    categories = list(set(categories))
    categories = sorted(categories)
    
    #Sort list of movie categories by movie name
    movie_categories_sorted = sorted(movie_categories, key=lambda k: k['name']) 
    
    return movie_categories_sorted,categories

def generateTokenMatrix(tokenDict,listOfTokens):
   matrix =[0]*len(tokenDict)     
   for token in listOfTokens: 
      matrix[tokenDict[token]] += 1
   
   return matrix 

if __name__ == "__main__":

        #profiles = open("aggregate_data.xml", "r+")
        profiles  = open("friendData.xml", "r+")
        #profiles  = open("friendData_small.xml", "r+")

        #open excel spreadsheet of movies and movie categories
        xlsFile = 'shows_all.xls'

        #convert to string
        profile_data = profiles.read()
        profiles.close()

        global movieCategory_list
        movieCategory_list,categories=makeMovieListFromXls(xlsFile)

        #read list of movie categories & put them in a list
        categories_file= "categories.txt"
        global listOfCategories 

	for line in open( categories_file, "r+" ).readlines():
	  #for value in line.split():
	    listOfCategories.append(line.rstrip('\r\n'))

        listOfCategories.extend(categories)
        listOfCategories = list(set(listOfCategories))

	global movie_names
	movie_names = [movie['name'] for movie in movieCategory_list]
 
        global movieCategory_list_tokenized

        #tokenize movie names and categories
        for movie in movieCategory_list:
	   movieCategory_list_dict= {}
           movieCategory_list_dict['movie']   = tokenizeList(movie['name'].split()) 
           movieCategory_list_dict['category']= movie['category']#tokenizeList(movie['category'])
	   movieCategory_list_tokenized.append(movieCategory_list_dict) 

        user_list,movie_list = xmlToList(profile_data)
        tokenList = []
        tokenListNoRepetition = []

        #generate token list & print file of movie & tv show names for each user
        print "generating list and dictionary of tokens & printing movie lists per user"
	user_movie_file = open("user_movie.txt", "w+")
        for user in user_list:
            print >> user_movie_file, ",".join(["%s" % movie for movie in user['movies']]) 
            tokenList.extend(user['tokens'])

        tokenListNoRepetition = list(set(tokenList))
        tokenNumbers = range(len(tokenListNoRepetition))   
        tokenDict    = dict(zip(tokenListNoRepetition, tokenNumbers)) 

        categoryNumbers = range(len(listOfCategories))
        categoryDict    = dict(zip(listOfCategories, categoryNumbers))  

        #generate a matrix of users and tokens 
        print "generating token matrix"
        user_token_matrix = []
        category_matrix = []
        i = 0
        for user in user_list:
           print "matrix #" + str(i)
           user_token_matrix.append(generateTokenMatrix(tokenDict, user['tokens']))
           category_matrix.append(generateTokenMatrix(categoryDict, user['categories']))
           i+=1

        '''
        #write matrix of users and tokens into a file
        print "writing matrix"
        user_token_matrix_file = open("user_token_matrix.txt", "w+")
        i=0
        for item in user_token_matrix:  
            print "writing #" + i
            print >> user_token_matrix_file, item
            i+=1
        user_token_matrix_file.close()

        #Write movie category matrix to output file 
        "writing category matrix"
        category_matrix_file = open("category_matrix.txt", "w+")
        for item in category_matrix:  
            print >> category_matrix_file, item
        category_matrix_file.close()
        '''

        #print the dictionary of categories into a file
        print "printing category dictionary"
        category_dict_file = open("category_dictionary.txt", "w+")
        for key,value in sorted(categoryDict.iteritems(), key=lambda item: -item[1], reverse=True): 
        #for key,value in categoryDict.items():
            print >> category_dict_file, key,value
        category_dict_file.close()

        #print the dictionray of tokens into a file
        print "printing token dictionary"
        token_dict_file = open("token_dictionary.txt", "w+")
        for key,value in sorted(tokenDict.iteritems(), key=lambda item: -item[1], reverse=True):
        #for key,value in tokenDict.items():  
            print >> token_dict_file, key,value 
        token_dict_file.close()
     
        #have a matrix of categories 1, if the user likes the category 
        #category_matrix = movieCategoryMatrix(user_list)

	#Create a giant matrix as in HW2 with a list of tokens in the beginning
        #and then each entry having a matrix of user categories, and tokens followed by 
        #-1 to show end of user entry  
        token_matrix_file = open("giant_token_numbers_matrix.txt", "w+") 
        print "writing matrix"
        print >> token_matrix_file, len(user_list),len(listOfCategories), len(tokenListNoRepetition)         
        i=0 
        print >> token_matrix_file, " ".join(["%s" % token for token in tokenListNoRepetition]) 
        for whatCategory, whichTokens in zip(category_matrix, user_token_matrix): 
            print i
	    print >> token_matrix_file, " ".join(["%s" % category for category in whatCategory]), " ".join(["%s" % token for token in whichTokens]), "-1"
        token_matrix_file.close()


