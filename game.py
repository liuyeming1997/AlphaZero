# -*- coding: utf-8 -*-
"""
@author: Junxiao Song
"""

from __future__ import print_function
import numpy as np
import operator


class Board(object):
    """board for the game"""

    def __init__(self, **kwargs):
        self.availables = []
        self.width = int(kwargs.get('width', 8))
        self.height = int(kwargs.get('height', 8))
        # board states stored as a dict,
        # key: move as location on the board,
        # value: player as pieces type
        self.states = {}
        self.players = [1, 2]
        # need how many pieces in a row to win
        self.n_in_row = int(kwargs.get('n_in_row', 5))
        self.validPos = self.validPos()

    def validPos(self):
        pos_list = []
        for x in range(self.width):
            for y in range(self.height):
                pos_list.append((x, y))
        return pos_list

    def init_board(self, start_player=0):
        if self.width < self.n_in_row or self.height < self.n_in_row:
            raise Exception('board width and height can not be '
                            'less than {}'.format(self.n_in_row))
        self.current_player = self.players[start_player]  # start player
        # keep available moves in a list
        self.states = {}
        half = int(self.width / 2)
        self.states[self.location_to_move((half - 1, half - 1))] = self.players[1]
        self.states[self.location_to_move((half, half))] = self.players[1]
        self.states[self.location_to_move((half, half - 1))] = self.players[0]
        self.states[self.location_to_move((half - 1, half))] = self.players[0]
        self.availables = self.get_logic_action(self.current_player)
        self.last_move = -1

    def move_to_location(self, move):
        """
        3*3 board's moves like:
        6 7 8
        3 4 5
        0 1 2
        and move 5's location is (1,2)
        """
        h = move // self.width
        w = move % self.width
        return [h, w]

    def location_to_move(self, location):
        if len(location) != 2:
            return -1
        h = location[0]
        w = location[1]
        move = h * self.width + w
        if move not in range(self.width * self.height):
            return -1
        return move

    def current_state(self):
        """return the board state from the perspective of the current player.
        state shape: 4*width*height
        """

        square_state = np.zeros((4, self.width, self.height))
        if self.states:
            moves, players = np.array(list(zip(*self.states.items())))
            move_curr = moves[players == self.current_player]
            move_oppo = moves[players != self.current_player]
            square_state[0][move_curr // self.width,
                            move_curr % self.height] = 1.0
            square_state[1][move_oppo // self.width,
                            move_oppo % self.height] = 1.0
            # indicate the last move location
            square_state[2][self.last_move // self.width,
                            self.last_move % self.height] = 1.0
        if len(self.states) % 2 == 0:
            square_state[3][:, :] = 1.0  # indicate the colour to play
        return square_state[:, ::-1, :]

    def do_move(self, move):
        if move == 64:
            self.current_player = (
                self.players[0] if self.current_player == self.players[1]
                else self.players[1]
            )
            return
        self.states[move] = self.current_player
        # update states
        width = self.width
        y = move // width
        x = move % width
        update_color = self.current_player
        for direction in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            temp_pos = (y, x)
            temp_pos = tuple(map(operator.add, temp_pos, direction))
            update_list = []
            flag = False
            m = self.location_to_move(temp_pos)
            while temp_pos in self.validPos and self.states.get(m, -1) != -1:
                m = self.location_to_move(temp_pos)
                if update_color == self.states.get(m, -1):
                    flag = True
                    break
                update_list.append(m)
                temp_pos = tuple(map(operator.add, temp_pos, direction))
            if flag:
                for m in update_list:
                    self.states[m] = update_color
        # update availablies
        # self.availables.remove(move)
        self.current_player = (
            self.players[0] if self.current_player == self.players[1]
            else self.players[1]
        )
        self.last_move = move
    def countScoreAndGetWinner(self):
        score = {}
        score[1] = 0
        score[2] = 0
        for key in self.states:
            score[self.states[key]] += 1
        # print("final_score: ")
        # print(score)
        if score[1] < score[2]:
            return 2
        elif score[1] > score[2]:
            return 1
        else:
            return -1

    def has_a_winner(self):
        width = self.width
        height = self.height
        states = self.states
        n = self.n_in_row
        actions = []
        for action in self.availables:
            if states.get(action, -1) == -1:
                y = action // width
                x = action % width
                player = self.current_player
                pos = (y, x)
                for direction in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    # print(pos)
                    temp_pos = tuple(map(operator.add, pos, direction))
                    # print(direction)
                    # print(temp_pos)
                    temp_color = player
                    flag = False
                    while temp_pos in self.validPos:
                        m = self.location_to_move(temp_pos)
                        if states.get(m, -1) == -1:
                            break
                        if not temp_color == states.get(m, -1):
                            flag = True
                        if temp_color == states.get(m, -1) and not flag:
                            break
                        if temp_color == states.get(m, -1) and flag:
                            actions.append(action)
                            break
                        temp_pos = tuple(map(operator.add, temp_pos, direction))
        return actions

    def next_move(self):
        actions = self.availables
        if len(actions) == 0:
            current_player_new = (
                self.players[0] if self.current_player == self.players[1]
                else self.players[1]
            )
            actions = self.get_logic_action(current_player_new)
            if len(actions) == 0:
                return True
            else:
                return False
        else:
            return False

    def game_end(self):
        """Check whether the game is ended or not"""
        flag = self.next_move()
        # actions = self.has_a_winner()
        if flag:
            return True, self.countScoreAndGetWinner()
        else:
            return False, -1

    def get_current_player(self):
        return self.current_player

    def boardToString(self):
        output = ""
        output += "  0 1 2 3 4 5 6 7\n"
        # print("  0 1 2 3 4 5 6 7")
        for i in range(self.width):
            output += str(i)
            output += " "
            for j in range(self.width):
                move = self.location_to_move((i, j))
                tmp = self.states.get(move, -1)

                if tmp == -1:
                    output = output + "_ "
                elif tmp == 1:
                    output = output + "B "
                elif tmp == 2:
                    output = output + "W "
                else:
                    output = output + "X "
            output = output + "\n"
        return output

    """
    def update_availables(self):
        width = self.width
        height = self.height
        states = self.states
        self.availables = []
        for x in range(width):
            for y in range(width):
                player = self.current_player
                pos = (x, y)
                for direction in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    # print(pos)
                    temp_pos = tuple(map(operator.add, pos, direction))
                    # print(direction)
                    temp_color = player
                    end_flag = False
                    flag = False
                    while temp_pos in self.validPos:
                        m = self.location_to_move(temp_pos)
                        if states.get(m, -1) == -1:
                            break
                        if not temp_color == states.get(m, -1):
                            flag = True
                        if temp_color == states.get(m, -1) and not flag:
                            break
                        if temp_color == states.get(m, -1) and flag:
                            action = self.location_to_move(pos)
                            self.availables.append(action)
                            end_flag = True
                            break
                        temp_pos = tuple(map(operator.add, temp_pos, direction))
                    if end_flag:
                        break
    """
    def get_logic_action(self, id):
        actions = []
        temp_color = id
        for key in self.states:
            val = self.states[key]
            if val == id:
                continue
            pos_f = self.move_to_location(key)
            for direction_f in [(1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]:
                pos = tuple(map(operator.add, pos_f, direction_f))
                pos_m = self.location_to_move(pos)
                if pos in self.validPos and self.states.get(pos_m, -1) == -1:
                    for direction in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                        if pos_m in actions:
                            continue
                        temp_pos = tuple(map(operator.add, pos, direction))
                        pos_new = self.location_to_move(temp_pos)
                        if temp_pos in self.validPos and self.states.get(pos_new, -1) != -1 and self.states.get(pos_new,
                                                                                                        -1) != temp_color:
                            while temp_pos in self.validPos:
                                pos_new = self.location_to_move(temp_pos)
                                if self.states.get(pos_new, -1) == -1:
                                    break
                                if self.states.get(pos_new, -1) == temp_color:
                                    actions.append(pos_m)
                                    break
                                temp_pos = tuple(map(operator.add, temp_pos, direction))

        return actions
    """
    def get_logic_action(self, id):
        states = self.states
        actions = []
        vis = dict()
        temp_color = id
        for key in self.states:
            val = self.states[key]
            if val == id:
                continue
            pos_f = self.move_to_location(key)
            for direction_f in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                pos = tuple(map(operator.add, pos_f, direction_f))
                pos_m = self.location_to_move(pos)
                if pos_m in actions:
                    continue
                if 0 <= pos_m < 64 and self.states.get(pos_m, -1) == -1:
                    for direction in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                        # print(pos)
                        temp_pos = tuple(map(operator.add, pos, direction))
                        # print(direction)
                        flag = False
                        m = self.location_to_move(temp_pos)
                        while 0 <= m < 64:
                            m = self.location_to_move(temp_pos)
                            if states.get(m, -1) == -1:
                                break
                            if not temp_color == states.get(m, -1):
                                flag = True
                            if temp_color == states.get(m, -1) and not flag:
                                break
                            if temp_color == states.get(m, -1) and flag:
                                actions.append(pos_m)
                                break
                            temp_pos = tuple(map(operator.add, temp_pos, direction))
        return actions

    
    def logic_action(self, action_probs):
        width = self.width
        height = self.height
        states = self.states
        n = self.n_in_row
        actions = []
        for action, prob in action_probs:
            if states.get(action, -1) == -1:
                y = action // width
                x = action % width
                player = self.current_player
                pos = (y, x)
                for direction in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    # print(pos)
                    temp_pos = tuple(map(operator.add, pos, direction))
                    # print(direction)
                    temp_color = player
                    flag = False
                    while temp_pos in self.validPos:
                        m = self.location_to_move(temp_pos)
                        if states.get(m, -1) == -1:
                            break
                        if not temp_color == states.get(m, -1):
                            flag = True
                        if temp_color == states.get(m, -1) and not flag:
                            break
                        if temp_color == states.get(m, -1) and flag:
                            actions.append((action, prob))
                            break
                        temp_pos = tuple(map(operator.add, temp_pos, direction))
        return actions
"""


class Game(object):
    """game server"""

    def __init__(self, board, **kwargs):
        self.board = board

    def graphic(self, board, player1, player2):
        """Draw the board and show game info"""
        width = board.width
        height = board.height

        print("Player", player1, "with X".rjust(3))
        print("Player", player2, "with O".rjust(3))
        print()
        for x in range(width):
            print("{0:8}".format(x), end='')
        print('\r\n')
        for i in range(height - 1, -1, -1):
            print("{0:4d}".format(i), end='')
            for j in range(width):
                loc = i * width + j
                p = board.states.get(loc, -1)
                if p == player1:
                    print('X'.center(8), end='')
                elif p == player2:
                    print('O'.center(8), end='')
                else:
                    print('_'.center(8), end='')
            print('\r\n\r\n')

    def start_play(self, player1, player2, start_player=0, is_shown=1):
        """start a game between two players"""
        if start_player not in (0, 1):
            raise Exception('start_player should be either 0 (player1 first) '
                            'or 1 (player2 first)')
        self.board.init_board(start_player)
        p1, p2 = self.board.players
        player1.set_player_ind(p1)
        player2.set_player_ind(p2)
        players = {p1: player1, p2: player2}
        if is_shown:
            self.graphic(self.board, player1.player, player2.player)
        while True:
            current_player = self.board.get_current_player()
            player_in_turn = players[current_player]
            move = player_in_turn.get_action(self.board)
            self.board.do_move(move)
            if is_shown:
                self.graphic(self.board, player1.player, player2.player)
            end, winner = self.board.game_end()
            if end:
                if is_shown:
                    if winner != -1:
                        print("Game end. Winner is", players[winner])
                    else:
                        print("Game end. Tie")
                return winner

    def start_self_play(self, player, is_shown=0, temp=1e-3):
        """ start a self-play game using a MCTS player, reuse the search tree,
        and store the self-play data: (state, mcts_probs, z) for training
        """
        self.board.init_board()
        p1, p2 = self.board.players
        states, mcts_probs, current_players = [], [], []
        while True:
            move, move_probs = player.get_action(self.board,
                                                 temp=temp,
                                                 return_prob=1)

            if is_shown:
                print("choose action: ", end=" ")
                print(self.board.move_to_location(move))
            # store the data
            states.append(self.board.current_state())
            mcts_probs.append(move_probs)
            current_players.append(self.board.current_player)
            # perform a move
            self.board.do_move(move)
            self.board.availables = self.board.get_logic_action(self.board.current_player)
            if is_shown:
                self.graphic(self.board, p1, p2)
            end, winner = self.board.game_end()
            if end:
                if is_shown:
                    score = dict()
                    score[1] = 0
                    score[2] = 0
                    for key in self.board.states:
                        score[self.board.states[key]] += 1
                    print("Winner!: ", end = " ")
                    print(winner)
                    print(self.board.boardToString())
                    print("final_score: ")
                    print(score)
                    print()
                    print("winner_players: ")
                    print(current_players)
                # winner from the perspective of the current player of each state
                winners_z = np.zeros(len(current_players))
                if winner != -1:
                    winners_z[np.array(current_players) == winner] = 1.0
                    winners_z[np.array(current_players) != winner] = -1.0
                # reset MCTS root node
                player.reset_player()
                if is_shown:
                    if winner != -1:
                        print("Game end. Winner is player:", winner)
                    else:
                        print("Game end. Tie")
                return winner, zip(states, mcts_probs, winners_z)
