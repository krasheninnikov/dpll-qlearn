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


class RunStats(object):
    def __init__(self):
        self.n_episodes = 0
        self.n_splits = 0
        self.episode_stats = []


    def finish_episode(self):
        self.episode_stats.append(self.n_splits)
        self.n_splits = 0
        self.n_episodes += 1

    def add_split(self):
        self.n_splits += 1


def main(options):
    global state_list
    state_list = []

    n_restarts = 1
    for restart in range(n_restarts):
        np.random.seed(restart)

        global replay_buf
        global q_l_agent
        global epsilon
        replay_buf = ReplayBuf(10000, 13, n_actions=4)
        q_l_agent = Estimator(replay_buf)
        run_stats = RunStats()

        n_episodes = 200
        epsilon = 1
        for i in range(n_episodes):


            epsilon = epsilon*0.97
            q_l_agent.train(discount_factor = 0.999, replay_buf = replay_buf)


            num_vars, clauses = datautil.parseCNF(options.file)
            res = None
            res = dpll.solve(num_vars,
                             clauses,
                             automatic_heuristic,
                             run_stats)
            #if res[0]:
            print("Ep {}  done in {} splits".format(i, run_stats.n_splits ))

            replay_buf.game_over()

            #if i>100:
            #    if run_stats.n_splits > 70:
                #np.percentile(np.asarray(run_stats.episode_stats), 40):
            #        replay_buf.reset_index_back_by_n(run_stats.n_splits)
            run_stats.finish_episode()

        #np.save("run_stats/run_stats"+str(restart),
        #            np.asarray(run_stats.episode_stats),
        #            allow_pickle=True, fix_imports=True)

    #np.save("state_var/state_list",
    #            np.asarray(state_list),
    #            allow_pickle=True, fix_imports=True)


        #print formatSystematicSearchResult(res)


def automatic_heuristic(var_range, cdata):

    s = make_state(var_range, cdata)

    state_list.append(s)

    action_probs = q_l_agent.policy_eps_greedy(epsilon, s)
    heuristic_id = np.random.choice(np.arange(len(action_probs)), p=action_probs)
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

    parser.add_argument('-vsh', '--vselection', action='store',
                        default=MOST_OFTEN,
                        choices=var_selection_heuristics.keys(),
                        help='Specfies the variable selection heuristic.'
                        'These heuristics are used only in the systematic '
                        'search algorithms. DEFAULT = %s' % MOST_OFTEN)

    options = parser.parse_args()

    main(options)
