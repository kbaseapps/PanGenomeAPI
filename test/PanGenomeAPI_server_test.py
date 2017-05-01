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
from PangenomeOrthomcl.PangenomeOrthomclClient import PangenomeOrthomcl
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
        cls.po = PangenomeOrthomcl(cls.callback_url)
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
        output_name = "pangenome.1"
        ret = cls.gcs.build_pangenome({
            'genomeset_ref': cls.ws_info[1] + "/" + genomeset_obj_name,
            'genome_refs': cls.genome_refs,
            'workspace': cls.ws_info[1],
            'output_id': output_name
            })

        cls.pangenome_ref = ret.get('pg_ref')

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

    def test_search_orthologs_from_pangenome(self):
        # no query
        search_params = {'ref': self.pangenome_ref}
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

        # with query
        search_params = {'ref': self.pangenome_ref, 'query': '238899407'}
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

        # with limit
        search_params = {'ref': self.pangenome_ref, 'limit': 1}
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

        # with start limit
        search_params = {'ref': self.pangenome_ref, 'start': 1, 'limit': 1}
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

    def test_search_genomes_from_pangenome(self):
        # non-exist genome_ref
        search_params = {'pangenome_ref': self.pangenome_ref, 'genome_ref': self.pangenome_ref}
        with self.assertRaisesRegexp(
                    ValueError, 'genome_ref \[.*\] does not exist in available genomes \[.*\]'):
            self.getImpl().search_genomes_from_pangenome(self.getContext(), search_params)

        # no query
        genome_ref = self.genome_refs[0]
        search_params = {'pangenome_ref': self.pangenome_ref, 'genome_ref': genome_ref}
        ret = self.getImpl().search_genomes_from_pangenome(self.getContext(), search_params)[0]
        self.assertEquals(ret['num_found'], 1)
        self.assertEquals(ret['query'], '')
        self.assertEquals(ret['start'], 0)
        self.assertIn('features', ret)
        self.assertEquals(len(ret['features']), 1)
        self.assertEquals(ret['features'][0]['feature_id'], 'gi|387605483|ref|YP_006094339.1|',)

        # with query
        genome_ref = self.genome_refs[0]
        search_params = {'pangenome_ref': self.pangenome_ref, 'genome_ref': genome_ref,
                         'query': '387605483'}
        ret = self.getImpl().search_genomes_from_pangenome(self.getContext(), search_params)[0]
        self.assertEquals(ret['num_found'], 1)
        self.assertEquals(ret['query'], '387605483')
        self.assertEquals(ret['start'], 0)
        self.assertIn('features', ret)
        self.assertEquals(len(ret['features']), 1)
        self.assertEquals(ret['features'][0]['feature_id'], 'gi|387605483|ref|YP_006094339.1|',)
