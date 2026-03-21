# HybridQA + Input Serialization Research

**How Input Serialization Shapes Hybrid Table–Text QA** (Targeting EMNLP 2026)

This repository extends the [HybridQA dataset](https://hybridqa.github.io/) with a **serialization pipeline** to study how different input representations of hybrid table-text data affect LLM question answering performance.

> **Original HybridQA Paper**: [Chen et al. (EMNLP 2020)](https://arxiv.org/pdf/2004.07347.pdf)
> **Original Repository**: [wenhuchen/HybridQA](https://github.com/wenhuchen/HybridQA)
> **Original README**: [README_HYBRIDQA.md](README_HYBRIDQA.md)

---

## Research Overview

### Research Questions

1. **RQ1**: How much does the choice of serialization format affect LLM QA accuracy (EM/F1)?
2. **RQ2**: What is the trade-off between token efficiency (information density) and QA performance?
3. **RQ3**: How do format-specific performance gaps differ between table-based and passage-based questions?

### 6 Serialization Formats

| # | Format | Description |
|---|--------|-------------|
| 1 | **Structured JSON** | Preserves original table/passage hierarchy as JSON |
| 2 | **YAML** | Preserves original table/passage hierarchy as YAML |
| 3 | **Markdown table** | Markdown table rendering with passages |
| 4 | **HTML table** | HTML table rendering with passages |
| 5 | **LaTeX table** | LaTeX tabular environment with passages |
| 6 | **CSV** | RFC 4180 CSV with passages appended |

### Experiment Stages

1. **Stage 1**: Baseline — Structured JSON + zero-shot QA
2. **Stage 2**: Format Comparison — All 6 formats
3. **Stage 3**: Perturbation — Row/column reorder, separator swap, distractors
4. **Stage 4**: Cross-model — GPT-4o, Claude Sonnet, Gemini, etc.
5. **Stage 5**: Breakdown Analysis — By answer source, hop count, table size
6. **Stage 6**: Ablation — Component-level contribution analysis

---

## Quick Start

### 1. Setup

```bash
# Clone repository
git clone https://github.com/cast-intotheworld/HybridQA.git
cd HybridQA

# Install WikiTables-WithLinks (required)
git clone https://github.com/wenhuchen/WikiTables-WithLinks

# Install dependencies
cd serialization
pip install -r requirements.txt
```

### 2. Preprocessing

```bash
# Check dependencies
python serialization/scripts/run_preprocess.py --check

# Preprocess dev split
python serialization/scripts/run_preprocess.py --split dev
```

### 3. Serialization

```bash
# Serialize with all formats
python serialization/scripts/run_serialize.py --format all --split dev

# Serialize with a specific format
python serialization/scripts/run_serialize.py --format json --split dev
```

### 4. Evaluation

```bash
# Evaluate predictions
python serialization/scripts/run_evaluate.py predictions.jsonl

# Compare all formats
python serialization/scripts/run_evaluate.py --compare
```

**Detailed usage guide**: [serialization/README.md](serialization/README.md)

---

## Project Structure

```
HybridQA/
├── released_data/           # Original HybridQA data (70K+ QA pairs)
├── WikiTables-WithLinks/    # Table + passage source (clone separately)
├── serialization/           # Serialization pipeline (new)
│   ├── configs/             # YAML configs (paths, formats, models)
│   ├── src/
│   │   ├── data_loader/     # HybridQA + WikiTables data loaders
│   │   ├── serializers/     # 6 serialization format implementations
│   │   ├── evaluation/      # EM/F1, token counting, evidence checking
│   │   ├── perturbation/    # Stage 3 perturbation experiments
│   │   └── inference/       # LLM inference (coming soon)
│   ├── scripts/             # CLI runner scripts
│   ├── tests/               # pytest tests (61 tests, all passing)
│   └── README.md            # Detailed usage guide
├── CLAUDE.md                # Claude Code project documentation
├── .claude/skills/          # Dev workflow skills
├── plan.md                  # Implementation plan
├── README_HYBRIDQA.md       # Original HybridQA README
└── (original HybridQA training code)
```

---

## Development Status

### Completed
- [x] 6 standard serialization formats (JSON, YAML, Markdown, HTML, LaTeX, CSV) with ABC + Registry pattern
- [x] HybridQA + WikiTables data loaders with LRU caching
- [x] EM/F1 evaluation metrics (identical logic to original evaluate_script.py)
- [x] Evidence preservation checker (cross-format validation)
- [x] Token counter (tiktoken-based)
- [x] Perturbation modules (row/col reorder, separator swap, distractors)
- [x] 61 pytest tests (100% passing)
- [x] Claude Code skills (/preprocess, /serialize, /evaluate, /validate, /debug, /test)

### In Progress
- [ ] LLM inference pipeline (inference/)
- [ ] Prompt builder
- [ ] OpenAI / Anthropic API clients
- [ ] Batch inference with rate limiting and checkpointing

---

## Dataset

**HybridQA**: Multi-hop QA over tabular and textual data
- **Questions**: 70,259 (train: 62,682 / dev: 3,466 / test: 4,111)
- **Tables**: 13,000+ unique Wikipedia tables
- **Passages**: Avg 44 linked passages per table
- **Answer Types**: Table cells (56%) + Passages (44%)

**Citation**:
```bibtex
@article{chen2020hybridqa,
  title={HybridQA: A Dataset of Multi-Hop Question Answering over Tabular and Textual Data},
  author={Chen, Wenhu and Zha, Hanwen and Chen, Zhiyu and Xiong, Wenhan and Wang, Hong and Wang, William},
  journal={Findings of EMNLP 2020},
  year={2020}
}
```

---

## Testing

```bash
cd HybridQA
pytest serialization/tests/ -v
```

- `test_loaders.py`: Data loaders (10 tests)
- `test_serializers.py`: 6 formats + evidence preservation
- `test_metrics.py`: EM/F1 metrics (17 tests)
- `test_evidence.py`: Cross-format validation (3 tests)

**Total**: 61 tests passed in 0.07s

---

## Documentation

- **[serialization/README.md](serialization/README.md)**: Detailed setup and usage guide
- **[CLAUDE.md](CLAUDE.md)**: Claude Code project documentation (architecture, coding style, data flow)
- **[README_HYBRIDQA.md](README_HYBRIDQA.md)**: Original HybridQA usage instructions

---

## Acknowledgements

This project builds upon the HybridQA dataset and codebase by Wenhu Chen, Hanwen Zha, Zhiyu Chen, Wenhan Xiong, Hong Wang, and William Wang (UCSB).

---

## License

Follows the original HybridQA license.
