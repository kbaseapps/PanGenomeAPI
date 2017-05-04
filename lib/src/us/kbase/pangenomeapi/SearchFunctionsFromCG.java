
package us.kbase.pangenomeapi;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import us.kbase.common.service.Tuple2;


/**
 * <p>Original spec-file type: SearchFunctionsFromCG</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "comparison_genome_ref",
    "query",
    "sort_by",
    "start",
    "limit",
    "num_found"
})
public class SearchFunctionsFromCG {

    @JsonProperty("comparison_genome_ref")
    private java.lang.String comparisonGenomeRef;
    @JsonProperty("query")
    private java.lang.String query;
    @JsonProperty("sort_by")
    private List<Tuple2 <String, Long>> sortBy;
    @JsonProperty("start")
    private java.lang.Long start;
    @JsonProperty("limit")
    private java.lang.Long limit;
    @JsonProperty("num_found")
    private java.lang.Long numFound;
    private Map<java.lang.String, Object> additionalProperties = new HashMap<java.lang.String, Object>();

    @JsonProperty("comparison_genome_ref")
    public java.lang.String getComparisonGenomeRef() {
        return comparisonGenomeRef;
    }

    @JsonProperty("comparison_genome_ref")
    public void setComparisonGenomeRef(java.lang.String comparisonGenomeRef) {
        this.comparisonGenomeRef = comparisonGenomeRef;
    }

    public SearchFunctionsFromCG withComparisonGenomeRef(java.lang.String comparisonGenomeRef) {
        this.comparisonGenomeRef = comparisonGenomeRef;
        return this;
    }

    @JsonProperty("query")
    public java.lang.String getQuery() {
        return query;
    }

    @JsonProperty("query")
    public void setQuery(java.lang.String query) {
        this.query = query;
    }

    public SearchFunctionsFromCG withQuery(java.lang.String query) {
        this.query = query;
        return this;
    }

    @JsonProperty("sort_by")
    public List<Tuple2 <String, Long>> getSortBy() {
        return sortBy;
    }

    @JsonProperty("sort_by")
    public void setSortBy(List<Tuple2 <String, Long>> sortBy) {
        this.sortBy = sortBy;
    }

    public SearchFunctionsFromCG withSortBy(List<Tuple2 <String, Long>> sortBy) {
        this.sortBy = sortBy;
        return this;
    }

    @JsonProperty("start")
    public java.lang.Long getStart() {
        return start;
    }

    @JsonProperty("start")
    public void setStart(java.lang.Long start) {
        this.start = start;
    }

    public SearchFunctionsFromCG withStart(java.lang.Long start) {
        this.start = start;
        return this;
    }

    @JsonProperty("limit")
    public java.lang.Long getLimit() {
        return limit;
    }

    @JsonProperty("limit")
    public void setLimit(java.lang.Long limit) {
        this.limit = limit;
    }

    public SearchFunctionsFromCG withLimit(java.lang.Long limit) {
        this.limit = limit;
        return this;
    }

    @JsonProperty("num_found")
    public java.lang.Long getNumFound() {
        return numFound;
    }

    @JsonProperty("num_found")
    public void setNumFound(java.lang.Long numFound) {
        this.numFound = numFound;
    }

    public SearchFunctionsFromCG withNumFound(java.lang.Long numFound) {
        this.numFound = numFound;
        return this;
    }

    @JsonAnyGetter
    public Map<java.lang.String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(java.lang.String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public java.lang.String toString() {
        return ((((((((((((((("SearchFunctionsFromCG"+" [comparisonGenomeRef=")+ comparisonGenomeRef)+", query=")+ query)+", sortBy=")+ sortBy)+", start=")+ start)+", limit=")+ limit)+", numFound=")+ numFound)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
