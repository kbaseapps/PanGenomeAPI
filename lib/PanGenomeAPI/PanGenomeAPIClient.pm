package PanGenomeAPI::PanGenomeAPIClient;

use JSON::RPC::Client;
use POSIX;
use strict;
use Data::Dumper;
use URI;
use Bio::KBase::Exceptions;
my $get_time = sub { time, 0 };
eval {
    require Time::HiRes;
    $get_time = sub { Time::HiRes::gettimeofday() };
};

use Bio::KBase::AuthToken;

# Client version should match Impl version
# This is a Semantic Version number,
# http://semver.org
our $VERSION = "0.1.0";

=head1 NAME

PanGenomeAPI::PanGenomeAPIClient

=head1 DESCRIPTION


A KBase module: PanGenomeAPI


=cut

sub new
{
    my($class, $url, @args) = @_;
    

    my $self = {
	client => PanGenomeAPI::PanGenomeAPIClient::RpcClient->new,
	url => $url,
	headers => [],
    };

    chomp($self->{hostname} = `hostname`);
    $self->{hostname} ||= 'unknown-host';

    #
    # Set up for propagating KBRPC_TAG and KBRPC_METADATA environment variables through
    # to invoked services. If these values are not set, we create a new tag
    # and a metadata field with basic information about the invoking script.
    #
    if ($ENV{KBRPC_TAG})
    {
	$self->{kbrpc_tag} = $ENV{KBRPC_TAG};
    }
    else
    {
	my ($t, $us) = &$get_time();
	$us = sprintf("%06d", $us);
	my $ts = strftime("%Y-%m-%dT%H:%M:%S.${us}Z", gmtime $t);
	$self->{kbrpc_tag} = "C:$0:$self->{hostname}:$$:$ts";
    }
    push(@{$self->{headers}}, 'Kbrpc-Tag', $self->{kbrpc_tag});

    if ($ENV{KBRPC_METADATA})
    {
	$self->{kbrpc_metadata} = $ENV{KBRPC_METADATA};
	push(@{$self->{headers}}, 'Kbrpc-Metadata', $self->{kbrpc_metadata});
    }

    if ($ENV{KBRPC_ERROR_DEST})
    {
	$self->{kbrpc_error_dest} = $ENV{KBRPC_ERROR_DEST};
	push(@{$self->{headers}}, 'Kbrpc-Errordest', $self->{kbrpc_error_dest});
    }

    #
    # This module requires authentication.
    #
    # We create an auth token, passing through the arguments that we were (hopefully) given.

    {
	my %arg_hash2 = @args;
	if (exists $arg_hash2{"token"}) {
	    $self->{token} = $arg_hash2{"token"};
	} elsif (exists $arg_hash2{"user_id"}) {
	    my $token = Bio::KBase::AuthToken->new(@args);
	    if (!$token->error_message) {
	        $self->{token} = $token->token;
	    }
	}
	
	if (exists $self->{token})
	{
	    $self->{client}->{token} = $self->{token};
	}
    }

    my $ua = $self->{client}->ua;	 
    my $timeout = $ENV{CDMI_TIMEOUT} || (30 * 60);	 
    $ua->timeout($timeout);
    bless $self, $class;
    #    $self->_validate_version();
    return $self;
}




