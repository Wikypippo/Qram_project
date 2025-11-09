from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def bucket_brigade_qram(data_map):
    # Dimensione della memoria
    n = 2
    N = 2*n
    
     # Inizializzazione
    addr = QuantumRegister(n, 'addr')  # n qubit per indirizzare 8 celle
    switch = QuantumRegister(n*2,'switch') # (N-1) switch per il routing simulando i qutrit
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

    # Fase 2: Carving (indirizzo -> qutrit wait)
    ''' 
    I qutrit son simulati tramite 2 qubit nel seguente modo:
    00 : wait
    01 : left
    10 : right
    11 : non utilizzato
    ''' 

    qc.cx(addr[0],switch[0])
    
    qc.x(switch[0])
    qc.cx(switch[0],switch[1])
    qc.x(switch[0])

    qc.cx(addr[1],switch[2])

    qc.x(switch[2])
    qc.cx(switch[2],switch[3])
    qc.x(switch[2])
    

    # determinazione della deirezione
    qc.barrier()
    
    qc.x(switch[0])
    qc.x(switch[2])
    qc.mcx([switch[0],switch[2],memory[0]],bus[0])
    qc.x(switch[0])
    qc.x(switch[2])
    
    qc.x(switch[0])
    qc.mcx([switch[0],switch[2],memory[1]],bus[0])
    qc.x(switch[0])
    
    qc.x(switch[2])
    qc.mcx([switch[0],switch[2],memory[2]],bus[0])
    qc.x(switch[2])
    
    qc.mcx([switch[0],switch[2],memory[3]],bus[0])
    
    
    
    qc.barrier()
    
    # Fase 4: Reset
    qc.x(switch[2])
    qc.cx(switch[2],switch[3])
    qc.x(switch[2])
        
    qc.ccx(addr[1],switch[1],switch[2])    
    
    qc.x(switch[0])
    qc.cx(switch[0],switch[1])
    qc.x(switch[0])
    
    qc.cx(addr[0],switch[0])
    

    qc.barrier()
    qc.measure(addr[:] + bus[:],cr[::-1])    # Misurazione

    return qc