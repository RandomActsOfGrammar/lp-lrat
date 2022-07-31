
all: sat.sig sat.mod redundant.sig redundant.mod proof.sig proof.mod verify


verify: verify.thm sat.sig sat.mod redundant.sig redundant.mod proof.sig proof.mod
	abella verify.thm


#We need to copy the specification here for two reasons:
# * Abella doesn't do any better with different directories than
#   Teyjus does.
# * The use of cut (!) and fail need to be removed from the
#   not_assigned specification before Abella can read it.
#We will assume the not_assigned predicate works.

sat.mod: ../src/sat.mod
	cp ../src/sat.mod ./temp.mod
	grep --invert "!" temp.mod > sat.mod
	rm temp.mod

sat.sig: ../src/sat.sig
	cp ../src/sat.sig ./

redundant.mod: ../src/redundant.mod
	cp ../src/redundant.mod ./temp.mod
	grep --invert "!" temp.mod > redundant.mod
	rm temp.mod

redundant.sig: ../src/redundant.sig
	cp ../src/redundant.sig ./

proof.mod: ../src/proof.mod
	cp ../src/proof.mod ./temp.mod
	grep --invert "!" temp.mod > proof.mod
	rm temp.mod

proof.sig: ../src/proof.sig
	cp ../src/proof.sig ./


part-clean:
	rm *~

clean:
	rm *~ *.sig *.mod *.thc

