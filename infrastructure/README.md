# 🏗️ Infrastructure Directory — Terraform HCL Infrastructure Declarations

## 📋 Directory Overview

The `infrastructure/` directory contains the declarative HCL2 Infrastructure as Code (IaC) configurations for provisioning the platform's AWS cloud architecture.

---

## 📁 Directory Structure & Key Files

```text
infrastructure/
├── main.tf                # Root Infrastructure Provisioning Declarations
├── variables.tf           # Infrastructure Variables & Constraints
├── outputs.tf             # Provisioned Resource Outputs
├── terraform.tfvars       # Environment Variable Values
└── modules/               # Modular Infrastructure Definitions
    ├── api_gateway/       # AWS API Gateway HTTP/REST Endpoints
    ├── cognito/           # Cognito User Pool & JWT Authorizers
    ├── dynamodb/          # DynamoDB Tables for Property History
    ├── ecs/               # ECS Container Cluster & Task Definitions
    ├── kms/               # KMS Customer Managed Keys (CMK)
    ├── s3/                # Private S3 Storage Buckets & Access Controls
    └── vpc/               # Isolated Virtual Private Cloud & Security Groups
```

---

## ⚙️ Key Security Gates & Policies Evaluated

The infrastructure configurations in this directory serve as the live target evaluated by **IaCSecBench**:
- **Layer 2 Native Testing:** Evaluated via `.tftest.hcl` suites verifying variable constraints and resource tags.
- **Layer 3 Policy-as-Code:** Evaluated by compiling Terraform execution plans (`terraform plan -out=tfplan.binary`) into JSON (`terraform show -json tfplan.binary`) and running Open Policy Agent (OPA) Rego security policies against them.

---

## 🔗 Related Knowledge Base Links
- [[Research/Threat-Model-STRIDE|🛡️ Threat Model & STRIDE Matrix]]
- [[Project-Structure|📐 View Project Architecture]]
