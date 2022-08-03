sig proof.

accum_sig redundant.


kind proof   type.

type p*         list clause_id -> proof. /*implicit empty clause*/
type add_line   clause -> list clause_id -> (clause_id -> proof) ->
                proof.
/*Note we do not have delete lines.  We can't delete clauses, so we
  can ignore the delete lines.*/


/*
 * Check whether a full proof is valid
 * Assumes original clauses are in context
 */
type check_proof   proof -> o.


kind problem   type.

type end_problem   proof -> problem.
type add_clause    clause -> (clause_id -> problem) -> problem.


/*
 *
 */
type check_problem   problem -> o.


/*
 * Give problems a name so they are easier to read
 */
kind problem_name   type.

type a_problem   problem_name.

type problem_name   problem_name -> problem -> o.