=head2 search_orthologs_from_pangenome

  $result = $obj->search_orthologs_from_pangenome($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a PanGenomeAPI.SearchOrthologsFromPG
$result is a PanGenomeAPI.SearchOrthologsFromPGResult
SearchOrthologsFromPG is a reference to a hash where the following keys are defined:
	pangenome_ref has a value which is a string
	query has a value which is a string
	sort_by has a value which is a reference to a list where each element is a PanGenomeAPI.column_sorting
	start has a value which is an int
	limit has a value which is an int
	num_found has a value which is an int
column_sorting is a reference to a list containing 2 items:
	0: (column) a string
	1: (ascending) a PanGenomeAPI.boolean
boolean is an int
SearchOrthologsFromPGResult is a reference to a hash where the following keys are defined:
	query has a value which is a string
	start has a value which is an int
	orthologs has a value which is a reference to a list where each element is a PanGenomeAPI.OrthologsData
	num_found has a value which is an int
OrthologsData is a reference to a hash where the following keys are defined:
	id has a value which is a string
	type has a value which is a string
	function has a value which is a string
	md5 has a value which is a string
	protein_translation has a value which is a string
	orthologs has a value which is a reference to a list where each element is a reference to a list containing 3 items:
		0: a string
		1: a float
		2: a string


</pre>

=end html

=begin text

$params is a PanGenomeAPI.SearchOrthologsFromPG
$result is a PanGenomeAPI.SearchOrthologsFromPGResult
SearchOrthologsFromPG is a reference to a hash where the following keys are defined:
	pangenome_ref has a value which is a string
	query has a value which is a string
	sort_by has a value which is a reference to a list where each element is a PanGenomeAPI.column_sorting
	start has a value which is an int
	limit has a value which is an int
	num_found has a value which is an int
column_sorting is a reference to a list containing 2 items:
	0: (column) a string
	1: (ascending) a PanGenomeAPI.boolean
boolean is an int
SearchOrthologsFromPGResult is a reference to a hash where the following keys are defined:
	query has a value which is a string
	start has a value which is an int
	orthologs has a value which is a reference to a list where each element is a PanGenomeAPI.OrthologsData
	num_found has a value which is an int
OrthologsData is a reference to a hash where the following keys are defined:
	id has a value which is a string
	type has a value which is a string
	function has a value which is a string
	md5 has a value which is a string
	protein_translation has a value which is a string
	orthologs has a value which is a reference to a list where each element is a reference to a list containing 3 items:
		0: a string
		1: a float
		2: a string



=end text

=item Description



=back

=cut

 sub search_orthologs_from_pangenome
{
    my($self, @args) = @_;

# Authentication: optional

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function search_orthologs_from_pangenome (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to search_orthologs_from_pangenome:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'search_orthologs_from_pangenome');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "PanGenomeAPI.search_orthologs_from_pangenome",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'search_orthologs_from_pangenome',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method search_orthologs_from_pangenome",
					    status_line => $self->{client}->status_line,
					    method_name => 'search_orthologs_from_pangenome',
				       );
    }
}
 


=head2 search_genomes_from_pangenome

  $result = $obj->search_genomes_from_pangenome($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a PanGenomeAPI.SearchGenomesFromPG
$result is a PanGenomeAPI.SearchGenomesFromPGResult
SearchGenomesFromPG is a reference to a hash where the following keys are defined:
	pangenome_ref has a value which is a string
	genome_ref has a value which is a string
	query has a value which is a string
	sort_by has a value which is a reference to a list where each element is a PanGenomeAPI.column_sorting
	start has a value which is an int
	limit has a value which is an int
	num_found has a value which is an int
column_sorting is a reference to a list containing 2 items:
	0: (column) a string
	1: (ascending) a PanGenomeAPI.boolean
boolean is an int
SearchGenomesFromPGResult is a reference to a hash where the following keys are defined:
	query has a value which is a string
	start has a value which is an int
	features has a value which is a reference to a list where each element is a PanGenomeAPI.FeatureData
	num_found has a value which is an int
FeatureData is a reference to a hash where the following keys are defined:
	feature_id has a value which is a string
	aliases has a value which is a reference to a hash where the key is a string and the value is a reference to a list where each element is a string
	function has a value which is a string
	location has a value which is a reference to a list where each element is a PanGenomeAPI.Location
	feature_type has a value which is a string
	global_location has a value which is a PanGenomeAPI.Location
	feature_idx has a value which is an int
	ontology_terms has a value which is a reference to a hash where the key is a string and the value is a string
Location is a reference to a hash where the following keys are defined:
	contig_id has a value which is a string
	start has a value which is an int
	strand has a value which is a string
	length has a value which is an int

</pre>

=end html

=begin text

$params is a PanGenomeAPI.SearchGenomesFromPG
$result is a PanGenomeAPI.SearchGenomesFromPGResult
SearchGenomesFromPG is a reference to a hash where the following keys are defined:
	pangenome_ref has a value which is a string
	genome_ref has a value which is a string
	query has a value which is a string
	sort_by has a value which is a reference to a list where each element is a PanGenomeAPI.column_sorting
	start has a value which is an int
	limit has a value which is an int
	num_found has a value which is an int
column_sorting is a reference to a list containing 2 items:
	0: (column) a string
	1: (ascending) a PanGenomeAPI.boolean
boolean is an int
SearchGenomesFromPGResult is a reference to a hash where the following keys are defined:
	query has a value which is a string
	start has a value which is an int
	features has a value which is a reference to a list where each element is a PanGenomeAPI.FeatureData
	num_found has a value which is an int
FeatureData is a reference to a hash where the following keys are defined:
	feature_id has a value which is a string
	aliases has a value which is a reference to a hash where the key is a string and the value is a reference to a list where each element is a string
	function has a value which is a string
	location has a value which is a reference to a list where each element is a PanGenomeAPI.Location
	feature_type has a value which is a string
	global_location has a value which is a PanGenomeAPI.Location
	feature_idx has a value which is an int
	ontology_terms has a value which is a reference to a hash where the key is a string and the value is a string
Location is a reference to a hash where the following keys are defined:
	contig_id has a value which is a string
	start has a value which is an int
	strand has a value which is a string
	length has a value which is an int


=end text

=item Description



=back

=cut

 sub search_genomes_from_pangenome
{
    my($self, @args) = @_;

# Authentication: optional

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function search_genomes_from_pangenome (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to search_genomes_from_pangenome:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'search_genomes_from_pangenome');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "PanGenomeAPI.search_genomes_from_pangenome",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'search_genomes_from_pangenome',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method search_genomes_from_pangenome",
					    status_line => $self->{client}->status_line,
					    method_name => 'search_genomes_from_pangenome',
				       );
    }
}
 


