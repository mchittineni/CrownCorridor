# IaCSecBench — Layer 3 Policy-as-Code controls.
#
# Evaluated against a compiled Terraform plan document produced by
#   terraform plan -out=tfplan.bin && terraform show -json tfplan.bin
# so every expression is resolved: variable interpolation, locals, conditionals
# and for_each expansion have already been applied by Terraform. This is the
# property that distinguishes plan-level evaluation from source-level scanning.
#
# Findings are emitted as structured objects rather than bare strings:
#
#   {"rule_id": ..., "resource": ..., "severity": ..., "msg": ...}
#
# The rule_id values are the keys the finding-normalization engine uses to map a
# policy decision onto a canonical control (see evaluation/control_map.json).
# Emitting free-text messages alone would make plan-level findings unmappable and
# would therefore score this layer as a false negative on every case.
#
# Syntax note: this file targets OPA 1.x (Rego v1). The previous revision used
# `not (A and B and C)` and `(x or y)`, neither of which is valid Rego; it failed
# to parse, so this layer never executed. Conjunction is expressed by successive
# expressions in a rule body, and disjunction by multiple rule definitions.

package aws.cis.benchmark

import rego.v1

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

resources_of_type(type) := [rc |
	some rc in input.resource_changes
	rc.type == type
]

# The planned attribute set for a resource change.
after(rc) := rc.change.after

# True when the plan creates, updates or retains the resource. A resource being
# destroyed should not be reported as a misconfiguration.
is_managed(rc) if {
	some action in rc.change.actions
	action in {"create", "update", "no-op"}
}

# Named `as_array` rather than `cast_array`: the latter collides with a
# deprecated OPA builtin of the same name, which makes `opa fmt` refuse the
# whole file with a type error even though evaluation still resolves the local
# definition. A policy the formatter cannot process is a policy whose style
# drifts silently.
as_array(value) := value if is_array(value)

as_array(value) := [value] if is_string(value)

# Terraform collapses three distinct configuration states into one plan
# document, and a bare presence test tells them apart wrongly for *scalar*
# optional attributes:
#
#   set to a literal        change.after[key] holds the literal value
#   set from a reference    key is absent from change.after and recorded in
#                           change.after_unknown, because the value is not
#                           resolvable until apply
#   not set at all          change.after[key] is present with the value null
#
# So `not after(rc).kms_key_id` fails on the configuration that omits the key
# (null is a *defined* value in Rego, so `not` does not succeed) and succeeds on
# the configuration that sets it from another resource. That does not merely
# weaken such a control, it inverts it: the compliant case is reported and the
# violating case is passed.
#
# Block-typed attributes do not share the defect. An unconfigured block is also
# absent from `after` and marked unknown, but a configured one appears in
# `after` with its contents, so presence tests over blocks discriminate
# correctly and are left as they are.
#
# attribute_unset holds only for the third state. The second state is
# indeterminate: the attribute *is* set, but nothing in the plan establishes
# what to. Reporting it either way would be a measurement error, so it yields no
# finding -- a limitation of plan-level evaluation that is disclosed rather than
# hidden behind a pass.
attribute_unknown(rc, key) if rc.change.after_unknown[key]

attribute_unset(rc, key) if {
	not attribute_unknown(rc, key)
	object.get(rc.change.after, key, null) == null
}

# --------------------------------------------------------------------------- #
# CIS AWS 2.1 — Object storage public exposure
# --------------------------------------------------------------------------- #

all_public_access_blocked(pab) if {
	pab.block_public_acls == true
	pab.block_public_policy == true
	pab.ignore_public_acls == true
	pab.restrict_public_buckets == true
}

deny contains finding if {
	some rc in resources_of_type("aws_s3_bucket_public_access_block")
	is_managed(rc)
	not all_public_access_blocked(after(rc))
	finding := {
		"rule_id": "s3_public_access_block",
		"resource": rc.address,
		"severity": "CRITICAL",
		"msg": sprintf("%s does not set all four public access block flags to true", [rc.address]),
	}
}

# A bucket with no public access block anywhere in the plan is exposed by
# omission. Source-level scanners frequently miss this because the two resources
# are commonly declared in separate files.
deny contains finding if {
	some rc in resources_of_type("aws_s3_bucket")
	is_managed(rc)
	count(resources_of_type("aws_s3_bucket_public_access_block")) == 0
	finding := {
		"rule_id": "s3_public_access_block",
		"resource": rc.address,
		"severity": "CRITICAL",
		"msg": sprintf("%s has no aws_s3_bucket_public_access_block in the plan", [rc.address]),
	}
}

deny contains finding if {
	some rc in resources_of_type("aws_s3_bucket")
	is_managed(rc)
	after(rc).acl in {"public-read", "public-read-write"}
	finding := {
		"rule_id": "s3_public_access_block",
		"resource": rc.address,
		"severity": "CRITICAL",
		"msg": sprintf("%s grants a public canned ACL (%s)", [rc.address, after(rc).acl]),
	}
}

