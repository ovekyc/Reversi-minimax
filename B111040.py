# -*- coding: cp949 -*-
from copy import deepcopy
from gamePlay import valid
from gamePlay import doMove
from gamePlay import opponent

MAX = 4
MIN = 5
INF = 0x0fffffff

CN = 100      # corner
SD = 50       # side
NM = 10       # normal
CB = -30      # corner band
SB = -20      # side band
WEIGHT_BOARD = [                    #   weight matrix
[CN, CB, SD, SD, SD, SD, CB, CN],
[CB, CB, SB, SB, SB, SB, CB, CB],
[SD, SB, NM, NM, NM, NM, SB, SD],
[SD, SB, NM, NM, NM, NM, SB, SD],
[SD, SB, NM, NM, NM, NM, SB, SD],
[SD, SB, NM, NM, NM, NM, SB, SD],
[CB, CB, SB, SB, SB, SB, CB, CB],
[CN, CB, SD, SD, SD, SD, CB, CN]
]

limitDepth = 3                      # depth limit


class Node:                         # node
	def __init__(self):
		self.data = 0               # �� ��尡 ���� �� ��ġ
		self.cost = 0               # �� ����� ��� (Ŭ���� ����)
		self.board = []             # ��忡 �ش��ϴ� ���� ��
		self.children = []          # ����� �ڽĵ�

	def calcRatio(self, color):     # ������ ���� �� ���� ������ ���
		opp = opponent(color)
		my = 0
		you = 0
		for i in range(8):
			for j in range(8):
				if self.board[i][j] == color:
					my += 1
				elif self.board[i][j] == opp:
					you += 1
		return (float(my) / float(my + you)) * 10

	def getWeight(self, color):     # weight matrix�� ���� ��ġ�� ���Ͽ� �� ���
		acc = 0
		opp = opponent(color)
		for i in range(8):
			for j in range(8):
				if self.board[i][j] == color or self.board[i][j] == color:
					acc += WEIGHT_BOARD[i][j]   # ���� ���Ҵٸ� plus
				elif self.board[i][j] == opp or self.board[i][j] == opp:
					acc -= WEIGHT_BOARD[i][j]   # ��밡 ���Ҵٸ� minus
		return acc

	def heuristic(self, color):         # �޸���ƽ ��� �Լ�
		ratio  = self.calcRatio(color)
		weight = self.getWeight(color)

		self.cost = ratio + weight
		return self.cost


def makeTree(root, color, depth):             # Ʈ�� ���� �Լ�
	if depth >= limitDepth:                   # �Ѱ� ���� �̻��̸� ����
		return
	moveslen = len(root.children)
	for k in range(moveslen):
		child = root.children[k]              # ������ �� �ִ� ���� �ϳ��� ��������

		another = opponent(color)
		for i in range(8):
			for j in range(8):
				if valid(child.board, another, (i, j)):     # ���� �Ͽ� ���� �� �ִ� ���̸� �ڽ����� �߰�
					temp = Node()
					temp.data = (i,j)
					temp.board = deepcopy(child.board)
					doMove(temp.board, another, temp.data)
					child.children.append(temp)
		if len(child.children) != 0:
			makeTree(child, another, depth + 1)             # ��������� �ڽ��� Ȯ��


def alphabeta(node, depth, alpha, beta, kind, color):   # ����-��Ÿ ����� �Լ�
	numchild = len(node.children)
	if depth == 0 or numchild == 0:         # ��������̰ų� Ȯ�� �� �ڽ��� ���ٸ� �޸���ƽ ���
		return node.heuristic(color)

	if kind == MAX:                         # MAX �� ��
		for i in range(numchild):
			temp = node.children[i]
			alpha = max(alpha, alphabeta(temp, depth - 1, alpha, beta, MIN, color))
			if beta <= alpha:
				break  # beta cut-off
		node.cost = alpha
		return alpha
	else:                                   # MIN �� ��
		for i in range(numchild):
			temp = node.children[i]
			beta = min(beta, alphabeta(temp, depth - 1, alpha, beta, MAX, color))
			if beta <= alpha:
				break  # alpha cut-off
		node.cost = beta
		return beta


def nextMove(board, color, time):
	root = Node()                                           # ��Ʈ��� ����
	for i in range(8):
		for j in range(8):
			if valid(board, color, (i, j)):                 # ���� �� �ִ� ���̸� �ڽ����� �߰�
				temp = Node()
				temp.data = (i,j)
				temp.board = deepcopy(board)
				doMove(temp.board, color, temp.data)
				root.children.append(temp)
	if len(root.children) == 0:
		return "pass"

	makeTree(root, color, 1)                         # Ʈ�� ����
	alphabeta(root, limitDepth, -INF, INF, MAX, color)      # assign cost

	maxx = -INF
	bestmove = 0
	n = len(root.children)
	for i in range(n):                                      # �ִ� ������ ����
		if maxx < root.children[i].cost:
			maxx = root.children[i].cost
			bestmove = root.children[i].data

	return bestmove