=head2 search_families_from_comparison_genome

  $result = $obj->search_families_from_comparison_genome($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a PanGenomeAPI.SearchFamiliesFromCG
$result is a PanGenomeAPI.SearchFamiliesFromCGResult
SearchFamiliesFromCG is a reference to a hash where the following keys are defined:
	comparison_genome_ref has a value which is a string
	query has a value which is a string
	sort_by has a value which is a reference to a list where each element is a PanGenomeAPI.column_sorting
	start has a value which is an int
	limit has a value which is an int
	num_found has a value which is an int
column_sorting is a reference to a list containing 2 items:
	0: (column) a string
	1: (ascending) a PanGenomeAPI.boolean
boolean is an int
SearchFamiliesFromCGResult is a reference to a hash where the following keys are defined:
	query has a value which is a string
	start has a value which is an int
	families has a value which is a reference to a list where each element is a PanGenomeAPI.GenomeComparisonFamily
	num_found has a value which is an int
GenomeComparisonFamily is a reference to a hash where the following keys are defined:
	core has a value which is an int
	genome_features has a value which is a reference to a hash where the key is a string and the value is a reference to a list where each element is a reference to a list containing 3 items:
		0: a PanGenomeAPI.Feature_id
		1: a reference to a list where each element is an int
		2: a float

	id has a value which is a string
	type has a value which is a string
	protein_translation has a value which is a string
	number_genomes has a value which is an int
	fraction_genomes has a value which is a float
	fraction_consistent_annotations has a value which is a float
	most_consistent_role has a value which is a string
Feature_id is a string

</pre>

=end html

=begin text

$params is a PanGenomeAPI.SearchFamiliesFromCG
$result is a PanGenomeAPI.SearchFamiliesFromCGResult
SearchFamiliesFromCG is a reference to a hash where the following keys are defined:
	comparison_genome_ref has a value which is a string
	query has a value which is a string
	sort_by has a value which is a reference to a list where each element is a PanGenomeAPI.column_sorting
	start has a value which is an int
	limit has a value which is an int
	num_found has a value which is an int
column_sorting is a reference to a list containing 2 items:
	0: (column) a string
	1: (ascending) a PanGenomeAPI.boolean
boolean is an int
SearchFamiliesFromCGResult is a reference to a hash where the following keys are defined:
	query has a value which is a string
	start has a value which is an int
	families has a value which is a reference to a list where each element is a PanGenomeAPI.GenomeComparisonFamily
	num_found has a value which is an int
GenomeComparisonFamily is a reference to a hash where the following keys are defined:
	core has a value which is an int
	genome_features has a value which is a reference to a hash where the key is a string and the value is a reference to a list where each element is a reference to a list containing 3 items:
		0: a PanGenomeAPI.Feature_id
		1: a reference to a list where each element is an int
		2: a float

	id has a value which is a string
	type has a value which is a string
	protein_translation has a value which is a string
	number_genomes has a value which is an int
	fraction_genomes has a value which is a float
	fraction_consistent_annotations has a value which is a float
	most_consistent_role has a value which is a string
Feature_id is a string


=end text

=item Description



=back

=cut

 sub search_families_from_comparison_genome
{
    my($self, @args) = @_;

# Authentication: optional

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function search_families_from_comparison_genome (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to search_families_from_comparison_genome:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'search_families_from_comparison_genome');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "PanGenomeAPI.search_families_from_comparison_genome",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'search_families_from_comparison_genome',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method search_families_from_comparison_genome",
					    status_line => $self->{client}->status_line,
					    method_name => 'search_families_from_comparison_genome',
				       );
    }
}
 


