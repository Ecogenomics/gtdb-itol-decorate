# gtdb-itol-decorate

Creates iTOL files for tree decoration, given a set of GTDB genomes.

## Installation

```bash
pip install gtdb-itol-decorate
```

## Usage

This program requires a taxonomy file (available from the [GTDB website](https://data.gtdb.ecogenomic.org/releases/latest/)), 
e.g. `bac120_taxonomy.tsv`, or `ar53_taxonomy.tsv`.

```bash
gtdb_itol_decorate /path/to/tree.tree /path/to/taxonomy.tsv /path/to/output
```

## Output

![](docs/itol_example.svg?raw=true)


The program will output the following files.

Note: Typical use will be:

1. Upload `[name_of_input_tree].tree_stripped`
2. Drag the following files into the tree: `itol_dataset_strip_phylum.txt`, `itol_labels.txt`, `itol_popup.txt`, `itol_tree_colours.txt`
3. Use the `itol_collapse_[rank].txt` files to manipulate the view of the tree as desired.


### [name_of_input_tree].tree_stripped

This is the tree that you should upload to iTOL. It has been stripped of all
internal labels to match the iTOL tree format.

### itol_collapse_[rank].txt

When this file is dropped into the iTOL tree, it will [collapse](https://itol.embl.de/help.cgi#coll)
all nodes at this rank.

### itol_dataset_strip_phylum.txt

This file will create a new [colour strip](https://itol.embl.de/help.cgi#strip) 
for each phylum.

![](docs/itol_dataset_strip.svg?raw=true)

### itol_labels.txt

This will add taxon [labels](https://itol.embl.de/help.cgi#textlabels) 
to the tree for both the internal and leaf nodes.

Note: To enable internal labels:

* Open the "Control panel"
* Select the "Advanced" tab.
* Under "Branch metadata display", make sure "Node IDs" is set to "Display".

![](docs/itol_labels.svg?raw=true)

### itol_popup.txt

This creates a [popup](https://itol.embl.de/help.cgi#popup) window when the 
mouse is hovered over each leaf node. It will display the genome id, and full 
taxonomy string.

### itol_tree_colours.txt

Creates a [colour range](https://itol.embl.de/help.cgi#colors) for each taxon, 
based on the phylum colour. It will increase in brightness from phylum to species.

Note: This can be changed by altering the "Coloured ranges" popup that will
appear after adding this file. In the "Cover" option, "Clade" view is recommended.

![](docs/itol_tree_colours.svg?raw=true)
