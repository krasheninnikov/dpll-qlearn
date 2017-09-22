#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dp
import dpll #TODO redo the algorithm
import gsat
import wgsat
import gwsat
import wgwsat
import argparse
import datautil
import traceback
import heuristics

__version__='0.4'
__license__='GPL'
__authors__=['Marc Piñol Pueyo <mpp5@alumnes.udl.cat>',
            'Josep Pon Farreny <jpf2@alumnes.udl.cat>']

__description__='FanSATstic v%s' % __version__

# List of possible algorithms
GSAT = 'gsat'
GWSAT = 'gwsat'
local_search_algs = [GSAT, GWSAT]

DAVIS_PUTNAM = 'dp'
DPLL = 'dpll'
systematic_search_algs = [DAVIS_PUTNAM, DPLL]

# Variable selection heuristics
MOST_OFTEN = 'most_often'
MOST_EQUILIBRATED = 'most_equilibrated'
MOM = 'mom'
JWOS = 'jwos'
JWTS = 'jwts'
DLCS = 'dlcs'
DLIS = 'dlis'
var_selection_heuristics = { 
                    MOST_OFTEN : heuristics.mostOftenVariable,
                    MOST_EQUILIBRATED : heuristics.mostEqulibratedVariable,
                    MOM : heuristics.mom,
                    JWOS : heuristics.jwOS,
                    JWTS : heuristics.jwTS,
                    DLCS : heuristics.dlcs,
                    DLIS : heuristics.dlis  
                                }

# Some output formats
SATISFIABLE_OUT = "s SATISFIABLE"
UNSATISFIABLE_OUT = "s UNSATISFIABLE"

#
#
def main(options):
    """
    Main(options): void
    """
    if isLocalSearch(options.algorithm):
        executeLocalSearchAlgorithm(options)

    elif isSystematicSearch(options.algorithm):
        executeSystematicSearchAlgorithm(options)

    else:
        print 'Unknown algorithm'   # This should never be printed if the argparser works well


################
#              #
# LOCAL SEARCH #
#              #
################

#
#
def executeLocalSearchAlgorithm(options):
    """
    Execute the specified algorithm and prints the result
    """

    try:
        num_vars, clauses = datautil.parseCNF(options.file)
        comments = ''

        # Chose and run algorithm
        res = None
        if GSAT == options.algorithm.lower():

            if options.weighted:
                comments += 'Solved With: Weighted GSAT'
                res = wgsat.solve(num_vars, clauses, len(clauses)//2)
            else:
                comments += 'Solved With: GSAT'
                res = gsat.solve(num_vars, clauses, len(clauses)//2)

        elif GWSAT == options.algorithm.lower():

            if options.weighted:
                comments += 'Solved With: Weighted GWSAT'
                res = wgwsat.solve(num_vars, clauses, len(clauses)//2, 0.4)
            else:
                comments += 'Solved With: GWSAT'
                res = gwsat.solve(num_vars, clauses, len(clauses)//2, 0.35)
        else:
            raise Exception('Unspecified algorithm')

        # If the formula it is not satisfiable this lines are never executed
        del res[0]
        printComments(comments)
        print formatLocalSearchResult(res)

    except Exception, e:
        traceback.print_exc()
        print '%s: %s' % (e.__class__.__name__, str(e))

#
#
def formatLocalSearchResult(bool_result):
    """
    formatLocalSearchResult(bool_result) -> string

        - bool_result: iterable with the truth value assignation in order

    f.e [True, False, False] has as output:

    s SATISFIABLE
    v 1 -2 -3
    """
    out = '%s\nv' % SATISFIABLE_OUT 
    
    for ind,b in enumerate(bool_result):
        if b:
            out += ' %d' % (ind+1)
        else:
            out += ' %d' % (-(ind+1) )
    return out


#####################
#                   #
# SYSTEMATIC SEARCH #
#                   #
#####################

#
#
def executeSystematicSearchAlgorithm(options):
    """
    Execute the specified algorthim and prints the result
    """

    try:
        num_vars, clauses = datautil.parseCNF(options.file)
        comments = ''
        res = None
        
        if DAVIS_PUTNAM == options.algorithm.lower():
            comments += 'Using DP algorithm (The orignal DP not DPLL)\n'
            comments += 'The DP algorithm do not give a prove of satisfiablity\n'
            comments += 'If the formula is unsatisfiable, the algorithm gives ' \
                        'you a core'

            res = dp.solve(num_vars, clauses,
                           var_selection_heuristics[options.vselection])
             
                
        elif DPLL == options.algorithm.lower():
            comments += 'Using DPLL algorithm\n'
            res = dpll.solve(num_vars, clauses,
                             var_selection_heuristics[options.vselection])
                           
        printComments(comments)
        print formatSystematicSearchResult(res)
                    
    except Exception, e:
        traceback.print_exc()
        print '%s: %s' % (e.__class__.__name__, str(e))

#
#
def formatSystematicSearchResult(result):
    """
    formatSystematicSearchResult(result) -> string

        - result: tuple with two elements
            result[0]: True/False = SATISFIABLE/UNSATISFIABLE
            result[1]: It depens on the value of result[0]
                        True: iterable with the truth value assignation in order
                        False: iterable with the core clauses

    f.e (True, [True, False, False]) has as output:

    s SATISFIABLE
    v 1 -2 -3

    f.e (False, ( [1, 2], [-1, 2], [1, -2], [-1, -2] ) ) has as output:

    s UNSATISFIABLE
    1 2 0
    -1 2 0
    1 -2 0
    -1 -2 0
    """

    sat, prove = result

    if sat:
        del prove[0]
        return formatLocalSearchResult(prove)

    else:
        core = []
        biggest_var = 0

        for c in prove:
            core.append(' '.join( map( lambda x: str(x), c) ) + ' 0')
            for l in c:
                biggest_var = max( biggest_var, abs(l) )

        return '%s\np cnf %d %d\n%s' % (UNSATISFIABLE_OUT, biggest_var,
                                        len(prove), '\n'.join(core) )


#############
#           #
# UTILITIES #
#           #
#############

#
#
def isSystematicSearch(alg):
    """
    Returns true if the algorithm is one of the local search list
    """
    return alg.lower() in systematic_search_algs

#
#
def isLocalSearch(alg):
    """
    Returns true if the algorithm is one of the local search list
    """
    return alg.lower() in local_search_algs

#
#
def printComments(comments):
    """
    Prints all the comment lines followed by the comment character
    """
    for comment in comments.splitlines():
        print 'c', comment


#######################
#                     #
# Program entry point #
#                     #
#######################

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description=__description__)

    parser.add_argument('-f', '--file', action='store', default="",
                    required=True, help='Path to a cnf file')

    parser.add_argument('-a', '--algorithm', action='store', default="",
                    choices=local_search_algs + systematic_search_algs,
                    required=True, help='Specifies which algorithm use to '
                                        'solve the formula')

    parser.add_argument('-vsh', '--vselection', action='store',
                        default=MOST_OFTEN,
                        choices=var_selection_heuristics.keys(),
                        help='Specfies the variable selection heuristic.'
                        'These heuristics are used only in the systematic '
                        'search algorithms. DEFAULT = %s' % MOST_OFTEN)

    parser.add_argument('-w', '--weighted', action='store_true',
                    default=False,
                    help='Uses a weighted version of the algorithms (If exists)')

    options = parser.parse_args()

    main(options)