=head2 search_functions_from_comparison_genome

  $result = $obj->search_functions_from_comparison_genome($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a PanGenomeAPI.SearchFunctionsFromCG
$result is a PanGenomeAPI.SearchFunctionsFromCGResult
SearchFunctionsFromCG is a reference to a hash where the following keys are defined:
	comparison_genome_ref has a value which is a string
	query has a value which is a string
	sort_by has a value which is a reference to a list where each element is a PanGenomeAPI.column_sorting
	start has a value which is an int
	limit has a value which is an int
	num_found has a value which is an int
column_sorting is a reference to a list containing 2 items:
	0: (column) a string
	1: (ascending) a PanGenomeAPI.boolean
boolean is an int
SearchFunctionsFromCGResult is a reference to a hash where the following keys are defined:
	query has a value which is a string
	start has a value which is an int
	functions has a value which is a reference to a list where each element is a PanGenomeAPI.GenomeComparisonFunction
	num_found has a value which is an int
GenomeComparisonFunction is a reference to a hash where the following keys are defined:
	core has a value which is an int
	genome_features has a value which is a reference to a hash where the key is a string and the value is a reference to a list where each element is a reference to a list containing 3 items:
		0: a PanGenomeAPI.Feature_id
		1: an int
		2: a float

	id has a value which is a string
	reactions has a value which is a reference to a list where each element is a reference to a list containing 2 items:
		0: a PanGenomeAPI.Reaction_id
		1: a string

	subsystem has a value which is a string
	primclass has a value which is a string
	subclass has a value which is a string
	number_genomes has a value which is an int
	fraction_genomes has a value which is a float
	fraction_consistent_families has a value which is a float
	most_consistent_family has a value which is a string
Feature_id is a string
Reaction_id is a string

</pre>

=end html

=begin text

$params is a PanGenomeAPI.SearchFunctionsFromCG
$result is a PanGenomeAPI.SearchFunctionsFromCGResult
SearchFunctionsFromCG is a reference to a hash where the following keys are defined:
	comparison_genome_ref has a value which is a string
	query has a value which is a string
	sort_by has a value which is a reference to a list where each element is a PanGenomeAPI.column_sorting
	start has a value which is an int
	limit has a value which is an int
	num_found has a value which is an int
column_sorting is a reference to a list containing 2 items:
	0: (column) a string
	1: (ascending) a PanGenomeAPI.boolean
boolean is an int
SearchFunctionsFromCGResult is a reference to a hash where the following keys are defined:
	query has a value which is a string
	start has a value which is an int
	functions has a value which is a reference to a list where each element is a PanGenomeAPI.GenomeComparisonFunction
	num_found has a value which is an int
GenomeComparisonFunction is a reference to a hash where the following keys are defined:
	core has a value which is an int
	genome_features has a value which is a reference to a hash where the key is a string and the value is a reference to a list where each element is a reference to a list containing 3 items:
		0: a PanGenomeAPI.Feature_id
		1: an int
		2: a float

	id has a value which is a string
	reactions has a value which is a reference to a list where each element is a reference to a list containing 2 items:
		0: a PanGenomeAPI.Reaction_id
		1: a string

	subsystem has a value which is a string
	primclass has a value which is a string
	subclass has a value which is a string
	number_genomes has a value which is an int
	fraction_genomes has a value which is a float
	fraction_consistent_families has a value which is a float
	most_consistent_family has a value which is a string
Feature_id is a string
Reaction_id is a string


=end text

=item Description



=back

=cut

 sub search_functions_from_comparison_genome
{
    my($self, @args) = @_;

# Authentication: optional

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function search_functions_from_comparison_genome (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to search_functions_from_comparison_genome:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'search_functions_from_comparison_genome');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "PanGenomeAPI.search_functions_from_comparison_genome",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'search_functions_from_comparison_genome',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method search_functions_from_comparison_genome",
					    status_line => $self->{client}->status_line,
					    method_name => 'search_functions_from_comparison_genome',
				       );
    }
}
 


