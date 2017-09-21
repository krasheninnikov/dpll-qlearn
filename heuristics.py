import numpy as np

# -*- coding: utf-8 -*-
def use_heuristic(heuristic_id, var_range, cdata):
    if heuristic_id == 0:
        return mostOftenVariable(var_range, cdata)

    if heuristic_id == 1:
        return mostEqulibratedVariable(var_range, cdata)

#
#
def mostOftenVariable(var_range, cdata):
    """
    mostOftenVariable(var_range, cdata.litclauses) -> variable

        - var_range: An Iterable that which returns all the possible variables

        - cdata.litclauses: A dictionary with all the clauses per literal in var_range

    Returns the variable that apears more times on the formula
    """

    best = -1
    var = 0

    for v in var_range:
        times = 0

        try:
            times += len(cdata.litclauses[v])
        except KeyError:
            pass

        try:
            times += len(cdata.litclauses[-v])
        except KeyError:
            pass

        if times > best:
            best = times
            var = v

    return var


#
#
def mostEqulibratedVariable(var_range, cdata):
    """
    mostEqulibratedVariable(var_range, cdata.litclauses) -> variable

        - var_range: An Iterable that which returns all the possible variables

        - cdata.litclauses: A dictionary with all the clauses per literal in var_range

    Returns the most equilibrated variable [ (len(var) * len(-var)) ]
    """

    var = 0
    best = -1

    for v in var_range:
        pvlen = nvlen = 0

        try:
            pvlen = len(cdata.litclauses[v])
        except KeyError:
            pass

        try:
            nvlen = len(cdata.litclauses[-v])
        except KeyError:
            pass

        eq_value = pvlen * nvlen * 1024 + pvlen + nvlen

        if eq_value > best:
            best = eq_value
            var = v

    return var
