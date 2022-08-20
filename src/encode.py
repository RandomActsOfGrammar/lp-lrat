#!/usr/bin/python

'''
This script reads a DIMACS file and an LRAT file (using only RUP
lines), and turns it into a Lambda Prolog file that can then be
checked by the Lambda Prolog proof checker.  There are several things
this encoding does:
 * Create var constants for all the variables in the problem
 * Build the clauses and put them into a Lambda Prolog problem
 * Build the proof and add it to the Lambda Prolog problem
 * Associate the whole problem with the problem_name a_problem
   constant to make it easy to run
'''

import argparse
import os.path


class ParseException(Exception):
    def __init__(self, filetype, filename, message):
        full_message = "Parse error in " + filename + " of type " + \
            filetype + ":  " + message
        super().__init__(full_message)

class NoFileError(FileNotFoundError):
    def __init__(self, filetype, filename):
        full_message = "Error:  Could not find file " + filename + \
            " of type " + filetype
        super().__init__(full_message)

class SemanticError(Exception):
    def __init__(self, filetype, filename, message):
        full_message = "Error in file " + filename + " of type " + \
            filetype + ":  " + message
        super().__init__(full_message)


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


#Build a string Lambda Prolog abstraction
#Arguments:
#  var:  name of the variable to bind
#  body:  string Lambda Prolog term (optionally) using var
#Return:  string abstraction
def build_abstraction(var, body):
    return "(" + var + r"\ " + body +")"


#Build a proof_line string
#Arguments:
#  lits:  integer clause literals
#  proof_clauses:  integer proof clause ID's
#Return:  string Lambda Prolog proof_line
def build_proof_line(lits, proof_clauses):
    clause = build_clause(lits)
    #check whether there is a proof given
    if len(proof_clauses) > 0:
        proof_ids = list(map(create_clause_id, proof_clauses))
        proof = ", ".join(proof_ids)
        #non-empty clause has more proofs to follow
        if len(lits) > 0:
            return "add_line " + clause + " [" + proof + "]"
        #empty clause ends it
        else:
            return "p* [" + proof + "]"
    else:
        #non-empty clause has more proofs to follow
        if len(lits) > 0:
            return "short_line " + clause
        #empty clause ends it
        else:
            return "short_p*"


#Build a Lambda Prolog proof string
#Argument:
#  proof_lines:  list of pairs of (partial proof line, clause_id)
#Return:  string Lambda Prolog proof
def build_proof(proof_lines):
    proof, _ = proof_lines[-1]
    rest = proof_lines[:-1]
    for pline, cid in rest[::-1]:
        var_cid = create_clause_id(cid)
        proof = pline + " (" + build_abstraction(var_cid, proof) + ")"
    return proof


#Build a Lambda Prolog definition of a problem by name a_problem
#Arguments:
#  clauses;  list of pairs of (string Lambda Prolog clause, clause ID
#            name)
#  proof:  string Lambda Prolog proof
#Return:  string Lambda Prolog problem name declaration
def build_problem_name_declaration(clauses, proof):
    #build the problem
    problem = "end_problem (" + proof + ")"
    for c, cid in clauses[::-1]: #go through backward
        problem = "add_clause (" + c + ") " + \
            build_abstraction(cid, problem)
    #declare the problem name
    return "problem_name a_problem (" + problem + ").\n"




######################################################################
#                           DIMACS PARSING                           #
######################################################################

#Process the DIMACS file, converting its contents to Lambda Prolog
#Arguments:
#  dimacs_filename:  DIMACS file to read
#  outsig:  open file into which to write the signature output
#Return:  (num original clauses,
#          list of pairs of (list int lits, clause ID))
def process_dimacs(dimacs_filename, outsig):
    #check if it exists and open it
    if not os.path.exists(dimacs_filename):
        raise NoFileError("DIMACS", dimacs_filename)
    dfile = open(dimacs_filename, "r")

    #read the header
    num_clauses = parse_dimacs_header(dfile, dimacs_filename, outsig)
    if num_clauses < 0:
        dfile.close()
        return num_clauses

    #read the clauses and output them
    num_read, clauses = parse_dimacs_clauses(dfile, dimacs_filename)
    if num_read != num_clauses:
        dfile.close()
        message = "DIMACS header declared " + str(num_clauses) + \
            "clauses but contained" + str(num_read) + "clauses"
        raise ParseException("DIMACS", dimacs_filename, message)

    dfile.close()
    return (num_clauses, clauses)


