module proof.

accumulate redundant.

/*
 * Last line in proof must be empty clause
 */
check_proof (add_line (proof_line CID c* ProofList) p*) :-
   no_clause CID, rup c* ProofList.
/*
 * Earlier lines must be valid and are added to the context then
 */
check_proof (add_line (proof_line CID C ProofList) Rest) :-
   no_clause CID,
   rup C ProofList, clause_id CID C => check_proof Rest.


/*
 * This relies on the order of clauses by using cut and fail.
 * If the clause ID is already assigned a clause, this will fail.
 * It only succeeds if it is unasigned.
 */
no_clause CID :- clause_id CID C, !, fail.
no_clause CID.