=head2 search_comparison_genome_from_comparison_genome

  $result = $obj->search_comparison_genome_from_comparison_genome($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a PanGenomeAPI.SearchComparisonGenomesFromCG
$result is a PanGenomeAPI.SearchComparisonGenomesFromCGResult
SearchComparisonGenomesFromCG is a reference to a hash where the following keys are defined:
	comparison_genome_ref has a value which is a string
	query has a value which is a string
	sort_by has a value which is a reference to a list where each element is a PanGenomeAPI.column_sorting
	start has a value which is an int
	limit has a value which is an int
	num_found has a value which is an int
column_sorting is a reference to a list containing 2 items:
	0: (column) a string
	1: (ascending) a PanGenomeAPI.boolean
boolean is an int
SearchComparisonGenomesFromCGResult is a reference to a hash where the following keys are defined:
	query has a value which is a string
	start has a value which is an int
	comparison_genomes has a value which is a reference to a list where each element is a PanGenomeAPI.GenomeComparisonGenome
	num_found has a value which is an int
GenomeComparisonGenome is a reference to a hash where the following keys are defined:
	id has a value which is a string
	genome_ref has a value which is a PanGenomeAPI.Genome_ref
	genome_similarity has a value which is a reference to a hash where the key is a string and the value is a reference to a list containing 2 items:
		0: an int
		1: an int

	name has a value which is a string
	taxonomy has a value which is a string
	features has a value which is an int
	families has a value which is an int
	functions has a value which is an int
Genome_ref is a string

</pre>

=end html

=begin text

$params is a PanGenomeAPI.SearchComparisonGenomesFromCG
$result is a PanGenomeAPI.SearchComparisonGenomesFromCGResult
SearchComparisonGenomesFromCG is a reference to a hash where the following keys are defined:
	comparison_genome_ref has a value which is a string
	query has a value which is a string
	sort_by has a value which is a reference to a list where each element is a PanGenomeAPI.column_sorting
	start has a value which is an int
	limit has a value which is an int
	num_found has a value which is an int
column_sorting is a reference to a list containing 2 items:
	0: (column) a string
	1: (ascending) a PanGenomeAPI.boolean
boolean is an int
SearchComparisonGenomesFromCGResult is a reference to a hash where the following keys are defined:
	query has a value which is a string
	start has a value which is an int
	comparison_genomes has a value which is a reference to a list where each element is a PanGenomeAPI.GenomeComparisonGenome
	num_found has a value which is an int
GenomeComparisonGenome is a reference to a hash where the following keys are defined:
	id has a value which is a string
	genome_ref has a value which is a PanGenomeAPI.Genome_ref
	genome_similarity has a value which is a reference to a hash where the key is a string and the value is a reference to a list containing 2 items:
		0: an int
		1: an int

	name has a value which is a string
	taxonomy has a value which is a string
	features has a value which is an int
	families has a value which is an int
	functions has a value which is an int
Genome_ref is a string


=end text

=item Description



=back

=cut

 sub search_comparison_genome_from_comparison_genome
{
    my($self, @args) = @_;

# Authentication: optional

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function search_comparison_genome_from_comparison_genome (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to search_comparison_genome_from_comparison_genome:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'search_comparison_genome_from_comparison_genome');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "PanGenomeAPI.search_comparison_genome_from_comparison_genome",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'search_comparison_genome_from_comparison_genome',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method search_comparison_genome_from_comparison_genome",
					    status_line => $self->{client}->status_line,
					    method_name => 'search_comparison_genome_from_comparison_genome',
				       );
    }
}
 
  
sub status
{
    my($self, @args) = @_;
    if ((my $n = @args) != 0) {
        Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
                                   "Invalid argument count for function status (received $n, expecting 0)");
    }
    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
        method => "PanGenomeAPI.status",
        params => \@args,
    });
    if ($result) {
        if ($result->is_error) {
            Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
                           code => $result->content->{error}->{code},
                           method_name => 'status',
                           data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
                          );
        } else {
            return wantarray ? @{$result->result} : $result->result->[0];
        }
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method status",
                        status_line => $self->{client}->status_line,
                        method_name => 'status',
                       );
    }
}
   

sub version {
    my ($self) = @_;
    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
        method => "PanGenomeAPI.version",
        params => [],
    });
    if ($result) {
        if ($result->is_error) {
            Bio::KBase::Exceptions::JSONRPC->throw(
                error => $result->error_message,
                code => $result->content->{code},
                method_name => 'search_comparison_genome_from_comparison_genome',
            );
        } else {
            return wantarray ? @{$result->result} : $result->result->[0];
        }
    } else {
        Bio::KBase::Exceptions::HTTP->throw(
            error => "Error invoking method search_comparison_genome_from_comparison_genome",
            status_line => $self->{client}->status_line,
            method_name => 'search_comparison_genome_from_comparison_genome',
        );
    }
}

sub _validate_version {
    my ($self) = @_;
    my $svr_version = $self->version();
    my $client_version = $VERSION;
    my ($cMajor, $cMinor) = split(/\./, $client_version);
    my ($sMajor, $sMinor) = split(/\./, $svr_version);
    if ($sMajor != $cMajor) {
        Bio::KBase::Exceptions::ClientServerIncompatible->throw(
            error => "Major version numbers differ.",
            server_version => $svr_version,
            client_version => $client_version
        );
    }
    if ($sMinor < $cMinor) {
        Bio::KBase::Exceptions::ClientServerIncompatible->throw(
            error => "Client minor version greater than Server minor version.",
            server_version => $svr_version,
            client_version => $client_version
        );
    }
    if ($sMinor > $cMinor) {
        warn "New client version available for PanGenomeAPI::PanGenomeAPIClient\n";
    }
    if ($sMajor == 0) {
        warn "PanGenomeAPI::PanGenomeAPIClient version is $svr_version. API subject to change.\n";
    }
}

=head1 TYPES



=head2 boolean

=over 4



=item Description

