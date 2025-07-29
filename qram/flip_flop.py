from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import RYGate
import numpy as np

def flip_flop_qram(data_map):
    n = 2  # Numero di qubit di indirizzo
    
    addr = QuantumRegister(n, 'addr')
    register = QuantumRegister(1, 'reg')
    cr = ClassicalRegister(3, 'c')
    
    qc = QuantumCircuit(addr, register, cr)
    
    # Inizializzazione in sovrapposizione
    qc.h(addr)
    qc.barrier()
    
    # Calcolo fattore di normalizzazione
    norm = np.sqrt(sum(x**2 for x in data_map))
    
    for i in range(len(data_map)):
        if data_map[i] == 0:
            continue
        
        # Flip 
        binary_addr = bin(i)[2:].zfill(n)
        for j in range(n):
            if binary_addr[j] == '0':
                qc.x(addr[j])
        
        
        # Creazione della porta RY controllata
        theta = 2 * np.arcsin(data_map[i] / norm)
        ry_gate = RYGate(theta).control(num_ctrl_qubits=n)
        qc.append(ry_gate, list(addr) + [register[0]])  # Register
        
        # Flop 
        for j in range(n):
            if binary_addr[j] == '0':
                qc.x(addr[j])
        
        qc.barrier()
    
    qc.measure(addr[:] + register[:],cr[::-1])    # Misurazione
    return qc


def postselection(results):
    # Filtra solo i risultati con chiavi stringa valide
    valid_results = {k: v for k, v in results.items() if isinstance(k, str)}

    # Post-selezione: registro == 1 (ultimo bit == '1')
    postselected = {k[:-1]: v for k, v in valid_results.items() if k[-1] == '1'}
    
    # Conteggio
    totale = sum(valid_results.values())
    n_selezionati = sum(postselected.values())
    
    # Protezione contro divisione per zero
    if totale == 0:
        return 0.0
    
    frequenza = n_selezionati / totale
    return frequenza


def recostruction(results, normalizzazione, approssima=False, metodo='round'):
    # 1. Post-selezione: tieni solo i risultati con register = 1 (ultimo bit)
    postselected = {k[:-1]: v for k, v in results.items() if k[-1] == '1'}

    # 2. Calcolo delle probabilità relative
    totale = sum(postselected.values())
    dati_ricostruiti = {}

    for addr, count in postselected.items():
        prob = count / totale
        valore = np.sqrt(prob) * normalizzazione
        dati_ricostruiti[addr] = valore

    # 3. (Opzionale) Approssimazione
    if approssima:
        metodi = {
            'round': lambda x: int(round(x)),
            'floor': lambda x: int(np.floor(x)),
            'ceil':  lambda x: int(np.ceil(x))
        }
        if metodo not in metodi:
            raise ValueError("Metodo non valido. Usa 'round', 'floor' o 'ceil'.")
        dati_ricostruiti = {addr: metodi[metodo](val) for addr, val in dati_ricostruiti.items()}

    return dati_ricostruiti
