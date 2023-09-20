from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    Or(AKnight, AKnave), # A is either a knight or a knave
    Not(And(AKnight, AKnave)), # A can't be both a knight and a knave
    Implication(AKnight, And(AKnight, AKnave)), # If A is a knight, then A is both a knight and a knave
    Implication(AKnave, Not(And(AKnight, AKnave))), # If A is a knave, then A is not both a knight and a knave
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    Or(AKnight, AKnave), # A is either a knight or a knave
    Not(And(AKnight, AKnave)), # A can't be both a knight and a knave
    Or(BKnight, BKnave), # B is either a knight or a knave
    Not(And(BKnight, BKnave)), # B can't be both a knight and a knave

    Implication(AKnight, And(AKnave, BKnave)), # If A is a knight, then A and B are both knaves
    Implication(AKnave, Not(And(AKnave, BKnave))), # If A is a knave, then A and B are not both knaves
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    Or(AKnight, AKnave), # A is either a knight or a knave
    Not(And(AKnight, AKnave)), # A can't be both a knight and a knave
    Or(BKnight, BKnave), # B is either a knight or a knave
    Not(And(BKnight, BKnave)), # B can't be both a knight and a knave
    
    # If A is a knight, then A and B are either both knights or both knaves
    Implication(AKnight, Or(And(AKnight, BKnight), And(AKnave, BKnave))),
    # If A is a knave, then A and B are not both knights or both knaves
    Implication(AKnave, Not(Or(And(AKnight, BKnight), And(AKnave, BKnave)))),
    # If B is a knight, then A and B are not both knights or both knaves
    Implication(BKnight, Not(Or(And(AKnight, BKnight), And(AKnave, BKnave)))),
    # If B is a knave, then A and B are either both knights or both knaves
    Implication(BKnave, Or(And(AKnight, BKnight), And(AKnave, BKnave))),
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    Or(AKnight, AKnave), # A is either a knight or a knave
    Not(And(AKnight, AKnave)), # A can't be both a knight and a knave
    Or(BKnight, BKnave), # B is either a knight or a knave
    Not(And(BKnight, BKnave)), # B can't be both a knight and a knave
    Or(CKnight, CKnave), # C is either a knight or a knave
    Not(And(CKnight, CKnave)), # C can't be both a knight and a knave

    # A says either "I am a knight" or "I am a knave", but you don't know which
    Or(
        # If A says "I am a knight"
        And(
            Implication(AKnight, AKnight), # If A is a knight, then A is a knight
            Implication(AKnave, Not(AKnight)) # If A is a knave, then A is not a knight
        ),
        # If A says "I am a knave"
        And(
            Implication(AKnight, AKnave), # If A is a knight, then A is a knave
            Implication(AKnave, Not(AKnave)) # If A is a knave, then A is a not a knave
        )
    ),
    # A says either "I am a knight" or "I am a knave" but not both
    Not(And(
        And(
            Implication(AKnight, AKnight),
            Implication(AKnave, Not(AKnight))
        ),
        And(
            Implication(AKnight, AKnave),
            Implication(AKnave, Not(AKnave))
        )
    )),

    # B says "A said 'I am a knave'"
    # If B is a knight, he is telling the truth
    Implication(BKnight, And(
        Implication(AKnight, AKnave), # If A is a knight, then A is a knave
        Implication(AKnave, Not(AKnave)) # If A is a knave, then A is not a knave
    )),
    # If B is a knave, he is lying
    Implication(BKnave, Not(And(
        Implication(AKnight, AKnave),
        Implication(AKnave, Not(AKnave))
    ))),

    # B says "C is a knave"
    Implication(BKnight, CKnave), # If B is a knight, he is telling the truth
    Implication(BKnave, Not(CKnave)), # If B is a knave, he is lying

    # C says "A is a knight"
    Implication(CKnight, AKnight), # If C is a knight, A is a knight
    Implication(CKnave, Not(AKnight)), # If C is a knave, A is not a knight
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
