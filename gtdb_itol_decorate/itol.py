from collections import deque, defaultdict
from pathlib import Path
from typing import Dict, Set

import dendropy
from gtdblib.file.itol.collapse import iTolCollapseFile
from gtdblib.file.itol.dataset_color_strip import iTolDatasetColorStripFile
from gtdblib.file.itol.label import iTolLabelFile
from gtdblib.file.itol.popup import iTolPopupFile
from gtdblib.file.itol.tree_colors import iTolTreeColorsFile
from gtdblib.taxonomy.taxonomy import Taxonomy
from gtdblib.util.color import TABLEAU_20, rgb_to_hex

from gtdb_itol_decorate.newick import parse_label

import seaborn as sns

from gtdb_itol_decorate.util import canonical_gid


def get_lca_str(node: dendropy.Node):
    if node.is_leaf():
        return node.taxon.label
    if len(node.child_nodes()) < 2:
        return node.child_nodes()[0].leaf_nodes()[0].taxon.label
    left = node.child_nodes()[0].leaf_nodes()[0]
    right = node.child_nodes()[1].leaf_nodes()[0]
    return f'{left.taxon.label}|{right.taxon.label}'



def get_phylum_colours(d_phylum_to_lca):
    """Generate a list of colours for each phylum. Order is inferred through a
    depth first search, to ensure no clade colours are side by side.
    """
    colours = TABLEAU_20

    d_phylum_to_colour = dict()
    for phylum in d_phylum_to_lca.keys():
        d_phylum_to_colour[phylum] = colours[len(d_phylum_to_colour) % len(colours)]

    # Generate a colour palette for each phylum (increasing brightness)
    out = dict()
    for phylum, colour in d_phylum_to_colour.items():
        cur_pal = sns.light_palette(colour, 6, reverse=True)
        out[phylum] = [rgb_to_hex(*[round(y * 255) for y in x]) for x in cur_pal]
    return out


def get_phylum_to_lca(tree: dendropy.Tree):
    """Calculate the LCA for each phylum. Considers singletons."""
    out = defaultdict(list)
    for node in tree.postorder_node_iter():
        # Consider the case where the domain shares the same label as the phylum
        if len(node.tax_label) > 0:
            if len(node.tax_label) >= 2:
                if node.tax_label[0].startswith('d__') and node.tax_label[1].startswith('p__'):
                    out[node.tax_label[1]].append(get_lca_str(node))
            else:
                if node.tax_label[0].startswith('p__'):
                    out[node.tax_label[0]].append(get_lca_str(node))
    return out



def write_color_datastrip(d_phylum_to_lca, d_phylum_palette, path):
    file = iTolDatasetColorStripFile(path, 'Phylum Labels', '#000000', strip_width=100, show_internal=True)

    for phylum, lst_node_ids in d_phylum_to_lca.items():
        colour = d_phylum_palette[phylum][0]

        for node_id in lst_node_ids:
            file.insert(node_id, colour, phylum)

    file.write()
    return


def get_internal_nodes_with_labels(tree: dendropy.Tree):
    out = defaultdict(list)
    for node in tree.preorder_node_iter():
        if len(node.tax_label) > 0:
            out[';'.join(node.tax_label)].append(get_lca_str(node))
    return out

def write_internal_node_labels( d_label_to_lca,path: Path):
    file = iTolLabelFile(path)

    # 1. Add internal node labels (trivial)
    for label, lst_lr_nodes in d_label_to_lca.items():
        for lr_nodes in lst_lr_nodes:
            file.insert(lr_nodes, label)
    file.write()



def write_tree_colours(tree, d_taxon_to_phylum, path, d_color_palette):
    file = iTolTreeColorsFile(path)

    ranks = ('p', 'c', 'o', 'f', 'g', 's')

    for node in tree.preorder_node_iter():
        if len(node.tax_label) > 0:
            highest_taxon = node.tax_label[0]

            # Ignore domain label
            if highest_taxon.startswith('d__'):
                continue

            # Get the highest rank label
            if highest_taxon.startswith('p__'):
                phylum = highest_taxon
            else:
                phylum = d_taxon_to_phylum[highest_taxon]

            phylum_palette = d_color_palette[phylum]
            colour_idx = ranks.index(highest_taxon[0])
            colour = phylum_palette[colour_idx]
            label = ';'.join(node.tax_label)
            file.insert_range(get_lca_str(node), colour, label)

    file.write()



def write_collapse_file(d_int_label_to_lca, path, taxon_prefix):
    file = iTolCollapseFile(path)
    for taxon, lst_lr_nodes in d_int_label_to_lca.items():
        if taxon.startswith(taxon_prefix):
            for lr_node in lst_lr_nodes:
                if '|' in lr_node:
                    file.insert(lr_node)
    file.write()

def write_popup_file(tree: dendropy.Tree, d_tax: Dict[str, Taxonomy], path: Path):
    file = iTolPopupFile(path)

    for leaf_node in tree.leaf_node_iter():
        gid = leaf_node.taxon.label
        row = d_tax[gid]
        branch_length = leaf_node.edge_length
        lines = [
            '<b>Genome ID</b>: ' + gid,
            '<br><b>Branch Length</b>: ' + str(branch_length),
            '<br><b>Domain</b>: ' + row.d.value,
            '<br><b>Phylum</b>: ' + row.p.value,
            '<br><b>Class</b>: ' + row.c.value,
            '<br><b>Order</b>: ' + row.o.value,
            '<br><b>Family</b>: ' + row.f.value,
            '<br><b>Genus</b>: ' + row.g.value,
            '<br><b>Species</b>: ' + row.s.value,
        ]
        file.insert(gid, row.s.value, ''.join(lines))

    file.write()
    return