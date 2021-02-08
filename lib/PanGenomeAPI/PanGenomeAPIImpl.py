# -*- coding: utf-8 -*-
#BEGIN_HEADER
from PanGenomeAPI.PanGenomeIndexer import PanGenomeIndexer
from PanGenomeAPI.fetch_summary.main import fetch_pangenome_summary
#END_HEADER


class PanGenomeAPI:
    '''
    Module Name:
    PanGenomeAPI

    Module Description:
    A KBase module: PanGenomeAPI
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "1.2.1"
    GIT_URL = "https://github.com/kbaseapps/PanGenomeAPI"
    GIT_COMMIT_HASH = "44d57aa82618e61624cd882e7f3f5ee91ea93b96"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.config = config
        self.indexer = PanGenomeIndexer(config)
        #END_CONSTRUCTOR
        pass


    def search_orthologs_from_pangenome(self, ctx, params):
        """
        :param params: instance of type "SearchOrthologsFromPG" (num_found -
           optional field which when set informs that there is no need to
           perform full scan in order to count this value because it was
           already done before; please don't set this value with 0 or any
           guessed number if you didn't get right value previously.) ->
           structure: parameter "pangenome_ref" of String, parameter "query"
           of String, parameter "sort_by" of list of type "column_sorting" ->
           tuple of size 2: parameter "column" of String, parameter
           "ascending" of type "boolean" (Indicates true or false values,
           false = 0, true = 1 @range [0,1]), parameter "start" of Long,
           parameter "limit" of Long, parameter "num_found" of Long
        :returns: instance of type "SearchOrthologsFromPGResult" (num_found -
           number of all items found in query search (with only part of it
           returned in "orthologs" list).) -> structure: parameter "query" of
           String, parameter "start" of Long, parameter "orthologs" of list
           of type "OrthologsData" (OrthologFamily object: this object holds
           all data for a single ortholog family in a metagenome @optional
           type function md5 protein_translation) -> structure: parameter
           "id" of String, parameter "type" of String, parameter "function"
           of String, parameter "md5" of String, parameter
           "protein_translation" of String, parameter "orthologs" of list of
           tuple of size 3: String, Double, String, parameter "num_found" of
           Long
        """
        # ctx is the context object
        # return variables are: result
        #BEGIN search_orthologs_from_pangenome
        result = self.indexer.search_orthologs_from_pangenome(ctx["token"],
                                                              params.get("pangenome_ref", None),
                                                              params.get("query", None),
                                                              params.get("sort_by", None),
                                                              params.get("start", None),
                                                              params.get("limit", None),
                                                              params.get("num_found", None))
        #END search_orthologs_from_pangenome

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method search_orthologs_from_pangenome return value ' +
                             'result is not type dict as required.')
        # return the results
        return [result]

    def search_families_from_comparison_genome(self, ctx, params):
        """
        :param params: instance of type "SearchFamiliesFromCG" -> structure:
           parameter "comparison_genome_ref" of String, parameter "query" of
           String, parameter "sort_by" of list of type "column_sorting" ->
           tuple of size 2: parameter "column" of String, parameter
           "ascending" of type "boolean" (Indicates true or false values,
           false = 0, true = 1 @range [0,1]), parameter "start" of Long,
           parameter "limit" of Long, parameter "num_found" of Long
        :returns: instance of type "SearchFamiliesFromCGResult" (num_found -
           number of all items found in query search (with only part of it
           returned in "families" list).) -> structure: parameter "query" of
           String, parameter "start" of Long, parameter "families" of list of
           type "GenomeComparisonFamily" (GenomeComparisonFamily object: this
           object holds information about a protein family across a set of
           genomes) -> structure: parameter "core" of Long, parameter
           "genome_features" of mapping from String to list of tuple of size
           3: type "Feature_id", list of Long, Double, parameter "id" of
           String, parameter "type" of String, parameter
           "protein_translation" of String, parameter "number_genomes" of
           Long, parameter "fraction_genomes" of Double, parameter
           "fraction_consistent_annotations" of Double, parameter
           "most_consistent_role" of String, parameter "num_found" of Long
        """
        # ctx is the context object
        # return variables are: result
        #BEGIN search_families_from_comparison_genome
        result = self.indexer.search_families_from_comparison_genome(
                                                          ctx["token"],
                                                          params.get("comparison_genome_ref", None),
                                                          params.get("query", None),
                                                          params.get("sort_by", None),
                                                          params.get("start", None),
                                                          params.get("limit", None),
                                                          params.get("num_found", None))
        #END search_families_from_comparison_genome

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method search_families_from_comparison_genome return value ' +
                             'result is not type dict as required.')
        # return the results
        return [result]

    def search_functions_from_comparison_genome(self, ctx, params):
        """
        :param params: instance of type "SearchFunctionsFromCG" -> structure:
           parameter "comparison_genome_ref" of String, parameter "query" of
           String, parameter "sort_by" of list of type "column_sorting" ->
           tuple of size 2: parameter "column" of String, parameter
           "ascending" of type "boolean" (Indicates true or false values,
           false = 0, true = 1 @range [0,1]), parameter "start" of Long,
           parameter "limit" of Long, parameter "num_found" of Long
        :returns: instance of type "SearchFunctionsFromCGResult" (num_found -
           number of all items found in query search (with only part of it
           returned in "functions" list).) -> structure: parameter "query" of
           String, parameter "start" of Long, parameter "functions" of list
           of type "GenomeComparisonFunction" (GenomeComparisonFunction
           object: this object holds information about a genome in a function
           across all genomes) -> structure: parameter "core" of Long,
           parameter "genome_features" of mapping from String to list of
           tuple of size 3: type "Feature_id", Long, Double, parameter "id"
           of String, parameter "reactions" of list of tuple of size 2: type
           "Reaction_id", String, parameter "subsystem" of String, parameter
           "primclass" of String, parameter "subclass" of String, parameter
           "number_genomes" of Long, parameter "fraction_genomes" of Double,
           parameter "fraction_consistent_families" of Double, parameter
           "most_consistent_family" of String, parameter "num_found" of Long
        """
        # ctx is the context object
        # return variables are: result
        #BEGIN search_functions_from_comparison_genome
        result = self.indexer.search_functions_from_comparison_genome(
                                                          ctx["token"],
                                                          params.get("comparison_genome_ref", None),
                                                          params.get("query", None),
                                                          params.get("sort_by", None),
                                                          params.get("start", None),
                                                          params.get("limit", None),
                                                          params.get("num_found", None))
        #END search_functions_from_comparison_genome

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method search_functions_from_comparison_genome return value ' +
                             'result is not type dict as required.')
        # return the results
        return [result]

    def search_comparison_genome_from_comparison_genome(self, ctx, params):
        """
        :param params: instance of type "SearchComparisonGenomesFromCG" ->
           structure: parameter "comparison_genome_ref" of String, parameter
           "query" of String, parameter "sort_by" of list of type
           "column_sorting" -> tuple of size 2: parameter "column" of String,
           parameter "ascending" of type "boolean" (Indicates true or false
           values, false = 0, true = 1 @range [0,1]), parameter "start" of
           Long, parameter "limit" of Long, parameter "num_found" of Long
        :returns: instance of type "SearchComparisonGenomesFromCGResult"
           (num_found - number of all items found in query search (with only
           part of it returned in "comparison genomes" list).) -> structure:
           parameter "query" of String, parameter "start" of Long, parameter
           "comparison_genomes" of list of type "GenomeComparisonGenome"
           (GenomeComparisonGenome object: this object holds information
           about a genome in a genome comparison) -> structure: parameter
           "id" of String, parameter "genome_ref" of type "Genome_ref",
           parameter "genome_similarity" of mapping from String to tuple of
           size 2: Long, Long, parameter "name" of String, parameter
           "taxonomy" of String, parameter "features" of Long, parameter
           "families" of Long, parameter "functions" of Long, parameter
           "num_found" of Long
        """
        # ctx is the context object
        # return variables are: result
        #BEGIN search_comparison_genome_from_comparison_genome
        result = self.indexer.search_comparison_genome_from_comparison_genome(
                                                          ctx["token"],
                                                          params.get("comparison_genome_ref", None),
                                                          params.get("query", None),
                                                          params.get("sort_by", None),
                                                          params.get("start", None),
                                                          params.get("limit", None),
                                                          params.get("num_found", None))
        #END search_comparison_genome_from_comparison_genome

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method search_comparison_genome_from_comparison_genome return value ' +
                             'result is not type dict as required.')
        # return the results
        return [result]

    def compute_summary_from_pangenome(self, ctx, params):
        """
        @deprecated compute_summary_from_pangenome2
        :param params: instance of type "ComputeSummaryFromPG" -> structure:
           parameter "pangenome_ref" of String
        :returns: instance of type "ComputeSummaryFromPGResult" -> structure:
           parameter "families" of mapping from String to Long, parameter
           "genes" of mapping from String to Long, parameter
           "shared_family_map" of mapping from String to mapping from String
           to Long, parameter "genome_ref_name_map" of mapping from String to
           mapping from String to String, parameter "pangenome_id" of String,
           parameter "genomes" of Long
        """
        # ctx is the context object
        # return variables are: result
        #BEGIN compute_summary_from_pangenome
        result = self.indexer.compute_summary_from_pangenome(
                                                          ctx["token"],
                                                          params.get("pangenome_ref", None))
        #END compute_summary_from_pangenome

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method compute_summary_from_pangenome return value ' +
                             'result is not type dict as required.')
        # return the results
        return [result]

    def compute_summary_from_pangenome2(self, ctx, params):
        """
        Compute a summary of the pangenome, with various counts and aggregations.
        :param params: instance of type "ComputeSummaryFromPG" -> structure:
           parameter "pangenome_ref" of String
        :returns: instance of type "Summary2Result" (* Return type for the
           compute_summary_from_pangenome2 function. * Much of this matches
           the ComputeSummaryFromPG type, with some corrections. *
           Properties: *     pangenome_id: string identifier from the
           Pangenome object (under data/id) *     genomes_count: total
           genomes included in this pangenome *     genes: counts of total
           genes, families, and singletons in the pangenome *     families:
           counts of total families and single families *     genomes:
           mapping of genome workspace reference to gene/family counts for
           each *     shared_family_map: *         mapping of genome IDs to
           other genome IDs, with the nested *         values being the count
           of shared gene families. For example: *         {"1": {"2": 10}}
           says that genome "1" and genome "2" have 10 *         shared gene
           families. *     genome_ref_name_map: *         mapping from genome
           refs to a unique displayable/readable string *         that
           includes the scientific and object names for each genome.) ->
           structure: parameter "pangenome_id" of String, parameter
           "genomes_count" of Long, parameter "genes" of type
           "GeneFamilyReport" (* Report of gene counts for a pangenome, or a
           subset within a pangenome. * Properties: *     genes_count: total
           number of genes *     homolog_family_genes_count: total number of
           genes in non-singleton families *    
           singleton_family_genes_count: total number of genes in families
           with only one member) -> structure: parameter "genes_count" of
           Long, parameter "homolog_family_genes_count" of Long, parameter
           "singleton_family_genes_count" of Long, parameter "families" of
           type "FamilyReport" (Report of counts for each homolog family * A
           lot of this is redundant with GeneFamilyReport, but included for
           backwards compatibility. * Properties: *     families_counts:
           total count of homolog families *     homolog_families_count:
           total count of non-singleton families (TODO is this right?) *    
           singleton_families_count: total count of singleton families) ->
           structure: parameter "families_count" of Long, parameter
           "homolog_families_count" of Long, parameter
           "singleton_families_count" of Long, parameter "genomes" of mapping
           from String to type "GenomeGeneFamilyReport" (* This is the same
           as GeneFamilyReport with different keys. This only * exists for
           frontend compatibility reasons. * Properties: *   genome_genes:
           total count of genes *   genome_homolog_family_genes: total count
           of genes in non-singleton families *  
           genome_singleton_family_genes: total count of genes in singleton
           families *   genome_homolog_family: total count of homolog
           families) -> structure: parameter "genome_genes" of Long,
           parameter "genome_homolog_family_genes" of Long, parameter
           "genome_singleton_family_genes" of Long, parameter
           "genome_homolog_family" of Long, parameter "shared_family_map" of
           mapping from String to mapping from String to Long, parameter
           "genome_ref_name_map" of mapping from String to String
        """
        # ctx is the context object
        # return variables are: result
        #BEGIN compute_summary_from_pangenome2
        result = fetch_pangenome_summary(
            params["pangenome_ref"],
            self.config["workspace-url"],
            ctx["token"],
        )
        #END compute_summary_from_pangenome2

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method compute_summary_from_pangenome2 return value ' +
                             'result is not type dict as required.')
        # return the results
        return [result]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
