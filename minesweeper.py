import itertools
import random
import pdb


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
        if self.count == len(self.cells):
            return self.cells
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
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def find_neighbors(self, cell):
        neighbors = []
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                if 0 <= i < self.height and 0 <= j < self.width:
                    if (i,j) not in self.moves_made or (i,j) not in self.mines:
                        neighbors.append((i, j))
                    elif (i, j) in self.mines:
                        count -= 1

        return neighbors

    def build_new_sentence(self, sentence1, sentence2):
        if sentence1 == sentence2 or sentence1 is sentence2:
            return

        if sentence1.cells == None or sentence2.cells == None:
            return

        if sentence1.cells.issubset(sentence2.cells):
            new_cells = sentence2.cells - sentence1.cells
            new_count = sentence2.count - sentence1.count
            new_sentence = Sentence(new_cells, new_count)
            if new_sentence not in self.knowledge:
                self.knowledge.append(new_sentence)

        elif sentence2.cells.issubset(sentence1.cells):
            new_cells = sentence1.cells - sentence2.cells
            new_count = sentence1.count - sentence2.count
            new_sentence = Sentence(new_cells, new_count)

            if new_sentence not in self.knowledge:
                self.knowledge.append(new_sentence) 
   

    def add_knowledge(self, cell, count):
        print('in add knowledge')
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

        self.moves_made.add(cell)
        self.mark_safe(cell)

        # neighboring cells add count
        neighboring_cells = self.find_neighbors(cell)
        new_sentence = Sentence(neighboring_cells, count)
        self.knowledge.append(new_sentence)

        # mark cells as safe or mines
        for sentence in self.knowledge:
            if len(sentence.cells) == 0:
                self.knowledge.remove(sentence)
                continue

            safes = sentence.known_safes()
            if safes:
                for cell in safes.copy():
                    # adds to self.safes and removes cell from sentences
                    self.mark_safe(cell)

            mines = sentence.known_mines()
            if mines:
                for cell in mines.copy():
                    # adds to self.mines and also updates
                    # internal knowledge to remove cell from knowledge base
                    # and lower count
                    self.mark_mine(cell)

        # remove reduncancies in self.knowledge
        for sentence1 in self.knowledge:
            for sentence2 in self.knowledge:
                if sentence1 == sentence2 and len(self.knowledge) > 1:
                    self.knowledge.remove(sentence2)

                self.build_new_sentence(sentence1, sentence2)


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """

        for safe_move in self.safes:
            if safe_move not in self.mines and safe_move not in self.moves_made:
                return safe_move

        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
    
        minesweeper_board = Minesweeper()

        height_of_board = minesweeper_board.height
        width_of_board = minesweeper_board.width

        cell_x = random.randrange(height_of_board)
        cell_y = random.randrange(width_of_board)

        #TODO: keep track of cells already picked
        while (cell_x, cell_y) not in self.mines and (cell_x, cell_y) not in self.moves_made:
            return (cell_x, cell_y)

            cell_x = random.randrange(height_of_board)
            cell_y = random.randrange(width_of_board)

        return None