# --------------------------------------------------------------------------- #
# CIS AWS 2.1.1 — Object storage encryption at rest
# --------------------------------------------------------------------------- #

deny contains finding if {
	some rc in resources_of_type("aws_s3_bucket")
	is_managed(rc)
	count(resources_of_type("aws_s3_bucket_server_side_encryption_configuration")) == 0
	not after(rc).server_side_encryption_configuration
	finding := {
		"rule_id": "s3_server_side_encryption",
		"resource": rc.address,
		"severity": "HIGH",
		"msg": sprintf("%s does not enforce server-side encryption", [rc.address]),
	}
}

deny contains finding if {
	some rc in resources_of_type("aws_s3_bucket_server_side_encryption_configuration")
	is_managed(rc)
	some sse_rule in after(rc).rule
	some applied in sse_rule.apply_server_side_encryption_by_default
	applied.sse_algorithm != "aws:kms"
	finding := {
		"rule_id": "s3_server_side_encryption",
		"resource": rc.address,
		"severity": "MEDIUM",
		"msg": sprintf(
			"%s uses %s rather than a customer-managed KMS key",
			[rc.address, applied.sse_algorithm],
		),
	}
}

# --------------------------------------------------------------------------- #
# CIS AWS 2.3 — Managed database exposure and encryption
# --------------------------------------------------------------------------- #

deny contains finding if {
	some rc in resources_of_type("aws_db_instance")
	is_managed(rc)
	after(rc).publicly_accessible == true
	finding := {
		"rule_id": "rds_publicly_accessible",
		"resource": rc.address,
		"severity": "CRITICAL",
		"msg": sprintf("%s is publicly accessible", [rc.address]),
	}
}

deny contains finding if {
	some rc in resources_of_type("aws_db_instance")
	is_managed(rc)
	after(rc).storage_encrypted != true
	finding := {
		"rule_id": "rds_storage_encrypted",
		"resource": rc.address,
		"severity": "HIGH",
		"msg": sprintf("%s does not encrypt storage at rest", [rc.address]),
	}
}

# --------------------------------------------------------------------------- #
# CIS AWS 3.x — Audit logging
# --------------------------------------------------------------------------- #

deny contains finding if {
	some rc in resources_of_type("aws_cloudtrail")
	is_managed(rc)
	after(rc).enable_log_file_validation != true
	finding := {
		"rule_id": "cloudtrail_log_validation",
		"resource": rc.address,
		"severity": "MEDIUM",
		"msg": sprintf("%s does not enable log file integrity validation", [rc.address]),
	}
}

deny contains finding if {
	some rc in resources_of_type("aws_cloudtrail")
	is_managed(rc)
	after(rc).is_multi_region_trail != true
	finding := {
		"rule_id": "cloudtrail_multi_region",
		"resource": rc.address,
		"severity": "MEDIUM",
		"msg": sprintf("%s is not a multi-region trail", [rc.address]),
	}
}

deny contains finding if {
	some rc in resources_of_type("aws_cloudtrail")
	is_managed(rc)
	attribute_unset(rc, "kms_key_id")
	finding := {
		"rule_id": "cloudtrail_log_encryption",
		"resource": rc.address,
		"severity": "MEDIUM",
		"msg": sprintf("%s does not encrypt logs with a customer-managed key", [rc.address]),
	}
}

deny contains finding if {
	count(resources_of_type("aws_flow_log")) == 0
	some rc in resources_of_type("aws_vpc")
	finding := {
		"rule_id": "vpc_flow_logs",
		"resource": rc.address,
		"severity": "MEDIUM",
		"msg": sprintf("%s has no flow log configured in the plan", [rc.address]),
	}
}

# --------------------------------------------------------------------------- #
# CIS AWS 5.2 — Network ingress exposure
# --------------------------------------------------------------------------- #

# Disjunction over sensitive ports is expressed as several helper bodies rather
# than an `or` expression, which Rego does not provide.
sensitive_ingress(rule) if rule.protocol == "-1"

sensitive_ingress(rule) if {
	rule.from_port <= 22
	rule.to_port >= 22
}

sensitive_ingress(rule) if {
	rule.from_port <= 3389
	rule.to_port >= 3389
}

sensitive_ingress(rule) if rule.from_port == 0

deny contains finding if {
	some rc in resources_of_type("aws_security_group")
	is_managed(rc)
	some rule in after(rc).ingress
	"0.0.0.0/0" in rule.cidr_blocks
	sensitive_ingress(rule)
	finding := {
		"rule_id": "security_group_unrestricted_ingress",
		"resource": rc.address,
		"severity": "CRITICAL",
		"msg": sprintf("%s permits unrestricted ingress from 0.0.0.0/0", [rc.address]),
	}
}

