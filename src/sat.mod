module sat.

sat_clause (or L Rest) :- sat_clause Rest.
sat_clause (or L Rest) :- is_true L.


sat f*.
sat (and C Rest) :- sat_clause C, sat Rest.


unsat_clause c*.
unsat_clause (or L Rest) :- negate L NL, is_true NL, unsat_clause Rest.


negate (var X) (neg X).
negate (neg X) (var X).

