#!/usr/bin/env python3
"""
五子棋游戏 - 终端版
AI执黑先行，玩家执白子

适用于没有图形界面的环境
"""

import numpy as np
import os
import sys
from typing import Optional, Tuple, List
from enum import IntEnum


class Stone(IntEnum):
    """棋子类型"""
    EMPTY = 0
    BLACK = 1  # AI
    WHITE = 2  # 玩家


class GomokuAI:
    """五子棋AI - 使用极大极小算法 + Alpha-Beta剪枝"""

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

    def __init__(self, board_size: int = 15, search_depth: int = 4):
        self.board_size = board_size
        self.search_depth = search_depth
        self.directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

    def get_best_move(self, board: np.ndarray, stone: Stone) -> Tuple[int, int]:
        """获取AI的最佳落子位置"""
        if np.sum(board != Stone.EMPTY) == 0:
            center = self.board_size // 2
            return (center, center)

        candidates = self._get_candidates(board)
        if not candidates:
            center = self.board_size // 2
            return (center, center)

        best_score = float('-inf')
        best_move = candidates[0]
        alpha = float('-inf')
        beta = float('inf')

        for move in candidates:
            board[move[0], move[1]] = stone
            if self._check_win(board, move[0], move[1], stone):
                board[move[0], move[1]] = Stone.EMPTY
                return move
            score = self._minimax(board, self.search_depth - 1, alpha, beta, False, stone)
            board[move[0], move[1]] = Stone.EMPTY

            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, score)

        return best_move

    def _minimax(self, board: np.ndarray, depth: int, alpha: float, beta: float,
                 is_maximizing: bool, ai_stone: Stone) -> float:
        winner = self._get_winner(board)
        if winner == ai_stone:
            return self.SCORES['FIVE']
        elif winner != Stone.EMPTY:
            return -self.SCORES['FIVE']

        if depth == 0:
            return self._evaluate_board(board, ai_stone)

        candidates = self._get_candidates(board)
        if not candidates:
            return 0

        opponent = Stone.WHITE if ai_stone == Stone.BLACK else Stone.BLACK

        if is_maximizing:
            max_score = float('-inf')
            for move in candidates[:15]:
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
            for move in candidates[:15]:
                board[move[0], move[1]] = opponent
                score = self._minimax(board, depth - 1, alpha, beta, True, ai_stone)
                board[move[0], move[1]] = Stone.EMPTY
                min_score = min(min_score, score)
                beta = min(beta, score)
                if beta <= alpha:
                    break
            return min_score

    def _get_candidates(self, board: np.ndarray) -> List[Tuple[int, int]]:
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

        scored_candidates = []
        for pos in candidates:
            score = self._evaluate_position(board, pos[0], pos[1])
            scored_candidates.append((score, pos))
        scored_candidates.sort(reverse=True)
        return [pos for _, pos in scored_candidates]

    def _evaluate_position(self, board: np.ndarray, row: int, col: int) -> int:
        score = 0
        board[row, col] = Stone.BLACK
        score += self._evaluate_point(board, row, col, Stone.BLACK)
        board[row, col] = Stone.EMPTY
        board[row, col] = Stone.WHITE
        score += self._evaluate_point(board, row, col, Stone.WHITE)
        board[row, col] = Stone.EMPTY
        return score

    def _evaluate_board(self, board: np.ndarray, ai_stone: Stone) -> int:
        ai_score = 0
        opponent_score = 0
        opponent = Stone.WHITE if ai_stone == Stone.BLACK else Stone.BLACK

        for i in range(self.board_size):
            for j in range(self.board_size):
                if board[i, j] == ai_stone:
                    ai_score += self._evaluate_point(board, i, j, ai_stone)
                elif board[i, j] == opponent:
                    opponent_score += self._evaluate_point(board, i, j, opponent)

        return ai_score - opponent_score * 1.1

    def _evaluate_point(self, board: np.ndarray, row: int, col: int, stone: Stone) -> int:
        score = 0
        for dx, dy in self.directions:
            count = 1
            block = 0
            empty = 0

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

            score += self._get_pattern_score(count, block, empty)
        return score

    def _get_pattern_score(self, count: int, block: int, empty: int) -> int:
        if count >= 5:
            return self.SCORES['FIVE']
        if block == 0:
            if count == 4:
                return self.SCORES['LIVE_FOUR']
            elif count == 3:
                return self.SCORES['LIVE_THREE']
            elif count == 2:
                return self.SCORES['LIVE_TWO']
            elif count == 1:
                return self.SCORES['LIVE_ONE']
        elif block == 1:
            if count == 4:
                return self.SCORES['RUSH_FOUR']
            elif count == 3:
                return self.SCORES['SLEEP_THREE']
            elif count == 2:
                return self.SCORES['SLEEP_TWO']
        return 0

    def _check_win(self, board: np.ndarray, row: int, col: int, stone: Stone) -> bool:
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

    def _get_winner(self, board: np.ndarray) -> Stone:
        for i in range(self.board_size):
            for j in range(self.board_size):
                if board[i, j] != Stone.EMPTY:
                    if self._check_win(board, i, j, board[i, j]):
                        return board[i, j]
        return Stone.EMPTY


