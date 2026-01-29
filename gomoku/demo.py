#!/usr/bin/env python3
"""
五子棋演示 - AI vs AI 自动对弈
展示AI的下棋能力
"""

import numpy as np
import time
from typing import Tuple, List
from enum import IntEnum


class Stone(IntEnum):
    EMPTY = 0
    BLACK = 1
    WHITE = 2


class GomokuAI:
    """五子棋AI"""

    SCORES = {
        'FIVE': 100000000,
        'LIVE_FOUR': 10000000,
        'RUSH_FOUR': 1000000,
        'LIVE_THREE': 100000,
        'SLEEP_THREE': 10000,
        'LIVE_TWO': 1000,
        'SLEEP_TWO': 100,
        'LIVE_ONE': 10,
    }

    def __init__(self, board_size: int = 15, search_depth: int = 3):
        self.board_size = board_size
        self.search_depth = search_depth
        self.directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

    def get_best_move(self, board: np.ndarray, stone: Stone) -> Tuple[int, int]:
        if np.sum(board != Stone.EMPTY) == 0:
            return (self.board_size // 2, self.board_size // 2)

        candidates = self._get_candidates(board)
        if not candidates:
            return (self.board_size // 2, self.board_size // 2)

        best_score = float('-inf')
        best_move = candidates[0]

        for move in candidates[:10]:
            board[move[0], move[1]] = stone
            if self._check_win(board, move[0], move[1], stone):
                board[move[0], move[1]] = Stone.EMPTY
                return move
            score = self._minimax(board, self.search_depth - 1, float('-inf'), float('inf'), False, stone)
            board[move[0], move[1]] = Stone.EMPTY

            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def _minimax(self, board, depth, alpha, beta, is_max, ai_stone):
        winner = self._get_winner(board)
        if winner == ai_stone:
            return self.SCORES['FIVE']
        elif winner != Stone.EMPTY:
            return -self.SCORES['FIVE']
        if depth == 0:
            return self._evaluate_board(board, ai_stone)

        candidates = self._get_candidates(board)[:8]
        if not candidates:
            return 0

        opponent = Stone.WHITE if ai_stone == Stone.BLACK else Stone.BLACK

        if is_max:
            max_score = float('-inf')
            for move in candidates:
                board[move[0], move[1]] = ai_stone
                score = self._minimax(board, depth - 1, alpha, beta, False, ai_stone)
                board[move[0], move[1]] = Stone.EMPTY
                max_score = max(max_score, score)
                alpha = max(alpha, score)
                if beta <= alpha:
                    break
            return max_score
        else:
            min_score = float('inf')
            for move in candidates:
                board[move[0], move[1]] = opponent
                score = self._minimax(board, depth - 1, alpha, beta, True, ai_stone)
                board[move[0], move[1]] = Stone.EMPTY
                min_score = min(min_score, score)
                beta = min(beta, score)
                if beta <= alpha:
                    break
            return min_score

    def _get_candidates(self, board):
        candidates = set()
        for i in range(self.board_size):
            for j in range(self.board_size):
                if board[i, j] != Stone.EMPTY:
                    for di in range(-2, 3):
                        for dj in range(-2, 3):
                            ni, nj = i + di, j + dj
                            if 0 <= ni < self.board_size and 0 <= nj < self.board_size:
                                if board[ni, nj] == Stone.EMPTY:
                                    candidates.add((ni, nj))
        scored = [(self._eval_pos(board, p[0], p[1]), p) for p in candidates]
        scored.sort(reverse=True)
        return [p for _, p in scored]

    def _eval_pos(self, board, row, col):
        score = 0
        for stone in [Stone.BLACK, Stone.WHITE]:
            board[row, col] = stone
            score += self._eval_point(board, row, col, stone)
            board[row, col] = Stone.EMPTY
        return score

    def _evaluate_board(self, board, ai_stone):
        ai_score = opponent_score = 0
        opponent = Stone.WHITE if ai_stone == Stone.BLACK else Stone.BLACK
        for i in range(self.board_size):
            for j in range(self.board_size):
                if board[i, j] == ai_stone:
                    ai_score += self._eval_point(board, i, j, ai_stone)
                elif board[i, j] == opponent:
                    opponent_score += self._eval_point(board, i, j, opponent)
        return ai_score - opponent_score * 1.1

    def _eval_point(self, board, row, col, stone):
        score = 0
        for dx, dy in self.directions:
            count, block, empty = 1, 0, 0
            for i in range(1, 5):
                nx, ny = row + dx * i, col + dy * i
                if 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                    if board[nx, ny] == stone:
                        count += 1
                    elif board[nx, ny] == Stone.EMPTY:
                        empty += 1
                        break
                    else:
                        block += 1
                        break
                else:
                    block += 1
                    break
            for i in range(1, 5):
                nx, ny = row - dx * i, col - dy * i
                if 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                    if board[nx, ny] == stone:
                        count += 1
                    elif board[nx, ny] == Stone.EMPTY:
                        empty += 1
                        break
                    else:
                        block += 1
                        break
                else:
                    block += 1
                    break
            score += self._pattern_score(count, block)
        return score

    def _pattern_score(self, count, block):
        if count >= 5:
            return self.SCORES['FIVE']
        if block == 0:
            return {4: self.SCORES['LIVE_FOUR'], 3: self.SCORES['LIVE_THREE'],
                    2: self.SCORES['LIVE_TWO'], 1: self.SCORES['LIVE_ONE']}.get(count, 0)
        elif block == 1:
            return {4: self.SCORES['RUSH_FOUR'], 3: self.SCORES['SLEEP_THREE'],
                    2: self.SCORES['SLEEP_TWO']}.get(count, 0)
        return 0

    def _check_win(self, board, row, col, stone):
        for dx, dy in self.directions:
            count = 1
            for i in range(1, 5):
                nx, ny = row + dx * i, col + dy * i
                if 0 <= nx < self.board_size and 0 <= ny < self.board_size and board[nx, ny] == stone:
                    count += 1
                else:
                    break
            for i in range(1, 5):
                nx, ny = row - dx * i, col - dy * i
                if 0 <= nx < self.board_size and 0 <= ny < self.board_size and board[nx, ny] == stone:
                    count += 1
                else:
                    break
            if count >= 5:
                return True
        return False

    def _get_winner(self, board):
        for i in range(self.board_size):
            for j in range(self.board_size):
                if board[i, j] != Stone.EMPTY and self._check_win(board, i, j, board[i, j]):
                    return board[i, j]
        return Stone.EMPTY


def print_board(board, last_move=None):
    """打印棋盘"""
    size = board.shape[0]

    # 列标号
    print("\n    ", end="")
    for j in range(size):
        print(f"{j:2}", end=" ")
    print()

    for i in range(size):
        print(f"{i:2}  ", end="")
        for j in range(size):
            if board[i, j] == Stone.EMPTY:
                print(" .", end=" ")
            elif board[i, j] == Stone.BLACK:
                if last_move == (i, j):
                    print("[X]", end="")
                else:
                    print(" X", end=" ")
            else:
                if last_move == (i, j):
                    print("[O]", end="")
                else:
                    print(" O", end=" ")
        print()
    print("\n  X = 黑子(AI-1)   O = 白子(AI-2)")
    print("  最后落子用方括号标记")


def demo():
    """AI vs AI 演示"""
    print("=" * 50)
    print("      五子棋演示 - AI vs AI 自动对弈")
    print("=" * 50)
    print("黑子(X): AI-1 先手")
    print("白子(O): AI-2")
    print("=" * 50)

    board = np.zeros((15, 15), dtype=int)
    ai = GomokuAI(15, search_depth=3)
    current = Stone.BLACK
    last_move = None
    move_count = 0

    while True:
        move_count += 1
        player_name = "AI-1 (黑)" if current == Stone.BLACK else "AI-2 (白)"

        print(f"\n第 {move_count} 步: {player_name} 思考中...")

        move = ai.get_best_move(board.copy(), current)
        board[move[0], move[1]] = current
        last_move = move

        print(f"{player_name} 落子: ({move[0]}, {move[1]})")
        print_board(board, last_move)

        # 检查获胜
        if ai._check_win(board, move[0], move[1], current):
            print("\n" + "=" * 50)
            print(f"    游戏结束! {player_name} 获胜!")
            print("=" * 50)
            break

        # 检查平局
        if np.sum(board == Stone.EMPTY) == 0:
            print("\n" + "=" * 50)
            print("    游戏结束! 平局!")
            print("=" * 50)
            break

        # 切换玩家
        current = Stone.WHITE if current == Stone.BLACK else Stone.BLACK

        # 限制步数
        if move_count >= 50:
            print("\n演示结束 (已下50步)")
            break


if __name__ == "__main__":
    demo()
