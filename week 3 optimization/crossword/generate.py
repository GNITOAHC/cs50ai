import sys

from crossword import *
import copy


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """

        domains = copy.deepcopy(self.domains)

        for var in domains:
            for word in domains[var]:
                # If the word is not the same length as the variable, remove it from the domain
                if len(word) != var.length:
                    self.domains[var].remove(word)

        return


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        # Set revised to false
        revised = False

        # Get the overlap between the two variables
        overlap = self.crossword.overlaps[x, y]

        # Make a domains copy
        domains = copy.deepcopy(self.domains)

        # If there is overlap
        if overlap[0]:
            for word_x in domains[x]: # For each word in the domain of x
                matched = False
                for word_y in self.domains[y]: # For each word in the domain of y
                    if word_x[overlap[0]] == word_y[overlap[1]]: # If the overlap matches
                        matched = True
                        break
                if matched: continue # If there is a match, continue
                else:
                    self.domains[x].remove(word_x)
                    revised = True

        return revised


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        # If arcs is None, set it to all arcs
        if arcs is None:
            arcs = []
            for var1 in self.domains:
                for var2 in self.crossword.neighbors(var1):
                    if self.crossword.overlaps[var1, var2]:
                        arcs.append((var1, var2))

        while len(arcs) > 0:
            x, y = arcs.pop()
            if self.revise(x, y):
                if not self.domains[x]:
                    return False
                for z in self.crossword.neighbors(x) - {y}:
                    arcs.append((z, x))

        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        for var in self.domains:
            if var not in assignment:
                return False
        return True


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # Check for duplicate values
        if len(assignment.values()) != len(set(assignment.values())):
            return False

        # Check for correct length
        for var in assignment:
            if len(assignment[var]) != var.length:
                return False

        # Check for conflicts
        for x in assignment:
            for y in self.crossword.neighbors(x):
                if y in assignment:
                    overlap = self.crossword.overlaps[x, y]
                    if assignment[x][overlap[0]] != assignment[y][overlap[1]]:
                        return False

        # If all checks pass, return True
        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        ruled_out = {}

        # iterating through var's words
        for word in self.domains[var]:
            eliminated = 0
            for neighbour in self.crossword.neighbors(var):
                # don't count if neighbor has already assigned value
                if neighbour in assignment:
                    continue
                else:
                    # calculate overlap between two variables
                    overlap = self.crossword.overlaps[var, neighbour]
                    for neighbour_word in self.domains[neighbour]:
                        # iterate through neighbour's words, check for eliminate ones
                        if word[overlap[0]] != neighbour_word[overlap[1]]:
                            eliminated += 1
            # add eliminated neighbour's words to temporary dict
            ruled_out[word] = eliminated

        return sorted([v for v in ruled_out], key = lambda v: ruled_out[v])


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        
        # Get unassigned variables
        unassigned = set(self.domains.keys()) - set(assignment.keys())
        
        result = [var for var in unassigned]
        result.sort(key = lambda x: (len(self.domains[x]), -len(self.crossword.neighbors(x))))

        return result[0]


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        # checking if assignment is complete
        if len(assignment) == len(self.domains):
            return assignment

        # select unassigned variable
        variable = self.select_unassigned_variable(assignment)

        # iterating through words in that variable
        for value in self.domains[variable]:
            current_assignment = copy.deepcopy(assignment)
            current_assignment[variable] = value
            """ assignment[variable] = value """
            # check if assignment is consistent
            """ if self.consistent(assignment): """
            """     if self.backtrack(assignment) is not None: """
            """         return self.backtrack(assignment) """
            if self.backtrack(current_assignment) is not None:
                return self.backtrack(current_assignment)

        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
