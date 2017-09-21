# -*- coding: utf-8 -*-

import random

#
#
def getRandomAssignation():
    """
    getRandomAssignation(): boolean
    
    Returns a random truth value (True, False)
    """
    return random.choice((True, False))

#
#
def isClauseSatisfied(clause, interpretation):
    """
    isClauseSatisfied(clause:iterable(int),
                      interpretation:iterable(boolean)): boolean

    Returns true if the given clause is satisfied by the specified
    interpretation
    """
    for lit in clause:
        if interpretation[lit] if lit > 0 else not interpretation[-lit]:
            return True
    return False

#
#
def satisfies(clauses, interpretation):
    """
    Satisfies(interpretation: [boolean]): boolean

    Check if an interpretation satisfies this formula
    """
    for clause in clauses:
        if not isClauseSatisfied(clause, interpretation):
            return False
    return True

#
#
def numSatisfiedClauses(clauses, interpretation):
    """
    NumSatisfiedClauses(clauses: [], interpretation: [boolean]): int

    Count all the satisfied clauses with the given interpretation
    """
    return sum(1 for c in clauses if isClauseSatisfied(c, interpretation))

#
#
def numSatisfiedWeightedClauses(clauses, interpretation, weights):
    """
    NumSatisfiedClauses(clauses: [], interpretation: [boolean],
                                                     weights: {clause:int}): int

    When a clause is satisfied increments the weight of that clause
    """
    return sum(weights[c] for c in clauses \
                                        if isClauseSatisfied(c, interpretation))
            
#
#
def numSatisfiedLiterals(clause, interpretation):
    """
    Counts the number of satisfied literals with the given interpretation
    
    Return the number of satisfied literals
    """
    satlits = 0
    
    for lit in clause:
        var = abs(lit)
        if (interpretation[var] and lit > 0) or \
            (not interpretation[var] and lit < 0):
            satlits += 1
            
    return satlits
    
#
#
def isTautology(clause):  
    """
    Returns true if the specified clause is a tautology, false otherwise
    """
    for l in clause:
        if -l in clause:
            return True
    return False
#
#
def removeTautologies(clauses):
    """
    Remove all the clauses that are tautologies from the given list/set of 
    clauses
    """
    tautologies = set()    
    
    for c in clauses:
        if isTautology(c):
            tautologies.add(c)
            break
            
    for c in tautologies:
        clauses.remove(c)