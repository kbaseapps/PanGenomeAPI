/*
A KBase module: PanGenomeAPI
*/

module PanGenomeAPI {
    /*
        Indicates true or false values, false = 0, true = 1
        @range [0,1]
    */
    typedef int boolean;

    typedef tuple<string column, boolean ascending> column_sorting;

    /*
        num_found - optional field which when set informs that there
            is no need to perform full scan in order to count this
            value because it was already done before; please don't
            set this value with 0 or any guessed number if you didn't 
            get right value previously.
    */
    typedef structure {
        string pangenome_ref;
        string query;
        list<column_sorting> sort_by;
        int start;
        int limit;
        int num_found;
    } SearchOrthologsFromPG;

    /*
        OrthologFamily object: this object holds all data for a single ortholog family in a metagenome

        @optional type function md5 protein_translation
    */
    typedef structure {
        string id;
        string type;
        string function;
        string md5;
        string protein_translation;
        list<tuple<string, float, string>> orthologs;
    } OrthologsData;

    /*
        num_found - number of all items found in query search (with 
            only part of it returned in "orthologs" list).
    */
    typedef structure {
        string query;
        int start;
        list<OrthologsData> orthologs;
        int num_found;
    } SearchOrthologsFromPGResult;

    funcdef search_orthologs_from_pangenome(SearchOrthologsFromPG params) 
        returns (SearchOrthologsFromPGResult result) authentication optional;

    typedef structure {
        string pangenome_ref;
        string genome_ref;
        string query;
        list<column_sorting> sort_by;
        int start;
        int limit;
        int num_found;
    } SearchGenomesFromPG;

    typedef structure {
        string contig_id;
        int start;
        string strand;
        int length;
    } Location;

    /*
        aliases - mapping from alias name (key) to set of alias sources 
            (value),
        global_location - this is location-related properties that are
            under sorting whereas items in "location" array are not,
        feature_idx - legacy field keeping the position of feature in
            feature array in legacy Genome object,
        ontology_terms - mapping from term ID (key) to term name (value).
    */
    typedef structure {
        string feature_id;
        mapping<string, list<string>> aliases;
        string function;
        list<Location> location;
        string feature_type;
        Location global_location;
        int feature_idx;
        mapping<string, string> ontology_terms;
    } FeatureData;

    /*
        num_found - number of all items found in query search (with 
            only part of it returned in "features" list).
    */
    typedef structure {
        string query;
        int start;
        list<FeatureData> features;
        int num_found;
    } SearchGenomesFromPGResult;

    funcdef search_genomes_from_pangenome(SearchGenomesFromPG params) 
        returns (SearchGenomesFromPGResult result) authentication optional;

    typedef structure {
        string comparison_genome_ref;
        string query;
        list<column_sorting> sort_by;
        int start;
        int limit;
        int num_found;
    } SearchFamiliesFromCG;

    typedef string Feature_id;

    /*
        GenomeComparisonFamily object: this object holds information about a protein family across a set of genomes
    */
    typedef structure {
      int core;
      mapping<string, list<tuple<Feature_id, list<int>, float>>> genome_features;
      string id;
      string type;
      string protein_translation;
      int number_genomes;
      float fraction_genomes;
      float fraction_consistent_annotations;
      string most_consistent_role;
    } GenomeComparisonFamily;

    /*
        num_found - number of all items found in query search (with 
            only part of it returned in "families" list).
    */
    typedef structure {
        string query;
        int start;
        list<GenomeComparisonFamily> families;
        int num_found;
    } SearchFamiliesFromCGResult;

    funcdef search_families_from_comparison_genome(SearchFamiliesFromCG params) 
        returns (SearchFamiliesFromCGResult result) authentication optional;

    typedef structure {
        string comparison_genome_ref;
        string query;
        list<column_sorting> sort_by;
        int start;
        int limit;
        int num_found;
    } SearchFunctionsFromCG;

    typedef string Reaction_id;

    /*
        GenomeComparisonFunction object: this object holds information about a genome in a function across all genomes
    */
    typedef structure {
        int core;
        mapping<string, list<tuple<Feature_id, int, float>>> genome_features;
        string id;
        list<tuple<Reaction_id, string>> reactions;
        string subsystem;
        string primclass;
        string subclass;
        int number_genomes;
        float fraction_genomes;
        float fraction_consistent_families;
        string most_consistent_family;
    } GenomeComparisonFunction;

    /*
        num_found - number of all items found in query search (with 
            only part of it returned in "functions" list).
    */
    typedef structure {
        string query;
        int start;
        list<GenomeComparisonFunction> functions;
        int num_found;
    } SearchFunctionsFromCGResult;

    funcdef search_functions_from_comparison_genome(SearchFunctionsFromCG params) 
        returns (SearchFunctionsFromCGResult result) authentication optional;

    typedef structure {
        string comparison_genome_ref;
        string query;
        list<column_sorting> sort_by;
        int start;
        int limit;
        int num_found;
    } SearchComparisonGenomesFromCG;

    typedef string Genome_ref;

    /*
        GenomeComparisonGenome object: this object holds information about a genome in a genome comparison
    */
    typedef structure {
        string id;
        Genome_ref genome_ref;
        mapping<string, tuple<int, int>> genome_similarity;
        string name;
        string taxonomy;
        int features;
        int families;
        int functions;
    } GenomeComparisonGenome;

    /*
        num_found - number of all items found in query search (with 
            only part of it returned in "comparison genomes" list).
    */
    typedef structure {
        string query;
        int start;
        list<GenomeComparisonGenome> comparison_genomes;
        int num_found;
    } SearchComparisonGenomesFromCGResult;

    funcdef search_comparison_genome_from_comparison_genome(SearchComparisonGenomesFromCG params) 
        returns (SearchComparisonGenomesFromCGResult result) authentication optional;
};
