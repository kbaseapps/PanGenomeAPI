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
        string ref;
        string query;
        list<column_sorting> sort_by;
        int start;
        int limit;
        int num_found;
    } SearchOrthologs;

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
            only part of it returned in "bins" list).
    */
    typedef structure {
        string query;
        int start;
        list<OrthologsData> orthologs;
        int num_found;
    } SearchOrthologsResult;

    funcdef search_orthologs_from_pangenome(SearchOrthologs params) 
        returns (SearchOrthologsResult result) authentication optional;
};
