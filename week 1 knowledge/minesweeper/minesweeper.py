import itertools
import random
import copy


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # If the number of cells in the sentence is equal to the count, then all cells are mines
        if len(self.cells) == self.count:
            return set(self.cells)
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # If the count is 0, then all cells are safe
        if self.count == 0:
            return set(self.cells)
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # If the cell is in the sentence, remove it and decrement the count by 1
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1
        return

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # If the cell is in the sentence, remove it
        if cell in self.cells:
            self.cells.remove(cell)
        return


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # 1) Mark the cell as a move that has been made
        self.moves_made.add(cell)

        # 2) Mark the cell as safe
        self.mark_safe(cell)

        # 3) Add a new sentence to the AI's knowledge base based on the value of `cell` and `count`
        # Create a new set of cells
        sentence_cells = set()
        # Copy the count of the cells
        copy_count = copy.deepcopy(count)
        # Loop over the surrounding cells
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself and any cells already marked as safe
                if (i, j) == cell or (i, j) in self.safes:
                    continue

                # If the cell is a mine, decrement the count by 1
                if (i, j) in self.mines:
                    copy_count -= 1
                    continue

                # Add other cells to the sentence (Remember to check if the cell is in bounds)
                if 0 <= i < self.height and 0 <= j < self.width:
                    sentence_cells.add((i, j))
        # Add the sentence to the knowledge base (Remember to check if the sentence is empty)
        if len(sentence_cells) > 0:
            self.knowledge.append(Sentence(sentence_cells, copy_count))

        # 4) Mark any additional cells as safe or as mines if it can be concluded based on the AI's knowledge base
        kb_changed = True # Keep track of whether the knowledge base has changed
        while kb_changed:
            kb_changed = False
            # Loop over the knowledge base
            for sentence in self.knowledge:
                # If the sentence contains known mines, mark them as mines
                if sentence.known_mines() != None:
                    for mine in sentence.known_mines():
                        self.mark_mine(mine)
                        kb_changed = True
                # If the sentence contains known safes, mark them as safes
                if sentence.known_safes() != None:
                    for safe in sentence.known_safes():
                        self.mark_safe(safe)
                        kb_changed = True

        # 5) Add any new sentences to the AI's knowledge base if they can be inferred from existing knowledge
        for sentence_a in self.knowledge:
            for sentence_b in self.knowledge:
                # Skip if sentence_a equals sentence_b
                if sentence_a == sentence_b: continue
                # If sentence_a is a subset of sentence_b, create a new sentence
                if sentence_a.cells.issubset(sentence_b.cells):
                    new_sentence = Sentence(sentence_b.cells - sentence_a.cells, sentence_b.count - sentence_a.count)
                    # If the new sentence is not already in the knowledge base, add it
                    if new_sentence not in self.knowledge:
                        self.knowledge.append(new_sentence)
        return

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # Get all safe moves (safe moves - moves already made)
        safe_moves = self.safes - self.moves_made
        # print(safe_moves)
        # If there are no safe moves, return None
        if len(safe_moves) == 0:
            return None
        # Otherwise, return a random safe move
        return random.choice(tuple(safe_moves))

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # Get all possible moves (all cells - moves already made - known mines)
        possible_moves = set()
        for i in range(self.height):
            for j in range(self.width):
                possible_moves.add((i, j))
        possible_moves = possible_moves - self.moves_made - self.mines

        # If there are no possible moves, return None
        if len(possible_moves) == 0:
            return None

        # Otherwise, return a random possible move
        return random.choice(tuple(possible_moves))
