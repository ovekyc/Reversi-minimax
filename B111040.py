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
		self.data = 0               # 이 노드가 착수 한 위치
		self.cost = 0               # 이 노드의 비용 (클수록 좋음)
		self.board = []             # 노드에 해당하는 게임 판
		self.children = []          # 노드의 자식들

	def calcRatio(self, color):     # 상대방의 돌과 내 돌의 비율을 계산
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

	def getWeight(self, color):     # weight matrix의 놓인 위치를 비교하여 값 계산
		acc = 0
		opp = opponent(color)
		for i in range(8):
			for j in range(8):
				if self.board[i][j] == color or self.board[i][j] == color:
					acc += WEIGHT_BOARD[i][j]   # 내가 놓았다면 plus
				elif self.board[i][j] == opp or self.board[i][j] == opp:
					acc -= WEIGHT_BOARD[i][j]   # 상대가 놓았다면 minus
		return acc

	def heuristic(self, color):         # 휴리스틱 계산 함수
		ratio  = self.calcRatio(color)
		weight = self.getWeight(color)

		self.cost = ratio + weight
		return self.cost


def makeTree(root, color, depth):             # 트리 생성 함수
	if depth >= limitDepth:                   # 한계 깊이 이상이면 종료
		return
	moveslen = len(root.children)
	for k in range(moveslen):
		child = root.children[k]              # 움직일 수 있는 곳을 하나씩 움직여봄

		another = opponent(color)
		for i in range(8):
			for j in range(8):
				if valid(child.board, another, (i, j)):     # 다음 턴에 놓을 수 있는 곳이면 자식으로 추가
					temp = Node()
					temp.data = (i,j)
					temp.board = deepcopy(child.board)
					doMove(temp.board, another, temp.data)
					child.children.append(temp)
		if len(child.children) != 0:
			makeTree(child, another, depth + 1)             # 재귀적으로 자식을 확장


def alphabeta(node, depth, alpha, beta, kind, color):   # 알파-베타 프루님 함수
	numchild = len(node.children)
	if depth == 0 or numchild == 0:         # 리프노드이거나 확장 할 자식이 없다면 휴리스틱 계산
		return node.heuristic(color)

	if kind == MAX:                         # MAX 일 때
		for i in range(numchild):
			temp = node.children[i]
			alpha = max(alpha, alphabeta(temp, depth - 1, alpha, beta, MIN, color))
			if beta <= alpha:
				break  # beta cut-off
		node.cost = alpha
		return alpha
	else:                                   # MIN 일 때
		for i in range(numchild):
			temp = node.children[i]
			beta = min(beta, alphabeta(temp, depth - 1, alpha, beta, MAX, color))
			if beta <= alpha:
				break  # alpha cut-off
		node.cost = beta
		return beta


def nextMove(board, color, time):
	root = Node()                                           # 루트노드 생성
	for i in range(8):
		for j in range(8):
			if valid(board, color, (i, j)):                 # 놓을 수 있는 곳이면 자식으로 추가
				temp = Node()
				temp.data = (i,j)
				temp.board = deepcopy(board)
				doMove(temp.board, color, temp.data)
				root.children.append(temp)
	if len(root.children) == 0:
		return "pass"

	makeTree(root, color, 1)                         # 트리 생성
	alphabeta(root, limitDepth, -INF, INF, MAX, color)      # assign cost

	maxx = -INF
	bestmove = 0
	n = len(root.children)
	for i in range(n):                                      # 최대 이익을 선택
		if maxx < root.children[i].cost:
			maxx = root.children[i].cost
			bestmove = root.children[i].data

	return bestmove