import os
import time
import tempfile
import subprocess
import string
import traceback

from Workspace.WorkspaceClient import Workspace as Workspace
from PanGenomeAPI.CombinedLineIterator import CombinedLineIterator


class TableIndexer:

    def __init__(self, ref, token, debug, ws_url, index_dir, object_suffix, search_object,
                 info_included, query, sort_by, start, limit, num_found):
        self.ref = ref
        self.token = token
        self.debug = debug
        self.ws_url = ws_url
        self.index_dir = index_dir
        self.object_suffix = object_suffix
        self.search_object = search_object
        self.info_included = info_included
        self.query = query
        self.sort_by = sort_by
        self.start = start
        self.limit = limit
        self.num_found = num_found
        self.max_sort_mem_size = 250000

        self.object_column_props_map = self.build_object_column_props_map(self.info_included)

    def run_search(self):

        if self.query is None:
            self.query = ""
        if self.start is None:
            self.start = 0
        if self.limit is None:
            self.limit = 50
        if self.debug:
            print("Search: Object =" + self.ref + ", query=[" + self.query + "], sort-by=[" +
                  self.get_sorting_code(self.object_column_props_map, self.sort_by) +
                  "], start=" + str(self.start) + ", limit=" + str(self.limit))
            t1 = time.time()

        inner_chsum = self.check_object_cache()
        index_iter = self.get_object_sorted_iterator(inner_chsum)
        ret = self.filter_obejct_query(index_iter)

        if self.debug:
            print("    (overall-time=" + str(time.time() - t1) + ")")

        return ret

    def check_object_cache(self):
        ws = Workspace(self.ws_url, token=self.token)
        info = ws.get_object_info3({"objects": [{"ref": self.ref}]})['infos'][0]
        inner_chsum = info[8]
        index_file = os.path.join(self.index_dir,
                                  inner_chsum + self.object_suffix + ".tsv.gz")
        if not os.path.isfile(index_file):
            if self.debug:
                print("    Loading WS object...")
                t1 = time.time()

            included = self.build_info_included(self.search_object, self.info_included)
            object = ws.get_objects2({'objects': [{'ref': self.ref,
                                                   'included': included}]})['data'][0]['data']
            self.save_object_tsv(object[self.search_object], inner_chsum)
            if self.debug:
                print("    (time=" + str(time.time() - t1) + ")")
        return inner_chsum

    def build_info_included(self, search_object, info_included):

        included = []

        for info in info_included:
            included.append("/{}/[*]/{}".format(search_object, info))

        return included

    def save_object_tsv(self, search_object_infos, inner_chsum):
        outfile = tempfile.NamedTemporaryFile(dir=self.index_dir,
                                              prefix=inner_chsum + self.object_suffix,
                                              suffix=".tsv", delete=False)
        with outfile:
            for search_object_info in search_object_infos:

                line = u""

                for info in self.info_included:
                    object_info = self.to_text(search_object_info, info)
                    line += object_info + "\t"

                line = line[:-1] + u"\n"
                outfile.write(line.encode("utf-8"))

        subprocess.Popen(["gzip", outfile.name],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
        os.rename(outfile.name + ".gz",
                  os.path.join(self.index_dir,
                               inner_chsum + self.object_suffix + ".tsv.gz"))

    def to_text(self, mapping, key):
        if key not in mapping or mapping[key] is None:
            return ""
        value = mapping[key]
        if type(value) is list:
            return ",".join(str(x) for x in value if x)
        return str(value)

    def get_object_sorted_iterator(self, inner_chsum):
        return self.get_sorted_iterator(inner_chsum, self.sort_by, self.object_suffix,
                                        self.object_column_props_map,
                                        self.index_dir)

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

    def get_column_props(self, column_props_map, col_name):
        if col_name not in column_props_map:
            raise ValueError("Unknown column name '" + col_name + "', " +
                             "please use one of " + str(column_props_map.keys()))
        return column_props_map[col_name]

    def build_object_column_props_map(self, info_included):

        object_column_props_map = {}
        count = 1

        for info in info_included:
            object_column_props_map.update({
                info: {"col": count, "type": ""}
                })
            count += 1

        return object_column_props_map

    def filter_obejct_query(self, index_iter):
        query_words = str(self.query).lower().translate(string.maketrans("\r\n\t,", "    ")).split()
        if self.debug:
            print("    Filtering...")
            t1 = time.time()
        fcount = 0
        objects = []
        with index_iter:
            for line in index_iter:
                if all(word in line.lower() for word in query_words):
                    if fcount >= self.start and fcount < self.start + self.limit:
                        objects.append(self.unpack_objects(line.rstrip('\n')))
                    fcount += 1
                    if self.num_found is not None and fcount >= self.start + self.limit:
                        # Having shortcut when real num_found was already known
                        fcount = self.num_found
                        break
        if self.debug:
                print("    (time=" + str(time.time() - t1) + ")")
        return {"num_found": fcount, "start": self.start,
                "{}".format(self.search_object): objects,
                "query": self.query}

    def unpack_objects(self, line, items=None):
        try:
            if items is None:
                items = line.split('\t')

            search_object_info = {}
            index = 0
            for item in items:
                if item:
                    search_object_info.update({self.info_included[index]: item})
                else:
                    search_object_info.update({self.info_included[index]: None})
                index += 1

            return search_object_info
        except:
            raise ValueError("Error parsing bin from: [" + line + "]\n" +
                             "Cause: " + traceback.format_exc())
