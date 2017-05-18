# -*- coding: utf-8 -*-
import unittest
import os  # noqa: F401
import json  # noqa: F401
import time
import requests  # noqa: F401
import shutil

from os import environ
try:
    from ConfigParser import ConfigParser  # py2
except:
    from configparser import ConfigParser  # py3

from pprint import pprint  # noqa: F401

from Bio import SeqIO

from biokbase.workspace.client import Workspace as workspaceService
from PanGenomeAPI.PanGenomeAPIImpl import PanGenomeAPI
from PanGenomeAPI.PanGenomeAPIServer import MethodContext
from PanGenomeAPI.authclient import KBaseAuth as _KBaseAuth
from GenomeComparisonSDK.GenomeComparisonSDKClient import GenomeComparisonSDK


class PanGenomeAPITest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('PanGenomeAPI'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'PanGenomeAPI',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = workspaceService(cls.wsURL)
        cls.serviceImpl = PanGenomeAPI(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        shutil.rmtree(cls.scratch)
        os.mkdir(cls.scratch)
        cls.callback_url = os.environ['SDK_CALLBACK_URL']

        suffix = int(time.time() * 1000)
        wsName = "test_pangenome_api_" + str(suffix)
        cls.ws_info = cls.wsClient.create_workspace({'workspace': wsName})
        cls.gcs = GenomeComparisonSDK(cls.callback_url)
        cls.prepare_data()

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    @classmethod
    def prepare_data(cls):
        # build PanGenome object
        contig_obj_name = "contigset.1"
        contig = {'id': '1', 'length': 10, 'md5': 'md5', 'sequence': 'agcttttcat'}
        obj = {'contigs': [contig], 'id': 'id', 'md5': 'md5', 'name': 'name',
               'source': 'source', 'source_id': 'source_id', 'type': 'type'}
        cls.wsClient.save_objects({'workspace': cls.ws_info[1],
                                   'objects': [{'type': 'KBaseGenomes.ContigSet',
                                                'name': contig_obj_name, 'data': obj}]})
        genome_fasta_files = ["Escherichia_coli_042_uid161985.faa",
                              "Escherichia_coli_BW2952_uid59391.faa"]
        genomeset_obj = {"description": "", "elements": {}}
        cls.genome_refs = []
        genome_feature_counts = {}
        for genome_index, genome_file_name in enumerate(genome_fasta_files):
            test_dir = os.path.dirname(os.path.realpath(__file__))
            file_path = test_dir + "/data/" + genome_file_name
            features = []
            for record in SeqIO.parse(file_path, "fasta"):
                id = record.id
                sequence = str(record.seq)
                descr = record.description
                if len(sequence) <= 100:
                    features.append({"id": id, "location": [["1", 0, "+", 0]],
                                     "type": "CDS", "protein_translation": sequence,
                                     "aliases": [], "annotations": [], "function": descr})
            genome_obj = {"complete": 0, "contig_ids": ["1"], "contig_lengths": [10],
                          "contigset_ref": cls.ws_info[1] + "/" + contig_obj_name,
                          "dna_size": 10, "domain": "Bacteria", "gc_content": 0.5,
                          "genetic_code": 11, "id": genome_file_name, "md5": "md5",
                          "num_contigs": 1, "scientific_name": genome_file_name,
                          "source": "test folder", "source_id": "noid",
                          "features": features}
            genome_obj_name = "genome." + str(genome_index)
            info = cls.wsClient.save_objects({'workspace': cls.ws_info[1],
                                              'objects': [{'type': 'KBaseGenomes.Genome',
                                                           'name': genome_obj_name,
                                                           'data': genome_obj}]})[0]
            full_ref = str(info[6]) + "/" + str(info[0]) + "/" + str(info[4])
            genome_feature_counts[full_ref] = len(features)
            genomeset_obj["elements"]["param" + str(genome_index)] = {
                                                    "ref": cls.ws_info[1] + "/" + genome_obj_name}
            cls.genome_refs.append(cls.ws_info[1] + "/" + genome_obj_name)
        genomeset_obj_name = "genomeset.1"
        cls.wsClient.save_objects({'workspace': cls.ws_info[1],
                                   'objects': [{'type': 'KBaseSearch.GenomeSet',
                                                'name': genomeset_obj_name,
                                                'data': genomeset_obj}]})
        pangenome_output_name = "pangenome.1"
        pangenome_ret = cls.gcs.build_pangenome({
            'genomeset_ref': cls.ws_info[1] + "/" + genomeset_obj_name,
            'genome_refs': cls.genome_refs,
            'workspace': cls.ws_info[1],
            'output_id': pangenome_output_name
            })

        cls.pangenome_ref = pangenome_ret.get('pg_ref')

        # build comparison genome object
        comparison_output_name = "comparison_genome.1"
        comparison_genome_ret = cls.gcs.compare_genomes({
            'pangenome_ref': cls.pangenome_ref,
            'workspace': cls.ws_info[1],
            'output_id': comparison_output_name
            })

        cls.comparison_genome_ref = comparison_genome_ret.get('cg_ref')

    def getWsClient(self):
        return self.__class__.wsClient

    def getWsName(self):
        if hasattr(self.__class__, 'wsName'):
            return self.__class__.wsName
        suffix = int(time.time() * 1000)
        wsName = "test_PanGenomeAPI_" + str(suffix)
        ret = self.getWsClient().create_workspace({'workspace': wsName})  # noqa
        self.__class__.wsName = wsName
        return wsName

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    def test_compute_summary_from_pangenome(self):
        search_params = {'pangenome_ref': self.pangenome_ref}
        ret = self.getImpl().compute_summary_from_pangenome(self.getContext(), search_params)[0]
        pprint(ret)
        self.assertIn('families', ret)
        self.assertIn('genes', ret)
        self.assertIn('families', ret)
        self.assertIn('shared_family_map', ret)
        self.assertEquals(len(ret['genomes']), 2)
        self.assertEquals(ret['pangenome_id'], 'pangenome.1')

    def test_search_orthologs_from_pangenome(self):
        # no query
        search_params = {'pangenome_ref': self.pangenome_ref}
        ret = self.getImpl().search_orthologs_from_pangenome(self.getContext(), search_params)[0]
        pprint(ret)
        self.assertEquals(ret['num_found'], 2)
        self.assertEquals(ret['query'], '')
        self.assertEquals(ret['start'], 0)
        self.assertEquals(len(ret['orthologs']), 2)
        self.assertIn('id', ret['orthologs'][0])
        self.assertIn('type', ret['orthologs'][0])
        self.assertIn('function', ret['orthologs'][0])
        self.assertIn('md5', ret['orthologs'][0])
        self.assertIn('protein_translation', ret['orthologs'][0])
        self.assertIn('orthologs', ret['orthologs'][0])
        self.assertIsInstance(ret['orthologs'][0]['orthologs'], list)

        # with query
        search_params = {'pangenome_ref': self.pangenome_ref, 'query': '238899407'}
        ret = self.getImpl().search_orthologs_from_pangenome(self.getContext(), search_params)[0]
        self.assertEquals(ret['num_found'], 1)
        self.assertEquals(ret['query'], '238899407')
        self.assertEquals(ret['start'], 0)
        self.assertEquals(len(ret['orthologs']), 1)
        self.assertEquals(ret['orthologs'][0]['id'], 'gi|238899407|ref|YP_002925203.1|')
        self.assertIn('type', ret['orthologs'][0])
        self.assertIn('function', ret['orthologs'][0])
        self.assertIn('md5', ret['orthologs'][0])
        self.assertIn('protein_translation', ret['orthologs'][0])
        self.assertIn('orthologs', ret['orthologs'][0])
        self.assertIsInstance(ret['orthologs'][0]['orthologs'], list)

        # with limit
        search_params = {'pangenome_ref': self.pangenome_ref, 'limit': 1}
        ret = self.getImpl().search_orthologs_from_pangenome(self.getContext(), search_params)[0]
        self.assertEquals(ret['num_found'], 2)
        self.assertEquals(ret['query'], '')
        self.assertEquals(ret['start'], 0)
        self.assertEquals(len(ret['orthologs']), 1)
        self.assertIsNotNone(ret['orthologs'][0]['id'])
        self.assertIn('id', ret['orthologs'][0])
        self.assertIn('type', ret['orthologs'][0])
        self.assertIn('function', ret['orthologs'][0])
        self.assertIn('md5', ret['orthologs'][0])
        self.assertIn('protein_translation', ret['orthologs'][0])
        self.assertIn('orthologs', ret['orthologs'][0])
        self.assertIsInstance(ret['orthologs'][0]['orthologs'], list)

        # with start limit
        search_params = {'pangenome_ref': self.pangenome_ref, 'start': 1, 'limit': 1}
        ret = self.getImpl().search_orthologs_from_pangenome(self.getContext(), search_params)[0]
        self.assertEquals(ret['num_found'], 2)
        self.assertEquals(ret['query'], '')
        self.assertEquals(ret['start'], 1)
        self.assertEquals(len(ret['orthologs']), 1)
        self.assertIsNotNone(ret['orthologs'][0]['id'])
        self.assertIn('type', ret['orthologs'][0])
        self.assertIn('function', ret['orthologs'][0])
        self.assertIn('md5', ret['orthologs'][0])
        self.assertIn('protein_translation', ret['orthologs'][0])
        self.assertIn('orthologs', ret['orthologs'][0])
        self.assertIsInstance(ret['orthologs'][0]['orthologs'], list)

        # sort by id
        search_params = {'pangenome_ref': self.pangenome_ref, 'sort_by': [['id', 0]]}
        ret = self.getImpl().search_orthologs_from_pangenome(self.getContext(), search_params)[0]
        self.assertEquals(ret['num_found'], 2)
        self.assertEquals(ret['query'], '')
        self.assertEquals(ret['start'], 0)
        self.assertEquals(len(ret['orthologs']), 2)
        id_1 = ret['orthologs'][0]['id']
        self.assertIn('type', ret['orthologs'][0])
        self.assertIn('function', ret['orthologs'][0])
        self.assertIn('md5', ret['orthologs'][0])
        self.assertIn('protein_translation', ret['orthologs'][0])
        self.assertIn('orthologs', ret['orthologs'][0])
        self.assertIsInstance(ret['orthologs'][0]['orthologs'], list)

        search_params = {'pangenome_ref': self.pangenome_ref, 'sort_by': [['id', 1]]}
        ret = self.getImpl().search_orthologs_from_pangenome(self.getContext(), search_params)[0]
        id_2 = ret['orthologs'][1]['id']
        self.assertEquals(id_1, id_2)

    def test_search_families_from_comparison_genome(self):
        # no query
        search_params = {'comparison_genome_ref': self.comparison_genome_ref}
        ret = self.getImpl().search_families_from_comparison_genome(self.getContext(),
                                                                    search_params)[0]
        pprint(ret)
        self.assertEquals(ret['num_found'], 2)
        self.assertEquals(ret['query'], '')
        self.assertEquals(ret['start'], 0)
        self.assertEquals(len(ret['families']), 2)
        self.assertIn('core', ret['families'][0])
        self.assertIn('genome_features', ret['families'][0])
        self.assertIn('id', ret['families'][0])
        self.assertIn('type', ret['families'][0])
        self.assertIn('protein_translation', ret['families'][0])
        self.assertIn('number_genomes', ret['families'][0])
        self.assertIn('fraction_genomes', ret['families'][0])
        self.assertIn('fraction_consistent_annotations', ret['families'][0])
        self.assertIn('most_consistent_role', ret['families'][0])
        self.assertIsInstance(ret['families'][0]['genome_features'], dict)

        # with query
        search_params = {'comparison_genome_ref': self.comparison_genome_ref, 'query': '238899407'}
        ret = self.getImpl().search_families_from_comparison_genome(self.getContext(),
                                                                    search_params)[0]
        self.assertEquals(ret['num_found'], 1)
        self.assertEquals(ret['query'], '238899407')
        self.assertEquals(ret['start'], 0)
        self.assertEquals(len(ret['families']), 1)
        self.assertEquals(ret['families'][0]['id'], 'gi|238899407|ref|YP_002925203.1|')
        self.assertIn('core', ret['families'][0])
        self.assertIn('genome_features', ret['families'][0])
        self.assertIn('id', ret['families'][0])
        self.assertIn('type', ret['families'][0])
        self.assertIn('protein_translation', ret['families'][0])
        self.assertIn('number_genomes', ret['families'][0])
        self.assertIn('fraction_genomes', ret['families'][0])
        self.assertIn('fraction_consistent_annotations', ret['families'][0])
        self.assertIn('most_consistent_role', ret['families'][0])
        self.assertIsInstance(ret['families'][0]['genome_features'], dict)

        # with limit
        search_params = {'comparison_genome_ref': self.comparison_genome_ref, 'limit': 1}
        ret = self.getImpl().search_families_from_comparison_genome(self.getContext(),
                                                                    search_params)[0]
        self.assertEquals(ret['num_found'], 2)
        self.assertEquals(ret['query'], '')
        self.assertEquals(ret['start'], 0)
        self.assertEquals(len(ret['families']), 1)
        self.assertIsNotNone(ret['families'][0]['id'])
        self.assertIn('core', ret['families'][0])
        self.assertIn('genome_features', ret['families'][0])
        self.assertIn('id', ret['families'][0])
        self.assertIn('type', ret['families'][0])
        self.assertIn('protein_translation', ret['families'][0])
        self.assertIn('number_genomes', ret['families'][0])
        self.assertIn('fraction_genomes', ret['families'][0])
        self.assertIn('fraction_consistent_annotations', ret['families'][0])
        self.assertIn('most_consistent_role', ret['families'][0])
        self.assertIsInstance(ret['families'][0]['genome_features'], dict)

        # with start limit
        search_params = {'comparison_genome_ref': self.comparison_genome_ref, 'start': 1,
                         'limit': 1}
        ret = self.getImpl().search_families_from_comparison_genome(self.getContext(),
                                                                    search_params)[0]
        self.assertEquals(ret['num_found'], 2)
        self.assertEquals(ret['query'], '')
        self.assertEquals(ret['start'], 1)
        self.assertEquals(len(ret['families']), 1)
        self.assertIsNotNone(ret['families'][0]['id'])
        self.assertIn('core', ret['families'][0])
        self.assertIn('genome_features', ret['families'][0])
        self.assertIn('id', ret['families'][0])
        self.assertIn('type', ret['families'][0])
        self.assertIn('protein_translation', ret['families'][0])
        self.assertIn('number_genomes', ret['families'][0])
        self.assertIn('fraction_genomes', ret['families'][0])
        self.assertIn('fraction_consistent_annotations', ret['families'][0])
        self.assertIn('most_consistent_role', ret['families'][0])
        self.assertIsInstance(ret['families'][0]['genome_features'], dict)

    def test_search_functions_from_comparison_genome(self):
        # no query
        search_params = {'comparison_genome_ref': self.comparison_genome_ref}
        ret = self.getImpl().search_functions_from_comparison_genome(self.getContext(),
                                                                     search_params)[0]
        pprint(ret)
        self.assertEquals(ret['num_found'], 3)
        self.assertEquals(ret['query'], '')
        self.assertEquals(ret['start'], 0)
        self.assertEquals(len(ret['functions']), 3)
        self.assertIn('core', ret['functions'][0])
        self.assertIn('genome_features', ret['functions'][0])
        self.assertIn('id', ret['functions'][0])
        self.assertIn('reactions', ret['functions'][0])
        self.assertIn('subsystem', ret['functions'][0])
        self.assertIn('primclass', ret['functions'][0])
        self.assertIn('subclass', ret['functions'][0])
        self.assertIn('number_genomes', ret['functions'][0])
        self.assertIn('fraction_genomes', ret['functions'][0])
        self.assertIn('fraction_consistent_families', ret['functions'][0])
        self.assertIn('most_consistent_family', ret['functions'][0])
        self.assertIsInstance(ret['functions'][0]['genome_features'], dict)

        # with query
        search_params = {'comparison_genome_ref': self.comparison_genome_ref, 'query': '387605483'}
        ret = self.getImpl().search_functions_from_comparison_genome(self.getContext(),
                                                                     search_params)[0]
        self.assertEquals(ret['num_found'], 1)
        self.assertEquals(ret['query'], '387605483')
        self.assertEquals(ret['start'], 0)
        self.assertEquals(len(ret['functions']), 1)
        self.assertEquals(ret['functions'][0]['id'],
                          'gi|387605483|ref|YP_006094339.1| putative exported protein ' +
                          '[Escherichia coli 042]')
        self.assertIn('core', ret['functions'][0])
        self.assertIn('genome_features', ret['functions'][0])
        self.assertIn('id', ret['functions'][0])
        self.assertIn('reactions', ret['functions'][0])
        self.assertIn('subsystem', ret['functions'][0])
        self.assertIn('primclass', ret['functions'][0])
        self.assertIn('subclass', ret['functions'][0])
        self.assertIn('number_genomes', ret['functions'][0])
        self.assertIn('fraction_genomes', ret['functions'][0])
        self.assertIn('fraction_consistent_families', ret['functions'][0])
        self.assertIn('most_consistent_family', ret['functions'][0])
        self.assertIsInstance(ret['functions'][0]['genome_features'], dict)

        # with limit
        search_params = {'comparison_genome_ref': self.comparison_genome_ref, 'limit': 1}
        ret = self.getImpl().search_functions_from_comparison_genome(self.getContext(),
                                                                     search_params)[0]
        self.assertEquals(ret['num_found'], 3)
        self.assertEquals(ret['query'], '')
        self.assertEquals(ret['start'], 0)
        self.assertEquals(len(ret['functions']), 1)
        self.assertIsNotNone(ret['functions'][0]['id'])
        self.assertIn('core', ret['functions'][0])
        self.assertIn('genome_features', ret['functions'][0])
        self.assertIn('id', ret['functions'][0])
        self.assertIn('reactions', ret['functions'][0])
        self.assertIn('subsystem', ret['functions'][0])
        self.assertIn('primclass', ret['functions'][0])
        self.assertIn('subclass', ret['functions'][0])
        self.assertIn('number_genomes', ret['functions'][0])
        self.assertIn('fraction_genomes', ret['functions'][0])
        self.assertIn('fraction_consistent_families', ret['functions'][0])
        self.assertIn('most_consistent_family', ret['functions'][0])
        self.assertIsInstance(ret['functions'][0]['genome_features'], dict)

        # with start limit
        search_params = {'comparison_genome_ref': self.comparison_genome_ref, 'start': 1,
                         'limit': 1}
        ret = self.getImpl().search_functions_from_comparison_genome(self.getContext(),
                                                                     search_params)[0]
        self.assertEquals(ret['num_found'], 3)
        self.assertEquals(ret['query'], '')
        self.assertEquals(ret['start'], 1)
        self.assertEquals(len(ret['functions']), 1)
        self.assertIn('core', ret['functions'][0])
        self.assertIn('genome_features', ret['functions'][0])
        self.assertIn('id', ret['functions'][0])
        self.assertIn('reactions', ret['functions'][0])
        self.assertIn('subsystem', ret['functions'][0])
        self.assertIn('primclass', ret['functions'][0])
        self.assertIn('subclass', ret['functions'][0])
        self.assertIn('number_genomes', ret['functions'][0])
        self.assertIn('fraction_genomes', ret['functions'][0])
        self.assertIn('fraction_consistent_families', ret['functions'][0])
        self.assertIn('most_consistent_family', ret['functions'][0])
        self.assertIsInstance(ret['functions'][0]['genome_features'], dict)

    def test_search_comparison_genome_from_comparison_genome(self):
        # no query
        search_params = {'comparison_genome_ref': self.comparison_genome_ref}
        ret = self.getImpl().search_comparison_genome_from_comparison_genome(self.getContext(),
                                                                             search_params)[0]
        pprint(ret)
        self.assertEquals(ret['num_found'], 2)
        self.assertEquals(ret['query'], '')
        self.assertEquals(ret['start'], 0)
        self.assertEquals(len(ret['genomes']), 2)
        self.assertIn('id', ret['genomes'][0])
        self.assertIn('genome_ref', ret['genomes'][0])
        self.assertIn('genome_similarity', ret['genomes'][0])
        self.assertIn('name', ret['genomes'][0])
        self.assertIn('taxonomy', ret['genomes'][0])
        self.assertIn('features', ret['genomes'][0])
        self.assertIn('families', ret['genomes'][0])
        self.assertIn('functions', ret['genomes'][0])
        self.assertIsInstance(ret['genomes'][0]['genome_similarity'], dict)

        # with query
        search_params = {'comparison_genome_ref': self.comparison_genome_ref,
                         'query': 'BW2952_uid59391'}
        ret = self.getImpl().search_comparison_genome_from_comparison_genome(self.getContext(),
                                                                             search_params)[0]
        self.assertEquals(ret['num_found'], 1)
        self.assertEquals(ret['query'], 'BW2952_uid59391')
        self.assertEquals(ret['start'], 0)
        self.assertEquals(len(ret['genomes']), 1)
        self.assertEquals(ret['genomes'][0]['name'],
                          'Escherichia_coli_BW2952_uid59391.faa')
        self.assertIn('id', ret['genomes'][0])
        self.assertIn('genome_ref', ret['genomes'][0])
        self.assertIn('genome_similarity', ret['genomes'][0])
        self.assertIn('name', ret['genomes'][0])
        self.assertIn('taxonomy', ret['genomes'][0])
        self.assertIn('features', ret['genomes'][0])
        self.assertIn('families', ret['genomes'][0])
        self.assertIn('functions', ret['genomes'][0])
        self.assertIsInstance(ret['genomes'][0]['genome_similarity'], dict)

        # with limit
        search_params = {'comparison_genome_ref': self.comparison_genome_ref, 'limit': 1}
        ret = self.getImpl().search_comparison_genome_from_comparison_genome(self.getContext(),
                                                                             search_params)[0]
        self.assertEquals(ret['num_found'], 2)
        self.assertEquals(ret['query'], '')
        self.assertEquals(ret['start'], 0)
        self.assertEquals(len(ret['genomes']), 1)
        self.assertIn('id', ret['genomes'][0])
        self.assertIn('genome_ref', ret['genomes'][0])
        self.assertIn('genome_similarity', ret['genomes'][0])
        self.assertIn('name', ret['genomes'][0])
        self.assertIn('taxonomy', ret['genomes'][0])
        self.assertIn('features', ret['genomes'][0])
        self.assertIn('families', ret['genomes'][0])
        self.assertIn('functions', ret['genomes'][0])
        self.assertIsInstance(ret['genomes'][0]['genome_similarity'], dict)

        # with start limit
        search_params = {'comparison_genome_ref': self.comparison_genome_ref, 'start': 1,
                         'limit': 1}
        ret = self.getImpl().search_comparison_genome_from_comparison_genome(self.getContext(),
                                                                             search_params)[0]
        self.assertEquals(ret['num_found'], 2)
        self.assertEquals(ret['query'], '')
        self.assertEquals(ret['start'], 1)
        self.assertEquals(len(ret['genomes']), 1)
        self.assertIn('id', ret['genomes'][0])
        self.assertIn('genome_ref', ret['genomes'][0])
        self.assertIn('genome_similarity', ret['genomes'][0])
        self.assertIn('name', ret['genomes'][0])
        self.assertIn('taxonomy', ret['genomes'][0])
        self.assertIn('features', ret['genomes'][0])
        self.assertIn('families', ret['genomes'][0])
        self.assertIn('functions', ret['genomes'][0])
