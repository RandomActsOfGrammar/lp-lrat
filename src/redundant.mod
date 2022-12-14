module redundant.

accumulate sat.

/*
 * We need to go through and generate the assumptions for the negation
 * of the clause before going to check the proof.
 */
rup c* CIDList :- rup_help CIDList.
rup (or L CRest) CIDList :-
   negate L NL, is_true NL => rup CRest CIDList.


/*Last clause must be falsified*/
rup_help (CID::nil) :- clause_id CID C, unsat_clause C.
/*Earlier clauses must become unit and propagate to the rest*/
rup_help (CID::Rest) :-
   clause_id CID C, unit_clause C L, is_true L => rup_help Rest.


/*
 * Like rup and rup_help, but with search for valid clauses instead of
 * having them given
 */
drup c* :- drup_help nil.
drup (or L CRest) :-
   negate L NL, is_true NL => drup CRest.
drup_help X :- clause_id CID C, unsat_clause C.
drup_help X :-
   clause_id CID C, unit_clause C L, is_true L => drup_help Rest.


/*first literal is the unit*/
unit_clause (or L Rest) L :-
   not_assigned L, negate L NL, not_assigned NL, unsat_clause Rest.
/*first literal is falsified*/
unit_clause (or L Rest) Unit :-
   negate L NL, is_true NL, unit_clause Rest Unit.


/*
 * This relies on the order of clauses by using cut and fail.
 * If L is assigned true, this will fail.  It only succeeds if it is
 * unassigned.
 */
not_assigned L :- is_true L, !, fail.
not_assigned L.

