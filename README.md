# QRAM Project – Simulazione e Ottimizzazione della Quantum RAM

Questo progetto esplora l'implementazione e la simulazione della **Quantum RAM (QRAM)** secondo vari modelli, utilizzando [Qiskit](https://qiskit.org/). Include strumenti per la creazione di oracoli quantistici e la simulazione di circuiti quantistici orientati alla ricerca e al miglioramento delle architetture QRAM.

## 📁 Struttura del progetto
```text
qram_project/
├── qram/
│   ├── naive.py               # Implementazione QRAM modello Naive
│   ├── bucket_brigade.py      # Implementazione QRAM modello Bucket Brigade
│
├── utils/
│   ├── Oracles.py             # Funzione Make_Oracle per creare oracoli quantistici
│   ├── QiskitUtils.py         # Funzione di raggruppamento per funzioni utili per esecuzione o presentazione dei circuiti
│
├── tests/
│   ├── tests.py               # Test per la correttezza degli oracoli
│
├── main.py                    # Esempio di utilizzo
├── requirements.txt           # Dipendenze del progetto
└── README.md                  # Questo file
```


## 🚀 Funzionalità

- ✅ Simulazione di QRAM in stile Naive
- ✅ Supporto per oracoli a più bit tramite `Make_Oracle`
- ✅ Supporto per test automatici con `unittest`
- ✅ Simulazione tramite `Qiskit` su backend locali
- ✅ Architettura modulare per future estensioni (es. modelli ibridi, qutrit, fanout, ecc.)

## 🧠 Obiettivo del progetto

Il progetto mira a:
- Simulare il comportamento logico dei modelli di QRAM
- Analizzare e migliorare la propagazione del segnale quantistico
- Investigare soluzioni ottimizzate per il routing delle informazioni usando strutture quantistiche

## Istalla le dipendenze con

```bash
- pip install -r requirements.txt
```

## Istalla il progetto con

```bash
- pip install -e .
```


## 🧪 Esecuzione dei test

Per eseguire i test automatici:

```bash
pytest -s tests/
```