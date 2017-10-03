import numpy as np

# -*- coding: utf-8 -*-
def use_heuristic(heuristic_id, var_range, cdata):


    if heuristic_id == 0:
        return jwOS(var_range, cdata)

    if heuristic_id == 1:
        return mom(var_range, cdata)

    if heuristic_id == 2:
        return mostOftenVariable(var_range, cdata)

    if heuristic_id == 3:
        return dlcs(var_range, cdata)

    if heuristic_id == 4:
        return jwTS(var_range, cdata)

    if heuristic_id == 5:
        return mom(var_range, cdata)

    if heuristic_id == 6:
        return dlis(var_range, cdata)
#
#
def mostOftenVariable(var_range, cdata):
    """
    mostOftenVariable(var_range, cdata.cdata.litclauses) -> variable

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



def mom(var_range, cdata):
    """
    mom(var_range, litclauses) -> variable

        - var_range: An Iterable that which returns all the possible variables

        - litclauses: A dictionary with all the clauses per literal in var_range

    Returns the variable that appears most often in the smallest clauses, and favours
    balanced variables
    """

    k = 10  #tuneable parameter

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

        mom_value = pvlen * nvlen + 2**k * (pvlen + nvlen)

        if mom_value > best:
            best = mom_value
            var = v

    return var

#
#
def jwOS(var_range, cdata):
    """
    jwOS(var_range, cdata.litclauses) -> variable

        - var_range: An Iterable that which returns all the possible variables

        - cdata.litclauses: A dictionary with all the clauses per literal in var_range

    Returns the variable with the highest One sided Jeroslow-Wang factor
    """


    var = 0
    best = -1

    for v in var_range:
        j_value = 0

        try:
            vpos_clauses = cdata.litclauses[v]
            for clause in vpos_clauses:
                j_value += 2**(-len(clause))
        except KeyError:
            pass

        try:
            vneg_clauses = cdata.litclauses[-v]
            for clause in vneg_clauses:
                j_value += 2**(-len(clause))
        except KeyError:
            pass

        if j_value > best:
            best = j_value
            var = v

    return var

#
#
def jwTS(var_range, cdata):
    """
    jwTS(var_range, cdata.litclauses) -> variable

        - var_range: An Iterable that which returns all the possible variables

        - cdata.litclauses: A dictionary with all the clauses per literal in var_range

    Returns the variable with the highest Two sided Jeroslow-Wang factor
    """


    var = 0
    best = -1

    for v in var_range:
        jpos_value = jneg_value = 0

        try:
            vpos_clauses = cdata.litclauses[v]
            for pos_clause in vpos_clauses:
                jpos_value += 2**(-len(pos_clause))
        except KeyError:
            pass

        try:
            vneg_clauses = cdata.litclauses[-v]
            for neg_clause in vneg_clauses:
                jneg_value += 2**(-len(neg_clause))
        except KeyError:
            pass

        j_value = jpos_value + jneg_value

        if j_value > best:
            best = j_value
            if jneg_value > jpos_value:
                var = -v
            else:
                var = v

    return var

#
#
def dlcs(var_range, cdata):
    """
    dlcs(var_range, cdata.litclauses) -> variable

        - var_range: An Iterable that which returns all the possible variables

        - cdata.litclauses: A dictionary with all the clauses per literal in var_range

    Returns the variable that apears most often in both polarities and chooses the
    polarity that occurs most
    """

    best = -1
    var = 0

    for v in var_range:
        times = vp = vn = 0


        try:
            vp = len(cdata.litclauses[v])
            times += vp
        except KeyError:
            pass

        try:
            vn = len(cdata.litclauses[-v])
            times += vn
        except KeyError:
            pass

        if times > best:
            best = times
            if vp >= vn:
                var = v
            else:
                var = -v

    return var

#
#
def dlis(var_range, cdata):
    """
    dlis(var_range, cdata.litclauses) -> variable

        - var_range: An Iterable that which returns all the possible variables

        - cdata.litclauses: A dictionary with all the clauses per literal in var_range

    Returns the literal that occurs most
    """

    best = -1
    var = 0

    for v in var_range:
        times = 0
        pvlen = nvlen = 0

        try:
            pvlen = len(cdata.litclauses[v])
            if pvlen > best:
                best = pvlen
                var = v
        except KeyError:
            pass

        try:
            nvlen = len(cdata.litclauses[-v])
            if nvlen > best:
                best = nvlen
                var = -v
        except KeyError:
            pass

    return var
