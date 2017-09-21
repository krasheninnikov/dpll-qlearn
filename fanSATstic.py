#!/usr/bin/env python
# -*- coding: utf-8 -*-
import dpll #TODO redo the algorithm
import argparse
import datautil
import traceback
import heuristics
import numpy as np
from rl_agent import ReplayBuf, Estimator, make_state



__version__='0.4'
__license__='GPL'
__authors__=['Marc Piñol Pueyo <mpp5@alumnes.udl.cat>',
            'Josep Pon Farreny <jpf2@alumnes.udl.cat>']

__description__='FanSATstic v%s' % __version__

# List of possible algorithms
DPLL = 'dpll'
systematic_search_algs = [DPLL]

# Variable selection heuristics
MOST_OFTEN = 'most_often'
MOST_EQUILIBRATED = 'most_equilibrated'
var_selection_heuristics = {
                    MOST_OFTEN : heuristics.mostOftenVariable,
                    MOST_EQUILIBRATED : heuristics.mostEqulibratedVariable
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
    if isSystematicSearch(options.algorithm):
        executeSystematicSearchAlgorithm(options)

    else:
        print 'Unknown algorithm'   # This should never be printed if the argparser works well


def automatic_heuristic(var_range, cdata):

    s = make_state(var_range, cdata)
    print(s)
    #heuristic_id = estimator.policy_eps_greedy(eps, s)
    heuristic_id = 0
    replay_buf.append_s_a_r(s, heuristic_id, -1)

    return heuristics.use_heuristic(heuristic_id, var_range, cdata)


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


def executeSystematicSearchAlgorithm(options):
    """
    Execute the specified algorthim and prints the result
    """

    try:
        num_vars, clauses = datautil.parseCNF(options.file)
        comments = ''
        res = None

        run_stats = RunStats()

        global replay_buf
        replay_buf = ReplayBuf(5000, 7, 2)


        res = dpll.solve(num_vars, clauses,
                         automatic_heuristic,
                         run_stats)
        if res[0]:
            print(run_stats.n_splits)

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
def printComments(comments):
    """
    Prints all the comment lines followed by the comment character
    """
    for comment in comments.splitlines():
        print 'c', comment


class RunStats(object):
    def __init__(self):
        self.n_splits = 0

    def add_split(self):
        self.n_splits += 1

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
                    choices=systematic_search_algs,
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