#Move past comments and parse DIMACS header:  p cnf <vars> <clauses>
#Output the variables into the outsig
#Arguments:
#  dfile:  open DIMACS file for reading
#  dimacs_filename:  DIMACS filename for printing error messages
#  outsig:  open file into which to write the signature output
#Return:  number of clauses
def parse_dimacs_header(dfile, dimacs_filename, outsig):
    #move past comments
    line = dfile.readline()
    while line and line[0] == "c":
        line = dfile.readline()

    #check if the file ran out without the header
    if line == "":
        message = "File ended before reading header"
        raise ParseException("DIMACS", dimacs_filename, message)

    #check if it is, indeed, the header
    split_line = line.split()
    if split_line[0] != "p" or split_line[1] != "cnf" or \
       not split_line[2].isdigit() or not split_line[3].isdigit():
        message = "Header has the wrong form"
        raise ParseException("DIMACS", dimacs_filename, message)

    num_vars = int(split_line[2])
    num_clauses = int(split_line[3])

    #create all the vars and put them in the file
    for i in range(1, num_vars + 1):
        outsig.write(create_var_def(i))

    return num_clauses


#Return the clauses from the DIMACS file as Lambda Prolog strings
#Arguments:
#  dfile:  open DIMACS file for reading
#  dimacs_filename:  DIMACS filename for prenting error messages
#Return:  pair of (number of clauses read, list of pairs of (list int
#         lits, clause ID))
def parse_dimacs_clauses(dfile, dimacs_filename):
    line = dfile.readline()
    clause_count = 0
    clauses = []
    while line:
        #only handle non-blank, non-comment lines
        if not line.isspace() and line[0] != "c":
            clause_count += 1
            split_line = line.split()
            if split_line[-1] != "0":
                message = "Clause " + str(clause_count) + \
                    " does not end with 0"
                raise ParseException("DIMACS", dimacs_filename,
                                     message)
            #put the clause literals into a list
            clause_lits = list(map(int, split_line[:-1]))
            #build clause definition
            clauses += [(clause_lits, create_clause_id(clause_count))]
        line = dfile.readline()
    return (clause_count, clauses)




######################################################################
#                            LRAT PARSING                            #
######################################################################

#Process the LRAT file, converting its contents to Lambda Prolog
#Arguments:
#  lrat_filename:  LRAT file to read
#Return:  Lambda Prolog proof string
def process_lrat(lrat_filename):
    #check if it exists and open it
    if not os.path.exists(lrat_filename):
        raise NoFileError("LRAT", lrat_filename)
    lfile = open(lrat_filename, "r")
    #read all the lines and build a list of Lambda Prolog proof_lines
    proof_lines = []
    line = lfile.readline()
    while line:
        #only handle non-blank, non-comment lines
        if not line.isspace() and line[0] != "c":
            pline, cid = process_lrat_line(line, lrat_filename)
            #add the line to the lines if it is not blank
            if pline != "":
                proof_lines += [(pline, cid)]
        line = lfile.readline()        
    #finish
    proof = build_proof(proof_lines)
    lfile.close()
    return proof


#Process a single, non-empty LRAT line to return the proof_line
#Arguments:
#  line:  line as read from file
#  filename:  file from which the line originated
#Return:  pair of (Lambda Prolog translation, clause ID number)
def process_lrat_line(line, filename):
    split_line = line.split()
    #skip delete lines
    if split_line and split_line[1] != "d":
        clause_id = int(split_line[0])
        rest = list(map(int, split_line[1:]))
        #check we have at least the last zero
        if rest[-1] != 0:
            message = "Added clause " + str(clause_id) + \
                " is incomplete"
            raise ParseException("LRAT", filename, message)
        first_zero = rest.index(0)
        clause_lits = rest[:first_zero]
        proof_clauses = rest[first_zero + 1:-1]
        #check there were, in fact, two separate zeroes
        if proof_clauses == []:
            message = "Added clause " + str(clause_id) + \
                " is incomplete"
            raise ParseException("DIMACS", dimacs_filename, message)
        #build the proof line
        pline = build_proof_line(clause_lits, proof_clauses)
        return (pline, clause_id)
    else:
        return ("", 0)




######################################################################
#                            FRAT PARSING                            #
######################################################################

#Process the FRAT file, converting its contents to Lambda Prolog
#Arguments:
#  frat_filename:  FRAT file to read
#  original_clauses:  clauses in original problem as list of pairs
#                     (list int lits, clause ID)
#Return:  Lambda Prolog proof string
def process_frat(frat_filename, original_clauses):
    #check if it exists and open it
    if not os.path.exists(frat_filename):
        raise NoFileError("FRAT", frat_filename)
    ffile = open(frat_filename, "r")
    #read all the lines and build a list of Lambda Prolog proof_lines
    proof_lines = []
    line = ffile.readline()
    while line:
        #only handle non-blank, non-comment lines
        if not line.isspace() and line[0] != "c":
            result_code, result, cid = process_frat_line(line, frat_filename)
            #add the line to the lines if it is an add line
            if result_code == 0:
                proof_lines += [(result, cid)]
            #check an original line exists, then proof it
            elif result_code == 1:
                i = 0
                found = False
                while not found and i < len(original_clauses):
                    lits, _ = original_clauses[i]
                    if set(lits) == set(result): #same clause
                        found = True
                    i += 1
                if not found:
                    message = "Contains a nonexistent original clause"
                    raise SemanticError("FRAT", frat_filename, message)
                #add it to the proof as a new clause with the right ID
                #can't use existing clause ID because it could have
                #   been overwritten, so use no proof
                pline = build_proof_line(result, [])
                proof_lines += [(pline, cid)]
            #any other kind of line is ignored
        line = ffile.readline()
    #finish
    proof = build_proof(proof_lines)
    ffile.close()
    return proof


