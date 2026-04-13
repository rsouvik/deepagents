---
name: data-ingestion-node
description: Validates and profiles bioinformatics input files (.fastq, .bam, .vcf) before downstream analysis. Use when a user asks to ingest sequencing/variant files, check file integrity, inspect metadata, or reject malformed inputs before running tools.
---

# Data Ingestion Node Skill

## Workflow

1. Identify file type from extension and quick header sniff (`.fastq`, `.fastq.gz`, `.bam`, `.vcf`, `.vcf.gz`).
2. Run a lightweight integrity check:
    - FASTQ: verify 4-line record structure for sampled records.
    - BAM: confirm BAM magic bytes.
    - VCF: confirm VCF header contains `##fileformat=VCF`.
3. Extract metadata:
    - file path, size, type, compression, record/header hints
4. Return structured output with:
    - `status` (`ok` / `warning` / `error`)
    - `issues` list
    - `metadata` object
5. Stop and report if integrity fails. Do not continue to downstream nodes.

## Safety Rails

- Never run alignment/calling tools from this node.
- Never modify input files.
- Fail fast on unknown extensions or unreadable files.
- Sample only small portions of large files for validation.

## Output Contract

Return JSON-compatible data:

```json
{
  "status": "ok",
  "file_type": "fastq",
  "issues": [],
  "metadata": {
    "path": "sample.fastq.gz",
    "size_bytes": 12345,
    "compressed": true,
    "records_sampled": 100
  }
}
