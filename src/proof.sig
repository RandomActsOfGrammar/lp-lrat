sig proof.

accum_sig redundant.


kind proof_line   type.

type proof_line   clause_id -> clause -> list clause_id -> proof_line.


kind proof   type.

type p*         proof.
type add_line   proof_line -> proof -> proof.
/*Note we do not have delete lines.  We can't delete clauses, so we
  can ignore the delete lines.*/


/*
 * Check whether a full proof is valid
 */
type check_proof   proof -> o.


/*
 *
 */
type no_clause   clause_id -> o.


/*
 * Give proofs a name so they are easier to read
 */
kind proof_name   type.

type a_proof   proof_name.

type proof_name   proof_name -> proof -> o.

