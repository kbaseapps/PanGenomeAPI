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

        self.ORTHOLOGS_SUFFIX = '_orthologs'

        self.ws_url = config["workspace-url"]
        self.pangenome_index_dir = config["pangenome-index-dir"]
        if not os.path.isdir(self.pangenome_index_dir):
            os.makedirs(self.pangenome_index_dir)
        self.debug = "debug" in config and config["debug"] == "1"
        self.max_sort_mem_size = 250000
        self.unicode_comma = u"\uFF0C"
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.gsu = GenomeSearchUtil(self.callback_url)

    # def search_genomes_from_pangenome(self, token, pangenome_ref, genome_ref, query, sort_by,
    #                                   start, limit, num_found):

    #     included = ["/genome_refs/"]

    #     # "/bins/[*]/bid"
    #     ws = Workspace(self.ws_url, token=token)
    #     pangenome = ws.get_objects2({'objects': [{'ref': pangenome_ref,
    #                                               'included': included}]})['data'][0]['data']

    #     print pangenome

    #     # ret = self.gsu.search({'ref': genome_ref,
    #     #                        'query': query,
    #     #                        'sort_by': sort_by,
    #     #                        'start': start,
    #     #                        'limit': limit,
    #     #                        'num_found': num_found})
    #     ret = {'a': 's'}
    #     return ret

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

    def save_orthologs_tsv(self, orthologs, inner_chsum):
        outfile = tempfile.NamedTemporaryFile(dir=self.pangenome_index_dir,
                                              prefix=inner_chsum + self.ORTHOLOGS_SUFFIX,
                                              suffix=".tsv", delete=False)
        with outfile:
            for ortholog_data in orthologs:
                ortholog_id = self.to_text(ortholog_data, "id")
                ortholog_type = ''
                if 'type' in ortholog_data:
                    ortholog_type = str(ortholog_data['type'])
                ortholog_function = ''
                if 'function' in ortholog_data:
                    ortholog_function = str(ortholog_data['function'])
                ortholog_md5 = ''
                if 'md5' in ortholog_data:
                    ortholog_md5 = str(ortholog_data['md5'])
                ortholog_protein_translation = ''
                if 'protein_translation' in ortholog_data:
                    ortholog_protein_translation = str(ortholog_data['protein_translation'])
                if 'orthologs' in ortholog_data:
                    ortholog_orthologs = str(ortholog_data['orthologs'])

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

    def to_text(self, mapping, key):
        if key not in mapping or mapping[key] is None:
            return ""
        value = mapping[key]
        if type(value) is list:
            return ",".join(str(x) for x in value if x)
        return str(value)

    def get_orthologs_sorted_iterator(self, inner_chsum, sort_by):
        return self.get_sorted_iterator(inner_chsum, sort_by, self.ORTHOLOGS_SUFFIX,
                                        self.orthologs_column_props_map)

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

    def get_sorted_iterator(self, inner_chsum, sort_by, item_type, column_props_map):
        input_file = os.path.join(self.pangenome_index_dir, inner_chsum + item_type + ".tsv.gz")
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
        final_output_file = os.path.join(self.pangenome_index_dir, fname + ".tsv.gz")
        if not os.path.isfile(final_output_file):
            if self.debug:
                print("    Sorting...")
                t1 = time.time()
            need_to_save = os.path.getsize(input_file) > self.max_sort_mem_size
            if need_to_save:
                outfile = tempfile.NamedTemporaryFile(dir=self.pangenome_index_dir,
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
