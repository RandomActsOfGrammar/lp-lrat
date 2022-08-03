module proof.

accumulate redundant.

/*
 * Last line in proof must be empty clause
 */
check_proof (p* ProofList) :- rup c* ProofList.
/*
 * Earlier lines must be valid and are added to the context then
 */
check_proof (add_line C ProofList Rest) :-
   rup C ProofList, pi CID\ clause_id CID C => check_proof (Rest CID).


check_problem (end_problem P) :- check_proof P.
check_problem (add_clause C Rest) :-
   pi CID\ clause_id CID C => check_problem (Rest CID).

