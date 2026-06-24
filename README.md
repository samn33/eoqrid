eoqrid
======

Exchange-Only Quantum Computing Simulator

## Feature

eoqrid is a Python library designed to simulate silicon quantum computers that control qubits using the Exchange-Only method. Itprovides the following two main features:

* **Logical Quantum Circuit Transpilation**
  - It can translate logically described quantum circuits into sets of exchange interactions and measurements so they can be executed on silicon qubits. Furthermore, it allows for the transformation and optimization of circuits to match the specific topology of a quantum chip.

* **Physical Quantum Circuit Execution**
  - It can simulate and verify the result from executing physical quantum circuits described by sets of exchange interactions and measurements.

## Install

```bash
pip install eoqrid
```
or

```bash
git clone https://github.com/samn33/eoqrid.git
cd eoqrid
pip install .
```

## Uninstall

```bash
pip uninstall eoqrid
```

## Usage

```pthon
$ cat sample.py
from qiskit import QuantumCircuit
from eoqrid import EoqSimulator

qc = QuantumCircuit(1)
qc.h(0)

print("== quantum circuit ==")
print(qc)

eoq = EoqSimulator()
qc_native = eoq.transpile(qc)

print("== transpiled quantum circuit ==")
print(qc_native)
print(f"depth = {qc_native.depth()}")

res = eoq.execute(qc_native)

print("== quantum state (logical) ==")
res.qstate.draw()

print("== quantum state (physical) ==")
res.qstate.draw(mode='physical')
```

```
$ python sample.py
== quantum circuit ==
   ┌───┐
q: ┤ H ├
   └───┘
== transpiled quantum circuit ==
         ┌───────────────┐                 ┌───────────────┐
q_0 -> 0 ┤0              ├─────────────────┤0              ├
         │  Ex(5.3279,1) │┌───────────────┐│  Ex(5.3279,1) │
q_1 -> 1 ┤1              ├┤0              ├┤1              ├
         └───────────────┘│  Ex(1.9106,1) │└───────────────┘
q_2 -> 2 ─────────────────┤1              ├─────────────────
                          └───────────────┘
depth = 3
== quantum state (logical) ==
c[0] = +0.7071+0.0000*i : 0.5000 |++++++
c[1] = +0.7071-0.0000*i : 0.5000 |++++++
== quantum state (physical) ==
c[000] = +0.0000+0.0000*i : 0.0000 |
c[001] = +0.5774-0.0000*i : 0.3333 |++++
c[010] = +0.2113-0.0000*i : 0.0447 |+
c[011] = +0.0000+0.0000*i : 0.0000 |
c[100] = -0.7887-0.0000*i : 0.6220 |+++++++
c[101] = +0.0000+0.0000*i : 0.0000 |
c[110] = +0.0000+0.0000*i : 0.0000 |
c[111] = -0.0000-0.0000*i : 0.0000 |
```															 

## Documents

- [Tutorial(japanese)](docs/tutorial_jp.md)

## References

1. [Aaron J. Weinstein, et al., "Universal logic with encoded spin qubits in silicon",arXiv:2202.03605](https://arxiv.org/abs/2202.03605)

2. [Exchange Only 量子ビットの仕組み：3つのスピンで「磁場」を超える(YuichiroMinato)](https://zenn.dev/yuichirominato/articles/96b88617c4bffa)

## Requirements

- Linux (Ubuntu 24.04 LTS)
- Python 3.12

## Licence

MIT

## Author

[Sam.N](http://github.com/samn33)