#Process a single, non-empty FRAT line to return the proof_line
#Arguments:
#  line:  line as read from file
#  filename:  name of file whence the line was read
#Return:  Tuple of (result code, result, clause ID number)
#         Result codes:
#            0:  add line (result is Lambda Prolog translation)
#            1:  original line (result is lits)
#            2:  other line (ignore result)
def process_frat_line(line, filename):
    split_line = line.split()
    #skip delete lines
    if split_line[0] == "a":
        clause_id = int(split_line[1])
        rest = split_line[2:]
        #check we have at least the last zero
        if rest[-1] != "0":
            message = "Added clause " + str(clause_id) + \
                " is incomplete"
            raise ParseException("FRAT", filename, message)
        first_zero = rest.index("0")
        clause_lits = list(map(int, rest[:first_zero]))
        #skip l if there
        proof_clauses = list(map(int, rest[first_zero + 2:-1]))
        #build the proof line
        pline = build_proof_line(clause_lits, proof_clauses)
        return (0, pline, clause_id)
    elif split_line[0] == "o":
        clause_id = int(split_line[1])
        lits = list(map(int, split_line[2:-1]))
        return (1, lits, clause_id)
    elif split_line[0].isdigit():
        message = "Contains a line starting with a number"
        raise SemanticError("FRAT", filename, message)
    else:
        return (2, "", 0)




######################################################################
#                            DRAT PARSING                            #
######################################################################

#Process the DRAT file, converting its contents to Lambda Prolog
#Arguments:
#  drat_filename:  DRAT file to read
#Return:  Lambda Prolog proof string
def process_drat(drat_filename):
    #check if it exists and open it
    if not os.path.exists(drat_filename):
        raise NoFileError("DRAT", drat_filename)
    dfile = open(drat_filename, "r")
    #read all the lines and build a list of Lambda Prolog proof_lines
    proof_lines = []
    line = dfile.readline()
    while line:
        #only handle non-blank, non-comment lines
        if not line.isspace() and line[0] != "c":
            pline = process_drat_line(line)
            #add the line to the lines if it is not blank
            if pline != "":
                proof_lines += [(pline, "u")]
        line = dfile.readline()        
    #finish
    proof = build_proof(proof_lines)
    dfile.close()
    return proof


#Process a single, non-empty DRAT line to return the proof_line
#Arguments:
#  line:  line as read from file
#Return:  Lambda Prolog translation (empty string for delete lines)
def process_drat_line(line):
    split_line = line.split()
    #skip delete lines
    if split_line[0] != "d":
        lits = list(map(int, split_line[0:-1]))
        #build the proof line
        pline = build_proof_line(lits, [])
        return pline
    else:
        return ""




######################################################################
#                                MAIN                                #
######################################################################

def main():
    #parse arguments
    argparser = \
        argparse.ArgumentParser(description="Convert a DIMACS file "
                                "and proof file to a Lambda Prolog "
                                "program")
    #positional arguments
    argparser.add_argument("dimacs", metavar="D", type=str,
                           help="DIMACS file to read")
    argparser.add_argument("proof", metavar="P", type=str,
                           help="proof file to read")
    argparser.add_argument("output", metavar="O", type=str,
                           help="base output name to write")
    #options
    argparser.add_argument('--force', dest='force',
                           action='store_const',
                           const=True, default=False,
                           help="force overwrite existing files")
    argparser.add_argument('--proof-type', dest='proof_type',
                           action='store', default="LRAT",
                           help="type of proof to read---LRAT, " + \
                                "FRAT, or DRAT")
    #parse arguments
    args = argparser.parse_args()
    force_overwrite = args.force

    #check args
    proof_type = args.proof_type.lower()
    if proof_type not in {"lrat", "frat", "drat"}:
        print("Unknown proof type '" + args.proof_type + "'")
        argparser.print_help()
        return -1

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
    num_original, clauses = process_dimacs(args.dimacs, outsig)
    if num_original < 0:
        outsig.close()
        outmod.close()
        return num_original

    #parse and process the proof file
    try:
        if proof_type == "lrat":
            lp_proof = process_lrat(args.proof)
        elif proof_type == "frat":
            lp_proof = process_frat(args.proof, clauses)
        else: #DRAT
            lp_proof = process_drat(args.proof)
    except Exception as e:
        print(e)
        outsig.close()
        outmod.close()
        return -1

    #build and write the module output
    string_clauses = []
    for lits, cid in clauses:
        string_clauses += [(build_clause(lits), cid)]
    proof = build_problem_name_declaration(string_clauses, lp_proof)
    outmod.write(proof)

    outsig.close()
    outmod.close()
    return 0


if __name__ == "__main__":
    exit(main())

