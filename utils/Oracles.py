from qiskit import QuantumRegister, QuantumCircuit
import itertools

def Make_Oracle(value):
    # Registri
    oracle = QuantumRegister(len(value), name="oracle")
    out = QuantumRegister(1, name="out")
    qc = QuantumCircuit(oracle, out)    # Circuito

    x_list = [] # Lista per ricordare le posizioni su cui riapplicare X
    for i, bit in enumerate(value):
        if bit == '0':
            qc.x(oracle[i])  # Applichiamo X solo sui bit a 0
            x_list.append(i)

    qc.mcx(list(range(len(value))), out[0])  # MCX controllato da oracle, target out

    for i in x_list:
        qc.x(oracle[i])  # Ripristiniamo gli X

    return qc

# Funzione per la conversione di numeri in stringhe binarie
def Generate_bin_strings(n):
    return [''.join(bits) for bits in itertools.product('01', repeat=n)]