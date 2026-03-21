# HybridQA Serialization Pipeline

**How Input Serialization Shapes Hybrid Table–Text QA** 연구를 위한 직렬화 파이프라인입니다.

HybridQA 데이터셋의 테이블+텍스트 데이터를 6가지 표준 포맷(JSON, YAML, Markdown, HTML, LaTeX, CSV)으로 변환하고, LLM 추론 및 평가까지 이어지는 실험 코드베이스입니다.

---

## Setup

### 1. WikiTables-WithLinks 다운로드

HybridQA의 테이블과 패시지 원본 데이터가 담긴 저장소입니다. **반드시 HybridQA 루트 디렉토리에서** clone해야 합니다.

```bash
cd /Users/casthood/codes/working/HybridQA
git clone https://github.com/wenhuchen/WikiTables-WithLinks
```

> **참고**: 저장소 용량이 크므로 (수 GB) 시간이 걸릴 수 있습니다.

Clone 완료 후 디렉토리 구조:

```
HybridQA/
├── released_data/           # 질문 JSON (이미 존재)
├── WikiTables-WithLinks/    # ← 새로 clone
│   ├── tables_tok/          # 테이블 JSON (table_id.json)
│   └── request_tok/         # 패시지 JSON (table_id.json)
├── serialization/           # 직렬화 파이프라인 (이 폴더)
└── ...
```

설치 확인:

```bash
# tables_tok, request_tok 디렉토리가 있는지 확인
ls WikiTables-WithLinks/tables_tok/ | head -5
ls WikiTables-WithLinks/request_tok/ | head -5
```

만약 경로를 다른 곳에 설치했다면, `serialization/configs/base.yaml`의 `paths.wikitables`를 수정하세요:

```yaml
paths:
  wikitables: "../WikiTables-WithLinks"  # ← 여기를 실제 경로로 변경
```

### 2. Python 의존성 설치

```bash
cd /Users/casthood/codes/working/HybridQA/serialization
pip install -r requirements.txt
```

주요 패키지:
- `pyyaml` — YAML 설정 파일
- `tiktoken` — 토큰 카운트 (OpenAI 토크나이저)
- `tqdm` — 진행률 표시
- `pytest` — 테스트
- `ruff` — 린팅/포매팅

---

## 전처리 (Preprocessing) 실행

### 의존성 확인만

WikiTables가 제대로 설치됐는지 확인:

```bash
cd /Users/casthood/codes/working/HybridQA
python serialization/scripts/run_preprocess.py --check
```

출력 예시:
```
INFO: ================================================================================
INFO: HybridQA Preprocessing Pipeline
INFO: Split: dev
INFO: ================================================================================
INFO: ✓ WikiTables-WithLinks found at .../WikiTables-WithLinks
INFO:   - tables_tok: 13000 files
INFO:   - request_tok: 13000 files
INFO: ✓ Dependency check passed
```

### dev split 전처리

```bash
python serialization/scripts/run_preprocess.py --split dev
```

출력 예시:
```
INFO: Loading questions from .../released_data...
INFO: ✓ Loaded 3466 questions, 1023 unique tables (0.45s)
INFO:   - Questions with answer_text: 3466
INFO:   - Questions with answer_nodes: 3466

INFO: Loading sample tables...
Loading tables: 100%|██████████| 5/5 [00:00<00:00, 23.4table/s]
INFO: ✓ Loaded 5 sample tables (0.21s, 42.8ms/table)
INFO:   - Avg table size: 12.4 rows x 4.2 cols
INFO:   - Avg passages per table: 38.6

INFO: Cache statistics:
INFO:   - Table cache: CacheInfo(hits=0, misses=5, maxsize=2048, currsize=5)
INFO:   - Passage cache: CacheInfo(hits=0, misses=5, maxsize=2048, currsize=5)
```

**로그 파일 자동 생성**: `serialization/outputs/logs/preprocess_{split}_{timestamp}.log`

### train split 전처리

```bash
python serialization/scripts/run_preprocess.py --split train
```

