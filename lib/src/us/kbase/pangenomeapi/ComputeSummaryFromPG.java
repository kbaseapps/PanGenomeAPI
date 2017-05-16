
package us.kbase.pangenomeapi;

import java.util.HashMap;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * <p>Original spec-file type: ComputeSummaryFromPG</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "pangenome_ref"
})
public class ComputeSummaryFromPG {

    @JsonProperty("pangenome_ref")
    private String pangenomeRef;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("pangenome_ref")
    public String getPangenomeRef() {
        return pangenomeRef;
    }

    @JsonProperty("pangenome_ref")
    public void setPangenomeRef(String pangenomeRef) {
        this.pangenomeRef = pangenomeRef;
    }

    public ComputeSummaryFromPG withPangenomeRef(String pangenomeRef) {
        this.pangenomeRef = pangenomeRef;
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
        return ((((("ComputeSummaryFromPG"+" [pangenomeRef=")+ pangenomeRef)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
