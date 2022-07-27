module output.
accumulate proof.

clause_id c1 (or (var v1) (or (var v2) (or (neg v3) c*))).
clause_id c2 (or (neg v1) (or (neg v2) (or (var v3) c*))).
clause_id c3 (or (var v2) (or (var v3) (or (neg v4) c*))).
clause_id c4 (or (neg v2) (or (neg v3) (or (var v4) c*))).
clause_id c5 (or (neg v1) (or (neg v3) (or (neg v4) c*))).
clause_id c6 (or (var v1) (or (var v3) (or (var v4) c*))).
clause_id c7 (or (neg v1) (or (var v2) (or (var v4) c*))).
clause_id c8 (or (var v1) (or (neg v2) (or (neg v4) c*))).
proof_name a_proof (add_line (proof_line c9 (or (var v1) (or (var v2) c*)) [c1, c6, c3]) (add_line (proof_line c10 (or (var v1) (or (var v3) c*)) [c9, c8, c6]) (add_line (proof_line c11 (or (var v1) c*) [c10, c9, c4, c8]) (add_line (proof_line c12 (or (var v2) c*) [c11, c7, c5]) (add_line (proof_line c13 c* [c11, c12, c2, c4, c5]) p*))))).
