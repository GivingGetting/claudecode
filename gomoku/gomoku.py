#!/usr/bin/env python3
"""
五子棋游戏 - AI执黑先行
玩家执白子，AI执黑子

AI使用极大极小算法 + Alpha-Beta剪枝
"""

import pygame
import numpy as np
import sys
from typing import Optional, Tuple, List
from enum import IntEnum
import time


class Stone(IntEnum):
    """棋子类型"""
    EMPTY = 0
    BLACK = 1  # AI
    WHITE = 2  # 玩家


class GomokuAI:
    """五子棋AI - 使用极大极小算法 + Alpha-Beta剪枝"""

    # 棋型分数
    SCORES = {
        'FIVE': 100000000,      # 连五
        'LIVE_FOUR': 10000000,  # 活四
        'RUSH_FOUR': 1000000,   # 冲四
        'LIVE_THREE': 100000,   # 活三
        'SLEEP_THREE': 10000,   # 眠三
        'LIVE_TWO': 1000,       # 活二
        'SLEEP_TWO': 100,       # 眠二
        'LIVE_ONE': 10,         # 活一
    }

    def __init__(self, board_size: int = 15, search_depth: int = 4):
        self.board_size = board_size
        self.search_depth = search_depth
        self.directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # 四个方向

    def get_best_move(self, board: np.ndarray, stone: Stone) -> Tuple[int, int]:
        """获取AI的最佳落子位置"""
        # 如果棋盘为空，下在中心
        if np.sum(board != Stone.EMPTY) == 0:
            center = self.board_size // 2
            return (center, center)

        # 获取候选位置
        candidates = self._get_candidates(board)

        if not candidates:
            center = self.board_size // 2
            return (center, center)

        best_score = float('-inf')
        best_move = candidates[0]

        alpha = float('-inf')
        beta = float('inf')

        for move in candidates:
            # 尝试落子
            board[move[0], move[1]] = stone

            # 检查是否直接获胜
            if self._check_win(board, move[0], move[1], stone):
                board[move[0], move[1]] = Stone.EMPTY
                return move

            # 极大极小搜索
            score = self._minimax(board, self.search_depth - 1, alpha, beta, False, stone)

            board[move[0], move[1]] = Stone.EMPTY

            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, score)

        return best_move

    def _minimax(self, board: np.ndarray, depth: int, alpha: float, beta: float,
                 is_maximizing: bool, ai_stone: Stone) -> float:
        """极大极小算法 + Alpha-Beta剪枝"""
        # 检查游戏结束
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
            for move in candidates[:15]:  # 限制搜索宽度
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
        """获取候选落子位置（已有棋子周围2格内的空位）"""
        candidates = set()

        for i in range(self.board_size):
            for j in range(self.board_size):
                if board[i, j] != Stone.EMPTY:
                    # 搜索周围2格内的空位
                    for di in range(-2, 3):
                        for dj in range(-2, 3):
                            ni, nj = i + di, j + dj
                            if 0 <= ni < self.board_size and 0 <= nj < self.board_size:
                                if board[ni, nj] == Stone.EMPTY:
                                    candidates.add((ni, nj))

        # 按照位置评分排序
        scored_candidates = []
        for pos in candidates:
            score = self._evaluate_position(board, pos[0], pos[1])
            scored_candidates.append((score, pos))

        scored_candidates.sort(reverse=True)
        return [pos for _, pos in scored_candidates]

    def _evaluate_position(self, board: np.ndarray, row: int, col: int) -> int:
        """评估单个位置的价值"""
        score = 0

        # 尝试放黑子
        board[row, col] = Stone.BLACK
        score += self._evaluate_point(board, row, col, Stone.BLACK)
        board[row, col] = Stone.EMPTY

        # 尝试放白子
        board[row, col] = Stone.WHITE
        score += self._evaluate_point(board, row, col, Stone.WHITE)
        board[row, col] = Stone.EMPTY

        return score

    def _evaluate_board(self, board: np.ndarray, ai_stone: Stone) -> int:
        """评估整个棋盘局面"""
        ai_score = 0
        opponent_score = 0
        opponent = Stone.WHITE if ai_stone == Stone.BLACK else Stone.BLACK

        for i in range(self.board_size):
            for j in range(self.board_size):
                if board[i, j] == ai_stone:
                    ai_score += self._evaluate_point(board, i, j, ai_stone)
                elif board[i, j] == opponent:
                    opponent_score += self._evaluate_point(board, i, j, opponent)

        return ai_score - opponent_score * 1.1  # 稍微重视防守

    def _evaluate_point(self, board: np.ndarray, row: int, col: int, stone: Stone) -> int:
        """评估单个点的棋型分数"""
        score = 0

        for dx, dy in self.directions:
            count = 1
            block = 0
            empty = 0

            # 正方向
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

            # 反方向
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
        """根据棋型获取分数"""
        if count >= 5:
            return self.SCORES['FIVE']

        if block == 0:  # 两端都没被堵
            if count == 4:
                return self.SCORES['LIVE_FOUR']
            elif count == 3:
                return self.SCORES['LIVE_THREE']
            elif count == 2:
                return self.SCORES['LIVE_TWO']
            elif count == 1:
                return self.SCORES['LIVE_ONE']
        elif block == 1:  # 一端被堵
            if count == 4:
                return self.SCORES['RUSH_FOUR']
            elif count == 3:
                return self.SCORES['SLEEP_THREE']
            elif count == 2:
                return self.SCORES['SLEEP_TWO']

        return 0

    def _check_win(self, board: np.ndarray, row: int, col: int, stone: Stone) -> bool:
        """检查是否获胜"""
        for dx, dy in self.directions:
            count = 1

            # 正方向
            for i in range(1, 5):
                nx, ny = row + dx * i, col + dy * i
                if 0 <= nx < self.board_size and 0 <= ny < self.board_size and board[nx, ny] == stone:
                    count += 1
                else:
                    break

            # 反方向
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
        """获取获胜方"""
        for i in range(self.board_size):
            for j in range(self.board_size):
                if board[i, j] != Stone.EMPTY:
                    if self._check_win(board, i, j, board[i, j]):
                        return board[i, j]
        return Stone.EMPTY


