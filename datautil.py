# -*- coding: utf-8 -*

import sys

#
#
def parseCNF(fname):
    """
    Parses the specified dimacs cnf file
    
    Returns: 
        - num_variables: Number of variables
        
        - clauses: All the clauses into a set of frozensets
                    
    """
    num_vars = 0
    clauses = set()

    cnf_file = open(fname, 'r')    
    
    try:
        for nline, line in enumerate(cnf_file):
            lvalues = line.strip().split()
            
            if not lvalues or lvalues[0] == 'c':
                continue
            
            elif lvalues[0] == 'p':
                if lvalues[1] != 'cnf':
                    raise SyntaxError('Invalid format identifier "%s".'
                                % ( lvalues[1]) )
                             
                num_vars = int(lvalues[2])
                #num_clauses = int(lvalues[3])                
                
            else:
                values = map(int, lvalues)                    
                clause = set()
                
                for lit in values:
                    if lit == 0:
                        if clause not in clauses:                        
                        
                            clause = frozenset(clause)
                            clauses.add( clause )

                        clause = None # Check line ends with 0
                        
                    else:
                        clause.add(lit)

                        if lit < -num_vars or lit > num_vars:
                            raise SyntaxError('Invalid literal %d '
                                ', it must be in range [1, %d].'
                                % (lit, num_vars) )

                if clause:
                    raise SyntaxError('Not found the trailing 0')
                
    except SyntaxError, e:
        sys.stderr.write('Error parsing file "%s" (%d): %s\n' % 
                                    (fname, nline, str(e)) )
        raise e
            
    return num_vars, clauses

#
#
def classifyClausesByVariable(num_vars, clauses):
    """
    Returns a list, sorted by variable value, that at each position contains
    a set with all the clauses where the variable appears
    
    For example to traverse all the clauses where appears the variable 
          2 and -2, simply do:
              
              for clause in litclauses[2]:
                  ... Lots of good code ...
    """
    
    litclauses = [set() for _ in xrange(num_vars+1)]
    
    for clause in clauses:
        for l in clause:
            alit = abs(l)
            litclauses[alit].add(clause)
            
    return litclauses

#
#
def classifyClausesByLiteral(clauses):
    """
    Returns a dictionary that for each literal of the formula contains a set
    with all the clauses where the literal appears
    
    For example to traverse all the clauses where appears the variable 
    2, simply do:
        
        for clause in litclauses[2]:
            ... Lots of good code ...
                  
    And for traverse all the clauses where appears the variable -2, do:
        
        for clause in litclauses[-2]:
            ... Lots of good code ...    
    """
    
    litclauses = {}
    
    for clause in clauses:
        for l in clause:
            if not litclauses.has_key(l):
                litclauses[l] = set()
                
            litclauses[l].add(clause)
            
    return litclauses
    
#
#
def isPureLiteral(lit, litclauses):
    """
    isPureLiteral(lit, litclauses)    
    
    - lit: literal value, f.e: -1, 1, 3, -2, ...
    - litclauses: Dictionary returned by classifyClausesByLiteral(...)    
    
    Returns true if the specified lit is a pure literal
    """
    return litclauses.has_key(lit) and not litclauses.has_key(-lit)