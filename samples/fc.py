'''
Two-stages fuzzy compromise approach for multi-objectives linear programming problems.

李学全,李辉;多目标线性规划的模糊折衷算法[J];中南大学学报(自然科学版);2004年03期
'''

import logging
from typing import (List, Union)
import pulp


class MOModel:
    def __init__(self, objectives:List[pulp.LpAffineExpression],
                    constraints:List[pulp.LpConstraint]=None) -> None:
        '''Multiple objectives model based on `pulp`, including variables, objectives and constraints.

        Args:
            objectives (list): objective functions list. NOTE: minimize each component.
            constraints (list): constraints list.
            kwargs (dict): solving parameters, e.g., solver name, rel_gap.
        '''
        self.objectives = objectives or []
        self.constrains = constraints or []

    @property
    def objective_values(self):
        return [obj.value() for obj in self.objectives]

    def membership_function(self, objs:List[Union[float, pulp.LpAffineExpression]],
                                min_range:list, max_range:list):
        '''The membership function is interpreted as the fuzzy value of the decision maker,
        which describes the behavior of indifference, preference or aversion toward uncertainty.
        In solving fuzzy mathematical programming problems, a linear membership function defined
        by two points, the upper and lower levels of acceptability is used because of its simplicity.
        '''
        return [1/(u-l) * (x-l) for l,u,x in zip(min_range, max_range, objs)]

    def solve(self):
        '''Solve multiple objectives linear programming problem with two stages fuzzy compromise approach.'''
        # stage 0: membership functions
        logging.info('(FC-1) Solving the lower and upper bounds of each objective...')
        min_range, max_range = self._solve_lower_and_upper_ranges()
        memberships = self.membership_function(self.objectives, min_range, max_range)

        # stage 1: minimize the maximum component
        logging.info('(FC-2) Minimizing the maximum component of objectives...')
        self.solve_stage_1(memberships=memberships)

        # stage 2: minimize sum of all components by taking stage 1 results as a baseline
        logging.info('(FC-3) Minimizing the sum of all objectives...')
        m0 = self.membership_function(self.objective_values, min_range, max_range)
        self.solve_stage_2(m0=m0, memberships=memberships)

    def solve_stage_1(self, memberships:List[pulp.LpAffineExpression]):
        '''Stage 1: minimize the maximum component of membership functions.'''
        # new temp variable
        x = pulp.LpVariable(name='lambda', lowBound=0, upBound=1)

        # the maximum component
        lower_cons = [x>=m for m in memberships]
        cons = self.constrains + lower_cons

        # solve problem
        return self._solve_single_objective_problem(name='stage_1', obj=x, cons=cons)

    def solve_stage_2(self, m0:List[float], memberships:List[pulp.LpAffineExpression]):
        '''Stage 2: minimize the sum of all membership function components.'''
        # new temp variables
        X = [pulp.LpVariable(name=f'lambda_{i}', lowBound=0) for i in range(len(self.objectives))]

        # optimize the bounds further
        upper_cons = [x<=m for x,m in zip(X,m0)] # upper bound of each component
        lower_cons = [x>=m for x,m in zip(X,memberships)] # lower bound of each component
        cons = self.constrains + lower_cons + upper_cons

        # solve problem
        return self._solve_single_objective_problem(name='stage_2', obj=pulp.lpSum(X), cons=cons)

    def _solve_lower_and_upper_ranges(self):
        '''Calculate lower and upper ranges by solving single objective optimization for each objective component.'''
        min_range, max_range = [], []
        for i,obj in enumerate(self.objectives):
            # check or calculate lower range
            res = obj.lowBound if hasattr(obj, 'lowBound') else None
            if res is None:
                p = self._solve_single_objective_problem(name=f'solve_lower_range_{i}', obj=obj, cons=self.constrains)
                res = p.objective.value()
            min_range.append(res)

            # check or calculate upper range
            res = obj.upBound if hasattr(obj, 'upBound') else None
            if res is None:
                p = self._solve_single_objective_problem(name=f'solve_upper_range_{i}', obj=-obj, cons=self.constrains)
                res = -p.objective.value()
            max_range.append(res)
        return min_range, max_range

    def _solve_single_objective_problem(self, name:str, obj:pulp.LpAffineExpression,
        cons:List[pulp.LpConstraint]) -> pulp.LpProblem:
        # problem
        prob = pulp.LpProblem(name=name, sense=pulp.LpMinimize)

        # objective and constraints
        prob += obj
        for c in cons: prob += c

        # solve
        status = prob.solve()
        assert status==1, f'Problem {name}: {pulp.LpStatus[status]} solution found.'
        return prob


if __name__=='__main__':

    # variables
    x = [pulp.LpVariable(name=f'x_{i+1}', lowBound=0) for i in range(4)]

    # objectives
    A = [
        [-2, -5, -7, -1],
        [-4, -1, -3, -11],
        [-9, -3, -1, -2],
        [1.5, 2, 0.3, 3],
        [0.5, 1, 0.7, 2]
    ]
    objs = [pulp.lpDot(x, a) for a in A]

    # constraints
    cons = [pulp.lpDot(x, [3, 4.5, 1.5, 7.5])==150]

    # solve
    m = MOModel(objectives=objs, constraints=cons)
    m.solve()

    # results
    print([t.value() for t in x])
