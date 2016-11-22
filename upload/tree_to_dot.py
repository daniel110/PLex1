"""
File with functions to draw a tree represented by tuples using DOT.

--- DO NOT MODIFY THIS FILE ---
"""


def tree_to_dot(tree):
    """
    Convert a parse tree to Graphviz dot format and return it.

    Tree should be a tree, represented by tuples of the
    structure:
    (label, (child1, child2, ..., childN))

    where the the children are either trees themselves, or values that
    represent leafs.

    """
    nodes = [] # list of (number, label)
    edges = [] # list of (number, number)

    def convert(t):
        if type(t) is not tuple:
            t = (t, ())
        n = len(nodes)
        nodes.append((n, t[0]))
        children = [convert(c) for c in t[1]]
        edges.extend((n, m) for m in children)
        return n

    convert(tree)

    dot = 'digraph G {\n'
    for n, label in nodes:
        dot += '    {} [label="{}"];\n'.format(n, label.replace('"', '\\"'))
    dot += '\n'
    for n, m in edges:
        dot += '    {} -> {};\n'.format(n, m)
    dot += '}'
    return dot

def view(x):
    try:
        import graphviz
    except ImportError:
        return
    d = graphviz.Digraph(body=x.splitlines()[1:-1])
    d.render(view=True)

def view_tree(tree):
    dot = tree_to_dot(tree)
    print dot
    view(dot)

if __name__ == '__main__':
    tree = ('E', (('E', ('1', '+', '2')), '+', ('E', ('4', '+', '5'))))
    view_tree(tree)
