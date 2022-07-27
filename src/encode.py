#!/usr/bin/python

'''
This script reads a DIMACS file and an LRAT file (using only RUP
lines), and turns it into a Lambda Prolog file that can then be
checked by the Lambda Prolog proof checker.  There are several things
this encoding does:
 * Create var constants for all the variables in the problem
 * Create clause_id constants for all the clauses in the original
   problem and the proof
 * Build the appropriate clause structure and associate it with the
   clause_id for that clause
 * Associate the whole problem with the proof_name a_proof constant to
   make it easy to run
'''

import argparse
import os.path


######################################################################
#                      LAMBDA PROLOG CONVERSION                      #
######################################################################

#Write the signature file header
#Argument:
#  module_name:  name of module being defined
#  sigfile:  open file into which to write the signature
#Returns:  None
def write_sig_header(module_name, sigfile):
    sigfile.write("sig " + module_name + ".\n")
    sigfile.write("accum_sig proof.\n\n")


#Write the module file header
#Argument:
#  module_name:  name of module being defined
#  modfile:  open file into which to write the module
#Returns:  None
def write_mod_header(module_name, modfile):
    modfile.write("module " + module_name + ".\n")
    modfile.write("accumulate proof.\n\n")


#Turn a variable integer into a Lambda Prolog var name
#Argument:
#  var_num:  integer number of variable in problem
#Return:  string variable name
def create_var_name(var_num):
    return "v" + str(var_num)


#Turn a clause ID into a Lambda Prolog clause ID
#Argument:
#  clause_id:  integer number of clause in problem
#Return:  string clause ID
def create_clause_id(clause_id):
    return "c" + str(clause_id)


#Turn a variable integer into a Lambda Prolog var def
#Argument:
#  var_num:  integer number of clause in problem
#Return:  string var def
def create_var_def(var_num):
    return "type " + create_var_name(var_num) + "   var.\n"


#Turn a clause ID into a Lambda Prolog clause_id def
#Argument:
#  clause_id:  integer number of clause in problem
#Return:  string clause_id def
def create_clause_id_def(clause_id):
    return "type " + create_clause_id(clause_id) + "   clause_id.\n"


#Turn a numeric literal into a Lambda Prolog lit
#Argument:
#  int_lit:  positive or negative integer literal
#Return:  string literal
def make_lit(int_lit):
    if int_lit < 0:
        return "(neg " + create_var_name(abs(int_lit)) + ")"
    else:
        return "(var " + create_var_name(int_lit) + ")"


#Build a string Lambda Prolog clause
#Argument:
#  lits:  integer literals of the clause
#Return:  string clause
def build_clause(lits):
    clause = "c*"
    for lit in lits[::-1]:
        lp_lit = make_lit(lit)
        clause = "(or " + lp_lit + " " + clause + ")"
    return clause


#Build a declaration of a clause having a certain ID
#Arguments:
#  clause_id:  integer clause ID
#  clause:  string Lambda Prolog clause
#Return:  string clause ID--clause association
def associate_clause_id(clause_id, clause):
    return "clause_id " + create_clause_id(clause_id) + " " + \
        clause + ".\n"


#Build a proof_line string
#Arguments:
#  clause_id:  integer clause ID
#  lits:  integer clause literals
#  proof_clauses:  integer proof clause ID's
#Return:  string Lambda Prolog proof_line
def build_proof_line(clause_id, lits, proof_clauses):
    clause = build_clause(lits)
    proof_ids = list(map(create_clause_id, proof_clauses))
    proof = ", ".join(proof_ids)
    return "(proof_line " + create_clause_id(clause_id) + " " + \
        clause + " [" + proof + "])"


#Build a Lambda Prolog definition of a proof by name a_proof
#Argument:
#  proof_lines:  list of string proof_lines
#Return:  string Lambda Prolog proof name declaration
def build_proof_name_declaration(proof_lines):
    #build the proof
    proof = "p*"
    for pl in proof_lines[::-1]:
        proof = "(add_line " + pl + " " + proof + ")"
    #declare the proof name
    return "proof_name a_proof " + proof + ".\n"




