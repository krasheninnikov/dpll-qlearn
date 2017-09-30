# -*- coding: utf-8 -*-
import numpy as np
import satutil
import datautil
import collections

# Contains clause information
ClausesData = collections.namedtuple('ClausesData',
                                     'clauses ctimes litclauses')

# Contains clause changes (removed and modified)
ClausesChanges = collections.namedtuple('ClausesChanges',
                                        'rclauses mclauses')


#
#
def solve(num_variables, clauses, selection_heuristic, run_stats):
    """
    Uses the dpll algorithm to determine if the formula is satisfiable or
    unsatisfiable

    Returns a tuple with the following formats:
        - If the formula is satisfiable
            (True, [None, truth_value1, truth_vaue2, ...] )
        - If the formula is unsatisfiable
            (False, frozenset() )
    """

    # Dictionary with clauses classified by literals
    litclauses = datautil.classifyClausesByLiteral(clauses)

    # Amount of times each clause appears in the formula.
    # At the beginning every clause appears only once but after some
    # branching some clauses can appear more than once
    ctimes = { c : 1 for c in clauses }

    # We use an struct to have less parameters
    cdata = ClausesData(clauses, ctimes, litclauses)

    variables, interpretation = getVarsAndFirstIntp(num_variables, cdata)

    return _solve(variables, cdata, interpretation, selection_heuristic, run_stats)


#
#
def _solve(variables, cdata, interpretation, heuristic, run_stats):
    """
    DPLL recursive implementation

    Performs the following steps:
        - Checks if a valid interpretation has been found
        - Unit Propagation
            - Restore data if empty clause was found
        - Checks if the formula has been solved by unit propagation
        - Pure Literal
        - Checks if the formula has been solved by pure literal

    """
    # Solved by previous assignation
    if not cdata.clauses:
        return (True, interpretation)

    # D.structures used to store unit propagation and pure literal changes
    used_vars = set()
    cchanges = ClausesChanges(set(), [])

    # Performs unit propagation
    if unitPropagation(variables, cdata, interpretation, used_vars, cchanges):

        # Recover state of unitPropagation
        variables.update(used_vars)
        undoClauseChanges(cdata, cchanges)

        return (False, frozenset())

    # Solved by unitPropagation
    if not cdata.clauses:
        return (True, interpretation)

    # Propagate pure literals
    pureLiteral(variables, cdata, interpretation, used_vars, cchanges)

    # Solved by pureLiteral
    if not cdata.clauses:
        return (True, interpretation)

    # select variable to explore
    var = heuristic(variables, cdata)

    used_vars.add(var)
    variables.remove(var)

    run_stats.add_split()

    # Recursive Call, internally recovers state between branches
    # if the return value of a branch is unsatisfiable
    res =  dpllBranch(var, variables, cdata, interpretation, heuristic, run_stats)

    # Recover Unit Propagatin and Pure Literal changes
    if not res[0]:
        variables.update(used_vars)
        undoClauseChanges(cdata, cchanges)

    return res


#
#
def dpllBranch(var, variables, cdata, interpretation, heuristic, run_stats):

    """
    Explore all the search space with var = True and var = False until
    a solution or empty clause are found
    """
    nvar = -var
    br_cchanges = ClausesChanges(set(), [])

    # Truth value for var = True
    interpretation[var] = True
    if not removeLiteralFromClauses(nvar, cdata, br_cchanges):
        removeClausesWithLiteral(var, cdata, br_cchanges)
        res = _solve(variables, cdata, interpretation, heuristic, run_stats)

        # Solution found. Do not undo changes
        if res[0]:
            return res

    undoClauseChanges(cdata, br_cchanges)
    br_cchanges = ClausesChanges(set(), [])

    # Truth value for var = False
    interpretation[var] = False
    if not removeLiteralFromClauses(var, cdata, br_cchanges):
        removeClausesWithLiteral(nvar, cdata, br_cchanges)
        res = _solve(variables, cdata, interpretation, heuristic, run_stats)

        # Solution found. Do not undo changes
        if res[0]:

            return res

    undoClauseChanges(cdata, br_cchanges)

    # Both assignations have failed
    return (False, frozenset())

#
#
def unitPropagation(variables, cdata, interpretation, used_vars, cchanges):
    """
    Search for clauses with only one literal and then remove the unnecessary
    information

    This is an special version for DPLL that logs all the changes

    Returns True as soon as an emtpy clause is reached, False otherwise
    """

    unit_lits = [iter(c).next() for c in cdata.clauses if len(c) == 1]

    while unit_lits:
        lit = unit_lits.pop()

        removeClausesWithLiteral(lit, cdata, cchanges)

        # If removing the literal from the other clauses, appears an empty
        # clause then returns false
        if cdata.litclauses.has_key(-lit):
            if removeLiteralFromClauses(-lit, cdata, cchanges):
                return True

        # Remove te used variable
        var = abs(lit)
        variables.remove(var)
        used_vars.add(var)

        # Save interpretation
        interpretation[var] = lit > 0

        # Check if the last propagations generated more unit clauses
        if not unit_lits:
            unit_lits = [iter(c).next() for c in cdata.clauses if len(c) == 1]

    return False

