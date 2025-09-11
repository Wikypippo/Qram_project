import numpy as np
from utils import QiskitUtils as qkt
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import ParameterVector
from qiskit.quantum_info import Statevector, state_fidelity
from scipy.optimize import minimize
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, thermal_relaxation_error, pauli_error

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

    # SWAP test
    for j in range(n):
        qc.cswap(anc, rho_qubits[j], sigma_qubits[j])
        
    for j in range(n):
        qc.cx(rho_qubits[j], sigma_qubits[j])

    qc.barrier()

    # Trasformazioni parametrizzate minimali
    qc.ry(theta_d[0], rho_qubits[0])
    qc.ry(theta_d[1], sigma_qubits[0])
    qc.ry(theta_d[2], rho_qubits[1])
    qc.ry(theta_d[3], sigma_qubits[1])
    
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



def noisy_evaluate_discriminator(theta_d, theta_g, target, shots=2048):
    
    noise_model = NoiseModel()

    # Errore di depolarizzazione (probabilità 5% su porte a 1 qubit)
    error_1q = depolarizing_error(0.05, 1)
    noise_model.add_quantum_error(error_1q, ["h", "x", "rz"], [0])
    noise_model.add_quantum_error(error_1q, ["h", "x", "rz"], [1])
    noise_model.add_quantum_error(error_1q, ["h", "x", "rz"], [2])
    noise_model.add_quantum_error(error_1q, ["h", "x", "rz"], [3])
    noise_model.add_quantum_error(error_1q, ["h", "x", "rz"], [4])

    # Errore di depolarizzazione (probabilità 10% su CX)
    error_2q = depolarizing_error(0.1, 2)
    noise_model.add_quantum_error(error_2q, ["cx"], [0, 1])

    # Decoerenza (T1/T2 relaxation) su entrambi i qubit
    t1, t2, gate_time = 50e3, 70e3, 100   # ns
    relax_error = thermal_relaxation_error(t1, t2, gate_time)
    noise_model.add_quantum_error(relax_error, ["u1", "u2", "u3"], [0])
    noise_model.add_quantum_error(relax_error, ["u1", "u2", "u3"], [1])
    noise_model.add_quantum_error(relax_error, ["u1", "u2", "u3"], [2])
    noise_model.add_quantum_error(relax_error, ["u1", "u2", "u3"], [3])
    noise_model.add_quantum_error(relax_error, ["u1", "u2", "u3"], [4])
    
    simulator = AerSimulator(noise_model=noise_model)
    
    
    
    gen_circ = generate_state(theta_g)
    target_circ = target

    qc = discriminator_circuit(theta_d, gen_circ, target_circ)
    
    
    qc_compiled = transpile(qc, simulator)
    
    # Simulazione
    result = simulator.run(qc_compiled, shots=1000).result()
    counts = result.get_counts()
    
    p0 = counts.get('0', 0) / shots
    d_val = 2 * abs(p0 - 0.5)
    
    return p0, d_val




'''
# =========================
# Training loop suggerito
# =========================
theta_g = np.random.rand(4) * 0.1  # 4 parametri
theta_d = np.random.rand(4) * 0.1

gen_losses, disc_losses, fidelities = [], [], []
max_epochs = 200
target_fidelity = 0.995
patience = 5
counter = 0
best_fidelity = 0
best_theta_g = theta_g.copy()
best_theta_d = theta_d.copy()

# Opzioni ottimizzatore
optimizer_options = {'maxiter': 50, 'disp': False}

print("Inizio training...")
print("Epoch | D loss  | G loss  | Fidelity  | p0     | θ_g change")
print("------|---------|---------|-----------|--------|-----------")

for epoch in range(max_epochs):
    # Salva theta_g vecchio per vedere i cambiamenti
    old_theta_g = theta_g.copy()
    
    # Update Discriminator con COBYLA
    res_d = minimize(cost_discriminator, theta_d, args=(theta_g,target),
                   method='COBYLA', options=optimizer_options)
    theta_d = res_d.x
    
    # Update Generator con COBYLA
    res_g = minimize(cost_generator, theta_g, args=(theta_d,target),
                   method='COBYLA', options=optimizer_options)
    theta_g = res_g.x
    
    # Valutazioni
    p0, d_val = evaluate_discriminator(theta_d, theta_g, target)
    current_state = generate_state(theta_g)
    current_fidelity = state_fidelity(Statevector.from_instruction(current_state), target_state)
    
    # Calcola cambiamento parametri generatore
    theta_g_change = np.linalg.norm(theta_g - old_theta_g)
    
    # Salva la migliore fidelity
    if current_fidelity > best_fidelity:
        best_fidelity = current_fidelity
        best_theta_g = theta_g.copy()
        best_theta_d = theta_d.copy()
    
    gen_losses.append(-np.log(p0 + 1e-8))
    disc_losses.append(-d_val)
    fidelities.append(current_fidelity)
    
    # Stampa dettagliata per debug
    print(f"{epoch+1:4d} | {-d_val:7.4f} | {-np.log(p0 + 1e-8):7.4f} | {current_fidelity:9.6f} | {p0:6.4f} | {theta_g_change:9.6f}")
    
    # Early stopping
    if current_fidelity >= target_fidelity:
        counter += 1
        if counter >= patience:
            print(f"\n✅ Fidelity target raggiunta!")
            break
    else:
        counter = 0
    
    # Learning rate decay più frequente
    if epoch % 50 == 0 and epoch > 0:  # Ogni 25 epoche
        theta_g *= 0.95 # Decay del 5%
        theta_d *= 0.95
        print(f"🔧 Learning rate decay applicato")

# Usa i migliori parametri trovati
final_state = generate_state(best_theta_g)
fid = state_fidelity(Statevector.from_instruction(final_state), target_state)
print(f"\nFidelity migliore: {fid:.6f}")
print(f"Parametri generatore migliori: {best_theta_g}")

# Verifica finale
print("\nVerifica finale:")
print(f"Stato generato: {Statevector.from_instruction(final_state)}")
print(f"Stato target:   {target_state}")
'''