######################################################################
#                           DIMACS PARSING                           #
######################################################################

#Process the DIMACS file, converting its contents to Lambda Prolog
#Arguments:
#  dimacs_filename:  DIMACS file to read
#  outmod:  open file into which to write the module output
#  outsig:  open file into which to write the signature output
#Return:  number of clauses or -1 for failure (prints error message)
def process_dimacs(dimacs_filename, outmod, outsig):
    #check if it exists and open it
    if not os.path.exists(dimacs_filename):
        print("DIMACS file '" + dimacs_filename + "' does not exist")
        return -1
    dfile = open(dimacs_filename, "r")

    #read the header
    num_clauses = parse_dimacs_header(dfile, dimacs_filename, outsig)
    if num_clauses < 0:
        dfile.close()
        return num_clauses

    #read the clauses and output them
    read_clauses = parse_dimacs_clauses(dfile, dimacs_filename, outmod)
    if read_clauses < 0:
        dfile.close()
        return read_clauses
    if read_clauses != num_clauses:
        print("DIMACS header declared", num_clauses,
              "clauses but contained", read_clauses, "clauses")
        dfile.close()
        return -1

    dfile.close()
    return num_clauses


#Move past comments and parse DIMACS header:  p cnf <vars> <clauses>
#Output the variables and clause ID's into the outmod
#Arguments:
#  dfile:  open DIMACS file for reading
#  dimacs_filename:  DIMACS filename for printing error messages
#  outsig:  open file into which to write the signature output
#Return:  number of clauses or -1 for failure (prints error message)
def parse_dimacs_header(dfile, dimacs_filename, outsig):
    #move past comments
    line = dfile.readline()
    while line and line[0] == "c":
        line = dfile.readline()

    #check if the file ran out without the header
    if line == "":
        print("DIMACS file '" + dimacs_filename +
              "' ended before reading the header")
        return -1

    #check if it is, indeed, the header
    split_line = line.split()
    if split_line[0] != "p" or split_line[1] != "cnf" or \
       not split_line[2].isdigit() or not split_line[3].isdigit():
        print("DIMACS file '" + dimacs_filename +
              "' header has the wrong form")
        return -1

    num_vars = int(split_line[2])
    num_clauses = int(split_line[3])

    #create all the vars and put them in the file
    for i in range(1, num_vars + 1):
        outsig.write(create_var_def(i))

    #create all the clause ID's for the original clauses
    for i in range(1, num_clauses + 1):
        outsig.write(create_clause_id_def(i))

    return num_clauses


#Output the clauses from the DIMACS file into the outmod
#Arguments:
#  dfile:  open DIMACS file for reading
#  dimacs_filename:  DIMACS filename for prenting error messages
#  outmod:  open file into which to write the module output
#Return:  number of clauses read or -1 for failure
def parse_dimacs_clauses(dfile, dimacs_filename, outmod):
    line = dfile.readline()
    clause_count = 0
    while line:
        #only handle non-blank, non-comment lines
        if not line.isspace() and line[0] != "c":
            clause_count += 1
            split_line = line.split()
            if split_line[-1] != "0":
                print("Error in clause " + str(clause_count) + \
                      ":  Does not end with 0")
                return -1
            #put the clause literals into a list
            clause_lits = list(map(int, split_line[:-1]))
            #build clause definition
            clause = build_clause(clause_lits)
            outmod.write(associate_clause_id(clause_count, clause))
        line = dfile.readline()
    return clause_count




######################################################################
#                            LRAT PARSING                            #
######################################################################

