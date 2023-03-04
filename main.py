# 1: INTITATE BASE-SETTINGS

# Import module
import pandas as pd
import numpy as np
import os
import treelib
from treelib import Tree
from pathlib import Path
import shutil
import glob
import openpyxl
import time
import datetime
import tkinter as tk
from tkinter import filedialog
root = tk.Tk()
root.withdraw()

# Assess script processing time --
# Grab Currrent Time Before Running the Code
start = time.time()

# Expand output view to display more columns
pd.set_option('display.max_columns',
              None)

# Get current directory
curr_dir = os.getcwd()
csv_path = r'*.csv'
csv_only = glob.glob(csv_path) # Call file path

# Get list of subdirectories
subdirs = [f.path for f in os.scandir(curr_dir) if f.is_dir()]

# Create the new folder for archiving directories from earlier runs
archive_dir = os.path.join(curr_dir, r'Archive')
# if it doesn't exist, only then it will be created
if not os.path.exists(archive_dir):
    os.makedirs(archive_dir)

# Intiate variables for some of our subdirectories, which includes subdirectories we will keep in
# the main path or move into our new Archive directory we created earlier
dir_to_move = ['CDEs', 'Converted_CSV', 'NCI_CL', 'Supp_Docs', 'Tree_Input', 'Trees']

# Set up archiving for directories created before this run 
seconds_in_day = 24 * 60 * 60 # Initiate variable
now = time.time()
before = now - seconds_in_day

# Define function for last modified datetime for the subdirectories
def last_mod_time(fn):
  return os.path.getmtime(fn)

# Iterate through subdirectories and move the ones that match the dir_to_move list
for subdir in subdirs:
    for dir_name in dir_to_move:
        if dir_name in subdir:
            if last_mod_time(subdir) > before:
                src = subdir
                dst = os.path.join(archive_dir, os.path.basename(subdir))
                shutil.move(src, dst)

# 2: CREATE THE DIRECTORIES FOR OUR FILES

# Initialize datetime variable
dir_dt = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

# Create the new folder for supporting documents, which will remain in the main directory
supp_dir = os.path.join(curr_dir, r'Supp_Docs_'+ dir_dt)
# if it doesn't exist, only then it will be created
if not os.path.exists(supp_dir):
    os.makedirs(supp_dir)

# Create the new folder for our CSV files, which will be parsed from the input
# file
csv_dir = os.path.join(curr_dir, r'Converted_CSV_' + dir_dt)
# If it doesn't exist, only then it will be created
if not os.path.exists(csv_dir):
    os.makedirs(csv_dir)

# Create a new folder for the CDE files
cde_dir = os.path.join(curr_dir, r'CDEs_' + dir_dt)
# If it doesn't exist, only then it will be created
if not os.path.exists(cde_dir):
    os.makedirs(cde_dir)

# Create a new folder for our tree output files
nci_dir = os.path.join(curr_dir, r'NCI_CL_' + dir_dt)
# If it doesn't exist, only then it will be created
if not os.path.exists(nci_dir):
    os.makedirs(nci_dir)

# Create a new folder for our tree input files --ingested by tree algorithm
# in the last step
input_dir = os.path.join(curr_dir, r'Tree_Input_' + dir_dt)
# If it doesn't exist, only then it will be created
if not os.path.exists(input_dir):
    os.makedirs(input_dir)

# Create a new folder for our tree output files --tree .txt files
tree_dir = os.path.join(curr_dir, r'Trees_' + dir_dt)
# If it doesn't exist, only then it will be created
if not os.path.exists(tree_dir):
    os.makedirs(tree_dir)

print('Open Excel file...\n')

# 3: PART I - PREPROCESSING:
# RESTRUCTURE FILES AND DIRECTORIES FOR PREPROCESSING - PART II

# Read our input file from GUI prompt --tkinter module is used here
user_file = filedialog.askopenfilename(
    filetypes=[("Excel files", ".xlsx .xls")])

# Read our file --user_file
uf_data = pd.read_excel(user_file, sheet_name=None)

# Iterate all the files and name each one after its sheet name and then save
# it as a CSV UTF-8 file.
for sheet_name, df in uf_data.items():
    df.to_csv(f'{sheet_name}.csv', encoding = 'utf-8', index = False)

