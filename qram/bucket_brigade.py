from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def bucket_brigade_qram(data_map):
    n = len(next(iter(data_map)))  # numero di bit per l'indirizzo
    assert all(len(k) == n for k in data_map), "Tutti gli indirizzi devono avere la stessa lunghezza"
    
    addr = QuantumRegister(n, "addr")
    qutrits = [QuantumRegister(2, f"qutrit_{i}") for i in range(n)]  # 1 qutrit per livello
    out = QuantumRegister(1, "out")
    c = ClassicalRegister(1, "c")

    qc = QuantumCircuit(addr, *qutrits, out, c)

    # 1. Superposizione sull'indirizzo
    for q in addr:
        qc.h(q)

    return qc