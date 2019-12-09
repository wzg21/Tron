#!/usr/bin/python

import numpy as np
from tronproblem import *
from trontypes import CellType, PowerupType
import random, math
from queue import Queue
import copy

# Throughout this file, ASP means adversarial search problem.

class TronStateInfo:

    def __init__(self, asp, state, powerup1, powerup2):
        self.p1_win = 0
        self.p2_win = 0
        self.ptm = -1
        self.powerup1 = powerup1
        self.powerup2 = powerup2
        self.p1_closest_num = 0
        self.p2_closest_num = 0
        self.p1_closest_powerups = {}
        self.p2_closest_powerups = {}
        self._extract_state_info(asp, state)

    def cmp(self, other):
        """
        Output: [x, y],
        x is the compare result of two states for player1,
        y is the compare result of two states for player2,
        can be -1, 0 or 1
        """
        # is terminate state
        if self.p1_win or other.p2_win:
            return [1, -1]
        if self.p2_win or other.p1_win:
            return [-1, 1]

        x = y = 0
        #x
        #player has no safe actions
        if self.p1_closest_num == 0:
            if self.ptm == 0:
                x = -1
            elif other.p1_closest_num == 0 and self.p2_closest_num < other.p2_closest_num:
                x = 1
            else:
                x = -1
        #TRAP
        if x == 0 and self.p1_closest_num >= self.p2_closest_num and other.p1_closest_num >= other.p2_closest_num:
            traps = []
            if self.p1_closest_num >= self.p2_closest_num and other.p1_closest_num >= other.p2_closest_num:
                traps = [CellType.TRAP, CellType.BOMB, CellType.ARMOR]
            else:
                traps = [CellType.BOMB, CellType.ARMOR, CellType.TRAP]

            if self.powerup1 in traps and other.powerup1 not in traps:
                x = 1
            elif self.powerup1 not in traps and other.powerup1 in traps:
                x = -1
            elif self.powerup1 in traps and other.powerup1 in traps:
                if traps.index(self.powerup1) < traps.index(other.powerup1):
                    x = 1
                elif traps.index(self.powerup1) > traps.index(other.powerup1):
                    x = -1

            if x == 0:
                for trap in traps:
                    if x != 0:
                        break
                    if trap in self.p1_closest_powerups and trap not in other.p1_closest_powerups:
                        x = 1
                    elif trap not in self.p1_closest_powerups and trap in other.p1_closest_powerups:
                        x = -1
                    elif trap in self.p1_closest_powerups and trap in other.p1_closest_powerups:
                        if self.p1_closest_powerups[trap][0] > other.p1_closest_powerups[trap][0]:
                            x = 1
                        elif self.p1_closest_powerups[trap][0] < other.p1_closest_powerups[trap][0]:
                            x = -1
                        else:
                            if self.p1_closest_powerups[trap][1] < other.p1_closest_powerups[trap][1]:
                                x = 1
                            elif self.p1_closest_powerups[trap][1] > other.p1_closest_powerups[trap][1]:
                                x = -1
        #closest number
        if x == 0:
            if self.p1_closest_num >= self.p2_closest_num and other.p1_closest_num >= other.p2_closest_num:
                if self.p1_closest_num - self.p2_closest_num > other.p1_closest_num - other.p2_closest_num:
                    x = 1
                elif self.p1_closest_num - self.p2_closest_num < other.p1_closest_num - other.p2_closest_num:
                    x = -1
            elif self.p1_closest_num >= self.p2_closest_num and other.p1_closest_num < other.p2_closest_num:
                x = 1
            elif self.p1_closest_num < self.p2_closest_num and other.p1_closest_num >= other.p2_closest_num:
                x = -1
            else:
                if self.p1_closest_num > other.p1_closest_num:
                    x = 1
                elif self.p1_closest_num < other.p1_closest_num:
                    x = -1

        #y
        #player has no safe actions
        if self.p2_closest_num == 0:
            if self.ptm == 1:
                y = -1
            elif other.p2_closest_num == 0 and self.p1_closest_num < other.p1_closest_num:
                y = 1
            else:
                y = -1
        #TRAP
        if y == 0 and self.p2_closest_num >= self.p1_closest_num and other.p2_closest_num >= other.p1_closest_num:
            traps = []
            if self.p2_closest_num >= self.p1_closest_num and other.p2_closest_num >= other.p1_closest_num:
                traps = [CellType.TRAP, CellType.BOMB, CellType.ARMOR]
            else:
                traps = [CellType.BOMB, CellType.ARMOR, CellType.TRAP]

            if self.powerup2 in traps and other.powerup2 not in traps:
                y = 1
            elif self.powerup2 not in traps and other.powerup2 in traps:
                y = -1
            elif self.powerup2 in traps and other.powerup2 in traps:
                if traps.index(self.powerup2) < traps.index(other.powerup2):
                    y = 1
                elif traps.index(self.powerup2) > traps.index(other.powerup2):
                    y = -1

            if y == 0:
                for trap in traps:
                    if y != 0:
                        break
                    if trap in self.p2_closest_powerups and trap not in other.p2_closest_powerups:
                        y = 1
                    elif trap not in self.p2_closest_powerups and trap in other.p2_closest_powerups:
                        y = -1
                    elif trap in self.p2_closest_powerups and trap in other.p2_closest_powerups:
                        if self.p2_closest_powerups[trap][0] > other.p2_closest_powerups[trap][0]:
                            y = 1
                        elif self.p2_closest_powerups[trap][0] < other.p2_closest_powerups[trap][0]:
                            y = -1
                        else:
                            if self.p2_closest_powerups[trap][1] < other.p2_closest_powerups[trap][1]:
                                y = 1
                            elif self.p2_closest_powerups[trap][1] > other.p2_closest_powerups[trap][1]:
                                y = -1
        #closest number
        if y == 0:
            if self.p2_closest_num >= self.p1_closest_num and other.p2_closest_num >= other.p1_closest_num:
                if self.p2_closest_num - self.p1_closest_num > other.p2_closest_num - other.p1_closest_num:
                    y = 1
                elif self.p2_closest_num - self.p1_closest_num < other.p2_closest_num - other.p1_closest_num:
                    y = -1
            elif self.p2_closest_num >= self.p1_closest_num and other.p2_closest_num < other.p1_closest_num:
                y = 1
            elif self.p2_closest_num < self.p1_closest_num and other.p2_closest_num >= other.p1_closest_num:
                y = -1
            else:
                if self.p2_closest_num > other.p2_closest_num:
                    y = 1
                elif self.p2_closest_num < other.p2_closest_num:
                    y = -1

        return [x, y]


    def _extract_state_info(self, asp, state):
        if asp.is_terminal_state(state):
            self.p1_win, self.p2_win = asp.evaluate_state(state)
            return
        ptm = state.ptm
        self.ptm = ptm
        loc1, loc2 = state.player_locs
        board = state.board

        q1 = Queue()
        q1.put(loc1 if ptm == 0 else loc2)
        d1, n1, n2, n = 1, 1, 0, 0
        powerups1 = {}
        q2 = Queue()
        q2.put(loc2 if ptm == 0 else loc1)
        d2, m1, m2, m = 1, 1, 0, 0
        powerups2 = {}
        s = set()
        while not q1.empty() or not q2.empty():
            while n1 > 0:
                loc = q1.get()
                n1 -= 1
                for action in TronProblem.get_safe_actions(board, loc):
                    next_loc = TronProblem.move(loc, action)
                    if tuple(next_loc) in s:
                        continue
                    s.add(tuple(next_loc))
                    q1.put(next_loc)
                    n2 += 1
                    # powerups
                    r, c = next_loc
                    if board[r][c] == CellType.TRAP or board[r][c] == CellType.BOMB or board[r][c] == CellType.ARMOR:
                        name = board[r][c]
                        if name not in powerups1:
                            powerups1[name] = [1, d1]
                        else:
                            powerups1[name][0] += 1
            n += n2
            n1, n2 = n2, 0
            d1 += 1

            while m1 > 0:
                loc = q2.get()
                m1 -= 1
                for action in TronProblem.get_safe_actions(board, loc):
                    next_loc = TronProblem.move(loc, action)
                    if tuple(next_loc) in s:
                        continue
                    s.add(tuple(next_loc))
                    q2.put(next_loc)
                    m2 += 1
                    # powerups
                    r, c = next_loc
                    if board[r][c] == CellType.TRAP or board[r][c] == CellType.BOMB or board[r][c] == CellType.ARMOR:
                        name = board[r][c]
                        if name not in powerups2:
                            powerups2[name] = [1, d2]
                        else:
                            powerups2[name][0] += 1
            m += m2
            m1, m2 = m2, 0
            d2 += 1

        self.p1_closest_num = n if ptm == 0 else m
        self.p2_closest_num = m if ptm == 0 else n
        self.p1_closest_powerups = copy.deepcopy(powerups1) if ptm == 0 else copy.deepcopy(powerups2)
        self.p2_closest_powerups = copy.deepcopy(powerups2) if ptm == 0 else copy.deepcopy(powerups1)


