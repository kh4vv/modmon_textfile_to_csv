import warnings
warnings.filterwarnings('ignore')

import os
import numpy as np
import pandas as pd

from util import get_data
from selectRegister import selectRegister

file_path = "./files/"
file_names = os.listdir("./files")
print(file_names)

for f in file_names:
    path = file_path + f     
    df = get_data(path)
    
    genFile = selectRegister(df)
    #df = genFile.finalDF()
    genFile.saveToCsv()
    print("file "+ path + " is done.")
    