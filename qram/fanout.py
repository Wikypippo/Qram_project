from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from utils.Oracles import Make_Oracle, Generate_bin_strings
import numpy as np

def fanout_qram(data_map):
    # Dimensione della memoria
    n = 2
    N = 2*n
    
     # Inizializzazione
    addr = QuantumRegister(n, 'addr')  # n qubit per indirizzare 8 celle
    switch = QuantumRegister(N-1,'switch') # N-1 switch per il routing
    memory = QuantumRegister(N, 'mem') # N qubit di memoria
    bus = QuantumRegister(1, 'bus_data')    # 1 qubit bus
    cr = ClassicalRegister(n + 1, 'c')
    
    qc = QuantumCircuit(addr, switch, memory, bus, cr)
    
    # Fase 1: Caricamento dati classici (preparazione memoria)
    for i, val in enumerate(data_map):
        if val == 1:
            qc.x(memory[i])  # Inizializza le celle a 1

    qc.h(addr)
    
    qc.barrier()
    
    # Fase 2: Fanout routing (indirizzo -> controllo gate paralleli)
    qc.cx(addr[0],switch[0])
    qc.cx(addr[1],switch[1])
    qc.cx(addr[1],switch[2])
    
    qc.barrier()    
        
    # Fase 3: Scrittura nel Bus e misurazione
    
    # path per l'indirizzo 00
    qc.x(switch[0])
    qc.x(switch[1])
    qc.mcx([switch[0],switch[1],memory[0]],bus)
    qc.x(switch[0])
    qc.x(switch[1])
    qc.barrier()
    
    # path per l'indirizzo 01
    qc.x(switch[0])
    qc.mcx([switch[0],switch[1],memory[1]],bus)
    qc.x(switch[0])
    qc.barrier()
    
    # path per l'indirizzo 10
    qc.x(switch[2])
    qc.mcx([switch[0],switch[2],memory[2]],bus)
    qc.x(switch[2])
    qc.barrier()
    
    # path per l'indirizzo 11
    qc.mcx([switch[0],switch[2],memory[3]],bus)
    qc.barrier()
    
    qc.measure(addr[:] + bus[:],cr[::-1])    # Misurazione
    
    return qc