from copy import deepcopy

# grammar = (S string, VN set[string], VT set[string], prods)
# prod = (head, body)
# prods = [prod]
# item = (i_prod, i_stacktop)
# state = items = set[item]
# canonical_collection = set[state]

# action_table[state, string] =
# ("shift", t_string)
# ("reduce", i_prod)
# ("accept")

# goto_table[state, NT string] = next_state


# fns

# state = closure(state)
# state = goto(state, Symbol string)
# [state] = canonical_collection(grammar)
# parse(tokens)
# first
# follow

# helpers
# prod = item_to_prod(item, prods)
# stacktop = item_to_stacktop(item, prods)
# grammarI = grammar_with_fake_start(grammar)

FAKE_S = "FAKE_S"
EOF = "EOF"
SHIFT = "shift"
REDUCE = "reduce"
ACCEPT = "accept"
LAMBDA = "lambda"

def grammar_with_fake_start(grammar):
    (prev_q0, vn, vt, prods) = deepcopy(grammar)
    q0 = FAKE_S
    vn.insert(0, q0)
    vt.append(EOF)
    prods.insert(0, (q0, [prev_q0]))
    return (q0, vn, vt, prods)

def canonical_collection(grammar):
    (q0, vn, vt, prods) = grammar
    grammar_symbols = vn + vt

    goto_table = { }

    q0_item = (0, 0)
    cc0 = closure(set([q0_item]), grammar)
    cc = set([cc0])


    while True:
        new_ccs = set([])
        for cc_i in cc:
            for symbol in grammar_symbols:
                cc_next = goto(cc_i, symbol, grammar)
                if len(cc_next) > 0 :
                    new_ccs.add(cc_next)
                    goto_table[(cc_i, symbol)] = cc_next

        if new_ccs <= cc:
            break
        else:
            cc = cc.union(new_ccs)

    return (cc0, cc, goto_table)



def closure(items, grammar):
    (q0, vn, vt, prods) = grammar

    clo = items
    while True:
        new_items = set([])
        for item in clo:
            stacktop = item_to_stacktop(item, grammar)
            if stacktop != None and stacktop not in vn:
                continue
            for prod_index, (head, body) in get_prods_with_head(stacktop, grammar):
                new_item = (prod_index, 0)
                new_items.add(new_item)

        if new_items <= clo:
            break
        else:
            clo = clo.union(new_items)

    return frozenset(clo)


def goto(cc_i, symbol, grammar):
    (q0, vn, vt, prods) = grammar
    items = set([])

    for item in cc_i:
        stacktop = item_to_stacktop(item, grammar)
        if symbol == stacktop:
            new_item = (item[0], item[1] + 1)
            items.add(new_item)

    return closure(items, grammar)



def build_action_table(cc, goto_table, follow_table, grammar):
    (_, _, vt, _) = grammar
    action_table = {}

    for cc_i in cc:
        for item in cc_i:
            stacktop = item_to_stacktop(item, grammar)

            if not (item_is_complete(item, grammar) or stacktop in vt):
                continue

            head, body = item_to_prod(item, grammar)
            # print head, body

            if head == FAKE_S:
                action_table.setdefault((cc_i, EOF), []).append((ACCEPT,))
            elif item_is_complete(item, grammar):
                for a in follow_table[head]:
                    action_table.setdefault((cc_i, a), []).append((REDUCE, item[0]))
            else:
                next_state = goto_table.get((cc_i, stacktop))
                action_table.setdefault((cc_i, stacktop), []).append((SHIFT, next_state))

    return action_table


def first(grammar):
    (q0, vn, vt, prods) = grammar
    first_table = {}
    first_table_snapshot = {}

    for t in vt:
        first_table[t] = set([t])

    for nt in vn:
        first_table[nt] = set([])

    while first_table != first_table_snapshot:
        first_table_snapshot = deepcopy(first_table)
        for head, body in prods:
            rhs = set([])
            for i, b in enumerate(body):
                if i == 0 or LAMBDA in first_table[body[i - 1]]:
                    if i == len(body) - 1:
                        rhs = rhs.union(first_table[b])
                    else:
                        rhs = rhs.union(first_table[b] - set([LAMBDA]))

            first_table[head] = first_table[head].union(rhs)

    return first_table

