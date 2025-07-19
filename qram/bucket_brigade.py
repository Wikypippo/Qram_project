from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def bucket_brigade_qram(data_map):
    # Dimensione della memoria
    n = 2
    N = 2*n
    
     # Inizializzazione
    addr = QuantumRegister(n, 'addr')  # n qubit per indirizzare 8 celle
    switch = QuantumRegister((N-1)*2,'switch') # (N-1) switch per il routing simulando i qutrit
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

    qc.measure(switch[1],cr[0])

    # determinazione della deirezione
    with qc.if_test((cr[0], 1)):  # Controlla se lo stato è left
        qc.cx(addr[1],switch[2])
        qc.x(switch[2])
        qc.cx(switch[2],switch[3])
        qc.x(switch[2])
        qc.measure(switch[3],cr[1])
        with qc.if_test((cr[1], 1)):
            qc.mcx([switch[1],switch[3],memory[0]],bus) # Fase 3: copia nel bus
        with qc.if_test((cr[1], 0)):
            qc.mcx([switch[1],switch[2],memory[1]],bus) # Fase 3: copia nel bus
            
    
    with qc.if_test((cr[0], 0)):  # Controlla se lo stato è right
        qc.cx(addr[1],switch[4])
        qc.x(switch[4])
        qc.cx(switch[4],switch[5])
        qc.x(switch[4])
        qc.measure(switch[5],cr[1])
        with qc.if_test((cr[1], 1)):
            qc.mcx([switch[0],switch[5],memory[2]],bus) # Fase 3: copia nel bus
        with qc.if_test((cr[1], 0)):
            qc.mcx([switch[0],switch[4],memory[3]],bus) # Fase 3: copia nel bus
    
    qc.barrier()
    
    # Fase 4: Reset
    
    with qc.if_test((cr[0],1)):
        qc.x(switch[1])
        with qc.if_test((cr[1],1)):
            qc.x(switch[3])
        with qc.if_test((cr[1],0)):
            qc.x(switch[2])
    
    with qc.if_test((cr[0],0)):
        qc.x(switch[0])
        with qc.if_test((cr[1],1)):
            qc.x(switch[5])
        with qc.if_test((cr[1],0)):
            qc.x(switch[4])
        

    qc.barrier()
    qc.measure(addr[:] + bus[:],cr[::-1])    # Misurazione

    return qc