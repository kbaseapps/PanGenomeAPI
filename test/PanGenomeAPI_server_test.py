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
                              "Escherichia_coli_BW2952_uid59391.faa",
                              "Escherichia_coli_K12_MG1655_uid57779.faa"]
        genomeset_obj = {"description": "", "elements": {}}
        genome_refs = []
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
            genome_refs.append(cls.ws_info[1] + "/" + genome_obj_name)
        genomeset_obj_name = "genomeset.1"
        cls.wsClient.save_objects({'workspace': cls.ws_info[1],
                                   'objects': [{'type': 'KBaseSearch.GenomeSet',
                                                'name': genomeset_obj_name,
                                                'data': genomeset_obj}]})
        print("Genome list mode\n")
        output_name = "pangenome.1"
        ret = cls.po.build_pangenome_with_orthomcl({
                "input_genomeset_ref": None,
                "output_workspace": cls.ws_info[1], "output_pangenome_id": output_name,
                "num_descriptions": 100000, "num_alignments": 100000, "evalue": "1e-5",
                "word_size": 3, "gapopen": 11, "gapextend": 1, "matrix": "BLOSUM62",
                "threshold": 11, "comp_based_stats": "2", "xdrop_gap_final": 25,
                "window_size": 40, "seg": "", "lcase_masking": 0, "use_sw_tback": 0,
                "mcl_p": 10000, "mcl_s": 1100, "mcl_r": 1400, "mcl_pct": 90,
                "mcl_warn_p": 10, "mcl_warn_factor": 1000, "mcl_init_l": 0,
                "mcl_main_l": 10000, "mcl_init_i": 2.0, "mcl_main_i": 1.5,
                "input_genome_refs": genome_refs})[0]

        print ret
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
        ret = self.getImpl().search_orthologs_from_pangenome(self.getContext(),
                                                             search_params)[0]
        pprint(ret)