class StudentBot:
    """ Write your student bot here"""
    def __init__(self):
        self.BOT_NAME = "tea bot"

    def decide(self, asp):
        """
        Input: asp, a TronProblem
        Output: A direction in {'U','D','L','R'}

        To get started, you can get the current
        state by calling asp.get_start_state()
        """
        max_depth = 2
        def maxvalue(asp, state, depth, b1, b2):
            nonlocal max_depth
            locs = state.player_locs
            board = state.board
            ptm = state.ptm
            loc = locs[ptm]
            maxval = act = None
            for action in asp.get_available_actions(state):
                r, c = TronProblem.move(loc, action)
                powerup1 = powerup2 = None
                if board[r][c] == CellType.TRAP or board[r][c] == CellType.BOMB or board[r][c] == CellType.ARMOR:
                    powerup1 = board[r][c]
                if ptm == 1:
                    powerup1, powerup2 = powerup2, powerup1
                next_state = asp.transition(state, action)
                info = None
                if asp.is_terminal_state(next_state) or depth > max_depth or (ptm == 0 and powerup1 or ptm == 1 and powerup2):
                    info = TronStateInfo(asp, next_state, powerup1, powerup2)
                else:
                    info, _ = maxvalue(asp, next_state, depth + 1, b1, b2)
                flag = 0
                if not maxval:
                    maxval = info
                    act = action
                    flag = 1
                else:
                    res = info.cmp(maxval)
                    x, y = res[ptm], res[0 if ptm == 1 else 1]
                    if x == 1 or (x == 0 and y == -1) or (x == 0 and y == 0 and len(TronProblem.get_safe_actions(board, [r, c])) < 3):
                        maxval = info
                        act = action
                        flag = 1
                if flag:
                    if ptm == 0:
                        if b1:
                            res = maxval.cmp(b1)
                            if res[0] == 1 or (res[0] == 0 and res[1] == -1):
                                return maxval, act
                        if not b2:
                            b2 = maxval
                        else:
                            res = maxval.cmp(b2)
                            if res[0] == 1 or (res[0] == 0 and res[1] == -1):
                                b2 = maxval
                    else:
                        if b2:
                            res = maxval.cmp(b2)
                            if res[1] == 1 or (res[1] == 0 and res[0] == -1):
                                return maxval, act
                        if not b1:
                            b1 = maxval
                        else:
                            res = maxval.cmp(b1)
                            if res[1] == 1 or (res[1] == 0 and res[0] == -1):
                                b1 = maxval
            return maxval, act

        start_state = asp.get_start_state()
        locs = start_state.player_locs
        if abs(locs[0][0] - locs[1][0]) + abs(locs[0][0] - locs[1][0]) <= 4:
            max_depth = 3
        _, act = maxvalue(asp, start_state, 1, None, None)
        return act

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

    # def alpha_beta_cutoff(asp, cutoff_ply):

    #     def max_value(asp, state, a, b, cutoff_ply, player):
    #         if asp.is_terminal_state(state):
    #             return TronStateInfo(state)

    #         if cutoff_ply == 0:
    #             return TronStateInfo(state)

    #         actions = asp.get_available_actions(state)
    #         cur_max = None
    #         for action in actions:
    #             next_state_info = min_value(asp, asp.transition(state, action), a, b, cutoff_ply - 1, player)
    #             if not cur_max:
    #                 cur_max = next_state_info

    #             cmp_result = cur_max.cmp(next_state_info)
    #             if cmp_result[player] == -1:
    #                 cur_max = next_state_info
    #             else if cmp_result[player] == 0:
    #                 if cmp_result[1 - player] == 1:
    #                     cur_max = next_state_info

    #             if cur_max.cmp(b)[player] == 1:
    #                 return cur_max
    #             if cur_max.cmp(a)[player] == 1:
    #                 a = cur_max

    #         return cur_max

    #     def min_value(asp, state, a, b, cutoff_ply, player):
    #         if asp.is_terminal_state(state):
    #             return TronStateInfo(state)

    #         if cutoff_ply == 0:
    #             return TronStateInfo(state)

    #         actions = asp.get_available_actions(state)
    #         cur_min = None
    #         for action in actions:
    #             next_state_info = max_value(asp, asp.transition(state, action), a, b, cutoff_ply - 1, player)
    #             if not cur_min:
    #                 cur_min = next_state_info

    #             cmp_result = cur_min.cmp(next_state_info)
    #             if cmp_result[player] == 1:
    #                 cur_min = next_state_info
    #             else if cmp_result[player] == 0:
    #                 if cmp_result[1 - player] == -1:
    #                     cur_min = next_state_info

    #             if cur_min.cmp(a)[player] == -1:
    #                 return cur_min
    #             if cur_max.cmp(b)[player] == -1:
    #                 b = cur_min

    #         return cur_min

    #     cur_state = asp.get_start_state()
    #     player = cur_state.player_to_move()
    #     actions = asp.get_available_actions(cur_state)
    #     ret_a = None

    #     a, b, cur_max = None, None, None
    #     for action in actions:
    #         next_state_info = min_value(asp, asp.transition(cur_state, action), a, b, cutoff_ply - 1, player)
    #         cur_max = next_state_info if not cur_max
    #         a = cur_max if not a
    #         b = cur_max if not b

    #         cmp_result = cur_max.cmp(next_state_info)
    #         if cmp_result[player] == -1:
    #             cur_max = next_state_info
    #             ret_a = action

    #         if cur_max.cmp(b)[player] == 1:
    #             return ret_a
    #         if cur_max.cmp(a)[player] == 1:
    #             a = cur_max

    #     return ret_a


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
