from utils.Oracles import Make_Oracle  

def test_oracle_single_bit_0():
    oracle = Make_Oracle("0")
    assert oracle.num_qubits == 2  # 1 controllo + 1 target
    assert oracle.count_ops().get('x', 0) == 2  # X per encoding e ripristino
    assert oracle.count_ops().get('cx', 0) == 1
    print(oracle.draw(output='text'))

def test_oracle_single_bit_1():
    oracle = Make_Oracle("1")
    assert oracle.num_qubits == 2
    assert oracle.count_ops().get('x', 0) == 0
    assert oracle.count_ops().get('cx', 0) == 1 
    print(oracle.draw(output='text'))

def test_oracle_two_bits_10():
    oracle = Make_Oracle("10")
    assert oracle.num_qubits == 3
    assert oracle.count_ops().get('x', 0) == 2  # solo per il bit 0
    assert oracle.count_ops().get('ccx', 0) == 1 
    print(oracle.draw(output='text'))

def test_oracle_three_bits_011():
    oracle = Make_Oracle("011")
    assert oracle.num_qubits == 4
    assert oracle.count_ops().get('x', 0) == 2  # solo per bit 0
    assert oracle.count_ops().get('mcx', 0) == 1
    print(oracle.draw(output='text'))

def test_oracle_all_zeros():
    oracle = Make_Oracle("000")
    assert oracle.num_qubits == 4
    assert oracle.count_ops().get('x', 0) == 6  # 3 X, 3 ripristini
    assert oracle.count_ops().get('mcx', 0) == 1
    print(oracle.draw(output='text'))

def test_oracle_all_ones():
    oracle = Make_Oracle("111")
    assert oracle.num_qubits == 4
    assert oracle.count_ops().get('x', 0) == 0
    assert oracle.count_ops().get('mcx', 0) == 1
    print(oracle.draw(output='text'))
