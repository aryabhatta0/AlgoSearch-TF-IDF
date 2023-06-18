# To preprocess the Leetcode scraped data

import os
import sys
import pandas as pd
import json

folder_path = "Leetcode-Scrapped-Data/Qdata/"
index_path = "Leetcode-Scrapped-Data/index.txt"
Qlink_path = "Leetcode-Scrapped-Data/Qindex.txt"
new_folder_path = "Data/QData"
num_ques = 2405

# store contents of index.txt with line numbers as index
title = {}
with open(index_path, 'r') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        title[i+1] = line.strip()

# store links of questions
links = {}
with open(Qlink_path, 'r') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        links[i+1] = line.strip()

# Creating a df to be used in better serving the results on the web
df = pd.DataFrame(columns=['index', 'title', 'content', 'qlink', 'score'])

# Iterate over Qdata folder to read files
for index in range(1, num_ques+1):
    subfolder_path = os.path.join(folder_path, str(index))
    file_path = os.path.join(subfolder_path, str(index) + ".txt")
    
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
            remove = "Example"
            removeIndex = None
            for ind, line in enumerate(lines):
                if remove in line:
                    removeIndex = ind
                    break
                    
            newContent = lines[:removeIndex]
            # print(newContent)
            # print(removeIndex)
            # break
        
        # Create a new folder to add preprocessed content
        if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)
            
        new_file_path = os.path.join(new_folder_path, f"{index}.txt")
        with open(new_file_path, 'w', encoding='utf-8') as file:
            file.write(title[index] + "\n")
            file.writelines(newContent)
            
        # Add to dataframe
        df.loc[len(df)] = {'index': index, 'title': ' '.join(title[index].split()[1:]), 'content': ''.join(newContent), 'qlink': links[index], 'score': 0}
        # df = df.append({'index': index, 'title': ' '.join(title[index].split()[1:]), 'content': newContent, 'qlink': links[index]}, ignore_index=True)
    else:
        print(f"File {index} does not exist")

df = df.set_index('index')

# Save the DataFrame to a JSON file
# not using .pkl coz compatibility issues while deploying
df.to_json('Data/df.json')

print("Preprocessing done")