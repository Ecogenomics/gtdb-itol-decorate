from datetime import datetime


def log(msg: str, title=False):
    if title:
        print('\n' + '-' * 80)
    print(f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] - {msg}')
    if title:
        print('-' * 80)

def canonical_gid(gid):
    """Get canonical form of NCBI genome accession.

    Example:
        G005435135 -> G005435135
        GCF_005435135.1 -> G005435135
        GCF_005435135.1_ASM543513v1_genomic -> G005435135
        RS_GCF_005435135.1 -> G005435135
        GB_GCA_005435135.1 -> G005435135
    """

    if gid.startswith('U'):
        return gid

    gid = gid.replace('RS_', '').replace('GB_', '')
    gid = gid.replace('GCA_', 'G').replace('GCF_', 'G')
    if '.' in gid:
        gid = gid[0:gid.find('.')]

    return gid



def is_float(s):
    """Check if a string can be converted to a float.

    Parameters
    ----------
    s : str
        String to evaluate.

    Returns
    -------
    boolean
        True if string can be converted, else False.
    """

    try:
        float(s)
    except ValueError:
        return False

    return True