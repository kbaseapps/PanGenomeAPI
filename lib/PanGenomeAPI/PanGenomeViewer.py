
from Workspace.WorkspaceClient import Workspace as Workspace
from pathos.multiprocessing import ProcessingPool as Pool
import multiprocessing


class PanGenomeViewer:

    def _process_pangenome(self, pangenome_ref):

        object_info = self.ws.get_objects2({'objects': 
                                            [{'ref': 
                                             pangenome_ref}]})['data'][0]['data']

        pangenome_id = object_info.get('id')

        orthologs = object_info.get('orthologs')
        genome_refs = object_info.get('genome_refs')
        shared_family_map = self._init_shared_family_map(genome_refs)

        family_map = {}
        gene_map = {}
        gene_ortholog_map = {}
        ortholog_gene_map = {}

        for ortholog in orthologs:
            id = ortholog.get('id')
            orthologs_struc = ortholog.get('orthologs')
            is_homolog = True if len(orthologs_struc) > 1 else False
            family_map.update({id: is_homolog})
            gene_ids = []
            for o in orthologs_struc:
                gene_id = o[0]
                gene_ids.append(gene_id)
                gene_map.update({gene_id: is_homolog})
                gene_ortholog_map.update({gene_id: id})

            if is_homolog:
                ortholog_gene_map.update({id: gene_ids})

        return (pangenome_id, genome_refs, family_map, gene_map, 
                gene_ortholog_map, ortholog_gene_map, shared_family_map)

    def _init_shared_family_map(self, genome_refs):
        init_map = {}
        shared_family_map = {}
        map(lambda genome_ref: init_map.update({genome_ref: 0}), genome_refs)
        for genome_ref in genome_refs:
            shared_family_map.update({genome_ref: init_map})

        return shared_family_map

    def _process_shared_family_map(self, shared_family_genome_refs, shared_family_map):
        for shared_family_genome_ref in shared_family_genome_refs:
            shared_family_genome_map = shared_family_map.get(shared_family_genome_ref).copy()
            for shared_family_genome_ref_copy in shared_family_genome_refs:
                if shared_family_genome_ref_copy != shared_family_genome_ref:
                    shared_family_genome_map[shared_family_genome_ref_copy] += 1
            shared_family_map.update({shared_family_genome_ref: shared_family_genome_map})

        return shared_family_map

    def _process_genome(self, genome_ref, gene_map, gene_ortholog_map):

        gene_genome_map = {}
        genome_ref_name_map = {}

        genome_gene_map = {}
        ortholog_ids = []
        object_info = self.ws.get_objects2({'objects': 
                                           [{'ref': genome_ref}]})['data'][0]['data']

        scientific_name = object_info.get('scientific_name')
        if scientific_name:
            genome_ref_name_map.update({genome_ref: scientific_name})
        else:
            genome_ref_name_map.update({genome_ref: object_info.get('id')})

        features = object_info.get('features')

        feature_array = []
        for feature in features:
            if feature.get('type') == 'CDS':
                gene_id = feature.get('id')
                feature_array.append(gene_id)
                if gene_map.get(gene_id):
                    genome_gene_map.update({gene_id: gene_map.get(gene_id)})
                    ortholog_ids.append(gene_ortholog_map.get(gene_id))
                    gene_genome_map.update({gene_id: genome_ref})
                else:
                    genome_gene_map.update({gene_id: False})

        returnVal = {'gene_genome_map': gene_genome_map,
                     'genome_ref_name_map': genome_ref_name_map,
                     'genome_ref': genome_ref,
                     'genome_gene_map': genome_gene_map,
                     'len_ortholog_ids': len(set(ortholog_ids))}

        return returnVal

    def _process_genomes(self, genome_refs, gene_map, gene_ortholog_map):

        # genome_ref_name_map = {}
        # gene_genome_map = {}
        # genome_map = {} 
        # genome_ortholog_map = {}

        # arg_2 = [gene_map] * len(genome_refs)
        # arg_3 = [gene_ortholog_map] * len(genome_refs)

        # cpus = min(4, multiprocessing.cpu_count())
        # pool = Pool(ncpus=cpus)
        # process_genome_returns = pool.map(self._process_genome, 
        #                                   genome_refs, arg_2, arg_3)

        # for process_genome_return in process_genome_returns:
        #     genome_ref_name_map.update(process_genome_return['genome_ref_name_map'])
        #     gene_genome_map.update(process_genome_return['gene_genome_map'])
        #     genome_map.update({process_genome_return['genome_ref']: 
        #                        process_genome_return['genome_gene_map']})
        #     genome_ortholog_map.update({process_genome_return['genome_ref']: 
        #                                 process_genome_return['len_ortholog_ids']})

        genome_ref_name_map = {}
        gene_genome_map = {}
        genome_map = {} 
        genome_ortholog_map = {}

        for genome_ref in genome_refs:
            genome_gene_map = {}
            ortholog_ids = []
            object_info = self.ws.get_objects2({'objects': 
                                               [{'ref': genome_ref}]})['data'][0]['data']

            scientific_name = object_info.get('scientific_name')
            if scientific_name:
                genome_ref_name_map.update({genome_ref: scientific_name})
            else:
                genome_ref_name_map.update({genome_ref: object_info.get('id')})

            features = object_info.get('features')

            feature_array = []
            for feature in features:
                if feature.get('type') == 'CDS':
                    gene_id = feature.get('id')
                    feature_array.append(gene_id)
                    if gene_map.get(gene_id):
                        genome_gene_map.update({gene_id: gene_map.get(gene_id)})
                        ortholog_ids.append(gene_ortholog_map.get(gene_id))
                        gene_genome_map.update({gene_id: genome_ref})
                    else:
                        genome_gene_map.update({gene_id: False})

            genome_map.update({genome_ref: genome_gene_map})
            genome_ortholog_map.update({genome_ref: len(set(ortholog_ids))})

        return (genome_ref_name_map, gene_genome_map, genome_map, genome_ortholog_map)

    def _compute_result_map(self, pangenome_id, genome_map, gene_map, family_map,
                            genome_ortholog_map, genome_ref_name_map, ortholog_gene_map,
                            gene_genome_map, shared_family_map):
        result = {}

        # Pan-genome object ID
        result.update({'pangenome_id': pangenome_id})

        # Total # of genomes
        result.update({'genomes_count': len(genome_map)})

        # Total # of protein coding genes
        genes = len(gene_map)
        if gene_map:
            homolog_family_genes = sum(gene_map.values())
        else:
            homolog_family_genes = 0
        result.update({'genes': {'genes_count': genes,
                                 'homolog_family_genes_count': homolog_family_genes,
                                 'singleton_family_genes_count': genes - homolog_family_genes}})

        # Total # of families
        families = len(family_map)
        if family_map:
            homolog_families = sum(family_map.values())
        else:
            homolog_families = 0
        result.update({'families': {'families_count': families,
                                    'homolog_families_count': homolog_families,
                                    'singleton_families_count': families - homolog_families}})

        # Genomes
        result.update({'genomes': {}})
        for genome_ref, genome_value in genome_map.items():
            genome_genes = len(genome_value)
            if genome_value:
                genome_homolog_family_genes = sum(genome_value.values())
            else:
                genome_homolog_family_genes = 0
            genome_homolog_family = genome_ortholog_map.get(genome_ref)
            result['genomes'].update({genome_ref_name_map.get(genome_ref): {
                        'genome_genes': genome_genes,
                        'genome_homolog_family_genes': genome_homolog_family_genes,
                        'genome_homolog_family': genome_homolog_family,
                        'genome_singleton_family_genes': genome_genes - genome_homolog_family_genes
                        }})

        #  Shared homolog familes
        for ortholog_id, gene_ids in ortholog_gene_map.items():
            shared_family_genome_refs = []
            for gene_id in list(set(gene_ids)):
                shared_family_genome_refs.append(gene_genome_map.get(gene_id))
            shared_family_map = self._process_shared_family_map(list(set(shared_family_genome_refs)), 
                                                                shared_family_map)

        for genome_ref, genome_family_map in shared_family_map.items():
            genome_family_map[genome_ref] = result['genomes'][genome_ref_name_map.get(
                                                            genome_ref)]['genome_homolog_family']
            for genome_ref, genome_name in genome_ref_name_map.items():
                genome_family_map[genome_ref_name_map.get(genome_ref)] = genome_family_map.pop(genome_ref)

        for genome_ref, genome_name in genome_ref_name_map.items():
            shared_family_map[genome_name] = shared_family_map.pop(genome_ref)

        result.update({'shared_family_map': shared_family_map})

        # Genome ref -> Name map
        result.update({'genome_ref_name_map': genome_ref_name_map})

        return result

    def __init__(self, pangenome_ref, token, ws_url):
        self.pangenome_ref = pangenome_ref
        self.ws = Workspace(ws_url, token=token)

    def compute_summary(self):

        (pangenome_id, genome_refs, family_map, 
         gene_map, gene_ortholog_map, ortholog_gene_map, 
         shared_family_map) = self._process_pangenome(self.pangenome_ref)

        (genome_ref_name_map, gene_genome_map, 
         genome_map, genome_ortholog_map) = self._process_genomes(genome_refs, 
                                                                  gene_map, 
                                                                  gene_ortholog_map)

        ret = self._compute_result_map(pangenome_id, genome_map, gene_map, family_map,
                                       genome_ortholog_map, genome_ref_name_map, ortholog_gene_map,
                                       gene_genome_map, shared_family_map)

        return ret
