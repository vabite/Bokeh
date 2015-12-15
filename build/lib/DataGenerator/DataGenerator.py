# coding: utf-8

import numpy as np
import time
    
#attende delay secondi e poi restituisce float con distribuzione di probabilità gaussiana 
#a media mean e deviazione standard std argomento
def normal_number(mean, std, delay):
    time.sleep(delay)
    return np.random.normal(mean, std)
    
#attende delay secondi e poi restituisce una lista di lunghezza argomento di float con distribuzione 
#di probabilità gaussiana a media mean e deviazione standard std argomento
def normal_list(listlen, mean, std, delay):
    time.sleep(delay)
    normallist = []
    for i in range(listlen):
        normallist.append(np.random.normal(mean, std))
    return normallist
    
#attende delay secondi e poi restituisce una lista di liste con lunghezza della lista e delle sottoliste
#argomento di float con distribuzione di probabilità gaussiana a media mean e deviazione standard std argomento
def normal_matrix(listlen, sublistlen, mean, std, delay):
    time.sleep(delay)
    normalmatrix = []
    for i in range(listlen):
        normallist = []
        for j in range(sublistlen):
            normallist.append(np.random.normal(mean, std))
        normalmatrix.append(normallist)
    return normalmatrix
