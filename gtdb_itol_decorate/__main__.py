from pathlib import Path

import typer

from gtdb_itol_decorate.gtdb import load_taxonomy_file, get_taxon_to_phylum
from gtdb_itol_decorate.itol import get_phylum_to_lca, get_phylum_colours, write_color_datastrip, \
    get_internal_nodes_with_labels, write_internal_node_labels, write_tree_colours, write_collapse_file, \
    write_popup_file
from gtdb_itol_decorate.newick import load_newick_to_tree, validate_dendropy_namespace, \
    get_canonical_mapping, validate_sets, strip_tree_labels, set_node_desc_taxa, set_taxon_label_for_internal_nodes
from gtdb_itol_decorate.util import log


def main(tree_path: Path, tax_path: Path, out_dir: Path):
    log(f'Creating output directory: {out_dir}')
    out_dir.mkdir(exist_ok=True)

    log(f'Reading tree from: {tree_path}')
    tree = load_newick_to_tree(str(tree_path))
    log(f'Found {len(tree.leaf_nodes()):,} leaf nodes in the tree.')
    validate_dendropy_namespace((x.label for x in tree.taxon_namespace))
    d_canonical_to_gid = get_canonical_mapping((x.label for x in tree.taxon_namespace))

    log(f'Reading taxonomy from: {tax_path}')
    d_tax = load_taxonomy_file(str(tax_path), set(d_canonical_to_gid.keys()))
    log(f'Read the taxonomy for {len(d_tax):,} genomes.')
    validate_sets(set(d_canonical_to_gid.keys()), set(d_tax.keys()))

    log('Reverse mapping taxon to phylum')
    d_taxon_to_phylum = get_taxon_to_phylum(d_tax)

    log('Annotating internal nodes with descendant taxa')
    set_node_desc_taxa(tree)
    set_taxon_label_for_internal_nodes(tree, d_tax)

    log('Getting the last common ancestor of each phylum.')
    d_phylum_to_lca = get_phylum_to_lca(tree)
    d_phylum_palette = get_phylum_colours(d_phylum_to_lca)
    write_color_datastrip(d_phylum_to_lca, d_phylum_palette, out_dir / 'itol_dataset_strip_phylum.txt')

    log('Making tree compatible with iTOL (stripping labels)')
    strip_tree_labels(tree)
    path_tree_out = out_dir / f'{tree_path.name}_stripped'
    tree.write_to_path(path_tree_out, schema='newick', suppress_rooting=True, unquoted_underscores=True)

    log('Writing internal node labels')
    d_int_label_to_lca = get_internal_nodes_with_labels(tree)
    write_internal_node_labels(d_int_label_to_lca, out_dir / 'itol_labels.txt')

    log('Getting tree colour palette')
    write_tree_colours(tree, d_taxon_to_phylum, out_dir / 'itol_tree_colours.txt', d_phylum_palette)

    log('Writing popup information file')
    write_popup_file(tree, d_tax, out_dir / 'itol_popup.txt')

    log('Writing collapse files')
    write_collapse_file(d_int_label_to_lca, out_dir / 'itol_collapse_phylum.txt', 'p__')
    write_collapse_file(d_int_label_to_lca, out_dir / 'itol_collapse_class.txt', 'c__')
    write_collapse_file(d_int_label_to_lca, out_dir / 'itol_collapse_order.txt', 'o__')
    write_collapse_file(d_int_label_to_lca, out_dir / 'itol_collapse_family.txt', 'f__')
    write_collapse_file(d_int_label_to_lca, out_dir / 'itol_collapse_genus.txt', 'g__')
    log('Done.')


def app():
    typer.run(main)


if __name__ == "__main__":
    typer.run(main)
