sig redundant.

accum_sig sat.


kind clause_id   type.
/*
 * Clause store is a context, so it is part of our logical context.
 * Each original line and learned line has one of these with the ID.
 */
type clause_id   clause_id -> clause -> o.


/*
 * Check the clause follows from the given clauses (in order) by
 * reverse unit propagation.
 */
exportdef rup   clause -> list clause_id -> o.


/*
 * Actually do the reverse unit propagation from a set of assumptions
 * and clauses
 */
exportdef rup_help   list clause_id -> o.


/*
 * Determine if a clause is unit under he assumptions, and give that
 * unit literal back
 */
exportdef unit_clause   clause -> lit -> o.


/*
 * Literal is not given true or false
 * I don't think we can reason about this, but we can assume things
 * about it for the proving part.
 */
exportdef not_assigned   lit -> o.