class GomokuTerminal:
    """终端版五子棋游戏"""

    def __init__(self, board_size: int = 15):
        self.board_size = board_size
        self.board = np.zeros((board_size, board_size), dtype=int)
        self.ai = GomokuAI(board_size, search_depth=4)
        self.game_over = False
        self.winner = None
        self.last_move = None
        self.current_player = Stone.BLACK

    def clear_screen(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_board(self):
        """打印棋盘"""
        self.clear_screen()
        print("\n" + "=" * 50)
        print("        五子棋 - AI执黑先行")
        print("=" * 50)

        # 列标号
        print("   ", end="")
        for j in range(self.board_size):
            print(f"{j:2}", end=" ")
        print()

        # 棋盘
        for i in range(self.board_size):
            print(f"{i:2} ", end="")
            for j in range(self.board_size):
                if self.board[i, j] == Stone.EMPTY:
                    if self.last_move == (i, j):
                        print(" +", end=" ")
                    else:
                        print(" .", end=" ")
                elif self.board[i, j] == Stone.BLACK:
                    if self.last_move == (i, j):
                        print("(X)", end="")
                    else:
                        print(" X", end=" ")
                else:  # WHITE
                    if self.last_move == (i, j):
                        print("(O)", end="")
                    else:
                        print(" O", end=" ")
            print()

        print()
        print("X = AI (黑子)   O = 你 (白子)")
        print("最后落子位置用括号标记")
        print("-" * 50)

    def make_move(self, row: int, col: int, stone: Stone) -> bool:
        """落子"""
        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            if self.board[row, col] == Stone.EMPTY:
                self.board[row, col] = stone
                self.last_move = (row, col)
                return True
        return False

    def check_winner(self) -> Optional[Stone]:
        """检查获胜者"""
        if self.last_move:
            row, col = self.last_move
            stone = self.board[row, col]
            if self.ai._check_win(self.board, row, col, stone):
                return stone
        return None

    def is_board_full(self) -> bool:
        """检查棋盘是否已满"""
        return np.sum(self.board == Stone.EMPTY) == 0

    def ai_turn(self):
        """AI下棋"""
        print("AI思考中...")
        move = self.ai.get_best_move(self.board.copy(), Stone.BLACK)
        self.make_move(move[0], move[1], Stone.BLACK)
        print(f"AI落子: ({move[0]}, {move[1]})")

    def player_turn(self):
        """玩家下棋"""
        while True:
            try:
                user_input = input("请输入落子位置 (行 列)，例如 '7 7'，或输入 'q' 退出: ").strip()

                if user_input.lower() == 'q':
                    print("游戏结束！")
                    sys.exit(0)

                parts = user_input.split()
                if len(parts) != 2:
                    print("格式错误！请输入两个数字，用空格分隔")
                    continue

                row, col = int(parts[0]), int(parts[1])

                if not (0 <= row < self.board_size and 0 <= col < self.board_size):
                    print(f"位置超出范围！请输入 0-{self.board_size - 1} 之间的数字")
                    continue

                if self.board[row, col] != Stone.EMPTY:
                    print("该位置已有棋子！请选择空位")
                    continue

                self.make_move(row, col, Stone.WHITE)
                break

            except ValueError:
                print("输入无效！请输入数字")
            except KeyboardInterrupt:
                print("\n游戏结束！")
                sys.exit(0)

    def run(self):
        """运行游戏"""
        print("=" * 50)
        print("五子棋游戏 - 终端版")
        print("=" * 50)
        print("- AI执黑子(X)先行")
        print("- 你执白子(O)")
        print("- 输入坐标落子，格式: 行 列")
        print("- 输入 q 退出游戏")
        print("=" * 50)
        input("按 Enter 开始游戏...")

        # AI先手
        self.print_board()
        self.ai_turn()

        while not self.game_over:
            self.print_board()

            # 检查AI是否获胜
            winner = self.check_winner()
            if winner:
                self.game_over = True
                self.winner = winner
                break

            if self.is_board_full():
                self.game_over = True
                break

            # 玩家回合
            self.player_turn()
            self.print_board()

            # 检查玩家是否获胜
            winner = self.check_winner()
            if winner:
                self.game_over = True
                self.winner = winner
                break

            if self.is_board_full():
                self.game_over = True
                break

            # AI回合
            self.ai_turn()

        # 游戏结束
        self.print_board()
        print("\n" + "=" * 50)
        if self.winner == Stone.BLACK:
            print("       游戏结束 - AI获胜！")
        elif self.winner == Stone.WHITE:
            print("       游戏结束 - 恭喜你赢了！")
        else:
            print("       游戏结束 - 平局！")
        print("=" * 50)


def main():
    game = GomokuTerminal()
    game.run()


if __name__ == "__main__":
    main()