#Process the LRAT file, converting its contents to Lambda Prolog
#Arguments:
#  lrat_filename:  LRAT file to read
#  outmod:  open file into which to write the module output
#  outsig:  open file into which to write the signatuer output
#  num_original_clauses:  number of clauses in the original problem
#Return:  True for success, False for failure (prints error message)
def process_lrat(lrat_filename, outmod, outsig, num_original_clauses):
    #check if it exists and open it
    if not os.path.exists(lrat_filename):
        print("LRAT file '" + lrat_filename + "' does not exist")
        return False
    lfile = open(lrat_filename, "r")
    #read all the lines and build a list of Lambda Prolog proof_lines
    proof_lines = []
    line = lfile.readline()
    while line:
        #only handle non-blank, non-comment lines
        if not line.isspace() and line[0] != "c":
            result, pline = process_lrat_line(line, outsig)
            #check for failure of line processing
            if not result:
                lfile.close()
                return False
            #add the line to the lines if it is not blank
            if pline != "":
                proof_lines.append(pline)
        line = lfile.readline()
    #output the proof to the file
    outmod.write(build_proof_name_declaration(proof_lines))
    lfile.close()
    return True


#Process a single, non-empty LRAT line to output its new clause ID's
#to Lambda Prolog in the outmod and return the proof_line
#Arguments:
#  line:  line as read from file
#  outsig:  open file into which to write the signature output
#Return:  Pair of (was successful, Lambda Prolog translation)---
#   translation is empty string for delete lines
def process_lrat_line(line, outsig):
    split_line = line.split()
    #skip delete lines
    if split_line[1] != "d":
        clause_id = int(split_line[0])
        rest = list(map(int, split_line[1:]))
        #check we have at least the last zero
        if rest[-1] != 0:
            print("Added clause", clause_id, "is incomplete")
            return (False, "")
        first_zero = rest.index(0)
        clause_lits = rest[:first_zero]
        proof_clauses = rest[first_zero + 1:-1]
        #check there were, in fact, two separate zeroes
        if proof_clauses == []:
            print("Added clause", clause_id, "is incomplete")
            return (False, "")
        #declare this new clause ID
        outsig.write(create_clause_id_def(clause_id))
        #build the proof line
        pline = build_proof_line(clause_id, clause_lits, proof_clauses)
        return (True, pline)
    else:
        return (True, "")




######################################################################
#                                MAIN                                #
######################################################################

def main():
    #parse arguments
    argparser = \
        argparse.ArgumentParser(description="Convert a DIMACS file "
                                "and LRAT file to a Lambda Prolog "
                                "program")
    #positional arguments
    argparser.add_argument("dimacs", metavar="D", type=str,
                           help="DIMACS file to read")
    argparser.add_argument("lrat", metavar="L", type=str,
                           help="LRAT file to read")
    argparser.add_argument("output", metavar="O", type=str,
                           help="base output name to write")
    #options
    argparser.add_argument('--force', dest='force',
                           action='store_const',
                           const=True, default=False,
                           help="force overwrite existing files")
    #parse arguments
    args = argparser.parse_args()
    force_overwrite = args.force

    #open the output files
    file_base = args.output
    outsig_name = file_base + ".sig"
    outmod_name = file_base + ".mod"
    for filename in [outsig_name, outmod_name]:
        if (not force_overwrite) and os.path.exists(filename):
            open_anyway = input("Output file '" + filename + \
                                "' exists; overwrite (Y/n)? ")
            if open_anyway != "" and open_anyway[0].lower() != "y":
                print("Exiting rather than overwriting", filename)
                return 0 #not a failure, just a change of mind
    outsig = open(outsig_name, "w")
    outmod = open(outmod_name, "w")

    #write the header information
    module_base = os.path.basename(args.output)
    write_sig_header(module_base, outsig)
    write_mod_header(module_base, outmod)

    #parse and process the DIMACS file
    num_original_clauses = process_dimacs(args.dimacs, outmod, outsig)
    if num_original_clauses < 0:
        outsig.close()
        outmod.close()
        return num_original_clauses

    #parse and process the LRAT file
    result = process_lrat(args.lrat, outmod, outsig,
                          num_original_clauses)

    outsig.close()
    outmod.close()
    return 0 if result else -1


if __name__ == "__main__":
    main()