#
#
def pureLiteral(variables, cdata, interpretation, used_vars, cchanges):
    """
    Search for pure literals and then remove the unnecessary information and
    logs all the changes
    """

    # Fill pure_lits with all the pure literals in the formula
    pure_lits = set()

    for v in variables:
        if datautil.isPureLiteral(v, cdata.litclauses):
            pure_lits.add(v)
        elif datautil.isPureLiteral(-v, cdata.litclauses):
            pure_lits.add(-v)

    # Remove clauses with pure lits
    while pure_lits:
        pl = pure_lits.pop()
        var = abs(pl)
        variables.remove(var)
        used_vars.add(var)

        # Save interpretation
        interpretation[var] = pl > 0

        # This comprovation avoids an exception when a clause have more than
        # one pure literal (otherwise the algorithm tries to delete it twice)
        if cdata.litclauses.has_key(pl):
            removeClausesWithLiteral(pl, cdata, cchanges)

        # Check if the last propagations genereted more pure literals
        if not pure_lits:
            for v in variables:
                if datautil.isPureLiteral(v, cdata.litclauses):
                    pure_lits.add(v)
                elif datautil.isPureLiteral(-v, cdata.litclauses):
                    pure_lits.add(-v)


#
#
def removeClausesWithLiteral(lit, cdata, cchanges):
    """
    Remove all the clauses with the specified literal and logs the changes
    """

    for clause in cdata.litclauses[lit]:
        # Record clause deletion
        cchanges.rclauses.add( (clause, cdata.ctimes[clause]) )

        # Remove clause
        cdata.clauses.remove(clause)
        cdata.ctimes[clause] = 0

        # Remove the clause from literal's local sets
        for l in clause:
            if l != lit:
                lset = cdata.litclauses[l]
                lset.remove(clause)
                # If empty set for literal l remove its local set
                if not lset:
                    del cdata.litclauses[l]

    del cdata.litclauses[lit]

#
#
def removeLiteralFromClauses(lit, cdata, cchanges):
    """
    Remove the specified literal from all the clauses it belongs to and
    logs the changes
    """
    for clause in cdata.litclauses[lit]:
        nc = frozenset([x for x in clause if x != lit])

        if not nc:
            return True

        # Record clause modification
        cchanges.mclauses.append( (nc, clause, cdata.ctimes[clause]) )

        # Delete clause
        cdata.clauses.remove(clause)
        cdata.clauses.add(nc)

        # Update times
        cdata.ctimes[clause] = 0
        try:
            cdata.ctimes[nc] += 1
        except KeyError:
            cdata.ctimes[nc] = 1

        # Update clause on literal's local sets
        for l in nc:
            lset = cdata.litclauses[l]
            lset.remove(clause)
            lset.add(nc)

    del cdata.litclauses[lit]

    return False

#
#
def undoClauseChanges(cdata, cchanges):
    readdRemovedClauses(cdata, cchanges)
    undoModifiedClauses(cdata, cchanges)

#
#
def readdRemovedClauses(cdata, cchanges):
    """
    Add all the clauses removed on a previous call to removeClausesWithLiteral
    """
    for clause, t in cchanges.rclauses:
        cdata.clauses.add(clause)
        cdata.ctimes[clause] = t

        for l in clause:
            if not cdata.litclauses.has_key(l):
                cdata.litclauses[l] = set()
            cdata.litclauses[l].add(clause)

#
#
def undoModifiedClauses(cdata, cchanges):
    """
    Undo all the modifications performed by removeLiteralFromClauses
    """

    # Traverse the list of modifications in reverse order
    for nclause, clause, t in reversed(cchanges.mclauses):

        # Remove the current clause if only appears once
        # In other words, only have one parent clause
        cdata.ctimes[nclause] -= 1
        if cdata.ctimes[nclause] == 0:
            cdata.clauses.remove(nclause)

        # Add the old clause
        cdata.clauses.add(clause)
        cdata.ctimes[clause] = t

        for l in clause:
            # Add literal set of clauses and the old clause
            if not cdata.litclauses.has_key(l):
                cdata.litclauses[l] = set()
                cdata.litclauses[l].add(clause)

            # Remove the newest clause if necessary and add the old one
            else:
                lset = cdata.litclauses[l]
                if cdata.ctimes[nclause] == 0 and nclause in lset:
                    lset.remove(nclause)
                lset.add(clause)

#
#
def getVarsAndFirstIntp(num_variables, cdata):
    # Generates a list with variables to be assigned and an initial interpretation
    variables = set()
    interpretation = [None]
    for v in xrange(1, num_variables+1):
        if cdata.litclauses.has_key(v) or cdata.litclauses.has_key(-v):
            variables.add(v)
            interpretation.append(None)
        else:
            interpretation.append(satutil.getRandomAssignation())

    return variables, interpretation
