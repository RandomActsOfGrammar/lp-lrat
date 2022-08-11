
# Lambda Prolog LRAT Checker
A verified proof checker for unsatisfiability proofs for SAT solvers,
written in Lambda Prolog.  This can handle [LRAT
proofs](https://www.cs.cmu.edu/~mheule/publications/lrat.pdf), [FRAT
proofs](https://www.cs.cmu.edu/~mheule/publications/FRAT-TACAS.pdf),
and [DRAT
proofs](https://www.cs.cmu.edu/~mheule/publications/drat-trim.pdf).
This only checks a subset of all of these formats:  clauses may only
be justified by RUP proof lines, not RAT proof lines.


## Usage
To check a proof, run
```
./check <DIMACS FILE> <PROOF FILE>
```
For example,
```
./check examples/lrat_paper/lrat_paper.cnf examples/lrat_paper/proof.lrat
```
If this succeeds, the result will show either `VERIFIED` or
`UNVERIFIED`.

The LRAT format is the default.  To use another format, use the `-p`
option and give it the format---`FRAT` or `DRAT`.  For example,
```
./check -p DRAT examples/lrat_paper/lrat_paper.cnf examples/lrat_paper/proof.drat
```


## Proof
The proof of correctness of the proof checker can be found in the
`proof` directory.  The assumptions made in this proof are listed at
the beginning of the proof file.  The main assumptions are about one
predicate from the proof checker specification that uses `!` (cut) and
`fail` from Lambda Prolog, about which Abella cannot reason.  We
verify that checking a problem (formula and unsatisfiability proof)
and having a satisfying assignment is impossible.

Note that the program used to translate the DIMACS file and proof file
into Lambda Prolog is written in Python and is not verified.


## Software Requirements
This is assuming you are using
[Teyjus](https://github.com/teyjus/teyjus) for Lambda Prolog.  This
con be obtained from [GitHub](https://github.com/teyjus/teyjus),
either by cloning the repository and building it or by [downloading
the binaries](https://github.com/teyjus/teyjus/releases).  The
Makefile and `check` script assume all the Teyjus programs are on your
path.

You might be able to use the proof checker with another Lambda Prolog
implementation, but you will likely need to set up your own build and
run scripts.

You will also need [Python 3](https://www.python.org/downloads/) to
encode the problem into Lambda Prolog.  This must be in your path as
well as `python3`.

If you want to run the proof, you will need
[Abella](http://abella-prover.org/index.html) installed.

