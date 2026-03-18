# HybridQA + Input Serialization Research

**How Input Serialization Shapes Hybrid Table–Text QA** (EMNLP 2026 목표)

이 저장소는 [HybridQA 데이터셋](https://hybridqa.github.io/)을 기반으로 **테이블+텍스트 하이브리드 데이터의 직렬화 포맷**이 LLM의 QA 성능에 미치는 영향을 연구하는 프로젝트입니다.

> **Original HybridQA Paper**: [Chen et al. (EMNLP 2020)](https://arxiv.org/pdf/2004.07347.pdf)
> **Original Repository**: [wenhuchen/HybridQA](https://github.com/wenhuchen/HybridQA)
> **Original README**: [README_HYBRIDQA.md](README_HYBRIDQA.md) ← 원본 HybridQA 사용법

---

## 🔬 Research Overview

### Research Questions

1. **RQ1**: 직렬화 포맷에 따라 LLM의 QA 정확도(EM/F1)가 얼마나 달라지는가?
2. **RQ2**: 토큰 효율성(정보 밀도)과 QA 성능 사이의 트레이드오프는?
3. **RQ3**: 테이블 기반 vs 패시지 기반 질문에서 포맷별 성능 차이는?

### 7 Serialization Formats

| # | Format | Description |
|---|--------|-------------|
| 1 | **Structured JSON** | 원본 구조를 JSON으로 표현 |
| 2 | **Row-wise text** | 행 단위 플랫 텍스트 |
| 3 | **Column-wise text** | 열 단위 플랫 텍스트 |
| 4 | **Markdown table** | Markdown/HTML 테이블 표기 |
| 5 | **Interleaved** | 테이블과 패시지를 인터리빙 |
| 6 | **Relation-explicit** | 관계를 명시적 트리플로 표현 |
| 7 | **Compressed** | 토큰 최소화 압축 포맷 |

### Experiment Stages

1. **Stage 1**: Baseline (Structured JSON + zero-shot QA)
2. **Stage 2**: Format Comparison (7개 포맷 비교)
3. **Stage 3**: Perturbation (행/열 재배열, 구분자 변경, 디스트랙터)
4. **Stage 4**: Cross-model (GPT-4o, Claude Sonnet, Gemini 등)
5. **Stage 5**: Breakdown Analysis (테이블/패시지, hop 수, 크기별)
6. **Stage 6**: Ablation (포맷 구성요소별 기여도)

---

## 🚀 Quick Start

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

# Serialize with specific format
python serialization/scripts/run_serialize.py --format json --split dev
```

### 4. Evaluation

```bash
# Evaluate predictions
python serialization/scripts/run_evaluate.py predictions.jsonl

# Compare all formats
python serialization/scripts/run_evaluate.py --compare
```

**자세한 사용법**: [serialization/README.md](serialization/README.md)

---

## 📁 Project Structure

```
HybridQA/
├── released_data/           # HybridQA 원본 데이터 (70K+ QA pairs)
├── WikiTables-WithLinks/    # 테이블 + 패시지 원본 (별도 clone 필요)
├── serialization/           # ✨ 직렬화 파이프라인 (신규 추가)
│   ├── configs/             # YAML 설정 (경로, 포맷, 모델)
│   ├── src/
│   │   ├── data_loader/     # HybridQA + WikiTables 데이터 로드
│   │   ├── serializers/     # 7개 직렬화 포맷 구현
│   │   ├── evaluation/      # EM/F1, 토큰 카운트, evidence 검증
│   │   ├── perturbation/    # Stage 3 변형 실험
│   │   └── inference/       # LLM 추론 (구현 예정)
│   ├── scripts/             # CLI 실행 스크립트
│   ├── tests/               # pytest 테스트 (61개, 모두 통과)
│   └── README.md            # 📖 상세 사용 가이드
├── CLAUDE.md                # Claude Code용 프로젝트 문서
├── .claude/skills/          # 전처리/직렬화/평가/검증 스킬
├── plan.md                  # 구현 계획 문서
├── README_HYBRIDQA.md       # 원본 HybridQA README
└── (원본 HybridQA 학습 코드)
```

---

## 🧪 Development Status

### ✅ Completed
- [x] 7개 직렬화 포맷 구현
- [x] HybridQA + WikiTables 데이터 로더 (LRU 캐시)
- [x] EM/F1 평가 메트릭 (원본 evaluate_script.py와 동일 로직)
- [x] Evidence 보존 검증 (교차 포맷 검증)
- [x] 토큰 카운터 (tiktoken)
- [x] Perturbation 모듈 (행/열 재배열, 구분자 변경 등)
- [x] 61개 pytest 테스트 (100% 통과)
- [x] Claude Code 스킬 6개 (/preprocess, /serialize, /evaluate, /validate, /debug, /test)

### 🚧 In Progress
- [ ] LLM 추론 파이프라인 (inference/)
- [ ] 프롬프트 빌더
- [ ] OpenAI/Anthropic API 클라이언트
- [ ] 배치 추론 + rate limiting

---

## 📊 Dataset

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

## 🛠️ Testing

```bash
cd HybridQA
pytest serialization/tests/ -v
```

- `test_loaders.py`: 데이터 로더 (10 tests)
- `test_serializers.py`: 7개 포맷 + evidence 보존 (31 tests)
- `test_metrics.py`: EM/F1 메트릭 (17 tests)
- `test_evidence.py`: 교차 포맷 검증 (3 tests)

**Total**: 61 tests passed in 0.07s ✅

---

## 📚 Documentation

- **[serialization/README.md](serialization/README.md)**: 상세 사용 가이드
- **[CLAUDE.md](CLAUDE.md)**: Claude Code용 프로젝트 문서 (아키텍처, 코딩 스타일, 데이터 플로우)
- **[README_HYBRIDQA.md](README_HYBRIDQA.md)**: 원본 HybridQA 사용법

---

## 🤝 Contributing

이 프로젝트는 연구 목적으로 개발되었습니다. 원본 HybridQA 데이터셋과 코드베이스를 기반으로 직렬화 실험 기능을 추가했습니다.

**Original HybridQA Authors**: Wenhu Chen, Hanwen Zha, Zhiyu Chen, Wenhan Xiong, Hong Wang, William Wang (UCSB)

---

## 📄 License

원본 HybridQA 라이선스를 따릅니다.
