
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


/**
 * <p>Original spec-file type: SearchComparisonGenomesFromCGResult</p>
 * <pre>
 * num_found - number of all items found in query search (with 
 *     only part of it returned in "comparison genomes" list).
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "query",
    "start",
    "comparison_genomes",
    "num_found"
})
public class SearchComparisonGenomesFromCGResult {

    @JsonProperty("query")
    private String query;
    @JsonProperty("start")
    private Long start;
    @JsonProperty("comparison_genomes")
    private List<GenomeComparisonGenome> comparisonGenomes;
    @JsonProperty("num_found")
    private Long numFound;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("query")
    public String getQuery() {
        return query;
    }

    @JsonProperty("query")
    public void setQuery(String query) {
        this.query = query;
    }

    public SearchComparisonGenomesFromCGResult withQuery(String query) {
        this.query = query;
        return this;
    }

    @JsonProperty("start")
    public Long getStart() {
        return start;
    }

    @JsonProperty("start")
    public void setStart(Long start) {
        this.start = start;
    }

    public SearchComparisonGenomesFromCGResult withStart(Long start) {
        this.start = start;
        return this;
    }

    @JsonProperty("comparison_genomes")
    public List<GenomeComparisonGenome> getComparisonGenomes() {
        return comparisonGenomes;
    }

    @JsonProperty("comparison_genomes")
    public void setComparisonGenomes(List<GenomeComparisonGenome> comparisonGenomes) {
        this.comparisonGenomes = comparisonGenomes;
    }

    public SearchComparisonGenomesFromCGResult withComparisonGenomes(List<GenomeComparisonGenome> comparisonGenomes) {
        this.comparisonGenomes = comparisonGenomes;
        return this;
    }

    @JsonProperty("num_found")
    public Long getNumFound() {
        return numFound;
    }

    @JsonProperty("num_found")
    public void setNumFound(Long numFound) {
        this.numFound = numFound;
    }

    public SearchComparisonGenomesFromCGResult withNumFound(Long numFound) {
        this.numFound = numFound;
        return this;
    }

    @JsonAnyGetter
    public Map<String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public String toString() {
        return ((((((((((("SearchComparisonGenomesFromCGResult"+" [query=")+ query)+", start=")+ start)+", comparisonGenomes=")+ comparisonGenomes)+", numFound=")+ numFound)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
