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
        if len(self.cells) == self.count:
            return self.cells
        else:
            return None

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        else:
            return None

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


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
            if cell in sentence.cells:
                sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            if cell in sentence.cells:
                sentence.mark_safe(cell)

    def get_neighbouring_cells(self, cell):
        """
        returns a set of neighbouring cells
        """

        # init neighbouring_cells to empty set
        neighbouring_cells = set()

        # add all possible neighbouring cells
        for row in range(cell[0]-1, cell[0]+2):
            for col in range(cell[1]-1, cell[1]+2):
                if 0 <= row < self.height and 0 <= col < self.width:
                    neighbouring_cells.add((row, col))

        # remove the center cell ( current cell )
        neighbouring_cells.remove(cell)

        return neighbouring_cells

    def get_hidden_neighbouring_cells(self, cell):
        """
        returns a set of hidden neighbouring cells
        """

        # init neighbouring cells
        neighbouring_cells = self.get_neighbouring_cells(cell)

        # remove the cells which are in moves_made
        neighbouring_cells.difference_update(self.moves_made)

        return neighbouring_cells

    def apply_knowledge(self):
        """
        recursively applies knowledge based on sentences and predict mines and safe cells
        """

        # init knowledge_copy
        knowledge_copy = copy.deepcopy(self.knowledge)

        # flag for recursive call
        repeat_flag = False

        # find mines and safe cells from knowledge
        for sentence in knowledge_copy:
            mine_cells = sentence.known_mines()
            safe_cells = sentence.known_safes()

            # remove sentences with no cells
            if len(sentence.cells) == 0:
                repeat_flag = True
                self.knowledge.remove(sentence)
                break

            # mark mine cells
            if mine_cells is not None:
                repeat_flag = True
                for mine in mine_cells:
                    self.mark_mine(mine)

            # mark safe cells
            if safe_cells is not None:
                repeat_flag = True
                for safe in safe_cells:
                    self.mark_safe(safe)

        # call recursively till flag is False
        if repeat_flag:
            self.apply_knowledge()

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

        # mark the cell as a move that has been made
        self.moves_made.add(cell)

        # mark the cell as safe
        self.mark_safe(cell)

        # add a new sentence to the AI's knowledge base
        # based on the value of `cell` and `count`
        cells = self.get_hidden_neighbouring_cells(cell)
        if len(cells) > 0:
            new_sentence = Sentence(cells, count)
            self.knowledge.append(new_sentence)

        # mark any additional cells as safe or as mines
        # if it can be concluded based on the AI's knowledge base
        self.apply_knowledge()

        # add any new sentences to the AI's knowledge based
        # if they can be inferred from existing knowledge
        new_knowledge = self.generate_new_knowledge()
        self.knowledge += new_knowledge

    def generate_new_knowledge(self):
        """
        Returns an array of sentences.

        This function uses self.knowledge to generate new logic.
        """

        # init new_sentences to empty array
        new_sentences = []

        # find a pair of sentences such that "Sentence1" is a subset of "Sentence2"
        #
        # Then add a new sentence with
        # cells = (Sentence2.cells - Sentence1.cells)
        # count = (sentence2.count - Sentence2.count)
        for sentence_1 in self.knowledge:
            for sentence_2 in self.knowledge:
                if sentence_1 != sentence_2 and sentence_1.cells.issubset(sentence_2.cells):
                    new_cells = sentence_2.cells - sentence_1.cells
                    new_count = sentence_2.count - sentence_1.count
                    if len(new_cells) > 0:
                        new_sentence = Sentence(new_cells, new_count)
                        new_sentences.append(new_sentence)

        return new_sentences

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """

        # init safe cell list to safe moves that have not been made
        safe_cells = self.safes - self.moves_made

        # check if safe cell available
        if len(safe_cells) > 0:
            safe = safe_cells.pop()
            # return the first unknown cell
            return safe
        # else return None
        else:
            return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        # init known_cells as empty set
        known_cells = set()
        known_cells.update(self.safes)          # add safe cells to known cells
        known_cells.update(self.mines)          # add mines to known cells
        known_cells.update(self.moves_made)     # add moves made to known cells

        # init unknown_cells as a empty set
        unknown_cells = set()
        # adding all the cell
        for row in range(self.height):
            for col in range(self.width):
                unknown_cells.add((row,col))
        # subtract the known_cell
        unknown_cells.difference_update(known_cells)

        # if cells available
        if len(unknown_cells) > 0:
            # return a random unknown cell
            return random.sample(unknown_cells,1)[0]
        # else return None
        else:
            return None
