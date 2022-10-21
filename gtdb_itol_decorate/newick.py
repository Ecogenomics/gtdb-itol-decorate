import dendropy
from collections import Counter, deque, defaultdict

from gtdb_itol_decorate.util import canonical_gid, log, is_float


def load_newick_file(path: str) -> str:
    """Read a newick file and remove any extra information (e.g IQTree) annotations."""
    lines = list()
    found_start = False
    with open(path) as f:
        for line in f.readlines():
            line = line.strip()
            if line.startswith('('):
                found_start = True
            if found_start:
                lines.append(line)
    return ''.join(lines)


def load_newick_to_tree(path: str) -> dendropy.Tree:
    str_tree = load_newick_file(path)
    return dendropy.Tree.get_from_string(str_tree,
                                         schema='newick',
                                         rooting='force-rooted',
                                         preserve_underscores=True)

def validate_dendropy_namespace(taxa):
    taxa_count = Counter(taxa)
    duplicates = {k: v for k, v in taxa_count.items() if v > 1}
    if len(duplicates) > 0:
        raise ValueError(f'The following taxa appear more than once: {duplicates}')
    return


def get_canonical_mapping(gids):
    out = dict()
    for gid in gids:
        out[canonical_gid(gid)] = gid
    return out

def validate_sets(newick_gids, tax_gids):
    if newick_gids != tax_gids:
        log('The following genomes are in the newick file but not in the taxonomy file:')
        for gid in newick_gids - tax_gids:
            log(gid)
        raise Exception(f'The newick file and taxonomy file contain different genomes.')


def parse_label(label):
    """Parse a Newick label which may contain a support value, taxon, and/or auxiliary information.

    Parameters
    ----------
    label : str
        Internal label in a Newick tree.

    Returns
    -------
    float
        Support value specified by label, or None
    str
        Taxon specified by label, or None
    str
        Auxiliary information, on None
    """

    support = None
    taxon = None
    auxiliary_info = None

    if label:
        label = label.strip()
        if '|' in label:
            label, auxiliary_info = label.split('|', 1)

        if ':' in label:
            support, taxon = label.split(':')
            support = float(support)
        else:
            if is_float(label):
                support = float(label)
            elif label != '':
                taxon = label

    return support, taxon, auxiliary_info

def strip_tree_labels(tree: dendropy.Tree):
    for node in tree.preorder_node_iter():
        if node.is_leaf():
            continue
        support, taxon, auxiliary_info = parse_label(node.label)
        if taxon:
            node.label = str(support)
    return

def get_node_depth(tree: dendropy.Tree):
    """Return the depth of every node in a tree."""
    depth_to_nodes = defaultdict(list)

    queue = deque([(tree.seed_node, 0)])
    while len(queue) > 0:
        node, depth = queue.popleft()
        depth_to_nodes[depth].append(node)
        for child in node.child_nodes():
            queue.append((child, depth + 1))
    return depth_to_nodes


def set_node_desc_taxa(tree: dendropy.Tree):
    # Get the depth of every node
    depth_to_nodes = get_node_depth(tree)

    # Iterate from the leaf nodes upwards, bringing up the desc taxa
    for depth, nodes in sorted(depth_to_nodes.items(), reverse=True):
        for node in nodes:
            if node.is_leaf():
                node.desc_taxa = {node.taxon.label}
            else:
                node.desc_taxa = set()
                for child in node.child_nodes():
                    node.desc_taxa.update(child.desc_taxa)

    return


def set_taxon_label_for_internal_nodes(tree: dendropy.Tree, d_tax):
    # Find the highest internal node that forms a monophyletic group

    ranks = ('d', 'p', 'c', 'o', 'f', 'g', 's')

    queue = deque([(tree.seed_node, 'd')])
    while len(queue) > 0:
        node, target_rank = queue.popleft()

        if not hasattr(node, 'tax_label'):
            node.tax_label = list()

        # Check if this forms a monophyletic group at the target taxon
        desc_taxa = {getattr(d_tax[x], target_rank).value for x in node.desc_taxa}
        if len(desc_taxa) == 1:
            node.tax_label.append(list(desc_taxa)[0])

            # Re-queue this node at the front, in-case it can be extended
            if target_rank != 's':
                next_rank = ranks[ranks.index(target_rank)+1]
                queue.appendleft((node, next_rank))

        # Otherwise, keep going down
        else:
            for child in node.child_nodes():
                queue.append((child, target_rank))
    return