Indicates true or false values, false = 0, true = 1
@range [0,1]


=item Definition

=begin html

<pre>
an int
</pre>

=end html

=begin text

an int

=end text

=back



=head2 column_sorting

=over 4



=item Definition

=begin html

<pre>
a reference to a list containing 2 items:
0: (column) a string
1: (ascending) a PanGenomeAPI.boolean

</pre>

=end html

=begin text

a reference to a list containing 2 items:
0: (column) a string
1: (ascending) a PanGenomeAPI.boolean


=end text

=back



=head2 SearchOrthologsFromPG

=over 4



=item Description

num_found - optional field which when set informs that there
    is no need to perform full scan in order to count this
    value because it was already done before; please don't
    set this value with 0 or any guessed number if you didn't 
    get right value previously.


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
pangenome_ref has a value which is a string
query has a value which is a string
sort_by has a value which is a reference to a list where each element is a PanGenomeAPI.column_sorting
start has a value which is an int
limit has a value which is an int
num_found has a value which is an int

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
pangenome_ref has a value which is a string
query has a value which is a string
sort_by has a value which is a reference to a list where each element is a PanGenomeAPI.column_sorting
start has a value which is an int
limit has a value which is an int
num_found has a value which is an int


=end text

=back



=head2 OrthologsData

=over 4



=item Description

OrthologFamily object: this object holds all data for a single ortholog family in a metagenome

@optional type function md5 protein_translation


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
id has a value which is a string
type has a value which is a string
function has a value which is a string
md5 has a value which is a string
protein_translation has a value which is a string
orthologs has a value which is a reference to a list where each element is a reference to a list containing 3 items:
	0: a string
	1: a float
	2: a string


</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
id has a value which is a string
type has a value which is a string
function has a value which is a string
md5 has a value which is a string
protein_translation has a value which is a string
orthologs has a value which is a reference to a list where each element is a reference to a list containing 3 items:
	0: a string
	1: a float
	2: a string



=end text

=back



=head2 SearchOrthologsFromPGResult

=over 4



=item Description

num_found - number of all items found in query search (with 
    only part of it returned in "orthologs" list).


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
query has a value which is a string
start has a value which is an int
orthologs has a value which is a reference to a list where each element is a PanGenomeAPI.OrthologsData
num_found has a value which is an int

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
query has a value which is a string
start has a value which is an int
orthologs has a value which is a reference to a list where each element is a PanGenomeAPI.OrthologsData
num_found has a value which is an int


=end text

=back



=head2 SearchGenomesFromPG

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
pangenome_ref has a value which is a string
genome_ref has a value which is a string
query has a value which is a string
sort_by has a value which is a reference to a list where each element is a PanGenomeAPI.column_sorting
start has a value which is an int
limit has a value which is an int
num_found has a value which is an int

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
pangenome_ref has a value which is a string
genome_ref has a value which is a string
query has a value which is a string
sort_by has a value which is a reference to a list where each element is a PanGenomeAPI.column_sorting
start has a value which is an int
limit has a value which is an int
num_found has a value which is an int


=end text

=back



=head2 Location

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
contig_id has a value which is a string
start has a value which is an int
strand has a value which is a string
length has a value which is an int

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
contig_id has a value which is a string
start has a value which is an int
strand has a value which is a string
length has a value which is an int


=end text

=back



=head2 FeatureData

=over 4



=item Description

aliases - mapping from alias name (key) to set of alias sources 
    (value),
global_location - this is location-related properties that are
    under sorting whereas items in "location" array are not,
feature_idx - legacy field keeping the position of feature in
    feature array in legacy Genome object,
ontology_terms - mapping from term ID (key) to term name (value).


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
feature_id has a value which is a string
aliases has a value which is a reference to a hash where the key is a string and the value is a reference to a list where each element is a string
function has a value which is a string
location has a value which is a reference to a list where each element is a PanGenomeAPI.Location
feature_type has a value which is a string
global_location has a value which is a PanGenomeAPI.Location
feature_idx has a value which is an int
ontology_terms has a value which is a reference to a hash where the key is a string and the value is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
feature_id has a value which is a string
aliases has a value which is a reference to a hash where the key is a string and the value is a reference to a list where each element is a string
function has a value which is a string
location has a value which is a reference to a list where each element is a PanGenomeAPI.Location
feature_type has a value which is a string
global_location has a value which is a PanGenomeAPI.Location
feature_idx has a value which is an int
ontology_terms has a value which is a reference to a hash where the key is a string and the value is a string


=end text

=back



=head2 SearchGenomesFromPGResult

=over 4



=item Description

