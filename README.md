
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
run.

You will also need [Python 3](https://www.python.org/downloads/) to
encode the problem into Lambda Prolog.  This must be in your path as
well as `python3`.

