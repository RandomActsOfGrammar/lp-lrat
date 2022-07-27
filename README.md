
# lp-lrat
A proof checker for [LRAT
proofs](https://www.cs.cmu.edu/~mheule/publications/lrat.pdf) written
in Lambda Prolog.  More accurately, this checks LRUP proofs---clauses
may only be justified by RUP proof lines, not RAT proof lines.


## Usage
To check a proof, run
```
./check <DIMACS FILE> <LRAT FILE>
```
For example,
```
./check examples/lrat_paper/lrat_paper.cnf examples/lrat_paper/lrat_paper.lrat
```
If this succeeds, the result will show either `VERIFIED` or
`UNVERIFIED`.