num_found - number of all items found in query search (with 
    only part of it returned in "features" list).


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
query has a value which is a string
start has a value which is an int
features has a value which is a reference to a list where each element is a PanGenomeAPI.FeatureData
num_found has a value which is an int

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
query has a value which is a string
start has a value which is an int
features has a value which is a reference to a list where each element is a PanGenomeAPI.FeatureData
num_found has a value which is an int


=end text

=back



=head2 SearchFamiliesFromCG

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
comparison_genome_ref has a value which is a string
query has a value which is a string
sort_by has a value which is a reference to a list where each element is a PanGenomeAPI.column_sorting
start has a value which is an int
limit has a value which is an int
num_found has a value which is an int

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
comparison_genome_ref has a value which is a string
query has a value which is a string
sort_by has a value which is a reference to a list where each element is a PanGenomeAPI.column_sorting
start has a value which is an int
limit has a value which is an int
num_found has a value which is an int


=end text

=back



=head2 Feature_id

=over 4



=item Definition

=begin html

<pre>
a string
</pre>

=end html

=begin text

a string

=end text

=back



=head2 GenomeComparisonFamily

=over 4



=item Description

GenomeComparisonFamily object: this object holds information about a protein family across a set of genomes


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
core has a value which is an int
genome_features has a value which is a reference to a hash where the key is a string and the value is a reference to a list where each element is a reference to a list containing 3 items:
	0: a PanGenomeAPI.Feature_id
	1: a reference to a list where each element is an int
	2: a float

id has a value which is a string
type has a value which is a string
protein_translation has a value which is a string
number_genomes has a value which is an int
fraction_genomes has a value which is a float
fraction_consistent_annotations has a value which is a float
most_consistent_role has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
core has a value which is an int
genome_features has a value which is a reference to a hash where the key is a string and the value is a reference to a list where each element is a reference to a list containing 3 items:
	0: a PanGenomeAPI.Feature_id
	1: a reference to a list where each element is an int
	2: a float

id has a value which is a string
type has a value which is a string
protein_translation has a value which is a string
number_genomes has a value which is an int
fraction_genomes has a value which is a float
fraction_consistent_annotations has a value which is a float
most_consistent_role has a value which is a string


=end text

=back



=head2 SearchFamiliesFromCGResult

=over 4



=item Description

num_found - number of all items found in query search (with 
    only part of it returned in "families" list).


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
query has a value which is a string
start has a value which is an int
families has a value which is a reference to a list where each element is a PanGenomeAPI.GenomeComparisonFamily
num_found has a value which is an int

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
query has a value which is a string
start has a value which is an int
families has a value which is a reference to a list where each element is a PanGenomeAPI.GenomeComparisonFamily
num_found has a value which is an int


=end text

=back



=head2 SearchFunctionsFromCG

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
comparison_genome_ref has a value which is a string
query has a value which is a string
sort_by has a value which is a reference to a list where each element is a PanGenomeAPI.column_sorting
start has a value which is an int
limit has a value which is an int
num_found has a value which is an int

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
comparison_genome_ref has a value which is a string
query has a value which is a string
sort_by has a value which is a reference to a list where each element is a PanGenomeAPI.column_sorting
start has a value which is an int
limit has a value which is an int
num_found has a value which is an int


=end text

=back



=head2 Reaction_id

=over 4



=item Definition

=begin html

<pre>
a string
</pre>

=end html

=begin text

a string

=end text

=back



=head2 GenomeComparisonFunction

=over 4



=item Description

GenomeComparisonFunction object: this object holds information about a genome in a function across all genomes


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
core has a value which is an int
genome_features has a value which is a reference to a hash where the key is a string and the value is a reference to a list where each element is a reference to a list containing 3 items:
	0: a PanGenomeAPI.Feature_id
	1: an int
	2: a float

id has a value which is a string
reactions has a value which is a reference to a list where each element is a reference to a list containing 2 items:
	0: a PanGenomeAPI.Reaction_id
	1: a string

subsystem has a value which is a string
primclass has a value which is a string
subclass has a value which is a string
number_genomes has a value which is an int
fraction_genomes has a value which is a float
fraction_consistent_families has a value which is a float
most_consistent_family has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
core has a value which is an int
genome_features has a value which is a reference to a hash where the key is a string and the value is a reference to a list where each element is a reference to a list containing 3 items:
	0: a PanGenomeAPI.Feature_id
	1: an int
	2: a float

id has a value which is a string
reactions has a value which is a reference to a list where each element is a reference to a list containing 2 items:
	0: a PanGenomeAPI.Reaction_id
	1: a string

subsystem has a value which is a string
primclass has a value which is a string
subclass has a value which is a string
number_genomes has a value which is an int
fraction_genomes has a value which is a float
fraction_consistent_families has a value which is a float
most_consistent_family has a value which is a string


=end text

=back



