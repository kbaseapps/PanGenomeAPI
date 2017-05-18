# -*- coding: utf-8 -*-
import os

from PanGenomeAPI.TableIndexer import TableIndexer
from PanGenomeAPI.PanGenomeViewer import PanGenomeViewer
from Workspace.WorkspaceClient import Workspace as Workspace


class PanGenomeIndexer:

    def __init__(self, config):

        self.ORTHOLOGS_SUFFIX = '_orthologs'
        self.FAMILIES_SUFFIX = '_families'
        self.FUNCTIONS_SUFFIX = '_functions'
        self.COMPARISON_GENOMES_SUFFIX = '_comparison_genomes'

        self.ws_url = config["workspace-url"]

        self.pangenome_index_dir = config["pangenome-index-dir"]
        if not os.path.isdir(self.pangenome_index_dir):
            os.makedirs(self.pangenome_index_dir)
        self.comparison_genome_index_dir = config["comparison-genome-index-dir"]
        if not os.path.isdir(self.comparison_genome_index_dir):
            os.makedirs(self.comparison_genome_index_dir)

        self.debug = "debug" in config and config["debug"] == "1"

    def search_families_from_comparison_genome(self, token, ref,
                                               query, sort_by, start, limit, num_found):

        search_object = 'families'
        info_included = ['core', 'genome_features', 'id', 'type', 'protein_translation',
                         'number_genomes', 'fraction_genomes', 'fraction_consistent_annotations',
                         'most_consistent_role']
        table_indexer = TableIndexer(ref, token, self.debug, self.ws_url,
                                     self.comparison_genome_index_dir,
                                     self.FAMILIES_SUFFIX, search_object, info_included,
                                     query, sort_by, start, limit, num_found)

        ret = table_indexer.run_search()

        for family in ret['families']:
            if family['genome_features']:
                family['genome_features'] = eval(family['genome_features'])

        return ret

    def search_functions_from_comparison_genome(self, token, ref,
                                                query, sort_by, start, limit, num_found):

        search_object = 'functions'
        info_included = ['core', 'genome_features', 'id', 'reactions', 'subsystem', 'primclass',
                         'subclass', 'number_genomes', 'fraction_genomes',
                         'fraction_consistent_families', 'most_consistent_family']
        table_indexer = TableIndexer(ref, token, self.debug, self.ws_url,
                                     self.comparison_genome_index_dir,
                                     self.FUNCTIONS_SUFFIX, search_object, info_included,
                                     query, sort_by, start, limit, num_found)

        ret = table_indexer.run_search()

        for function in ret['functions']:
            if function['genome_features']:
                function['genome_features'] = eval(function['genome_features'])

        return ret

    def search_comparison_genome_from_comparison_genome(self, token, ref,
                                                        query, sort_by, start, limit, num_found):

        search_object = 'genomes'
        info_included = ['id', 'genome_ref', 'genome_similarity', 'name', 'taxonomy', 'features',
                         'families', 'functions']
        table_indexer = TableIndexer(ref, token, self.debug, self.ws_url,
                                     self.comparison_genome_index_dir,
                                     self.COMPARISON_GENOMES_SUFFIX, search_object, info_included,
                                     query, sort_by, start, limit, num_found)

        ret = table_indexer.run_search()

        for genome in ret['genomes']:
            if genome['genome_similarity']:
                genome['genome_similarity'] = eval(genome['genome_similarity'])

        return ret

    def search_orthologs_from_pangenome(self, token, ref, query, sort_by, start, limit, num_found):

        search_object = 'orthologs'
        info_included = ['id', 'type', 'function', 'md5', 'protein_translation', 'orthologs']
        table_indexer = TableIndexer(ref, token, self.debug, self.ws_url, self.pangenome_index_dir,
                                     self.ORTHOLOGS_SUFFIX, search_object, info_included,
                                     query, sort_by, start, limit, num_found)

        ret = table_indexer.run_search()

        for orthologs in ret['orthologs']:
            orthologs_string = orthologs['orthologs']
            if orthologs_string:
                orthologs['orthologs'] = list(eval(orthologs_string))
                if not isinstance(orthologs['orthologs'][0], list):
                    orthologs['orthologs'] = [orthologs['orthologs']]

        ws = Workspace(self.ws_url, token=token)
        genome_feature_function_map = {}
        for orthologs in ret['orthologs']:
            for orthologs_obj in orthologs['orthologs']:
                gene_id = orthologs_obj[0]

                if gene_id in genome_feature_function_map:
                    orthologs_obj.append(genome_feature_function_map.get(gene_id))
                else:
                    object_info = ws.get_objects2(
                                {'objects': [{'ref': orthologs_obj[2]}]})['data'][0]['data']
                    map(lambda feature: genome_feature_function_map.update(
                                    {gene_id: feature.get('function')}), object_info['features'])

                    orthologs_obj.append(genome_feature_function_map.get(gene_id))

        return ret

    def compute_summary_from_pangenome(self, token, ref):

        pangenome_viewer = PanGenomeViewer(ref, token, self.ws_url)
        ret = pangenome_viewer.compute_summary()

        return ret