# Intiate variables for some of our files, which includes files we will keep in
# the main path or move into our new folder we created earlier
files_to_stay = ['NCIt Concept Code and Lineage.csv', 'Count CDE Concept Lineage Done .csv',
                 'Count CDE Concept Lineage D (2).csv', 'CDE Domains.csv']
csv_path = r'*.csv'
csv_only = glob.glob(csv_path) # Call file path

# Move all files, except for files in 'files_to_stay' into the 'Converted_CSV'
# folder
for file in csv_only:
    if file not in files_to_stay:
        src = curr_dir + '/' + file  # Initiate variable for source directory
        dst = csv_dir + '/' + file  # Initiate variable for destination directory
        # Move file from source to destination based on filtered list
        shutil.move(src, dst)

# Call our CSV directory files
csv_file = glob.glob(os.path.join(csv_dir, '*.csv'))

# PART II - PREPROCESSING / STEP ONE:
# Write the CDE cols from the CSV files to a separate file, which we will later
# combine to the NCIt Concept Lineage cols

# Initiate list to store the CDE cols generated by for loop in the next step
cde_list = []

# For loop to read in each file from the csv_dir
for file in csv_file:
    # reads in the 'CDE Name' col
    cde_df = pd.read_csv(file, usecols=lambda x: x == 'CDE Name')

    # Drop rows with any empty cells
    cde_df.dropna(
        axis=0,
        how='all',
        subset=None,
        inplace=True
    )

    # Extract filename without extension
    file_name = Path(file).stem
    fp = os.path.join(cde_dir, file_name + '.csv')
    cde_df.to_csv(fp, index=False)
    cde_list.append(cde_df)  # Append the files back to the list

# For loop iterates over list of dataframes and creates file path where it's
# exported
for i, df in enumerate(cde_list):
    fp = os.path.join(cde_dir, file_name + '.csv')
    df.to_csv(fp, index=False)

# PART II - PREPROCESSING / STEP TWO: Write the NCI Concept Lineage cols from
# the CSV files to a separate file, which we will later combine to the CDE cols

# Initiate list to store the NCI Concept Lineage cols generated by for loop
# below
nci_list = []

# For loop to read in each file from the csv_dir
for file in os.listdir(csv_dir):
    if file.endswith('.csv'):
        file_path = os.path.join(csv_dir, file)
        # reads in the 'NCI Concept Lineage' col
        nci_df = pd.read_csv(file_path, usecols=['NCIt Concept Lineage'])

        # Drop rows with any empty cells
        nci_df.dropna(inplace=True)

        # Split column values into separate columns
        nci_df = nci_df['NCIt Concept Lineage'].str.split('>', expand=True)

        # Insert new columns after every other column until the end of the data frame:
        [nci_df.insert(i, 'ID', np.nan, allow_duplicates=True)
         for i in range(nci_df.shape[1], 0, -1)]

        # Copy data from every other column starting at index 0 to every other column starting at index 1 and retain only what is in the parenthesis
        for i in range(0, nci_df.shape[1]-1, 2):
            nci_df.iloc[:, i+1] = nci_df.iloc[:,
                                              i].str.extract(r"\((.*?)\)", expand=False)

        # Extract filename without extension and save to file
        file_name = os.path.splitext(file)[0]
        fp = os.path.join(nci_dir, file_name + '.csv')
        nci_df.to_csv(fp, index=False)
        nci_list.append(nci_df)  # appends the files back to the list

# Save each dataframe in the nci_list to a separate file
for i, df in enumerate(nci_list):
    file_name = os.path.splitext(os.listdir(csv_dir)[i])[0]
    fp = os.path.join(nci_dir, file_name + '.csv')
    df.to_csv(fp, index=False)

