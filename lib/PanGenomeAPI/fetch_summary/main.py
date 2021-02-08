"""
Fetch and construct summary data for previewing a pangenome.
"""
from installed_clients.WorkspaceClient import Workspace as Workspace


def fetch_pangenome_summary(
        pangenome_ref: str,
        workspace_url: str,
        token: str) -> dict:
    """
    Construct a summary data object for a single pangenome, used in the
    "simple_summary" method.
    Args:
        pangenome_ref: Workspace reference to the pangenome object
        workspace_url: URL of the Workspace being used in the current env
        token: authorization token for fetching the data
    Returns:
        A python object adhering to the SimpleSummaryResult type in
        PanGenomeAPI.spec
    """
    ws_client = Workspace(workspace_url, token=token)
    # Download the full pangenome workspace dataset
    resp = ws_client.get_objects2({
        'objects': [{'ref': pangenome_ref}]
    })
    data = resp['data'][0]['data']
    # Fetch the object infos for each genome
    genome_refs = [{"ref": ref} for ref in data["genome_refs"]]
    genome_infos = ws_client.get_object_info3({
        "objects": genome_refs,
        "includeMetadata": 1
    })["infos"]
    name_mapping = _genome_name_mapping(genome_infos)
    ret = {
        "pangenome_id": data["id"],
        "genomes_count": len(data["genome_refs"]),
        "genes": _count_genes(data),
        "families": _count_families(data),
        "genomes": _genome_counts(data, genome_infos, name_mapping),
        "shared_family_map": _shared_family_map(data, name_mapping),
        "genome_ref_name_map": name_mapping,
    }
    return ret


def _count_genes(pg_data: dict) -> dict:
    """
    Calculate gene counts for a pangenome object
    Args:
        pg_data: workspace data object for the Pangenome
    Returns:
        Dict of counts with the GeneFamilyReport type in PanGenomeAPI.spec
    """
    counts = {
        "genes_count": 0,
        "homolog_family_genes_count": 0,
        "singleton_family_genes_count": 0,
    }
    for family in pg_data["orthologs"]:
        count = len(family["orthologs"])
        counts["genes_count"] += count
        if count == 1:
            counts["singleton_family_genes_count"] += count
        elif count > 1:
            counts["homolog_family_genes_count"] += count
    return counts


def _count_families(pg_data: dict) -> dict:
    """
    Aggregate counts for the homolog families in the pangenome
    Args:
        pg_data: workspace data object for the Pangenome
    Returns:
        dict matching the type FamilyReport from PanGenomeAPI.spec
    """
    counts = {
        "families_count": 0,
        "homolog_families_count": 0,
        "singleton_families_count": 0,
    }
    counts["families_count"] = len(pg_data["orthologs"])
    for family in pg_data["orthologs"]:
        count = len(family["orthologs"])
        if count == 1:
            counts["singleton_families_count"] += 1
        elif count > 1:
            counts["homolog_families_count"] += 1
    return counts


def _genome_name_mapping(genome_infos: list) -> dict:
    """
    Construct a mapping of genome workspace reference to sciname
    Args:
        pg_data: workspace data object for the Pangenome
        genome_infos: list of object info tuples (with metadata) for every
            genome in the pangenome
    Returns:
        Mapping of genome ref to scientific name and obj name
    """
    ret = {}
    names = set()
    # Fetch the object infos for every ref
    for info in genome_infos:
        ref = _get_ref(info)
        sciname = info[-1].get("Name", "unknown taxon")
        # Create a unique display name for each genome
        name = sciname
        if name in names:
            name = f"{sciname} ({ref})"
        names.add(name)
        ret[ref] = name
    return ret


def _genome_counts(
        pg_data: dict,
        genome_infos: list,
        name_mapping: dict) -> dict:
    """
    Aggregate counts of genes and families for every genome
    Args:
        pg_data: workspace data object for the Pangenome
        genome_infos: list of genome info tuples for each object
        name_mapping: mapping of workspace ref to readable name for use as keys
    Returns:
        Mapping of genome ref to GenomeGeneFamilyReport (from
        PanGenomeAPI.spec)
    """
    # Initialize the result structure
    ret = {}
    for name in name_mapping.values():
        ret[name] = {
            "genome_genes": 0,
            "genome_homolog_family_genes": 0,
            "genome_singleton_family_genes": 0,
            "genome_homolog_family": 0,
        }
    # Set total feature counts from the obj info
    for info in genome_infos:
        key = name_mapping[_get_ref(info)]
        ret[key]["genome_genes"] = _get_feature_count(info)
    # Aggregate other counts from the ortholog families
    for family in pg_data["orthologs"]:
        count = len(family["orthologs"])
        found_genomes = set()
        for gene in family["orthologs"]:
            genome_ref = gene[2]
            key = name_mapping[genome_ref]
            if count > 1:
                ret[key]["genome_homolog_family_genes"] += 1
                found_genomes.add(genome_ref)
        for ref in found_genomes:
            ret[name_mapping[ref]]["genome_homolog_family"] += 1
    # Set the singleton family gene counts to be the difference of the total
    # features and the homolog family counts
    for ref in pg_data["genome_refs"]:
        key = name_mapping[ref]
        total = ret[key]["genome_genes"]
        homologs = ret[key]["genome_homolog_family_genes"]
        ret[key]["genome_singleton_family_genes"] = total - homologs
    return ret


def _shared_family_map(pg_data: dict, name_mapping: dict) -> dict:
    """
    Calculate the number of shared ortholog families between any two genomes
    Args:
        pg_data: workspace data object for the Pangenome
        name_mapping: mapping of workspace ref to readable name for use as keys
    Returns:
        dict where keys are genome refs, and values are mapping of genome refs
        to shared family counts.
        Example: {"1": {"2": 10}} represents genome "1" and "2" sharing 10
        families
    """
    # Initialize the return structure
    ret = {}
    for ref1 in pg_data["genome_refs"]:
        key1 = name_mapping[ref1]
        ret[key1] = {}
        for ref2 in pg_data["genome_refs"]:
            key2 = name_mapping[ref2]
            ret[key1][key2] = 0
    # Aggregate counts of all genomes that share genes in an ortholog family
    for family in pg_data["orthologs"]:
        if len(family["orthologs"]) <= 1:
            # We only record non-singletons
            continue
        genome_refs = set(orth[2] for orth in family["orthologs"])
        for ref1 in genome_refs:
            for ref2 in genome_refs:
                key1, key2 = name_mapping[ref1], name_mapping[ref2]
                ret[key1][key2] += 1
    return ret


def _get_feature_count(genome_info: dict) -> int:
    """
    Get the total feature count (coding and non-coding) for a genome.
    We fetch this number from the genome metadata.
    Older Genome versions store this as "Number features", while newer versions
    (>=9) store it as "Number of Protein Encoding Genes".
    Genome versions before 8 (older than July, 2014) have no metadata and
    aren't supported for now.
    """
    valid_keys = ("Number of Protein Encoding Genes", "Number features")
    meta = genome_info[-1]
    for key in valid_keys:
        if key in meta:
            return int(meta[key])
    # TODO fallback to something else?
    raise RuntimeError(
        "Unable to read the number of features "
        f"from the Genome metadata: {genome_info}")


def _get_ref(info: list) -> str:
    """Get the workspace reference from an info tuple"""
    return f"{info[6]}/{info[0]}/{info[4]}"
