import unittest
from main import *


prods = [
    ("E", ["E", "+", "T"]),
    ("E", ["T"]),
    ("T", ["T", "*", "F"]),
    ("T", ["F"]),
    ("F", ["(", "E", ")"]),
    ("F", ["id"]),
]
q0 = "E"
vn = ["E", "T", "F"]
vt = ["+", "*", "(", ")", "id"]

grammar = (q0, vn, vt, prods)

class Test(unittest.TestCase):
    def test_grammar_with_fake_start(self):
        grammar_ext = grammar_with_fake_start(grammar)

        expected = (
            FAKE_S,
            [FAKE_S, "E", "T", "F"],
            ["+", "*", "(", ")", "id", EOF],
            [
                (FAKE_S, ["E"]),
                ("E", ["E", "+", "T"]),
                ("E", ["T"]),
                ("T", ["T", "*", "F"]),
                ("T", ["F"]),
                ("F", ["(", "E", ")"]),
                ("F", ["id"]),
            ]
        )
        self.assertEqual(grammar_ext, expected)

    def test_closure(self):
        items = closure(set([(0, 0)]), grammar)
        expected = frozenset([
            (0, 0),
            (1, 0),
            (2, 0),
            (3, 0),
            (4, 0),
            (5, 0)
        ])
        self.assertEqual(items, expected)

    def test_goto(self):
        cc0 = closure(set([(0, 0)]), grammar)
        cc_i = goto(cc0, "E", grammar)
        expected = frozenset([
            (0, 1),
        ])

        self.assertEqual(cc_i, expected)

    def test_first(self):
        (q0, vn, vt, prods) = grammar
        first_table = first(grammar)
        for t in vt:
            self.assertEqual(first_table[t], set([t]))

        self.assertEqual(first_table["E"], set(["(", "id"]))
        self.assertEqual(first_table["T"], set(["(", "id"]))
        self.assertEqual(first_table["F"], set(["(", "id"]))

    def test_follow(self):
        (q0, vn, vt, prods) = grammar
        first_table = first(grammar)
        follow_table = follow(grammar, first_table)

        self.assertEqual(follow_table["E"], set([EOF, "+", ")"]))
        self.assertEqual(follow_table["T"], set([EOF, "+", "*", ")"]))
        self.assertEqual(follow_table["F"], set([EOF, "+", "*", ")"]))

    def test_parse(self):
        (ok) = parse(grammar, [("id", ), ("+", ), ("id",), (EOF, )])
        self.assertEqual(ok, True)




    def test_canonical_collection(self):
        q0, cc, goto_table = canonical_collection(grammar)

        self.assertEqual(q0, frozenset([
            (0, 0),
            (1, 0),
            (2, 0),
            (3, 0),
            (4, 0),
            (5, 0)
        ]))

        self.assertEqual(
            cc,
            set([
                frozenset([(2, 3)]),
                frozenset([
                    (2, 0),
                    (0, 0),
                    (5, 0),
                    (3, 0),
                    (1, 0),
                    (4, 0),
                    ]),
                frozenset([
                    (2, 0),
                    (0, 0),
                    (5, 0),
                    (3, 0),
                    (1, 0),
                    (4, 1),
                    (4, 0),
                    ]),
                frozenset([(0, 1)]),
                frozenset([(0, 1), (4, 2)]),
                frozenset([(1, 1), (2, 1)]),
                frozenset([(2, 2), (5, 0), (4, 0)]),
                frozenset([(3, 0), (2, 0), (0, 2), (5, 0), (4, 0)]),
                frozenset([(3, 1)]),
                frozenset([(5, 1)]),
                frozenset([(4, 3)]),
                frozenset([(0, 3), (2, 1)]),
            ])
        )

        self.assertEqual(
            goto_table,
            {
                (frozenset([(0, 1)]), '+'): frozenset([(3, 0), (2, 0), (0, 2), (5,
                        0), (4, 0)]),
                (frozenset([(3, 0), (2, 0), (0, 2), (5, 0), (4, 0)]), 'id'
                ): frozenset([(5, 1)]),
                (frozenset([
                    (2, 0),
                    (0, 0),
                    (5, 0),
                    (3, 0),
                    (1, 0),
                    (4, 0),
                    ]), 'E'): frozenset([(0, 1)]),
                (frozenset([
                    (2, 0),
                    (0, 0),
                    (5, 0),
                    (3, 0),
                    (1, 0),
                    (4, 1),
                    (4, 0),
                    ]), '('): frozenset([
                    (2, 0),
                    (0, 0),
                    (5, 0),
                    (3, 0),
                    (1, 0),
                    (4, 1),
                    (4, 0),
                    ]),
                (frozenset([(2, 2), (5, 0), (4, 0)]), 'id'): frozenset([(5, 1)]),
                (frozenset([
                    (2, 0),
                    (0, 0),
                    (5, 0),
                    (3, 0),
                    (1, 0),
                    (4, 0),
                    ]), 'T'): frozenset([(1, 1), (2, 1)]),
                (frozenset([(3, 0), (2, 0), (0, 2), (5, 0), (4, 0)]), 'T'
                ): frozenset([(0, 3), (2, 1)]),
                (frozenset([
                    (2, 0),
                    (0, 0),
                    (5, 0),
                    (3, 0),
                    (1, 0),
                    (4, 0),
                    ]), 'F'): frozenset([(3, 1)]),
                (frozenset([(0, 1), (4, 2)]), ')'): frozenset([(4, 3)]),
                (frozenset([(3, 0), (2, 0), (0, 2), (5, 0), (4, 0)]), 'F'
                ): frozenset([(3, 1)]),
                (frozenset([
                    (2, 0),
                    (0, 0),
                    (5, 0),
                    (3, 0),
                    (1, 0),
                    (4, 1),
                    (4, 0),
                    ]), 'E'): frozenset([(0, 1), (4, 2)]),
                (frozenset([(3, 0), (2, 0), (0, 2), (5, 0), (4, 0)]), '('
                ): frozenset([
                    (2, 0),
                    (0, 0),
                    (5, 0),
                    (3, 0),
                    (1, 0),
                    (4, 1),
                    (4, 0),
                    ]),
                (frozenset([
                    (2, 0),
                    (0, 0),
                    (5, 0),
                    (3, 0),
                    (1, 0),
                    (4, 0),
                    ]), '('): frozenset([
                    (2, 0),
                    (0, 0),
                    (5, 0),
                    (3, 0),
                    (1, 0),
                    (4, 1),
                    (4, 0),
                    ]),
                (frozenset([(0, 3), (2, 1)]), '*'): frozenset([(2, 2), (5, 0), (4,
                        0)]),
                (frozenset([
                    (2, 0),
                    (0, 0),
                    (5, 0),
                    (3, 0),
                    (1, 0),
                    (4, 1),
                    (4, 0),
                    ]), 'T'): frozenset([(1, 1), (2, 1)]),
                (frozenset([
                    (2, 0),
                    (0, 0),
                    (5, 0),
                    (3, 0),
                    (1, 0),
                    (4, 0),
                    ]), 'id'): frozenset([(5, 1)]),
                (frozenset([(2, 2), (5, 0), (4, 0)]), '('): frozenset([
                    (2, 0),
                    (0, 0),
                    (5, 0),
                    (3, 0),
                    (1, 0),
                    (4, 1),
                    (4, 0),
                    ]),
                (frozenset([(2, 2), (5, 0), (4, 0)]), 'F'): frozenset([(2, 3)]),
                (frozenset([
                    (2, 0),
                    (0, 0),
                    (5, 0),
                    (3, 0),
                    (1, 0),
                    (4, 1),
                    (4, 0),
                    ]), 'F'): frozenset([(3, 1)]),
                (frozenset([(1, 1), (2, 1)]), '*'): frozenset([(2, 2), (5, 0), (4,
                        0)]),
                (frozenset([(0, 1), (4, 2)]), '+'): frozenset([(3, 0), (2, 0), (0,
                        2), (5, 0), (4, 0)]),
                (frozenset([
                    (2, 0),
                    (0, 0),
                    (5, 0),
                    (3, 0),
                    (1, 0),
                    (4, 1),
                    (4, 0),
                    ]), 'id'): frozenset([(5, 1)]),
                }
        )

    def test_build_action_table(self):
        grammar_ext = grammar_with_fake_start(grammar)
        cc0, cc, goto_table = canonical_collection(grammar_ext)
        first_table = first(grammar_ext)
        follow_table = follow(grammar_ext, first_table)
        action_table = build_action_table(cc, goto_table, follow_table, grammar_ext)

        print_action_table(action_table, cc, grammar_ext)

        self.assertEqual(
            action_table,
            {
                (frozenset([(4, 1)]), ')'): [('reduce', 4)],
                (frozenset([(5, 3)]), '*'): [('reduce', 5)],
                (frozenset([(1, 2), (3, 0), (6, 0), (5, 0), (4, 0)]), 'id'
                ): [('shift', frozenset([(6, 1)]))],
                (frozenset([(5, 2), (1, 1)]), '+'): [('shift', frozenset([(1, 2),
                        (3, 0), (6, 0), (5, 0), (4, 0)]))],
                (frozenset([(0, 1), (1, 1)]), 'EOF'): [('accept', )],
                (frozenset([(3, 3)]), ')'): [('reduce', 3)],
                (frozenset([(3, 2), (6, 0), (5, 0)]), 'id'): [('shift',
                        frozenset([(6, 1)]))],
                (frozenset([(3, 1), (2, 1)]), '+'): [('reduce', 2)],
                (frozenset([(1, 3), (3, 1)]), '*'): [('shift', frozenset([(3, 2),
                        (6, 0), (5, 0)]))],
                (frozenset([(5, 3)]), ')'): [('reduce', 5)],
                (frozenset([(3, 3)]), 'EOF'): [('reduce', 3)],
                (frozenset([(5, 3)]), '+'): [('reduce', 5)],
                (frozenset([(6, 1)]), '+'): [('reduce', 6)],
                (frozenset([(4, 1)]), 'EOF'): [('reduce', 4)],
                (frozenset([
                    (2, 0),
                    (0, 0),
                    (5, 0),
                    (3, 0),
                    (1, 0),
                    (6, 0),
                    (4, 0),
                    ]), '('): [('shift', frozenset([
                    (2, 0),
                    (5, 0),
                    (3, 0),
                    (5, 1),
                    (1, 0),
                    (6, 0),
                    (4, 0),
                    ]))],
                (frozenset([(5, 3)]), 'EOF'): [('reduce', 5)],
                (frozenset([(3, 3)]), '*'): [('reduce', 3)],
                (frozenset([(1, 3), (3, 1)]), ')'): [('reduce', 1)],
                (frozenset([(3, 2), (6, 0), (5, 0)]), '('): [('shift', frozenset([
                    (2, 0),
                    (5, 0),
                    (3, 0),
                    (5, 1),
                    (1, 0),
                    (6, 0),
                    (4, 0),
                    ]))],
                (frozenset([(0, 1), (1, 1)]), '+'): [('shift', frozenset([(1, 2),
                        (3, 0), (6, 0), (5, 0), (4, 0)]))],
                (frozenset([(6, 1)]), '*'): [('reduce', 6)],
                (frozenset([(4, 1)]), '+'): [('reduce', 4)],
                (frozenset([(6, 1)]), 'EOF'): [('reduce', 6)],
                (frozenset([(3, 3)]), '+'): [('reduce', 3)],
                (frozenset([(1, 3), (3, 1)]), 'EOF'): [('reduce', 1)],
                (frozenset([(3, 1), (2, 1)]), 'EOF'): [('reduce', 2)],
                (frozenset([(5, 2), (1, 1)]), ')'): [('shift', frozenset([(5,
                        3)]))],
                (frozenset([
                    (2, 0),
                    (5, 0),
                    (3, 0),
                    (5, 1),
                    (1, 0),
                    (6, 0),
                    (4, 0),
                    ]), '('): [('shift', frozenset([
                    (2, 0),
                    (5, 0),
                    (3, 0),
                    (5, 1),
                    (1, 0),
                    (6, 0),
                    (4, 0),
                    ]))],
                (frozenset([(3, 1), (2, 1)]), ')'): [('reduce', 2)],
                (frozenset([(4, 1)]), '*'): [('reduce', 4)],
                (frozenset([(6, 1)]), ')'): [('reduce', 6)],
                (frozenset([
                    (2, 0),
                    (0, 0),
                    (5, 0),
                    (3, 0),
                    (1, 0),
                    (6, 0),
                    (4, 0),
                    ]), 'id'): [('shift', frozenset([(6, 1)]))],
                (frozenset([(1, 2), (3, 0), (6, 0), (5, 0), (4, 0)]), '('
                ): [('shift', frozenset([
                    (2, 0),
                    (5, 0),
                    (3, 0),
                    (5, 1),
                    (1, 0),
                    (6, 0),
                    (4, 0),
                    ]))],
                (frozenset([(3, 1), (2, 1)]), '*'): [('shift', frozenset([(3, 2),
                        (6, 0), (5, 0)]))],
                (frozenset([(1, 3), (3, 1)]), '+'): [('reduce', 1)],
                (frozenset([
                    (2, 0),
                    (5, 0),
                    (3, 0),
                    (5, 1),
                    (1, 0),
                    (6, 0),
                    (4, 0),
                    ]), 'id'): [('shift', frozenset([(6, 1)]))],
                }
        )



if __name__ == '__main__':
    unittest.main()