class GomokuGame:
    """五子棋游戏主类"""

    # 颜色定义
    BOARD_COLOR = (220, 179, 92)
    LINE_COLOR = (0, 0, 0)
    BLACK_COLOR = (0, 0, 0)
    WHITE_COLOR = (255, 255, 255)
    HIGHLIGHT_COLOR = (255, 0, 0)
    TEXT_COLOR = (50, 50, 50)
    BG_COLOR = (240, 230, 200)

    def __init__(self, board_size: int = 15, cell_size: int = 40):
        self.board_size = board_size
        self.cell_size = cell_size
        self.margin = 40

        # 计算窗口大小
        self.window_width = self.margin * 2 + self.cell_size * (board_size - 1)
        self.window_height = self.margin * 2 + self.cell_size * (board_size - 1) + 60

        # 初始化pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption('五子棋 - AI执黑先行')

        # 初始化字体
        self.font = pygame.font.SysFont('simhei', 24)
        self.small_font = pygame.font.SysFont('simhei', 18)

        # 游戏状态
        self.board = np.zeros((board_size, board_size), dtype=int)
        self.ai = GomokuAI(board_size, search_depth=4)
        self.game_over = False
        self.winner = None
        self.last_move = None
        self.current_player = Stone.BLACK  # AI先手
        self.thinking = False

        # 历史记录
        self.history = []

    def reset(self):
        """重置游戏"""
        self.board = np.zeros((self.board_size, self.board_size), dtype=int)
        self.game_over = False
        self.winner = None
        self.last_move = None
        self.current_player = Stone.BLACK
        self.thinking = False
        self.history = []

    def _board_to_screen(self, row: int, col: int) -> Tuple[int, int]:
        """棋盘坐标转屏幕坐标"""
        x = self.margin + col * self.cell_size
        y = self.margin + row * self.cell_size
        return (x, y)

    def _screen_to_board(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """屏幕坐标转棋盘坐标"""
        col = round((x - self.margin) / self.cell_size)
        row = round((y - self.margin) / self.cell_size)

        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            return (row, col)
        return None

    def _draw_board(self):
        """绘制棋盘"""
        # 背景
        self.screen.fill(self.BG_COLOR)

        # 棋盘底色
        board_rect = pygame.Rect(
            self.margin - 20,
            self.margin - 20,
            self.cell_size * (self.board_size - 1) + 40,
            self.cell_size * (self.board_size - 1) + 40
        )
        pygame.draw.rect(self.screen, self.BOARD_COLOR, board_rect)
        pygame.draw.rect(self.screen, self.LINE_COLOR, board_rect, 2)

        # 绘制网格线
        for i in range(self.board_size):
            # 横线
            start_pos = self._board_to_screen(i, 0)
            end_pos = self._board_to_screen(i, self.board_size - 1)
            pygame.draw.line(self.screen, self.LINE_COLOR, start_pos, end_pos, 1)

            # 竖线
            start_pos = self._board_to_screen(0, i)
            end_pos = self._board_to_screen(self.board_size - 1, i)
            pygame.draw.line(self.screen, self.LINE_COLOR, start_pos, end_pos, 1)

        # 绘制星位（天元和四个角星）
        star_points = [(7, 7)]  # 天元
        if self.board_size == 15:
            star_points.extend([(3, 3), (3, 11), (11, 3), (11, 11)])

        for row, col in star_points:
            x, y = self._board_to_screen(row, col)
            pygame.draw.circle(self.screen, self.LINE_COLOR, (x, y), 4)

    def _draw_stones(self):
        """绘制棋子"""
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i, j] != Stone.EMPTY:
                    x, y = self._board_to_screen(i, j)
                    color = self.BLACK_COLOR if self.board[i, j] == Stone.BLACK else self.WHITE_COLOR

                    # 绘制棋子
                    pygame.draw.circle(self.screen, color, (x, y), self.cell_size // 2 - 2)

                    # 白子加边框
                    if self.board[i, j] == Stone.WHITE:
                        pygame.draw.circle(self.screen, self.BLACK_COLOR, (x, y), self.cell_size // 2 - 2, 1)

                    # 标记最后一步
                    if self.last_move == (i, j):
                        pygame.draw.circle(self.screen, self.HIGHLIGHT_COLOR, (x, y), 5)

    def _draw_status(self):
        """绘制状态信息"""
        y = self.window_height - 50

        if self.game_over:
            if self.winner == Stone.BLACK:
                text = "游戏结束 - AI获胜！"
            elif self.winner == Stone.WHITE:
                text = "游戏结束 - 你赢了！"
            else:
                text = "游戏结束 - 平局！"
            color = (200, 0, 0)
        elif self.thinking:
            text = "AI思考中..."
            color = self.TEXT_COLOR
        else:
            text = "轮到你下 (白子)"
            color = self.TEXT_COLOR

        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(self.window_width // 2, y))
        self.screen.blit(text_surface, text_rect)

        # 显示操作提示
        hint = "按 R 重新开始 | 按 Q 退出"
        hint_surface = self.small_font.render(hint, True, (100, 100, 100))
        hint_rect = hint_surface.get_rect(center=(self.window_width // 2, y + 25))
        self.screen.blit(hint_surface, hint_rect)

    def _draw_hover(self, pos: Optional[Tuple[int, int]]):
        """绘制鼠标悬停效果"""
        if pos and not self.game_over and self.current_player == Stone.WHITE and not self.thinking:
            row, col = pos
            if self.board[row, col] == Stone.EMPTY:
                x, y = self._board_to_screen(row, col)
                # 绘制半透明预览
                s = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                pygame.draw.circle(s, (255, 255, 255, 128), (self.cell_size // 2, self.cell_size // 2), self.cell_size // 2 - 2)
                self.screen.blit(s, (x - self.cell_size // 2, y - self.cell_size // 2))

    def _check_winner(self) -> Optional[Stone]:
        """检查是否有获胜方"""
        if self.last_move:
            row, col = self.last_move
            stone = self.board[row, col]
            if self.ai._check_win(self.board, row, col, stone):
                return stone
        return None

    def _is_board_full(self) -> bool:
        """检查棋盘是否已满"""
        return np.sum(self.board == Stone.EMPTY) == 0

    def _make_move(self, row: int, col: int, stone: Stone) -> bool:
        """落子"""
        if self.board[row, col] == Stone.EMPTY:
            self.board[row, col] = stone
            self.last_move = (row, col)
            self.history.append((row, col, stone))
            return True
        return False

    def _ai_move(self):
        """AI落子"""
        self.thinking = True
        self._draw()
        pygame.display.flip()

        # AI计算最佳落子
        move = self.ai.get_best_move(self.board.copy(), Stone.BLACK)

        # 短暂延迟，让玩家看清
        time.sleep(0.3)

        self._make_move(move[0], move[1], Stone.BLACK)
        self.thinking = False

        # 检查获胜
        winner = self._check_winner()
        if winner:
            self.game_over = True
            self.winner = winner
        elif self._is_board_full():
            self.game_over = True
        else:
            self.current_player = Stone.WHITE

    def _player_move(self, row: int, col: int):
        """玩家落子"""
        if self._make_move(row, col, Stone.WHITE):
            # 检查获胜
            winner = self._check_winner()
            if winner:
                self.game_over = True
                self.winner = winner
            elif self._is_board_full():
                self.game_over = True
            else:
                self.current_player = Stone.BLACK

    def _draw(self):
        """绘制整个界面"""
        self._draw_board()
        self._draw_stones()
        self._draw_status()

    def run(self):
        """运行游戏主循环"""
        clock = pygame.time.Clock()
        hover_pos = None

        # AI先手
        self._ai_move()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEMOTION:
                    hover_pos = self._screen_to_board(event.pos[0], event.pos[1])

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # 左键
                        if not self.game_over and self.current_player == Stone.WHITE and not self.thinking:
                            pos = self._screen_to_board(event.pos[0], event.pos[1])
                            if pos and self.board[pos[0], pos[1]] == Stone.EMPTY:
                                self._player_move(pos[0], pos[1])

                                # 如果游戏没结束，AI下棋
                                if not self.game_over:
                                    self._ai_move()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset()
                        self._ai_move()
                    elif event.key == pygame.K_q:
                        running = False

            self._draw()
            self._draw_hover(hover_pos)
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()


def main():
    """主函数"""
    print("=" * 50)
    print("五子棋游戏")
    print("=" * 50)
    print("- AI执黑子先行")
    print("- 你执白子")
    print("- 点击棋盘落子")
    print("- 按 R 重新开始")
    print("- 按 Q 退出游戏")
    print("=" * 50)

    game = GomokuGame()
    game.run()


if __name__ == "__main__":
    main()
