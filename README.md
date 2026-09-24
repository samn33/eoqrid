eoqrid
======

Exchange-Only Quantum Computing Simulator

## Feature

eoqrid is a Python library for simulating silicon-based quantum processors operating on the exchange-only architecture. Key features include:

* **Logical Circuit Transpilation**
  - Translates logical quantum circuits into native exchange interactions and measurement sequences, optimizing circuits for target chip topologies.

* **Physical Circuit Simulation**
  - Simulates physical quantum circuits defined by exchange interactions and measurements, enabling verification of execution results.


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
from qiskit import QuantumCircuit
from eoqrid import EoqEngine

qc = QuantumCircuit(1)
qc.h(0)

print("== quantum circuit ==")
print(qc)

eoq = EoqEngine(3)
qc_phys = eoq.transpile(qc)

print("== transpiled quantum circuit ==")
print(qc_phys)
print(f"depth = {qc_phys.depth()}")

res = eoq.execute(qc_phys)

print("== quantum state (logical) ==")
res.qstate.draw()

print("== quantum state (physical) ==")
res.qstate.draw(mode='physical')
```

```
== quantum circuit ==
   ┌───┐
q: ┤ H ├
   └───┘
== transpiled quantum circuit ==
         ┌──────┐┌───────────────┐                 ┌───────────────┐
q_0 -> 0 ┤0     ├┤0              ├─────────────────┤0              ├
         │  Sin ││  Ex(5.3279,1) │┌───────────────┐│  Ex(5.3279,1) │
q_1 -> 1 ┤1     ├┤1              ├┤0              ├┤1              ├
         └──────┘└───────────────┘│  Ex(1.9106,1) │└───────────────┘
q_2 -> 2 ──|0>────────────────────┤1              ├─────────────────
                                  └───────────────┘
depth = 4
== quantum state (logical) ==
c[0] = +0.7071+0.0000*i : 0.5000 |++++++
c[1] = +0.7071+0.0000*i : 0.5000 |++++++
== quantum state (physical) ==
c[000] = +0.0000+0.0000*i : 0.0000 |
c[001] = +0.0000+0.5774*i : 0.3333 |++++
c[010] = +0.0000+0.2113*i : 0.0447 |+
c[011] = +0.0000+0.0000*i : 0.0000 |
c[100] = -0.0000-0.7887*i : 0.6220 |+++++++
c[101] = +0.0000+0.0000*i : 0.0000 |
c[110] = +0.0000+0.0000*i : 0.0000 |
c[111] = +0.0000+0.0000*i : 0.0000 |
```															 

## Documents

- [Tutorial(japanese)](docs/tutorial/jp/main.md)

## Requirements

- Linux (Ubuntu 24.04 LTS)
- Python 3.12

## Licence

MIT

## Author

[Sam.N](http://github.com/samn33)
