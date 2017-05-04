
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
 * <p>Original spec-file type: SearchFunctionsFromCGResult</p>
 * <pre>
 * num_found - number of all items found in query search (with 
 *     only part of it returned in "functions" list).
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "query",
    "start",
    "functions",
    "num_found"
})
public class SearchFunctionsFromCGResult {

    @JsonProperty("query")
    private String query;
    @JsonProperty("start")
    private Long start;
    @JsonProperty("functions")
    private List<GenomeComparisonFunction> functions;
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

    public SearchFunctionsFromCGResult withQuery(String query) {
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

    public SearchFunctionsFromCGResult withStart(Long start) {
        this.start = start;
        return this;
    }

    @JsonProperty("functions")
    public List<GenomeComparisonFunction> getFunctions() {
        return functions;
    }

    @JsonProperty("functions")
    public void setFunctions(List<GenomeComparisonFunction> functions) {
        this.functions = functions;
    }

    public SearchFunctionsFromCGResult withFunctions(List<GenomeComparisonFunction> functions) {
        this.functions = functions;
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

    public SearchFunctionsFromCGResult withNumFound(Long numFound) {
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
        return ((((((((((("SearchFunctionsFromCGResult"+" [query=")+ query)+", start=")+ start)+", functions=")+ functions)+", numFound=")+ numFound)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
