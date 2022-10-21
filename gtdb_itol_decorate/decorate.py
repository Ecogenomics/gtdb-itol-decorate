from collections import defaultdict



def decorate_tree(tree, d_gid_to_tax):

    d_node_to_leaf_taxa = defaultdict(set)
    for node in tree.postorder_node_iter():
        # desc_taxa = get_node_desc_taxa(node)

        print(node)


    # Create a mapping from the taxon to each gid
    d_taxon_to_gids = defaultdict(set)
    for gid, taxon in d_gid_to_tax.items():
        d_taxon_to_gids[taxon.p.value].add(gid)
        d_taxon_to_gids[taxon.c.value].add(gid)
        d_taxon_to_gids[taxon.o.value].add(gid)
        d_taxon_to_gids[taxon.f.value].add(gid)
        d_taxon_to_gids[taxon.g.value].add(gid)
        d_taxon_to_gids[taxon.s.value].add(gid)

    # Find the highest node that forms a monophyletic group
    d_node_to_taxa = defaultdict(set)
    for taxon, gids in d_taxon_to_gids.items():
        mrca_node = tree.mrca(taxon_labels=gids)

        # This is the seed node, so we can't decorate it
        if mrca_node.parent_node is None:
            continue

        d_node_to_taxa[mrca_node].add(taxon)
    return d_node_to_taxa
