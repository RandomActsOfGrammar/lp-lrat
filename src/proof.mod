module proof.

accumulate redundant.

/*
 * Last line in proof must be empty clause (proof optional)
 */
check_proof (p* ProofList) :- rup c* ProofList.
check_proof short_p* :- drup c*.
/*
 * Earlier lines must be valid and are added to the context then
 * (proof optional)
 */
check_proof (add_line C ProofList Rest) :-
   rup C ProofList, pi CID\ clause_id CID C => check_proof (Rest CID).
check_proof (short_line C Rest) :-
   drup C, pi CID\ clause_id CID C => check_proof (Rest CID).


check_problem (end_problem P) :- check_proof P.
check_problem (add_clause C Rest) :-
   pi CID\ clause_id CID C => check_problem (Rest CID).

