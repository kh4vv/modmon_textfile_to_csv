import numpy as np
import pandas as pd

def get_data(file_path):
    import time, pandas as pd 
    print('reading txt file ...')
    now = time.time()
    skiprows = find_header_row(file_path)
    df = pd.read_csv(file_path, sep='\t', skiprows=skiprows).reset_index()
    df.columns = [*df.columns[1:], None]
    print(f'reading txt file ... time spent = {int(time.time() - now)}s')
    return df
    
    
def find_header_row(file_path): 
    with open(file_path) as f:
        for i, line in enumerate(f.readlines()[:20], 0):
            if line.startswith('Count'):
                return i
        else:
            return 12
        