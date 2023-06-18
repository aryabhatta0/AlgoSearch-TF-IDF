# To prepare vocab, idf-values, inverted index for the search engine

import os
import json

data_path = "Data/QData"
num_ques = 2405

# split line into words, remove punctuation, convert to lowercase, remove not alphanumeric characters
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

# Create a vocab of all words
# TODO: Can we do anything about non-meaningful words?
vocab = {}
documents = []    # list of list of processed words for each document
for index in range(1, num_ques+1):
    file_path = os.path.join(data_path, str(index) + ".txt")
    
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        tokens = []  # all words in the document
        for line in lines:
            words = process_line(line)
            tokens += words # merge 2 lists
            
        documents.append(tokens) 
        tokens = set(tokens)     # removing duplicates will help in calculating idf
        for token in tokens:
            if(token == ""):
                continue
            if token not in vocab:
                vocab[token] = 1
            else:
                vocab[token] += 1   
    else:
        print(f"File {index} does not exist")
     
# reverse sort vocab by idf
vocab = {k: v for k, v in sorted(vocab.items(), key=lambda item: item[1], reverse=True)}
        
print("Vocab created")
print("Size of vocab:", len(vocab))
print("Size of documents:", len(documents))
# print(vocab)

# Save the vocab in a json file
with open("Data/vocab.json", 'w', encoding='utf-8') as file:
    file.write(json.dumps(vocab))

# Save the documents in a json file
with open("Data/documents.json", 'w', encoding='utf-8') as file:
    file.write(json.dumps(documents))

# Creare inverted_index to store the docs vocab words are present in 
inverted_index = {}   # key: word, value: list of doc ids
for ind, doc in enumerate(documents):
    ind+=1     # 0-based index
    words = set(doc)
    for word in words:
            if word not in inverted_index:
                inverted_index[word] = [ind]
            else:
                inverted_index[word].append(ind)
            # break
                
print("Inverted index created")
print("Size of inverted index:", len(inverted_index))
# print(inverted_index)
        
# save inverted index in a json file
with open("Data/inverted_index.json", 'w', encoding='utf-8') as file:
    file.write(json.dumps(inverted_index))
