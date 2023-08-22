import warnings
warnings.filterwarnings('ignore')

import os
import json
import numpy as np
import pandas as pd


class selectRegister:
    """
    _summary_
    
    Generate new csv datafile with selected columns (or registers) from the original text file (modmon)

    Args:
        df (pd.DataFrame): pandas dataframe from files
        string_number (list) : 12 string numbers from "01" to "12"
        module_number (list) : 12 module numbers from "01" to "12"
        Cutoff (int) : assign to 25000
        registerMap (dict) : full register map saved in Json file
    """
    def __init__(self, df) -> None:
        self.df = df

        # There are total 12 strings and 12 modules per one string.
        self.string_number = ["01","02","03","04","05","06","07","08","09","10","11","12"]
        self.module_number = ["01","02","03","04","05","06","07","08","09","10","11","12"]
        
        # Threshold
        self.Cutoff = 25000
        
        # Registers map
        with open('registerMap.json', 'r') as fp:
            self.registerMap = json.load(fp)

    def genInit(self):
        df = self.df
        df = df.rename(columns=self.registerMap)
        
        df['datetime'] = df['date'] + " " + df['time']
        df['datetime'] = pd.to_datetime(df['datetime'], format='%m/%d/%Y %H:%M:%S',errors='coerce')
        df['Time'] = (df['datetime']-df['datetime'].iloc[0]).dt.total_seconds()
        
        # Cutoff Threshold
        Cutoff = self.Cutoff
        df_c = df[Cutoff:]
        
        return df_c
    
    def firstPieceDF(self):
        df_c = self.genInit()
        
        # Initial dataframe
        
        wantedColumn = ['datetime', 'Time', "ChaSt", "State", "EBCBt", "MxCP", "MxDP", "EBSen1"]
        existColumn = []
        for c in wantedColumn:
            if c in df_c.columns:
                existColumn.append(c)

        df_new = df_c[existColumn]
        
        return df_new
    
    def stringPieceDF(self):
        df_c = self.genInit()
        string_number = self.string_number
        module_number = self.module_number
        
        # string value
        df_current = pd.concat([df_c[f'Current_{i}']*(-1/1000) for i in string_number], axis=1)
        df_voltage = pd.concat([df_c[f'Voltage_{i}']*(1/10) for i in string_number], axis=1)
        
        # fill NaN to 0
        df_current = df_current.fillna(0)
        df_voltage = df_voltage.fillna(0)
        
        df_power = pd.concat([df_c[f'Current_{i}']*(-1/1000)*df_c[f'Voltage_{i}']*(1/10) for i in string_number], keys = [f'Power_{i}' for i in string_number], axis=1)
    
        # Energy
        time = df_c['Time'].array

        df_energy = pd.DataFrame()
        for s in string_number:
            power = df_power[f'Power_{s}'].array
            energy_cha = [0]
            energy_dis = [0]
            
            for i in range(len(df_c)-1):
                if power[i] >= 0 and power[i+1] >= 0:
                    energy_cha.append(0.5*abs(power[i+1]-power[i])*(time[i+1]-time[i])+energy_cha[-1])
                    energy_dis.append(energy_dis[-1])
                elif power[i] < 0 and power[i+1] < 0:
                    energy_dis.append(0.5*abs(power[i+1]-power[i])*(time[i+1]-time[i])+energy_dis[-1])
                    energy_cha.append(energy_cha[-1])            
                else:
                    energy_dis.append(energy_dis[-1])
                    energy_cha.append(energy_cha[-1])
            df_energy[f'ChargeEnergy_{s}']    = energy_cha
            df_energy[f'DischargeEnergy_{s}'] = energy_dis
    
        df_string = pd.concat([df_current, df_voltage, df_power, df_energy], axis =1)
        return df_string
    
    def modulePieceDF(self):
        df_c = self.genInit()
        string_number = self.string_number
        module_number = self.module_number

        # module value
        sm_matrix = []
        for i in range(len(string_number)):
            for j in range(len(module_number)):
                sm_matrix.append(string_number[i] + module_number[j])
                
        df_voltage_module = pd.concat([df_c[f"Voltage_{i}"]*(1/100) for i in sm_matrix], axis = 1)
        df_voltage_module = df_voltage_module.fillna(0)
        df_temp_module    = pd.concat([df_c[f"Temp_{i}"]*(1/10) for i in sm_matrix], axis = 1)
        df_soc_module     = pd.concat([df_c[f"SoC_{i}"] for i in sm_matrix], axis = 1)
        
        # Power Module
        st = "01"
        df_power_module = pd.concat([df_c[f'Current_{st}']*(-1/1000)*df_c[f'Voltage_{st}{m}']*(1/10) for m in module_number], keys = [f'Power_{st}{m}' for m in module_number], axis=1)
        df_power_module = df_power_module.fillna(0)
        for s in string_number[1:]:
            df_temp = pd.concat([df_c[f'Current_{s}']*(-1/1000)*df_c[f'Voltage_{s}{m}']*(1/10) for m in module_number], keys = [f'Power_{s}{m}' for m in module_number], axis=1)
            df_temp = df_temp.fillna(0)
            df_power_module = df_power_module.join(df_temp)
            
        # Energy Module
        time = df_c['Time'].array
        df_energy_module = pd.DataFrame()
        for s in string_number:
            for m in module_number:
                power = df_power_module[f'Power_{s}{m}'].array
                energy_cha = [0]
                energy_dis = [0]
            
                for i in range(len(df_c)-1):
                    if power[i] >= 0 and power[i+1] >= 0:
                        energy_cha.append(0.5*abs(power[i+1]-power[i])*(time[i+1]-time[i])+energy_cha[-1])
                        energy_dis.append(energy_dis[-1])
                    elif power[i] < 0 and power[i+1] < 0:
                        energy_dis.append(0.5*abs(power[i+1]-power[i])*(time[i+1]-time[i])+energy_dis[-1])
                        energy_cha.append(energy_cha[-1])            
                    else:
                        energy_dis.append(energy_dis[-1])
                        energy_cha.append(energy_cha[-1])
                df_energy_module[f'ChargeEnergy_{s}{m}']    = energy_cha
                df_energy_module[f'DischargeEnergy_{s}{m}'] = energy_dis
                
        df_module = pd.concat([df_voltage_module, df_temp_module, df_soc_module, df_power_module, df_energy_module], axis=1)
        return df_module
    
    def finalDF(self):
        df_first  = self.firstPieceDF()
        df_string = self.stringPieceDF()
        df_module = self.modulePieceDF()
        
        df_final = pd.concat([df_first, df_string, df_module], axis=1)
        #df_final = df_final.dropna()
        
        return df_final
    
    def saveToCsv(self, path):
        Cutoff = self.Cutoff
        
        df_final = self.finalDF()
        date = df_final["datetime"].dt.strftime('%Y_%m-%d').dropna()
        date = date.array
        
        filename = path+"/DataRecord_"+date[0]+"_to_"+date[-1]+".csv"
        print(filename+ " is saved in path "+str(os.getcwd())+"\outputs")
        df_final.to_csv(filename, index=False)
        
        