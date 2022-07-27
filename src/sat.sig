sig sat.

kind var   type.


kind lit   type.

type var   var -> lit.
type neg   var -> lit.


/*
 * Linear encodings of clauses and formulas (c*, f* are empty)
 * I think this might end up easier to work with than a branching encoding
 */
kind clause   type.

type c*   clause.
type or   lit -> clause -> clause.


kind formula   type.

type f*    formula.
type and   clause -> formula -> formula.


/*
 * Our context of assumed assumptions is assuming (is_true lit) for
 * each literal.
 */
type is_true   lit -> o.



/*
 * Checking satisfiability for both formulas and clauses
 */
exportdef sat          formula -> o.
exportdef sat_clause   clause -> o.


/*
 * Clause is falsified by the assumptions
 */
exportdef unsat_clause   clause -> o.


/*
 * Negate a literal
 */
exportdef negate   lit -> lit -> o.

