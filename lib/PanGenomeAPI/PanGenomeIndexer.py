# -*- coding: utf-8 -*-
import os
# import base64
import time
import subprocess
import traceback
import string
import tempfile

from Workspace.WorkspaceClient import Workspace as Workspace
from PanGenomeAPI.CombinedLineIterator import CombinedLineIterator
from GenomeSearchUtil.GenomeSearchUtilClient import GenomeSearchUtil
from DataFileUtil.DataFileUtilClient import DataFileUtil


class PanGenomeIndexer:

    def __init__(self, config):

        self.orthologs_column_props_map = {
            "id": {"col": 1, "type": ""},
            "type": {"col": 2, "type": ""},
            "function": {"col": 3, "type": ""},
            "md5": {"col": 4, "type": ""},
            "protein_translation": {"col": 5, "type": ""},
            "orthologs": {"col": 6, "type": ""}
        }
        self.families_column_props_map = {
            "core": {"col": 1, "type": "n"},
            "genome_features": {"col": 2, "type": ""},
            "id": {"col": 3, "type": ""},
            "type": {"col": 4, "type": ""},
            "protein_translation": {"col": 5, "type": ""},
            "number_genomes": {"col": 6, "type": "n"},
            "fraction_genomes": {"col": 7, "type": "n"},
            "fraction_consistent_annotations": {"col": 8, "type": "n"},
            "most_consistent_role": {"col": 9, "type": ""}
        }
        self.functions_column_props_map = {
            "core": {"col": 1, "type": "n"},
            "genome_features": {"col": 2, "type": ""},
            "id": {"col": 3, "type": ""},
            "reactions": {"col": 4, "type": ""},
            "subsystem": {"col": 5, "type": ""},
            "primclass": {"col": 6, "type": ""},
            "subclass": {"col": 7, "type": ""},
            "number_genomes": {"col": 8, "type": "n"},
            "fraction_genomes": {"col": 9, "type": "n"},
            "fraction_consistent_families": {"col": 10, "type": "n"},
            "most_consistent_family": {"col": 11, "type": ""}
        }
        self.comparison_genomes_column_props_map = {
            "id": {"col": 1, "type": ""},
            "genome_ref": {"col": 2, "type": ""},
            "genome_similarity": {"col": 3, "type": ""},
            "name": {"col": 4, "type": ""},
            "taxonomy": {"col": 5, "type": ""},
            "features": {"col": 6, "type": "n"},
            "families": {"col": 7, "type": "n"},
            "functions": {"col": 8, "type": "n"}
        }

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
        self.max_sort_mem_size = 250000
        self.unicode_comma = u"\uFF0C"
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.gsu = GenomeSearchUtil(self.callback_url)
        self.dfu = DataFileUtil(self.callback_url)

    def search_families_from_comparison_genome(self, token, comparison_genome_ref,
                                               query, sort_by, start, limit, num_found):
        if query is None:
            query = ""
        if start is None:
            start = 0
        if limit is None:
            limit = 50
        if self.debug:
            print("Search: ComparisonGenome =" + comparison_genome_ref + ", query=[" + query +
                  "], sort-by=[" + self.get_sorting_code(self.families_column_props_map, sort_by) +
                  "], start=" + str(start) + ", limit=" + str(limit))
            t1 = time.time()
        inner_chsum = self.check_families_cache(comparison_genome_ref, token)
        index_iter = self.get_families_sorted_iterator(inner_chsum, sort_by)
        ret = self.filter_families_query(index_iter, query, start, limit, num_found)
        if self.debug:
            print("    (overall-time=" + str(time.time() - t1) + ")")

        return ret

    def search_functions_from_comparison_genome(self, token, comparison_genome_ref,
                                                query, sort_by, start, limit, num_found):
        if query is None:
            query = ""
        if start is None:
            start = 0
        if limit is None:
            limit = 50
        if self.debug:
            print("Search: ComparisonGenome =" + comparison_genome_ref + ", query=[" + query +
                  "], sort-by=[" + self.get_sorting_code(self.functions_column_props_map, sort_by) +
                  "], start=" + str(start) + ", limit=" + str(limit))
            t1 = time.time()
        inner_chsum = self.check_functions_cache(comparison_genome_ref, token)
        index_iter = self.get_functions_sorted_iterator(inner_chsum, sort_by)
        ret = self.filter_functions_query(index_iter, query, start, limit, num_found)
        if self.debug:
            print("    (overall-time=" + str(time.time() - t1) + ")")

        return ret

    def search_comparison_genome_from_comparison_genome(self, token, comparison_genome_ref,
                                                        query, sort_by, start, limit, num_found):
        if query is None:
            query = ""
        if start is None:
            start = 0
        if limit is None:
            limit = 50
        if self.debug:
            print("Search: ComparisonGenome =" + comparison_genome_ref + ", query=[" + query +
                  "], sort-by=[" +
                  self.get_sorting_code(self.comparison_genomes_column_props_map, sort_by) +
                  "], start=" + str(start) + ", limit=" + str(limit))
            t1 = time.time()
        inner_chsum = self.check_comparison_genomes_cache(comparison_genome_ref, token)
        index_iter = self.get_comparison_genomes_sorted_iterator(inner_chsum, sort_by)
        ret = self.filter_comparison_genomes_query(index_iter, query, start, limit, num_found)
        if self.debug:
            print("    (overall-time=" + str(time.time() - t1) + ")")

        return ret

    def search_genomes_from_pangenome(self, token, pangenome_ref, genome_ref, query, sort_by,
                                      start, limit, num_found):

        ws = Workspace(self.ws_url, token=token)
        pangenome_genomes = ws.get_objects2({'objects': [{'ref': pangenome_ref,
                                             'included': ["/genome_refs/"]}]})['data'][0]['data']

        genome_refs = pangenome_genomes.get('genome_refs')
        genome_info = self.dfu.get_objects({'object_refs': [genome_ref]})['data'][0].get('info')

        genome_ref = str(genome_info[6]) + '/' + str(genome_info[0]) + '/' + str(genome_info[4])

        if genome_ref in genome_refs:
            ret = self.gsu.search({'ref': genome_ref,
                                   'query': query,
                                   'sort_by': sort_by,
                                   'start': start,
                                   'limit': limit,
                                   'num_found': num_found})
        else:
            raise ValueError('genome_ref [{}] does not exist in available genomes [{}]'.format(
                                                            genome_ref, ', '.join(genome_refs)))
        return ret

    def search_orthologs_from_pangenome(self, token, ref, query, sort_by, start, limit, num_found):
        if query is None:
            query = ""
        if start is None:
            start = 0
        if limit is None:
            limit = 50
        if self.debug:
            print("Search: PanGenome =" + ref + ", query=[" + query + "], sort-by=[" +
                  self.get_sorting_code(self.orthologs_column_props_map, sort_by) +
                  "], start=" + str(start) + ", limit=" + str(limit))
            t1 = time.time()
        inner_chsum = self.check_orthologs_cache(ref, token)
        index_iter = self.get_orthologs_sorted_iterator(inner_chsum, sort_by)
        ret = self.filter_orthologs_query(index_iter, query, start, limit, num_found)
        if self.debug:
            print("    (overall-time=" + str(time.time() - t1) + ")")

        return ret

    def filter_orthologs_query(self, index_iter, query, start, limit, num_found):
        query_words = str(query).lower().translate(string.maketrans("\r\n\t,", "    ")).split()
        if self.debug:
            print("    Filtering...")
            t1 = time.time()
        fcount = 0
        orthologs = []
        with index_iter:
            for line in index_iter:
                if all(word in line.lower() for word in query_words):
                    if fcount >= start and fcount < start + limit:
                        orthologs.append(self.unpack_orthologs(line.rstrip('\n')))
                    fcount += 1
                    if num_found is not None and fcount >= start + limit:
                        # Having shortcut when real num_found was already known
                        fcount = num_found
                        break
        if self.debug:
                print("    (time=" + str(time.time() - t1) + ")")
        return {"num_found": fcount, "start": start, "orthologs": orthologs,
                "query": query}

    def filter_families_query(self, index_iter, query, start, limit, num_found):
        query_words = str(query).lower().translate(string.maketrans("\r\n\t,", "    ")).split()
        if self.debug:
            print("    Filtering...")
            t1 = time.time()
        fcount = 0
        families = []
        with index_iter:
            for line in index_iter:
                if all(word in line.lower() for word in query_words):
                    if fcount >= start and fcount < start + limit:
                        families.append(self.unpack_families(line.rstrip('\n')))
                    fcount += 1
                    if num_found is not None and fcount >= start + limit:
                        # Having shortcut when real num_found was already known
                        fcount = num_found
                        break
        if self.debug:
                print("    (time=" + str(time.time() - t1) + ")")
        return {"num_found": fcount, "start": start, "families": families,
                "query": query}

    def filter_functions_query(self, index_iter, query, start, limit, num_found):
        query_words = str(query).lower().translate(string.maketrans("\r\n\t,", "    ")).split()
        if self.debug:
            print("    Filtering...")
            t1 = time.time()
        fcount = 0
        functions = []
        with index_iter:
            for line in index_iter:
                if all(word in line.lower() for word in query_words):
                    if fcount >= start and fcount < start + limit:
                        functions.append(self.unpack_functions(line.rstrip('\n')))
                    fcount += 1
                    if num_found is not None and fcount >= start + limit:
                        # Having shortcut when real num_found was already known
                        fcount = num_found
                        break
        if self.debug:
                print("    (time=" + str(time.time() - t1) + ")")
        return {"num_found": fcount, "start": start, "functions": functions,
                "query": query}

    def filter_comparison_genomes_query(self, index_iter, query, start, limit, num_found):
        query_words = str(query).lower().translate(string.maketrans("\r\n\t,", "    ")).split()
        if self.debug:
            print("    Filtering...")
            t1 = time.time()
        fcount = 0
        comparison_genomes = []
        with index_iter:
            for line in index_iter:
                if all(word in line.lower() for word in query_words):
                    if fcount >= start and fcount < start + limit:
                        comparison_genomes.append(self.unpack_comparison_genomes(line.rstrip('\n')))
                    fcount += 1
                    if num_found is not None and fcount >= start + limit:
                        # Having shortcut when real num_found was already known
                        fcount = num_found
                        break
        if self.debug:
                print("    (time=" + str(time.time() - t1) + ")")
        return {"num_found": fcount, "start": start, "comparison_genomes": comparison_genomes,
                "query": query}

    def unpack_orthologs(self, line, items=None):
        try:
            if items is None:
                items = line.split('\t')

            ortholog_id = items[0]
            ortholog_type = None
            ortholog_function = None
            ortholog_md5 = None
            ortholog_protein_translation = None
            ortholog_orthologs = None

            if items[1]:
                ortholog_type = items[1]
            if items[2]:
                ortholog_function = items[2]
            if items[3]:
                ortholog_md5 = items[3]
            if items[4]:
                ortholog_protein_translation = items[4]
            if items[5]:
                ortholog_orthologs = items[5]

            return {'id': ortholog_id,
                    'type': ortholog_type,
                    'function': ortholog_function,
                    'md5': ortholog_md5,
                    'protein_translation': ortholog_protein_translation,
                    'orthologs': ortholog_orthologs
                    }
        except:
            raise ValueError("Error parsing bin from: [" + line + "]\n" +
                             "Cause: " + traceback.format_exc())

    def unpack_families(self, line, items=None):
        try:
            if items is None:
                items = line.split('\t')

            family_core = None
            family_genome_features = None
            family_id = None
            family_type = None
            family_protein_translation = None
            family_number_genomes = None
            family_fraction_genomes = None
            family_fraction_consistent_annotations = None
            family_most_consistent_role = None

            if items[0]:
                family_core = items[0]
            if items[1]:
                family_genome_features = items[1]
            if items[2]:
                family_id = items[2]
            if items[3]:
                family_type = items[3]
            if items[4]:
                family_protein_translation = items[4]
            if items[5]:
                family_number_genomes = items[5]
            if items[6]:
                family_fraction_genomes = items[6]
            if items[7]:
                family_fraction_consistent_annotations = items[7]
            if items[8]:
                family_most_consistent_role = items[8]

            return {'core': family_core,
                    'genome_features': family_genome_features,
                    'id': family_id,
                    'type': family_type,
                    'protein_translation': family_protein_translation,
                    'number_genomes': family_number_genomes,
                    'fraction_genomes': family_fraction_genomes,
                    'fraction_consistent_annotations': family_fraction_consistent_annotations,
                    'most_consistent_role': family_most_consistent_role
                    }
        except:
            raise ValueError("Error parsing bin from: [" + line + "]\n" +
                             "Cause: " + traceback.format_exc())

    def unpack_functions(self, line, items=None):
        try:
            if items is None:
                items = line.split('\t')

            function_core = None
            function_genome_features = None
            function_id = None
            function_reactions = None
            function_subsystem = None
            function_primclass = None
            function_subclass = None
            function_number_genomes = None
            function_fraction_genomes = None
            function_fraction_consistent_families = None
            function_most_consistent_family = None

            if items[0]:
                function_core = items[0]
            if items[1]:
                function_genome_features = items[1]
            if items[2]:
                function_id = items[2]
            if items[3]:
                function_reactions = items[3]
            if items[4]:
                function_subsystem = items[4]
            if items[5]:
                function_primclass = items[5]
            if items[6]:
                function_subclass = items[6]
            if items[7]:
                function_number_genomes = items[7]
            if items[8]:
                function_fraction_genomes = items[8]
            if items[9]:
                function_fraction_consistent_families = items[9]
            if items[10]:
                function_most_consistent_family = items[10]

            return {'core': function_core,
                    'genome_features': function_genome_features,
                    'id': function_id,
                    'reactions': function_reactions,
                    'subsystem': function_subsystem,
                    'primclass': function_primclass,
                    'subclass': function_subclass,
                    'number_genomes': function_number_genomes,
                    'fraction_genomes': function_fraction_genomes,
                    'fraction_consistent_families': function_fraction_consistent_families,
                    'most_consistent_family': function_most_consistent_family
                    }
        except:
            raise ValueError("Error parsing bin from: [" + line + "]\n" +
                             "Cause: " + traceback.format_exc())

    def unpack_comparison_genomes(self, line, items=None):
        try:
            if items is None:
                items = line.split('\t')

            comparison_genome_id = None
            comparison_genome_genome_ref = None
            comparison_genome_genome_similarity = None
            comparison_genome_name = None
            comparison_genome_taxonomy = None
            comparison_genome_features = None
            comparison_genome_families = None
            comparison_genome_functions = None

            if items[0]:
                comparison_genome_id = items[0]
            if items[1]:
                comparison_genome_genome_ref = items[1]
            if items[2]:
                comparison_genome_genome_similarity = items[2]
            if items[3]:
                comparison_genome_name = items[3]
            if items[4]:
                comparison_genome_taxonomy = items[4]
            if items[5]:
                comparison_genome_features = items[5]
            if items[6]:
                comparison_genome_families = items[6]
            if items[7]:
                comparison_genome_functions = items[7]

            return {'id': comparison_genome_id,
                    'genome_ref': comparison_genome_genome_ref,
                    'genome_similarity': comparison_genome_genome_similarity,
                    'name': comparison_genome_name,
                    'taxonomy': comparison_genome_taxonomy,
                    'features': comparison_genome_features,
                    'families': comparison_genome_families,
                    'functions': comparison_genome_functions
                    }
        except:
            raise ValueError("Error parsing bin from: [" + line + "]\n" +
                             "Cause: " + traceback.format_exc())

    def check_orthologs_cache(self, ref, token):
        ws = Workspace(self.ws_url, token=token)
        info = ws.get_object_info3({"objects": [{"ref": ref}]})['infos'][0]
        inner_chsum = info[8]
        index_file = os.path.join(self.pangenome_index_dir,
                                  inner_chsum + self.ORTHOLOGS_SUFFIX + ".tsv.gz")
        if not os.path.isfile(index_file):
            if self.debug:
                print("    Loading WS object...")
                t1 = time.time()

            included = ["/orthologs/[*]/id",
                        "/orthologs/[*]/type",
                        "/orthologs/[*]/function",
                        "/orthologs/[*]/md5",
                        "/orthologs/[*]/protein_translation",
                        "/orthologs/[*]/orthologs"
                        ]

            pangenome = ws.get_objects2({'objects': [{'ref': ref,
                                                      'included': included}]})['data'][0]['data']
            self.save_orthologs_tsv(pangenome["orthologs"], inner_chsum)
            if self.debug:
                print("    (time=" + str(time.time() - t1) + ")")
        return inner_chsum

    def check_families_cache(self, ref, token):
        ws = Workspace(self.ws_url, token=token)
        info = ws.get_object_info3({"objects": [{"ref": ref}]})['infos'][0]
        inner_chsum = info[8]
        index_file = os.path.join(self.comparison_genome_index_dir,
                                  inner_chsum + self.FAMILIES_SUFFIX + ".tsv.gz")
        if not os.path.isfile(index_file):
            if self.debug:
                print("    Loading WS object...")
                t1 = time.time()

            included = ["/families/[*]/core",
                        "/families/[*]/genome_features",
                        "/families/[*]/id",
                        "/families/[*]/type",
                        "/families/[*]/protein_translation",
                        "/families/[*]/number_genomes",
                        "/families/[*]/fraction_genomes",
                        "/families/[*]/fraction_consistent_annotations",
                        "/families/[*]/most_consistent_role"
                        ]

            comparison_genome = ws.get_objects2({'objects': [{'ref': ref,
                                                 'included': included}]})['data'][0]['data']
            self.save_families_tsv(comparison_genome["families"], inner_chsum)
            if self.debug:
                print("    (time=" + str(time.time() - t1) + ")")
        return inner_chsum

    def check_functions_cache(self, ref, token):
        ws = Workspace(self.ws_url, token=token)
        info = ws.get_object_info3({"objects": [{"ref": ref}]})['infos'][0]
        inner_chsum = info[8]
        index_file = os.path.join(self.comparison_genome_index_dir,
                                  inner_chsum + self.FUNCTIONS_SUFFIX + ".tsv.gz")
        if not os.path.isfile(index_file):
            if self.debug:
                print("    Loading WS object...")
                t1 = time.time()

            included = ["/functions/[*]/core",
                        "/functions/[*]/genome_features",
                        "/functions/[*]/id",
                        "/functions/[*]/reactions",
                        "/functions/[*]/subsystem",
                        "/functions/[*]/primclass",
                        "/functions/[*]/subclass",
                        "/functions/[*]/number_genomes",
                        "/functions/[*]/fraction_genomes",
                        "/functions/[*]/fraction_consistent_families",
                        "/functions/[*]/most_consistent_family"
                        ]

            comparison_genome = ws.get_objects2({'objects': [{'ref': ref,
                                                 'included': included}]})['data'][0]['data']
            self.save_functions_tsv(comparison_genome["functions"], inner_chsum)
            if self.debug:
                print("    (time=" + str(time.time() - t1) + ")")
        return inner_chsum

    def check_comparison_genomes_cache(self, ref, token):
        ws = Workspace(self.ws_url, token=token)
        info = ws.get_object_info3({"objects": [{"ref": ref}]})['infos'][0]
        inner_chsum = info[8]
        index_file = os.path.join(self.comparison_genome_index_dir,
                                  inner_chsum + self.COMPARISON_GENOMES_SUFFIX + ".tsv.gz")
        if not os.path.isfile(index_file):
            if self.debug:
                print("    Loading WS object...")
                t1 = time.time()

            included = ["/genomes/[*]/id",
                        "/genomes/[*]/genome_ref",
                        "/genomes/[*]/genome_similarity",
                        "/genomes/[*]/name",
                        "/genomes/[*]/taxonomy",
                        "/genomes/[*]/features",
                        "/genomes/[*]/families",
                        "/genomes/[*]/functions"
                        ]

            comparison_genome = ws.get_objects2({'objects': [{'ref': ref,
                                                 'included': included}]})['data'][0]['data']
            self.save_comparison_genomes_tsv(comparison_genome["genomes"], inner_chsum)
            if self.debug:
                print("    (time=" + str(time.time() - t1) + ")")
        return inner_chsum

    def save_orthologs_tsv(self, orthologs, inner_chsum):
        outfile = tempfile.NamedTemporaryFile(dir=self.pangenome_index_dir,
                                              prefix=inner_chsum + self.ORTHOLOGS_SUFFIX,
                                              suffix=".tsv", delete=False)
        with outfile:
            for ortholog_data in orthologs:
                ortholog_id = self.to_text(ortholog_data, "id")
                ortholog_type = self.to_text(ortholog_data, "type")
                ortholog_function = self.to_text(ortholog_data, "function")
                ortholog_md5 = self.to_text(ortholog_data, "md5")
                ortholog_protein_translation = self.to_text(ortholog_data, "protein_translation")
                ortholog_orthologs = self.to_text(ortholog_data, "orthologs")

                line = u"\t".join(x for x in [ortholog_id, ortholog_type,
                                              ortholog_function, ortholog_md5,
                                              ortholog_protein_translation,
                                              ortholog_orthologs]) + u"\n"
                outfile.write(line.encode("utf-8"))

        subprocess.Popen(["gzip", outfile.name],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
        os.rename(outfile.name + ".gz",
                  os.path.join(self.pangenome_index_dir,
                               inner_chsum + self.ORTHOLOGS_SUFFIX + ".tsv.gz"))

    def save_families_tsv(self, families, inner_chsum):
        outfile = tempfile.NamedTemporaryFile(dir=self.comparison_genome_index_dir,
                                              prefix=inner_chsum + self.FAMILIES_SUFFIX,
                                              suffix=".tsv", delete=False)
        with outfile:
            for family_data in families:
                family_core = self.to_text(family_data, "core")
                family_genome_features = self.to_text(family_data, "genome_features")
                family_id = self.to_text(family_data, "id")
                family_type = self.to_text(family_data, "type")
                family_protein_translation = self.to_text(family_data, "protein_translation")
                family_number_genomes = self.to_text(family_data, "number_genomes")
                family_fraction_genomes = self.to_text(family_data, "fraction_genomes")
                family_fraction_consistent_annotations = self.to_text(
                                                                family_data,
                                                                "fraction_consistent_annotations")
                family_most_consistent_role = self.to_text(family_data, "most_consistent_role")

                line = u"\t".join(x for x in [family_core, family_genome_features, family_id,
                                              family_type, family_protein_translation,
                                              family_number_genomes, family_fraction_genomes,
                                              family_fraction_consistent_annotations,
                                              family_most_consistent_role]) + u"\n"
                outfile.write(line.encode("utf-8"))

        subprocess.Popen(["gzip", outfile.name],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
        os.rename(outfile.name + ".gz",
                  os.path.join(self.comparison_genome_index_dir,
                               inner_chsum + self.FAMILIES_SUFFIX + ".tsv.gz"))

    def save_functions_tsv(self, functions, inner_chsum):
        outfile = tempfile.NamedTemporaryFile(dir=self.comparison_genome_index_dir,
                                              prefix=inner_chsum + self.FUNCTIONS_SUFFIX,
                                              suffix=".tsv", delete=False)
        with outfile:
            for function_data in functions:
                function_core = self.to_text(function_data, "core")
                function_genome_features = self.to_text(function_data, "genome_features")
                function_id = self.to_text(function_data, "id")
                function_reactions = self.to_text(function_data, "reactions")
                function_subsystem = self.to_text(function_data, "subsystem")
                function_primclass = self.to_text(function_data, "primclass")
                function_subclass = self.to_text(function_data, "subclass")
                function_number_genomes = self.to_text(function_data, "number_genomes")
                function_fraction_genomes = self.to_text(function_data, "fraction_genomes")
                function_fraction_consistent_families = self.to_text(
                                                                function_data,
                                                                "fraction_consistent_families")
                function_most_consistent_family = self.to_text(function_data,
                                                               "most_consistent_family")

                line = u"\t".join(x for x in [function_core, function_genome_features, function_id,
                                              function_reactions, function_subsystem,
                                              function_primclass, function_subclass,
                                              function_number_genomes, function_fraction_genomes,
                                              function_fraction_consistent_families,
                                              function_most_consistent_family]) + u"\n"
                outfile.write(line.encode("utf-8"))

        subprocess.Popen(["gzip", outfile.name],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
        os.rename(outfile.name + ".gz",
                  os.path.join(self.comparison_genome_index_dir,
                               inner_chsum + self.FUNCTIONS_SUFFIX + ".tsv.gz"))

    def save_comparison_genomes_tsv(self, comparison_genomes, inner_chsum):
        outfile = tempfile.NamedTemporaryFile(dir=self.comparison_genome_index_dir,
                                              prefix=inner_chsum + self.COMPARISON_GENOMES_SUFFIX,
                                              suffix=".tsv", delete=False)
        with outfile:
            for comparison_genome_data in comparison_genomes:
                comparison_genome_id = self.to_text(comparison_genome_data, "id")
                comparison_genome_genome_ref = self.to_text(comparison_genome_data, "genome_ref")
                comparison_genome_genome_similarity = self.to_text(comparison_genome_data,
                                                                   "genome_similarity")
                comparison_genome_name = self.to_text(comparison_genome_data, "name")
                comparison_genome_taxonomy = self.to_text(comparison_genome_data, "taxonomy")
                comparison_genome_features = self.to_text(comparison_genome_data, "features")
                comparison_genome_families = self.to_text(comparison_genome_data, "families")
                comparison_genome_functions = self.to_text(comparison_genome_data, "functions")

                line = u"\t".join(x for x in [comparison_genome_id, comparison_genome_genome_ref,
                                              comparison_genome_genome_similarity,
                                              comparison_genome_name, comparison_genome_taxonomy,
                                              comparison_genome_features,
                                              comparison_genome_families,
                                              comparison_genome_functions]) + u"\n"
                outfile.write(line.encode("utf-8"))

        subprocess.Popen(["gzip", outfile.name],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
        os.rename(outfile.name + ".gz",
                  os.path.join(self.comparison_genome_index_dir,
                               inner_chsum + self.COMPARISON_GENOMES_SUFFIX + ".tsv.gz"))

    def to_text(self, mapping, key):
        if key not in mapping or mapping[key] is None:
            return ""
        value = mapping[key]
        if type(value) is list:
            return ",".join(str(x) for x in value if x)
        return str(value)

    def get_orthologs_sorted_iterator(self, inner_chsum, sort_by):
        return self.get_sorted_iterator(inner_chsum, sort_by, self.ORTHOLOGS_SUFFIX,
                                        self.orthologs_column_props_map,
                                        self.pangenome_index_dir)

    def get_families_sorted_iterator(self, inner_chsum, sort_by):
        return self.get_sorted_iterator(inner_chsum, sort_by, self.FAMILIES_SUFFIX,
                                        self.families_column_props_map,
                                        self.comparison_genome_index_dir)

    def get_functions_sorted_iterator(self, inner_chsum, sort_by):
        return self.get_sorted_iterator(inner_chsum, sort_by, self.FUNCTIONS_SUFFIX,
                                        self.functions_column_props_map,
                                        self.comparison_genome_index_dir)

    def get_comparison_genomes_sorted_iterator(self, inner_chsum, sort_by):
        return self.get_sorted_iterator(inner_chsum, sort_by, self.COMPARISON_GENOMES_SUFFIX,
                                        self.comparison_genomes_column_props_map,
                                        self.comparison_genome_index_dir)

    def get_sorting_code(self, column_props_map, sort_by):
        ret = ""
        if sort_by is None or len(sort_by) == 0:
            return ret
        for column_sorting in sort_by:
            col_name = column_sorting[0]
            col_props = self.get_column_props(column_props_map, col_name)
            col_pos = str(col_props["col"])
            ascending_order = column_sorting[1]
            ret += col_pos + ('a' if ascending_order else 'd')
        return ret

    def get_sorted_iterator(self, inner_chsum, sort_by, item_type, column_props_map, index_dir):
        input_file = os.path.join(index_dir, inner_chsum + item_type + ".tsv.gz")
        if not os.path.isfile(input_file):
            raise ValueError("File not found: " + input_file)
        if sort_by is None or len(sort_by) == 0:
            return CombinedLineIterator(input_file)
        cmd = "gunzip -c \"" + input_file + "\" | sort -f -t\\\t"
        for column_sorting in sort_by:
            col_name = column_sorting[0]
            col_props = self.get_column_props(column_props_map, col_name)
            col_pos = str(col_props["col"])
            ascending_order = column_sorting[1]
            sort_arg = "-k" + col_pos + "," + col_pos + col_props["type"]
            if not ascending_order:
                sort_arg += "r"
            cmd += " " + sort_arg
        fname = (inner_chsum + "_" + item_type + "_" +
                 self.get_sorting_code(column_props_map, sort_by))
        final_output_file = os.path.join(index_dir, fname + ".tsv.gz")
        if not os.path.isfile(final_output_file):
            if self.debug:
                print("    Sorting...")
                t1 = time.time()
            need_to_save = os.path.getsize(input_file) > self.max_sort_mem_size
            if need_to_save:
                outfile = tempfile.NamedTemporaryFile(dir=index_dir,
                                                      prefix=fname + "_", suffix=".tsv.gz",
                                                      delete=False)
                outfile.close()
                output_file = outfile.name
                cmd += " | gzip -c > \"" + output_file + "\""
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            if not need_to_save:
                if self.debug:
                    print("    (time=" + str(time.time() - t1) + ")")
                return CombinedLineIterator(p)
            else:
                p.wait()
                os.rename(output_file, final_output_file)
                if self.debug:
                    print("    (time=" + str(time.time() - t1) + ")")
        return CombinedLineIterator(final_output_file)
