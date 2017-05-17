
from Workspace.WorkspaceClient import Workspace as Workspace


class PanGenomeViewer:

    def _process_pangenome(self):

        object_info = self.ws.get_objects2(
                                {'objects': [{'ref': self.pangenome_ref}]})['data'][0]['data']

        self.pangenome_id = object_info.get('id')

        orthologs = object_info.get('orthologs')
        self.genome_refs = object_info.get('genome_refs')
        self._init_shared_family_map(self.genome_refs)

        for ortholog in orthologs:
            id = ortholog.get('id')
            orthologs_struc = ortholog.get('orthologs')
            is_homolog = True if len(orthologs_struc) > 1 else False
            self.family_map.update({id: is_homolog})
            gene_ids = []
            for o in orthologs_struc:
                gene_id = o[0]
                gene_ids.append(gene_id)
                self.gene_map.update({gene_id: is_homolog})
                self.gene_ortholog_map.update({gene_id: id})

            if is_homolog:
                self.ortholog_gene_map.update({id: gene_ids})

    def _init_shared_family_map(self, genome_refs):
        init_map = {}
        map(lambda genome_ref: init_map.update({genome_ref: 0}), genome_refs)
        for genome_ref in self.genome_refs:
            self.shared_family_map.update({genome_ref: init_map})

    def _process_shared_family_map(self, shared_family_genome_refs):
        for shared_family_genome_ref in shared_family_genome_refs:
            shared_family_genome_map = self.shared_family_map.get(shared_family_genome_ref).copy()
            for shared_family_genome_ref_copy in shared_family_genome_refs:
                if shared_family_genome_ref_copy != shared_family_genome_ref:
                    shared_family_genome_map[shared_family_genome_ref_copy] += 1
            self.shared_family_map.update({shared_family_genome_ref: shared_family_genome_map})

    def _process_genomes(self, genome_refs):
        for genome_ref in genome_refs:
            genome_gene_map = {}
            ortholog_ids = []
            object_info = self.ws.get_objects2(
                                {'objects': [{'ref': genome_ref}]})['data'][0]['data']

            scientific_name = object_info.get('scientific_name')
            if scientific_name:
                self.genome_ref_name_map.update({genome_ref: scientific_name})
            else:
                self.genome_ref_name_map.update({genome_ref: object_info.get('id')})

            features = object_info.get('features')

            feature_array = []
            for feature in features:
                if feature.get('type') == 'CDS':
                    gene_id = feature.get('id')
                    feature_array.append(gene_id)
                    if self.gene_map.get(gene_id):
                        genome_gene_map.update({gene_id: self.gene_map.get(gene_id)})
                        ortholog_ids.append(self.gene_ortholog_map.get(gene_id))
                        self.gene_genome_map.update({gene_id: genome_ref})
                    else:
                        genome_gene_map.update({gene_id: False})

            self.genome_map.update({genome_ref: genome_gene_map})
            self.genome_ortholog_map.update({genome_ref: len(set(ortholog_ids))})

    def _compute_result_map(self):
        result = {}

        # Pan-genome object ID
        result.update({'pangenome_id': self.pangenome_id})

        # Total # of genomes
        result.update({'genomes_count': len(self.genome_map)})

        # Total # of protein coding genes
        genes = len(self.gene_map)
        if self.gene_map:
            homolog_family_genes = sum(self.gene_map.values())
        else:
            homolog_family_genes = 0
        result.update({'genes': {'genes_count': genes,
                                 'homolog_family_genes_count': homolog_family_genes,
                                 'singleton_family_genes_count': genes - homolog_family_genes}})

        # Total # of families
        families = len(self.family_map)
        if self.family_map:
            homolog_families = sum(self.family_map.values())
        else:
            homolog_families = 0
        result.update({'families': {'families_count': families,
                                    'homolog_families_count': homolog_families,
                                    'singleton_families_count': families - homolog_families}})

        # Genomes
        result.update({'genomes': {}})
        for genome_ref, genome_value in self.genome_map.items():
            genome_genes = len(genome_value)
            if genome_value:
                genome_homolog_family_genes = sum(genome_value.values())
            else:
                genome_homolog_family_genes = 0
            genome_homolog_family = self.genome_ortholog_map.get(genome_ref)
            result['genomes'].update({self.genome_ref_name_map.get(genome_ref): {
                        'genome_genes': genome_genes,
                        'genome_homolog_family_genes': genome_homolog_family_genes,
                        'genome_homolog_family': genome_homolog_family,
                        'genome_singleton_family_genes': genome_genes - genome_homolog_family_genes
                        }})

        #  Shared homolog familes
        for ortholog_id, gene_ids in self.ortholog_gene_map.items():
            shared_family_genome_refs = []
            for gene_id in list(set(gene_ids)):
                shared_family_genome_refs.append(self.gene_genome_map.get(gene_id))
            self._process_shared_family_map(list(set(shared_family_genome_refs)))

        for genome_ref, genome_family_map in self.shared_family_map.items():
            genome_family_map[genome_ref] = result['genomes'][self.genome_ref_name_map.get(
                                                            genome_ref)]['genome_homolog_family']
            for genome_ref, genome_name in self.genome_ref_name_map.items():
                genome_family_map[self.genome_ref_name_map.get(genome_ref)] = genome_family_map.pop(
                                                                                        genome_ref)

        for genome_ref, genome_name in self.genome_ref_name_map.items():
            self.shared_family_map[genome_name] = self.shared_family_map.pop(genome_ref)

        result.update({'shared_family_map': self.shared_family_map})

        # Genome ref -> Name map
        result.update({'genome_ref_name_map': self.genome_ref_name_map})

        return result

    def __init__(self, pangenome_ref, token, ws_url):
        self.pangenome_ref = pangenome_ref
        self.token = token
        self.ws_url = ws_url
        self.ws = Workspace(self.ws_url, token=self.token)
        self.genome_ref_name_map = {}
        self.genome_ortholog_map = {}
        self.ortholog_gene_map = {}
        self.gene_ortholog_map = {}
        self.gene_genome_map = {}

        self.gene_map = {}
        self.family_map = {}
        self.genome_map = {}
        self.shared_family_map = {}

    def compute_summary(self):

        self._process_pangenome()
        self._process_genomes(self.genome_refs)

        ret = self._compute_result_map()

        return ret
