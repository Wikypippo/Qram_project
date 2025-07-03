from setuptools import setup, find_packages

setup(
    name='qram_project',
    version='0.1.0',
    description='Quantum RAM implementation project',
    author='Tuo Nome',
    packages=find_packages(),
    install_requires=[
        'qiskit',  # o altre dipendenze
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
