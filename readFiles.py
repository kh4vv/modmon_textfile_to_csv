import warnings
warnings.filterwarnings('ignore')

import os
import numpy as np
import pandas as pd

from util import get_data

file_path = "./files/"
file_names = os.listdir("./files")
print(file_names)

for f in file_names:
    path = file_path + f     
    df = get_data(path)