#!/usr/bin/python

import numpy as np
from tronproblem import *
from trontypes import CellType, PowerupType
import random, math

# Throughout this file, ASP means adversarial search problem.


class StudentBot:
    """ Write your student bot here"""

    def decide(self, asp):
        """
        Input: asp, a TronProblem
        Output: A direction in {'U','D','L','R'}

        To get started, you can get the current
        state by calling asp.get_start_state()
        """
        return "U"

    def cleanup(self):
        """
        Input: None
        Output: None

        This function will be called in between
        games during grading. You can use it
        to reset any variables your bot uses during the game
        (for example, you could use this function to reset a
        turns_elapsed counter to zero). If you don't need it,
        feel free to leave it as "pass"
        """
        pass

    def alpha_beta_cutoff(asp, cutoff_ply):

        def max_value(asp, state, a, b, cutoff_ply, player):
            if asp.is_terminal_state(state):
                return TronStateInfo(state)

            if cutoff_ply == 0:
                return TronStateInfo(state)

            actions = asp.get_available_actions(state)
            cur_max = None
            for action in actions:
                next_state_info = min_value(asp, asp.transition(state, action), a, b, cutoff_ply - 1, player)
                if not cur_max:
                    cur_max = next_state_info

                cmp_result = cur_max.cmp(next_state_info)
                if cmp_result[player] == -1:
                    cur_max = next_state_info
                else if cmp_result[player] == 0:
                    if cmp_result[1 - player] == 1:
                        cur_max = next_state_info

                if cur_max.cmp(b)[player] == 1:
                    return cur_max
                if cur_max.cmp(a)[player] == 1:
                    a = cur_max

            return cur_max

        def min_value(asp, state, a, b, cutoff_ply, player):
            if asp.is_terminal_state(state):
                return TronStateInfo(state)

            if cutoff_ply == 0:
                return TronStateInfo(state)

            actions = asp.get_available_actions(state)
            cur_min = None
            for action in actions:
                next_state_info = max_value(asp, asp.transition(state, action), a, b, cutoff_ply - 1, player)
                if not cur_min:
                    cur_min = next_state_info

                cmp_result = cur_min.cmp(next_state_info)
                if cmp_result[player] == 1:
                    cur_min = next_state_info
                else if cmp_result[player] == 0:
                    if cmp_result[1 - player] == -1:
                        cur_min = next_state_info

                if cur_min.cmp(a)[player] == -1:
                    return cur_min
                if cur_max.cmp(b)[player] == -1:
                    b = cur_min

            return cur_min

        cur_state = asp.get_start_state()
        player = cur_state.player_to_move()
        actions = asp.get_available_actions(cur_state)
        ret_a = None

        a, b, cur_max = None, None, None
        for action in actions:
            next_state_info = min_value(asp, asp.transition(cur_state, action), a, b, cutoff_ply - 1, player)
            cur_max = next_state_info if not cur_max
            a = cur_max if not a
            b = cur_max if not b

            cmp_result = cur_max.cmp(next_state_info)
            if cmp_result[player] == -1:
                cur_max = next_state_info
                ret_a = action

            if cur_max.cmp(b)[player] == 1:
                return ret_a
            if cur_max.cmp(a)[player] == 1:
                a = cur_max

        return ret_a


class RandBot:
    """Moves in a random (safe) direction"""

    def decide(self, asp):
        """
        Input: asp, a TronProblem
        Output: A direction in {'U','D','L','R'}
        """
        state = asp.get_start_state()
        locs = state.player_locs
        board = state.board
        ptm = state.ptm
        loc = locs[ptm]
        possibilities = list(TronProblem.get_safe_actions(board, loc))
        if possibilities:
            return random.choice(possibilities)
        return "U"

    def cleanup(self):
        pass


class WallBot:
    """Hugs the wall"""

    def __init__(self):
        order = ["U", "D", "L", "R"]
        random.shuffle(order)
        self.order = order

    def cleanup(self):
        order = ["U", "D", "L", "R"]
        random.shuffle(order)
        self.order = order

    def decide(self, asp):
        """
        Input: asp, a TronProblem
        Output: A direction in {'U','D','L','R'}
        """
        state = asp.get_start_state()
        locs = state.player_locs
        board = state.board
        ptm = state.ptm
        loc = locs[ptm]
        possibilities = list(TronProblem.get_safe_actions(board, loc))
        if not possibilities:
            return "U"
        decision = possibilities[0]
        for move in self.order:
            if move not in possibilities:
                continue
            next_loc = TronProblem.move(loc, move)
            if len(TronProblem.get_safe_actions(board, next_loc)) < 3:
                decision = move
                break
        return decision