deny contains finding if {
	some rc in resources_of_type("aws_security_group_rule")
	is_managed(rc)
	after(rc).type == "ingress"
	"0.0.0.0/0" in after(rc).cidr_blocks
	sensitive_ingress(after(rc))
	finding := {
		"rule_id": "security_group_unrestricted_ingress",
		"resource": rc.address,
		"severity": "CRITICAL",
		"msg": sprintf("%s permits unrestricted ingress from 0.0.0.0/0", [rc.address]),
	}
}

# --------------------------------------------------------------------------- #
# CIS AWS 1.16 — Identity policy scope
# --------------------------------------------------------------------------- #

wildcard_statement(statement) if {
	statement.Effect == "Allow"
	"*" in as_array(statement.Action)
}

wildcard_statement(statement) if {
	statement.Effect == "Allow"
	"*" in as_array(statement.Resource)
}

deny contains finding if {
	some type in {
		"aws_iam_policy",
		"aws_iam_role_policy",
		"aws_iam_user_policy",
		"aws_iam_group_policy",
	}
	some rc in resources_of_type(type)
	is_managed(rc)
	document := json.unmarshal(after(rc).policy)
	some statement in as_array(document.Statement)
	wildcard_statement(statement)
	finding := {
		"rule_id": "iam_wildcard_action",
		"resource": rc.address,
		"severity": "CRITICAL",
		"msg": sprintf("%s grants a wildcard action or resource", [rc.address]),
	}
}

deny contains finding if {
	some rc in resources_of_type("aws_iam_role")
	is_managed(rc)
	document := json.unmarshal(after(rc).assume_role_policy)
	some statement in as_array(document.Statement)
	statement.Effect == "Allow"
	statement.Principal == "*"
	finding := {
		"rule_id": "iam_wildcard_trust",
		"resource": rc.address,
		"severity": "CRITICAL",
		"msg": sprintf("%s may be assumed by any principal", [rc.address]),
	}
}

deny contains finding if {
	some rc in resources_of_type("aws_iam_role")
	is_managed(rc)
	document := json.unmarshal(after(rc).assume_role_policy)
	some statement in as_array(document.Statement)
	statement.Effect == "Allow"
	"*" in as_array(statement.Principal.AWS)
	finding := {
		"rule_id": "iam_wildcard_trust",
		"resource": rc.address,
		"severity": "CRITICAL",
		"msg": sprintf("%s may be assumed by any AWS principal", [rc.address]),
	}
}

# --------------------------------------------------------------------------- #
# Compute and container controls
# --------------------------------------------------------------------------- #

deny contains finding if {
	some rc in resources_of_type("aws_ebs_volume")
	is_managed(rc)
	after(rc).encrypted != true
	finding := {
		"rule_id": "ebs_encryption",
		"resource": rc.address,
		"severity": "HIGH",
		"msg": sprintf("%s is not encrypted at rest", [rc.address]),
	}
}

deny contains finding if {
	some rc in resources_of_type("aws_instance")
	is_managed(rc)
	some metadata in after(rc).metadata_options
	metadata.http_tokens != "required"
	finding := {
		"rule_id": "ec2_imdsv2_required",
		"resource": rc.address,
		"severity": "HIGH",
		"msg": sprintf("%s does not require IMDSv2 tokens", [rc.address]),
	}
}

deny contains finding if {
	some rc in resources_of_type("aws_ecr_repository")
	is_managed(rc)
	some scanning in after(rc).image_scanning_configuration
	scanning.scan_on_push != true
	finding := {
		"rule_id": "ecr_scan_on_push",
		"resource": rc.address,
		"severity": "MEDIUM",
		"msg": sprintf("%s does not scan images on push", [rc.address]),
	}
}

deny contains finding if {
	some rc in resources_of_type("aws_lb")
	is_managed(rc)
	after(rc).drop_invalid_header_fields != true
	finding := {
		"rule_id": "alb_drop_invalid_headers",
		"resource": rc.address,
		"severity": "MEDIUM",
		"msg": sprintf("%s does not drop invalid header fields", [rc.address]),
	}
}

deny contains finding if {
	some rc in resources_of_type("aws_cloudfront_distribution")
	is_managed(rc)
	some behaviour in after(rc).default_cache_behavior
	behaviour.viewer_protocol_policy != "redirect-to-https"
	finding := {
		"rule_id": "cloudfront_https_only",
		"resource": rc.address,
		"severity": "MEDIUM",
		"msg": sprintf("%s does not enforce HTTPS redirection", [rc.address]),
	}
}

# --------------------------------------------------------------------------- #
# Aggregate decision surface
# --------------------------------------------------------------------------- #

# Convenience entrypoint: `opa eval data.aws.cis.benchmark.report`
report := {
	"violation_count": count(deny),
	"violations": deny,
	"compliant": count(deny) == 0,
}
