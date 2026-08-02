# Terraform Environment & Lockfiles (`terraform/`)

This directory contains shared Terraform provider lockfiles (`.terraform.lock.hcl`) and workspace variables used during local validation and policy evaluation.

## 📌 Usage

- **Provider Constraints**: Standardizes provider versions across HashiCorp AWS provider (`~> 6.56.0`) and Terraform CLI (`>= 1.15.0`).
- **Validation**: Module configurations are defined under `infrastructure/` and tested via `.tftest.hcl` files.
