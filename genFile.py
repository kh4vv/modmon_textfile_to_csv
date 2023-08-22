import warnings
warnings.filterwarnings('ignore')

import os
import sys 

import numpy as np
import pandas as pd

from util import get_data
from selectRegister import selectRegister

args = sys.argv[1:]

if len(args) == 0:
    file_path = "./"
else:
    file_path = args[0]

file_names = os.listdir(file_path)
modmon_text_files =[]

for f in file_names:
    if "txt" in f and "modbus" in f:
        modmon_text_files.append(f)
        
print("List of modbusfiles: ", modmon_text_files)
if len(modmon_text_files) == 0:
    print("There is no file in this directory. Re-run the file with correct path.")
    sys.exit()
    
print(" ")
print(" ")
print("Path to save files: ")
path = input()
isExist = os.path.exists(path)
print("Directory Exist: ", isExist)
print(" ")
print(" ")

if not isExist:
    os.makedirs(path)
    print("The new directory is created")

for f in file_names:
    file_path = file_path + f
    print("Current File : ", file_path)
    df = get_data(file_path)
    
    genFile = selectRegister(df)
    #df = genFile.finalDF()
    genFile.saveToCsv(path)
    print("file "+ path + " is done.")
    