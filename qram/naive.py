from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from utils.Oracles import Make_Oracle, Generate_bin_strings
import numpy as np

def naive_qram(data_map):
    # Calcola il numero di qubit necessari (arrotondando per eccesso)
    n = int(np.ceil(np.log2(len(data_map))))
    
    # Registri quantistici e classici
    addr = QuantumRegister(n, "addr")
    data_reg = QuantumRegister(1, 'data')  # 1 qubit per il dato
    cr = ClassicalRegister(n + 1, 'c')
    
    qc = QuantumCircuit(addr, data_reg, cr)
    
    # Sovrapposizione degli indirizzi
    qc.h(addr)
    qc.barrier()
    
    # Genera tutte le possibili stringhe binarie di lunghezza n
    bin_conversion = Generate_bin_strings(n)
    
    # Applicazione degli oracoli
    for i in range(len(data_map)):
        if data_map[i] == 1:
            # Assicurati che i non superi la lunghezza di bin_conversion
            if i < len(bin_conversion):
                oracle_circuit = Make_Oracle(bin_conversion[i]) 
                oracle_gate = oracle_circuit.to_gate(label=f"Oracle_{i}")   # Trasformazione dell'oracolo in gate
                qc.append(oracle_gate, range(n + 1))  # Applica a tutti i qubit
                qc.barrier()

    qc.measure(addr[:]+data_reg[:],cr[::-1])    # Misurazione
    
    return qc