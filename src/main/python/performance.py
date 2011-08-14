#!/usr/bin/python

# 
# performance.py
# 
# Copyright (c) 2010, Jonathan Fuerth
# 
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in
#       the documentation and/or other materials provided with the
#       distribution.
#     * Neither the name of Jonathan Fuerth nor the names of other
#       contributors may be used to endorse or promote products derived
#       from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#def Move(fromh, jumped, to):
#    return (fromh, jumped, to)

#def Coordinate(row, hole):
#    return (row, hole)

def possibleMoves(self, rowCount):
    row, hole = self

    # upward (needs at least 2 rows above)
    if (row >= 3):

        # up-left
        if (hole >= 3):
            yield (
                self,
                (row - 1, hole - 1),
                (row - 2, hole - 2))

        # up-right
        if (row - hole >= 2):
            yield (
                self,
                (row - 1, hole),
                (row - 2, hole))

    # leftward (needs at least 2 pegs to the left)
    if (hole >= 3):
        yield (
            self,
            (row, hole - 1),
            (row, hole - 2))

    # rightward (needs at least 2 holes to the right)
    if (row - hole >= 2):
        yield (
            self,
            (row, hole + 1),
            (row, hole + 2))

    # downward (needs at least 2 rows below)
    if (rowCount - row >= 2):

        # down-left (always possible when there are at least 2 rows below)
        yield (
            self,
            (row + 1, hole),
            (row + 2, hole))

        # down-right (always possible when there are at least 2 rows below)
        yield (
            self,
            (row + 1, hole + 1),
            (row + 2, hole + 2))


class GameState:

    @classmethod
    def setupBoard(cls, rows, emptyHole):
        # normal constructor that sets up board
        rowCount = rows;
        occupiedHoles = set()
        for row in range(1, rows + 1):
            for hole in range(1, row + 1):
                peg = (row, hole)
                if (not peg == emptyHole):
                    occupiedHoles.add(peg)

        return GameState(rowCount, occupiedHoles)

    def __init__(self, rowCount, occupiedHoles):
        self.rowCount = rowCount
        self.occupiedHoles = occupiedHoles

    def legalMoves(self):
        legalMoves = []
        for c in self.occupiedHoles:
            for _, jumped, to in possibleMoves(c, self.rowCount):
                containsJumped = jumped in self.occupiedHoles
                containsTo = to in self.occupiedHoles

                if containsJumped and not containsTo:
                    legalMoves.append((c, jumped, to))
                
        return legalMoves
    
    def applyMove(self, move):
        # top-secret constructor overload for applying a move
        occupiedHoles = self.occupiedHoles.copy()

        # Note to those comparing this implementation to the others:
        # List.remove() raises ValueError if thr requested item is
        # not present, so the explicit errors are not raised here.
        # The self-checking nature of this method is still intact.

        apply_fromh, apply_jumped, apply_to = move
        apply_to_row, apply_to_hole = apply_to

        occupiedHoles.remove(apply_fromh)
        occupiedHoles.remove(apply_jumped)

        if apply_to in occupiedHoles:
            raise RuntimeError, "Move is not consistent with game state: 'to' hole was occupied."

        if (apply_to_row > self.rowCount or apply_to_hole < 1):
            raise RuntimeError, "Move is not legal because the 'to' hole does not exist: " + str(apply_to)

        occupiedHoles.add(apply_to)

        return GameState(self.rowCount, occupiedHoles)

    def pegsRemaining(self):
        return len(self.occupiedHoles)

    def __str__(self):
        sb = []
        sb.append("Game with " + str(self.pegsRemaining()) + " pegs:\n")
        for row in range(1, self.rowCount + 1):
            indent = self.rowCount - row
            for i in range(0, indent):
                sb.append(" ")
            for hole in range(1, row + 1):
                if (row, hole) in self.occupiedHoles:
                    sb.append(" *")
                else:
                    sb.append(" O")
            sb.append("\n")
        return "".join(sb)


def performance():
    class GlobalStats:
        def __init__(self):
            self.gamesPlayed = 0
            self.solutions = []

    globalStats = GlobalStats()

    def search(gs, moveStack):
        if (gs.pegsRemaining() == 1):
            #print("Found a winning sequence. Final state:")
            #print(gs);

            solutionCopy = []
            solutionCopy.extend(moveStack)
            globalStats.solutions.append(solutionCopy)

            globalStats.gamesPlayed += 1

            return

        legalMoves = gs.legalMoves()

        if (len(legalMoves) == 0):
            globalStats.gamesPlayed += 1
            return

        for m in legalMoves:
            nextState = gs.applyMove(m)
            moveStack.append(m)
            search(nextState, moveStack)
            moveStack.pop()

    from time import time

    startTime = time()
    gs = GameState.setupBoard(5, (3, 2))
    search(gs, [])
    endTime = time()

    print "Games played:    %6d" % (globalStats.gamesPlayed)
    print "Solutions found: %6d" % (len(globalStats.solutions))
    print "Time elapsed:    %6dms" % ((endTime - startTime) * 1000)

if __name__ == '__main__':
    performance()
