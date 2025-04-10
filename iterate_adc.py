import h5py
import numpy as np
import matplotlib.pyplot as plt
import os
from tqdm import tqdm
import math as m
import scipy.stats as stats
import scipy.special as sc
from scipy.optimize import curve_fit
import subprocess

import pandas as pd
import sys, os

sys.path.append("/home/nulab4/Documents/MULE_WIP/")

from packs.proc import proc as proc


def make_config_ADC(initial_config, new_config, ADC):
    '''
    Create a new config with an ADC value of X
    
    initial_config -> path to config + config
    new_config -> path to new config + config
    ADC        -> new ADC values
    '''
    with open(initial_config) as file:
        data = file.readlines()
        
    for i, line in enumerate(data):
        if line[:17] == 'TRIGGER_THRESHOLD':
            data[i] = f'TRIGGER_THRESHOLD      {ADC}\n'
    
    with open(new_config, 'w') as file:
        file.writelines( data )

def make_config_MULE(initial_config, new_config, output_path):
    '''
    same as above, but just adjusts the config to output a file with the appropriate ADC tag
    '''
    
    with open(initial_config) as file:
        data = file.readlines()
        
    for i, line in enumerate(data):
        if line[:9] == 'save_path':
            data[i] = f'save_path         = \'{output_path}\''
    
    with open(new_config, 'w') as file:
        file.writelines( data )
    
    
def define_wavedump_runner(time, config_path):
    return f'(sleep 3s && echo "W" && sleep 3s && echo "s" && sleep {time}s && echo "s" && sleep 3s && echo "q") | wavedump {config_path}'

def main():
    
    # list of ADC values to iterate through
    adc_vals = [39, 91, 143, 195, 403, 611, 819]
    
    # How long do you want them to run for?
    seconds = 50
    
    # where to get the base config
    config_path = '/home/nulab4/Documents/MULE_WIP/packs/configs/threshold_checker/'
    initial_config = 'WDconf_1730B_00ADC.txt'
    initial_config_MULE = 'process_WD2_3channel.conf'
    
    # this directory describes the run type, make sure it exists!
    final_dir = 'alphas_vac'
    output_directory = '/home/nulab4/Documents/MULE_WIP/packs/acq/John/' + final_dir
    
    
    
    for adc in adc_vals:
        # create the WD config
        new_config = f'WDconf_1730B_{adc}ADC.txt'
        new_config_MULE = f'process_WD2_3channel_{adc}ADC.conf'
        make_config_ADC(config_path + initial_config, config_path + new_config, adc)
        
        # run wavedump here
        subprocess.call([define_wavedump_runner(seconds, f'{config_path}{new_config}')], shell = True)
        
        # make MULE config, altering the output
        make_config_MULE(config_path + initial_config_MULE, config_path + new_config_MULE, output_directory + f'/{final_dir}_{adc}.h5')
        
        # process the output
        proc.proc(f'{config_path}/{new_config_MULE}')


main()