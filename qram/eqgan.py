import numpy as np
from utils import QiskitUtils as qkt
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.quantum_info import Statevector, state_fidelity
from scipy.optimize import minimize

def generate_state(theta_g):
    qc = QuantumCircuit(2)
    qc.ry(theta_g[0], 0)
    qc.ry(theta_g[1], 1)
    qc.cx(0, 1)
    qc.ry(theta_g[2], 0)
    qc.ry(theta_g[3], 1)
    return qc

def discriminator_circuit(theta_d, rho_circ, sigma_circ):
    n = rho_circ.num_qubits
    qc = QuantumCircuit(1 + 2*n, 1)
    anc = 0
    rho_qubits = list(range(1, 1+n))
    sigma_qubits = list(range(1+n, 1+2*n))

    # Inizializzazione
    qc.h(anc)
    
    # Carica stati
    qc.compose(rho_circ, qubits=rho_qubits, inplace=True)
    qc.compose(sigma_circ, qubits=sigma_qubits, inplace=True)

    for j in range(n):
        qc.cx(rho_qubits[j], sigma_qubits[j])

    # SWAP test
    for j in range(n):
        qc.cswap(anc, rho_qubits[j], sigma_qubits[j])

    # Trasformazioni parametrizzate minimali
    qc.ry(theta_d[0], rho_qubits[0])
    qc.ry(theta_d[1], sigma_qubits[0])
    
    # Misurazione
    qc.h(anc)
    qc.measure(anc, 0)
    
    return qc

def evaluate_discriminator(theta_d, theta_g, target, shots=2048):
    gen_circ = generate_state(theta_g)
    target_circ = target

    qc = discriminator_circuit(theta_d, gen_circ, target_circ)
    
    # Simulazione
    counts = qkt.run(qc,shots)
    
    p0 = counts.get('0', 0) / shots
    d_val = 2 * abs(p0 - 0.5)
    
    return p0, d_val

def cost_discriminator(theta_d, theta_g, target):
    theta_d = np.asarray(theta_d)
    theta_g = np.asarray(theta_g)
    _, d_val = evaluate_discriminator(theta_d, theta_g, target)
    return -d_val  # Loss principale

def cost_generator(theta_g, theta_d, target):
    theta_g = np.asarray(theta_g)
    theta_d = np.asarray(theta_d)
    p0, _ = evaluate_discriminator(theta_d, theta_g, target)
    
    # Loss diretta - massimizza la probabilità che D sbagli
    gen_loss = -np.log(p0 + 1e-8)
    
    return gen_loss