# Loop through each file in nci_dir folder
for nci_file in os.listdir(nci_dir):
    if nci_file.endswith('.csv'):
        nci_path = os.path.join(nci_dir, nci_file)  # get full path of nci_file

        # Create empty dataframe to store combined data
        combined_df = pd.DataFrame()

        # Loop through each file in cde_dir folder to find corresponding file to append
        for cde_file in os.listdir(cde_dir):
            if cde_file.endswith('.csv') and nci_file[:-4] in cde_file:
                # get full path of cde_file
                cde_path = os.path.join(cde_dir, cde_file)

                # Read both files and append to combined dataframe
                nci_df = pd.read_csv(nci_path)
                cde_df = pd.read_csv(cde_path)
                combined_df = pd.concat([nci_df, cde_df], axis=1)
        # Add a new column 'ID' auto-incrementing to the length of the data frame
                for i, row in enumerate(combined_df.iterrows()):
                    combined_df.at[row[0], 'id'] = i + 1

                # Relabel the nci concept/CDE column(s) as level + 1
                num_cols_lvl = len(combined_df.columns)
                for i in range(0, num_cols_lvl, 2):
                    combined_df = combined_df.rename(
                        columns={combined_df.columns[i]: f'Level{(i+2)//2}'})

              # Relabel the key column(s) as id + 1 --the key column is
              # important for the tree algorithm ahead
                num_cols_id = len(combined_df.columns)
                for i in range(1, num_cols_id, 2):
                    combined_df = combined_df.rename(
                        columns={combined_df.columns[i]: f'ID{(i+1)//2}'})

              # Move all data left by taking over np.nan cells which are then
              # moved to end --correctly represents hierarchy in CSV format
                combined_df = combined_df.apply(lambda row: pd.Series(sorted(row.tolist(
                ), key=lambda x: np.isnan(x) if isinstance(x, float) else 0), index=row.index), axis=1)

        # Output the combined dataframe to new CSV file in input_dir folder
        # with same name as nci_file
        input_file = os.path.join(input_dir, nci_file)
        combined_df.to_csv(input_file, index=False)

# PART III: INPUT FILE -> TREE METHODOLOGY
# # We will allow the tree alogrithm below to ingest our input file located
# in the Tree_Input folder or input_dir. This will output multiple trees into
# the Trees folder. By the end of the script we will have a combined version of
# the trees available in the Trees folder.

# Define tree function


def create_tree(df, items, parent, root=None, tree=None, i=0):
    # Create a tree from a dataframe
    if tree is None:
        tree = Tree()
        root = root if root else parent
        tree.create_node(root, parent)
    i = i + 1

    for parental, group_df in df.groupby(items[i - 1]):
        tree.create_node(parental[0], parental[1], parent=parent)
        if i <= len(items) - 1:
            create_tree(group_df, items, parental[1], tree=tree, i=i)
    return tree


# Loop through each file in the directory
for tree_file in os.listdir(input_dir):
    # Set the name of the tree to the filename
    tree_name = os.path.splitext(tree_file)[0]

    # Read in the dataframe from the input file
    file_path = os.path.join(input_dir, tree_file)
    df = pd.read_csv(file_path)

    # Create a list of the headers
    header_list = df.columns.tolist()

    # Put the list of headers into a nested list by pairs (concept, ID)
    my_list = [header_list[i:i + 2] for i in range(0, len(header_list), 2)]

    # Initiate items as my_list
    items = my_list

    # Initiate variable for length of dataframe
    df_len = len(df)

    # Initiate tree variable from final_file
    tree = create_tree(df.head(df_len), items, 'concepts', 'NCI Concept')
    # Check whether the file exists, otherwise create a .txt file
    output_path = os.path.join(tree_dir, tree_name + '.txt')
    if not os.path.exists(output_path):
        tree.save2file(output_path)
    print(tree_file + '...file processing complete')

  # Iterate directory to count number of tree files
count = 0 # Initiate counter
for path in os.listdir(tree_dir):
  # Check if current path is a file
  count +=1
print('\n' + 'Total tree file count:', count)

cp_updated = r'*.csv' # Initiate variable for updated path
co_updated = glob.glob(cp_updated) # Call file path

# Move all remaining files to the supp_dir --Supp_Docs
for file in co_updated:
        src = curr_dir + '/' + file  # Initiate variable for source directory
        dst = supp_dir + '/' + file  # Initiate variable for destination directory
        # Move file from source to destination
        shutil.move(src, dst)

# EOF (End of File) marker
# concatenate all tree output files into a single file
outfile = open(os.path.join(tree_dir, 'Aggr_Tree_Output.txt'), 'w')
for file_name in os.listdir(tree_dir):
    if file_name != 'Aggr_Tree_Output.txt':
        with open(os.path.join(tree_dir, file_name), "r") as infile:
            outfile.write(infile.read())
outfile.close()

# Grab Currrent Time After Running the Code
end = time.time()

#Subtract Start Time from The End Time
total_time = end - start
print('\n' + 'Total program execution time:' + '\n' + str(total_time))
