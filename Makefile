
#In order to link, we need all the lpo files
default: build/proof.lpo build/redundant.lpo build/sat.lpo


all: build/proof.lp build/sat.lp build/redundant.lp


#A note on the *.lp lines:
#There is apparently no other way to make it put the .lp file in the
#build directory.  It wants to put it in the root directory unless I
#cd on the same line, and it has no -o option.

build/sat.lpo: src/sat.sig src/sat.mod
	tjcc src/sat.mod -o build/sat.lpo

build/sat.lp: build/sat.lpo
	cd build; TJPATH=build tjlink sat

build/redundant.lpo: src/sat.sig src/redundant.sig src/redundant.mod
	TJPATH=src tjcc src/redundant.sig -o build/redundant.lpo

build/redundant.lp: build/redundant.lpo build/sat.lpo
	cd build; TJPATH=build tjlink redundant

build/proof.lpo: src/redundant.sig src/proof.sig src/proof.mod
	TJPATH=src tjcc proof.sig -o build/proof.lpo

build/proof.lp: build/proof.lpo build/redundant.lpo build/sat.lpo
	cd build; TJPATH=build tjlink proof


part-clean:
	find . -name "*~" -delete
	find build/ -name "*.sig" -delete
	find build/ -name "*.mod" -delete

clean: part-clean
	find . -name "*.lpo" -delete
	find . -name "*.lp" -delete