def follow(grammar, first_table):
    (q0, vn, vt, prods) = grammar
    follow_table = {}
    follow_table_snapshot = {}

    for nt in vn:
        follow_table[nt] = set([])

    follow_table[q0] = set([EOF])

    while follow_table != follow_table_snapshot:
        follow_table_snapshot = deepcopy(follow_table)
        for head, body in prods:
            trailer = follow_table[head]
            for b in reversed(body):
                if b in vt:
                    trailer = set([b])
                else:
                    follow_table[b] = follow_table[b].union(trailer)
                    if LAMBDA in first_table[b]:
                        trailer = trailer.union(first_table[b] - set([LAMBDA]))
                    else:
                        trailer = first_table[b]

    return follow_table






def parse(grammar, tokens):
    grammar = grammar_with_fake_start(grammar)
    cc0, cc, goto_table = canonical_collection(grammar)
    first_table = first(grammar)
    follow_table = follow(grammar, first_table)
    action_table = build_action_table(cc, goto_table, follow_table, grammar)
    stack = [cc0]
    token_index = 0
    ok = True
    while True:
        print "ITER"
        print(token_index)
        print_stack(stack, cc)

        token = tokens[token_index]
        print "token", token
        stacktop_state = stack[-1]
        actions = action_table.get((stacktop_state, token[0]))
        action = actions[0]
        print "ACTION", action

        if action[0] == SHIFT:
            next_state = action[1]
            stack.append(next_state)
            token_index += 1

        elif action[0] == REDUCE:
            prod_index= action[1]
            prods = grammar[3]
            (head, body) = prods[prod_index]
            for _ in range(len(body)):
                stack.pop()
            stacktop_state = stack[-1]
            next_state = goto_table.get((stacktop_state, head), "DEFAULT2")
            stack.append(next_state)
            print("reducing by % -> %", (head, body))

        elif action[0] == ACCEPT:
            break
        else:
            print "ERROR"
            print_stack(stack, cc, True)
            ok = False
            break

    return (ok)

##################
# Helpers
###################

def item_to_stacktop(item, grammar):
    (_, _, _, prods) = grammar
    (prod_index, stacktop_index) = item
    (head, body) = prods[prod_index]
    if stacktop_index >= len(body):
        # Complete Item
        return None
    else:
        stacktop = body[stacktop_index]
        return stacktop

def item_to_prod(item, grammar):
    (_, _, _, prods) = grammar
    (prod_index, _) = item
    return prods[prod_index]


def item_is_complete(item, grammar):
    res = item_to_stacktop(item, grammar)
    if res == None:
        return True
    else:
        return False



def get_prods_with_head(desired_head, grammar):
    if desired_head == None:
        return []
    (_, _, _, prods) = grammar
    result = []
    for prod_index, (current_head, body) in enumerate(prods):
        if current_head != desired_head:
            continue
        result.append((prod_index, (current_head, body)))
    return result


def print_goto_table(goto_table, cc):
    id_map = {}
    cc_list = list(cc)

    print "INDEX"
    for i, cc_i in enumerate(cc_list):
        id_map[cc_i] = i
        print "{0} -> {1}".format(i, cc_i)

    print "GOTO"
    for key, next_state in goto_table.iteritems():
        state, symbol = key
        print "{0:<10} {1:<10} -> {2}".format(id_map.get(state), symbol, id_map.get(next_state))

def print_action_table(action_table, cc, grammar):
    id_map = {}
    cc_list = list(cc)

    print "INDEX"
    for i, cc_i in enumerate(cc_list):
        id_map[cc_i] = i
        print "{0} -> {1}".format(i, cc_i)

    print "ACTION"
    for key, actions in action_table.iteritems():
        state, symbol = key
        action_str = []
        for action in actions:
            if action[0] == ACCEPT:
                action_str.append("ACCEPT")
            elif action[0] == REDUCE:
                action_str.append("Reduce {0}".format(prod_to_string(grammar[3][action[1]])))
            elif action[0] == SHIFT:
                action_str.append("Shift {0}".format(id_map.get(action[1])))

        print "{0:<10} {1:<10} -> {2}".format(id_map.get(state), symbol, "".join(action_str))

def print_stack(stack, cc, index=False):
    id_map = {}
    cc_list = list(cc)

    if index:
        print "INDEX"
        for i, cc_i in enumerate(cc_list):
            id_map[cc_i] = i
            print "{0} -> {1}".format(i, cc_i)

    print "STACK"
    for state in reversed(stack):
        print "{0}".format(id_map.get(state, "FUCKED UP"))

    print "======="

def prod_to_string(prod):
    head, body = prod
    return "{0} -> {1}".format(head, " ".join(body))




if __name__ == '__main__':
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
    print parse(grammar, [("id", ), ("+", ), ("id", ), (EOF, )])
