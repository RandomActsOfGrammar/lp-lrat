module proof.

accumulate redundant.

/*
 * Last line in proof must be empty clause
 */
check_proof (add_line (proof_line CID c* ProofList) p*) :-
   rup c* ProofList.
/*
 * Earlier lines must be valid and are added to the context then
 */
check_proof (add_line (proof_line CID C ProofList) Rest) :-
   rup C ProofList, clause_id CID C => check_proof Rest.

