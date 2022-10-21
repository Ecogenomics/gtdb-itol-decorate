from collections import defaultdict
from typing import Dict

from gtdblib.taxon.rank import TaxonRank
from gtdblib.taxon.taxon import Taxon
from gtdblib.taxonomy.taxonomy import Taxonomy

from gtdb_itol_decorate.util import canonical_gid


def load_taxonomy_file(path: str, limit_to_gids: set):
    gtdb_ranks = [TaxonRank.DOMAIN, TaxonRank.PHYLUM, TaxonRank.CLASS,
                   TaxonRank.ORDER, TaxonRank.FAMILY, TaxonRank.GENUS,
                   TaxonRank.SPECIES]
    out = dict()
    with open(path) as f:
        for line in f.readlines():
            gid, tax = line.strip().split('\t')
            gid = canonical_gid(gid)
            if gid not in limit_to_gids:
                continue
            if gid in out:
                raise Exception(f'Duplicate genome id found: {gid}')
            ranks = tax.split(';')
            if len(ranks) != 7:
                raise Exception(f'Invalid taxonomy for {gid} (expected 7 ranks): {tax}')

            d_rank_to_taxon = dict()
            for rank, taxon_rank in zip(ranks, gtdb_ranks):
                taxon = Taxon(taxon_rank, rank)
                d_rank_to_taxon[taxon_rank.value[0]] = taxon
            taxonomy = Taxonomy(**d_rank_to_taxon)
            out[gid] = taxonomy
    return out



def get_taxon_to_phylum(d_tax: Dict[str, Taxonomy]):
    out = dict()
    for gid, taxonomy in d_tax.items():
        for rank in ('c', 'o', 'f', 'g', 's'):
            taxon = getattr(taxonomy, rank).value
            out[taxon] = taxonomy.p.value
    return out