### 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--split` | 데이터 split (train/dev/test) | `dev` |
| `--check` | 의존성 확인만 (WikiTables 설치 체크) | - |
| `--sample-tables` | 로딩할 샘플 테이블 수 | `5` |
| `--no-log-file` | 로그 파일 생성 비활성화 | - |
| `--config` | 설정 파일 경로 | `configs/base.yaml` |

예시:
```bash
# 로그 파일 없이 10개 테이블 샘플링
python serialization/scripts/run_preprocess.py --split dev --sample-tables 10 --no-log-file
```

---

## 직렬화 (Serialization) 실행

### 전체 포맷으로 dev split 직렬화

```bash
python serialization/scripts/run_serialize.py --format all --split dev
```

### 특정 포맷만

```bash
python serialization/scripts/run_serialize.py --format json --split dev
python serialization/scripts/run_serialize.py --format yaml --split dev
python serialization/scripts/run_serialize.py --format markdown --split dev
python serialization/scripts/run_serialize.py --format html --split dev
python serialization/scripts/run_serialize.py --format latex --split dev
python serialization/scripts/run_serialize.py --format csv --split dev
```

### 샘플링 (빠른 테스트)

```bash
# 10개 샘플만 직렬화
python serialization/scripts/run_serialize.py --format json --split dev --sample 10
```

### Dry-run (저장 없이 1개 미리보기)

```bash
python serialization/scripts/run_serialize.py --format json --dry-run
```

출력 결과는 `serialization/outputs/serialized/{format}/{split}/data.jsonl`에 저장됩니다.

---

## 평가 (Evaluation) 실행

```bash
# 단일 예측 파일 평가
python serialization/scripts/run_evaluate.py predictions.jsonl

# 전체 포맷 비교 테이블
python serialization/scripts/run_evaluate.py --compare
```

---

## 테스트

```bash
cd /Users/casthood/codes/working/HybridQA
pytest serialization/tests/ -v
```

모듈별 실행:

```bash
pytest serialization/tests/test_loaders.py -v      # 데이터 로더
pytest serialization/tests/test_serializers.py -v   # 직렬화 포맷
pytest serialization/tests/test_metrics.py -v       # EM/F1 메트릭
pytest serialization/tests/test_evidence.py -v      # evidence 보존
```

---

## 사용 가능한 6가지 직렬화 포맷

| 포맷 | 명령어 옵션 | 설명 |
|------|------------|------|
| Structured JSON | `--format json` | 원본 구조를 JSON으로 표현 |
| YAML | `--format yaml` | 원본 구조를 YAML로 표현 |
| Markdown table | `--format markdown` | Markdown 테이블 표기 |
| HTML table | `--format html` | HTML 테이블 표기 |
| LaTeX table | `--format latex` | LaTeX tabular 환경 |
| CSV | `--format csv` | RFC 4180 CSV 포맷 |

---

## 디렉토리 구조

```
serialization/
├── configs/
│   ├── base.yaml           # 경로, split, 샘플링 설정
│   ├── formats.yaml        # 6개 직렬화 포맷 정의
│   └── models.yaml         # LLM 모델 설정
├── src/
│   ├── types.py            # 커스텀 타입 별칭
│   ├── data_loader/        # HybridQA + WikiTables 데이터 로드
│   ├── serializers/        # 6개 직렬화 포맷 구현
│   ├── evaluation/         # EM/F1, 토큰 카운트, evidence 검증
│   ├── perturbation/       # Stage 3 변형 실험
│   └── inference/          # LLM 추론 (이후 구현)
├── scripts/
│   ├── run_preprocess.py   # 전처리 파이프라인
│   ├── run_serialize.py    # 직렬화 실행
│   ├── run_evaluate.py     # 평가 실행
│   └── run_inference.py    # LLM 추론 (이후 구현)
├── tests/                  # pytest 테스트
├── outputs/                # 생성된 결과물 (gitignored)
└── notebooks/              # 탐색/분석용
```
