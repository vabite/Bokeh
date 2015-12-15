# coding: utf-8

import numpy as np
from random import shuffle

    
#ritorna una lista data dalla somma membro a membro di due liste, anche annidate, purche 
#di ugual shape e grandezza delle dimensioni
def sum_list(list1, list2):
    sumarray = np.array(list1) + np.array(list2)
    return sumarray.tolist()
    
#data una lista di liste argomento, ritorna una lista di liste in cui gli elementi di ciascuna lista 
#sono dati dalla somma cumulata degli elementi della corrispettiva lista della lista di liste argomento
#NB: il metodo non funziona se la lista passata non è annidata (rango = 1)
def cumsum_matrix(tocumsum_matrix):
    cumsum_array = np.cumsum(np.array(tocumsum_matrix), axis = 1)
    return cumsum_array.tolist()
    
#data una lista di liste argomento, ritorna una lista di liste in cui gli elementi di ciascuna lista 
#sono dati dagli elementi della lista passata cui è stato aggiunto un elemento 0.0 all'indice 0
#NB: il metodo non funziona se la lista passata non è annidata (rango = 1)
def zeroappend_matrix(tozeroappend_matrix):
    zeroappended_matrix = []
    for i in range(len(tozeroappend_matrix)):
        zeroappended_matrix += [[0.0]]
        zeroappended_matrix[i] += tozeroappend_matrix[i]
    return zeroappended_matrix
    
#ritorna -1 se il numero argomento è negativo, 1 se positivo, 0 se il numero argomento è zero.
def sign(n):
    if n > 0: return 1
    elif n < 0: return -1
    else: return 0
    
#se direction True o non specificato, allora elimina il primo elemento di una lista argomento,
#shiftando indietro di un indice i restanti elementi, e vi appende (in fondo) l'elemento argomento.
#se direction False, allora elimina l'ultimo elemento di una lista argomento,
#shiftando avanti di un indice i restanti elementi, e vi inserisce l'elemento argomento all'indice 0.
#Ritorna la lista così modificata
def shift_insert(alist, new_elem, shift_sx = True):
    if shift_sx:
        alist.pop(0)
        alist.append(new_elem)
    else: 
        alist.pop()
        alist.insert(0, new_elem)
    return alist 
    
#ritorna una lista ottenuta mischiando gli elementi di una lista argomento
def shuffle_return(alist):
    shuffle(alist)
    return alist

#data una sequenza argomento, definisce un generatore che restituisce gli elementi della sequenza
#dall'ultimo al primo
def yield_from_last(sequence):
    for index in range(len(sequence) - 1, -1, -1):
        yield sequence[index]