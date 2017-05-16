
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
 * <p>Original spec-file type: ComputeSummaryFromPGResult</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "families",
    "genes",
    "shared_family_map",
    "genome_ref_name_map",
    "pangenome_id",
    "genomes"
})
public class ComputeSummaryFromPGResult {

    @JsonProperty("families")
    private Map<String, Long> families;
    @JsonProperty("genes")
    private Map<String, Long> genes;
    @JsonProperty("shared_family_map")
    private Map<String, Map<String, Long>> sharedFamilyMap;
    @JsonProperty("genome_ref_name_map")
    private Map<String, Map<String, String>> genomeRefNameMap;
    @JsonProperty("pangenome_id")
    private java.lang.String pangenomeId;
    @JsonProperty("genomes")
    private java.lang.Long genomes;
    private Map<java.lang.String, Object> additionalProperties = new HashMap<java.lang.String, Object>();

    @JsonProperty("families")
    public Map<String, Long> getFamilies() {
        return families;
    }

    @JsonProperty("families")
    public void setFamilies(Map<String, Long> families) {
        this.families = families;
    }

    public ComputeSummaryFromPGResult withFamilies(Map<String, Long> families) {
        this.families = families;
        return this;
    }

    @JsonProperty("genes")
    public Map<String, Long> getGenes() {
        return genes;
    }

    @JsonProperty("genes")
    public void setGenes(Map<String, Long> genes) {
        this.genes = genes;
    }

    public ComputeSummaryFromPGResult withGenes(Map<String, Long> genes) {
        this.genes = genes;
        return this;
    }

    @JsonProperty("shared_family_map")
    public Map<String, Map<String, Long>> getSharedFamilyMap() {
        return sharedFamilyMap;
    }

    @JsonProperty("shared_family_map")
    public void setSharedFamilyMap(Map<String, Map<String, Long>> sharedFamilyMap) {
        this.sharedFamilyMap = sharedFamilyMap;
    }

    public ComputeSummaryFromPGResult withSharedFamilyMap(Map<String, Map<String, Long>> sharedFamilyMap) {
        this.sharedFamilyMap = sharedFamilyMap;
        return this;
    }

    @JsonProperty("genome_ref_name_map")
    public Map<String, Map<String, String>> getGenomeRefNameMap() {
        return genomeRefNameMap;
    }

    @JsonProperty("genome_ref_name_map")
    public void setGenomeRefNameMap(Map<String, Map<String, String>> genomeRefNameMap) {
        this.genomeRefNameMap = genomeRefNameMap;
    }

    public ComputeSummaryFromPGResult withGenomeRefNameMap(Map<String, Map<String, String>> genomeRefNameMap) {
        this.genomeRefNameMap = genomeRefNameMap;
        return this;
    }

    @JsonProperty("pangenome_id")
    public java.lang.String getPangenomeId() {
        return pangenomeId;
    }

    @JsonProperty("pangenome_id")
    public void setPangenomeId(java.lang.String pangenomeId) {
        this.pangenomeId = pangenomeId;
    }

    public ComputeSummaryFromPGResult withPangenomeId(java.lang.String pangenomeId) {
        this.pangenomeId = pangenomeId;
        return this;
    }

    @JsonProperty("genomes")
    public java.lang.Long getGenomes() {
        return genomes;
    }

    @JsonProperty("genomes")
    public void setGenomes(java.lang.Long genomes) {
        this.genomes = genomes;
    }

    public ComputeSummaryFromPGResult withGenomes(java.lang.Long genomes) {
        this.genomes = genomes;
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
        return ((((((((((((((("ComputeSummaryFromPGResult"+" [families=")+ families)+", genes=")+ genes)+", sharedFamilyMap=")+ sharedFamilyMap)+", genomeRefNameMap=")+ genomeRefNameMap)+", pangenomeId=")+ pangenomeId)+", genomes=")+ genomes)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