=head2 SearchFunctionsFromCGResult

=over 4



=item Description

num_found - number of all items found in query search (with 
    only part of it returned in "functions" list).


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
query has a value which is a string
start has a value which is an int
functions has a value which is a reference to a list where each element is a PanGenomeAPI.GenomeComparisonFunction
num_found has a value which is an int

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
query has a value which is a string
start has a value which is an int
functions has a value which is a reference to a list where each element is a PanGenomeAPI.GenomeComparisonFunction
num_found has a value which is an int


=end text

=back



=head2 SearchComparisonGenomesFromCG

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
comparison_genome_ref has a value which is a string
query has a value which is a string
sort_by has a value which is a reference to a list where each element is a PanGenomeAPI.column_sorting
start has a value which is an int
limit has a value which is an int
num_found has a value which is an int

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
comparison_genome_ref has a value which is a string
query has a value which is a string
sort_by has a value which is a reference to a list where each element is a PanGenomeAPI.column_sorting
start has a value which is an int
limit has a value which is an int
num_found has a value which is an int


=end text

=back



=head2 Genome_ref

=over 4



=item Definition

=begin html

<pre>
a string
</pre>

=end html

=begin text

a string

=end text

=back



=head2 GenomeComparisonGenome

=over 4



=item Description

GenomeComparisonGenome object: this object holds information about a genome in a genome comparison


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
id has a value which is a string
genome_ref has a value which is a PanGenomeAPI.Genome_ref
genome_similarity has a value which is a reference to a hash where the key is a string and the value is a reference to a list containing 2 items:
	0: an int
	1: an int

name has a value which is a string
taxonomy has a value which is a string
features has a value which is an int
families has a value which is an int
functions has a value which is an int

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
id has a value which is a string
genome_ref has a value which is a PanGenomeAPI.Genome_ref
genome_similarity has a value which is a reference to a hash where the key is a string and the value is a reference to a list containing 2 items:
	0: an int
	1: an int

name has a value which is a string
taxonomy has a value which is a string
features has a value which is an int
families has a value which is an int
functions has a value which is an int


=end text

=back



=head2 SearchComparisonGenomesFromCGResult

=over 4



=item Description

num_found - number of all items found in query search (with 
    only part of it returned in "comparison genomes" list).


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
query has a value which is a string
start has a value which is an int
comparison_genomes has a value which is a reference to a list where each element is a PanGenomeAPI.GenomeComparisonGenome
num_found has a value which is an int

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
query has a value which is a string
start has a value which is an int
comparison_genomes has a value which is a reference to a list where each element is a PanGenomeAPI.GenomeComparisonGenome
num_found has a value which is an int


=end text

=back



=cut

package PanGenomeAPI::PanGenomeAPIClient::RpcClient;
use base 'JSON::RPC::Client';
use POSIX;
use strict;

#
# Override JSON::RPC::Client::call because it doesn't handle error returns properly.
#

sub call {
    my ($self, $uri, $headers, $obj) = @_;
    my $result;


    {
	if ($uri =~ /\?/) {
	    $result = $self->_get($uri);
	}
	else {
	    Carp::croak "not hashref." unless (ref $obj eq 'HASH');
	    $result = $self->_post($uri, $headers, $obj);
	}

    }

    my $service = $obj->{method} =~ /^system\./ if ( $obj );

    $self->status_line($result->status_line);

    if ($result->is_success) {

        return unless($result->content); # notification?

        if ($service) {
            return JSON::RPC::ServiceObject->new($result, $self->json);
        }

        return JSON::RPC::ReturnObject->new($result, $self->json);
    }
    elsif ($result->content_type eq 'application/json')
    {
        return JSON::RPC::ReturnObject->new($result, $self->json);
    }
    else {
        return;
    }
}


sub _post {
    my ($self, $uri, $headers, $obj) = @_;
    my $json = $self->json;

    $obj->{version} ||= $self->{version} || '1.1';

    if ($obj->{version} eq '1.0') {
        delete $obj->{version};
        if (exists $obj->{id}) {
            $self->id($obj->{id}) if ($obj->{id}); # if undef, it is notification.
        }
        else {
            $obj->{id} = $self->id || ($self->id('JSON::RPC::Client'));
        }
    }
    else {
        # $obj->{id} = $self->id if (defined $self->id);
	# Assign a random number to the id if one hasn't been set
	$obj->{id} = (defined $self->id) ? $self->id : substr(rand(),2);
    }

    my $content = $json->encode($obj);

    $self->ua->post(
        $uri,
        Content_Type   => $self->{content_type},
        Content        => $content,
        Accept         => 'application/json',
	@$headers,
	($self->{token} ? (Authorization => $self->{token}) : ()),
    );
}



1;
