#1 Processing the query
import math
import os
import pandas as pd
import json

# vocab = {}
# documents = []
# inverted_index = {}
# df = DataFrame()
    
# load json files
with open('Data/vocab.json', 'r') as file:
    vocab = json.load(file)
with open('Data/inverted_index.json', 'r') as file:
    inverted_index = json.load(file)
with open('Data/documents.json', 'r') as file:
    documents = json.load(file)
df = pd.read_json('Data/df.json')
df.rename_axis('index', inplace=True)

print("Size of loaded vocab:", len(vocab))
print("Size of loaded inverted index:", len(inverted_index))
print("Size of loaded documents:", len(documents))

# to split, remove punctuation, lowercase, remove not alphanumeric chars
def process_line(line):
    words = line.split()
    processed_words = []

    for word in words:
        word = word.strip('.,;:?!')
        word = word.lower()
        word = ''.join(ch for ch in word if ch.isalnum())
        word = word.strip('0123456789')

        if word != "":
            processed_words.append(word)

    return processed_words

'''
TERMS:
    tf(term, doc)
    idf(term)
    tf-idf(term, doc) = tf(term, doc) * idf(term)
    score(doc) = sum(tf-idf(term, doc) for term in query)
'''

# returns a dict containing tf scores of each document for given term
# one which isn't here has 0 tf score
# TODO: Any new term will have 0 tf, so why not preprocess tf for all vocab as well?
def get_tf_dict(term):
    tf_dict = {}
    # using inverted index to only count over docs that actually contain the term
    if term in inverted_index.keys():
        for doc in inverted_index[term]:
            # print("doc", doc)
            tf_dict[doc] = documents[doc-1].count(term)
    
    # TODO: normalize or not? _/
    for doc in tf_dict.keys():
        tf_dict[doc] /= float(len(documents[doc-1]))
    
    return tf_dict

# returns the idf score of given term: (overall uniqueness of term)
def get_idf(term):
    # TODO: idf when term not in vocab? => log(N/(df+1)) _/
    if term not in vocab.keys():
        return 1
    idf = float(vocab[term])  # Doubt: if term not in vocab? _/
    return math.log(len(documents) / idf)
    
# returns scores (sorted) of each documents for given query
# only those docs with non-zero score
def getScore(query):
    terms = process_line(query)
    # print(terms)
    
    tf_idf_dict = {}   # tf-idf score for each document by simple average over all terms
    for term in terms:
        tf_dict = get_tf_dict(term)
        idf = get_idf(term)
        for ind, doc in enumerate(documents):
            ind+=1   # 0-based index
            tf_idf = 0
            if ind in tf_dict.keys():
                tf_idf = tf_dict[ind] * idf
                
            if ind not in tf_idf_dict.keys():
                if(tf_idf != 0):    # only add if non-zero score
                    tf_idf_dict[ind] = tf_idf
            else:
                tf_idf_dict[ind] += tf_idf
                
    for ind in tf_idf_dict.keys():
        tf_idf_dict[ind] /= float(len(documents))
        
    # reverse sort tf_idf_dict by value
    tf_idf_dict = dict(sorted(tf_idf_dict.items(), key=lambda item: item[1], reverse=True))
    
    return tf_idf_dict
            
def print_potential_documents(score_dict, num_docs):
    print(f"Printing top {num_docs} result...")
    with open('Data/index.txt', 'r') as file:
        title = file.readlines()

    for i, doc_ind in enumerate(score_dict.keys()):
        # display no result if no document has score > 0
        if(i == 0 and score_dict[doc_ind] == 0):
            print("No result found!")
            break
                  
        if i == num_docs or score_dict[doc_ind] == 0:
            break
        print(f"#{i+1} {doc_ind}\t{title[doc_ind-1].strip()}\t: Score={round(score_dict[doc_ind], 3)}")

# create a subset of df from top num_docs doc_ind of score_dict as rows
def getDataFrame(score_dict, num_docs):
    if(num_docs > len(score_dict)): 
        doc_ind = list(score_dict.keys())
    else:
        doc_ind = list(score_dict.keys())[:num_docs]
        
    # fill score column
    for ind in doc_ind:
        df.loc[ind, 'score'] = score_dict[ind]
        
    return df.loc[doc_ind]
    

# query = input("Enter your query: ")
# score_dict = getScore(query)   # dict {doc_ind: score} for each doc sorted by score
# print_potential_documents(score_dict, 10)
# print(getDataFrame(score_dict, 5))


#2 Serving on web
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def home():
    print("Request method:", request.method)
    if request.method == 'POST':
        query = request.form['query']
        num_docs = int(request.form['num_docs'])
        
        score_dict = getScore(query)
        if(num_docs==-1 or num_docs>len(score_dict)):    # -1 means all
            num_docs = len(score_dict)
        print(f"Query: {query}\nNumber of documents: {num_docs}")
        
        return render_template('index.html', query=query, num_docs=num_docs, results=getDataFrame(score_dict, num_docs))
    
    # Handling the GET request
    return render_template('index.html')
            
if(__name__ == '__main__'):
    app.run()
    # app.run(debug=True)