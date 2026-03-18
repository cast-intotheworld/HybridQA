# Claude Code Instructions

이 문서는 Claude Code가 HybridQA serialization 프로젝트를 효과적으로 이해하고 작업할 수 있도록 프로젝트 컨텍스트, 아키텍처, 코딩 패턴을 설명합니다.

---

## Project Overview

**How Input Serialization Shapes Hybrid Table–Text QA** (EMNLP 2026 목표)

HybridQA 데이터셋(70K+ QA pairs)에서 테이블+텍스트 하이브리드 데이터를 7가지 직렬화 포맷으로 변환하여 LLM에 입력했을 때, 포맷 선택이 QA 성능에 미치는 영향을 분석하는 연구입니다.

### Research Questions

1. **RQ1**: 직렬화 포맷에 따라 LLM의 QA 정확도(EM/F1)가 얼마나 달라지는가?
2. **RQ2**: 토큰 효율성(정보 밀도)과 QA 성능 사이의 트레이드오프는 어떠한가?
3. **RQ3**: 테이블 기반 질문 vs 패시지 기반 질문에서 포맷별 성능 차이는?

### 7 Serialization Formats

| # | Format | Description |
|---|--------|-------------|
| 1 | Structured JSON | 원본 구조를 JSON으로 표현 |
| 2 | Row-wise text | 행 단위 플랫 텍스트 |
| 3 | Column-wise text | 열 단위 플랫 텍스트 |
| 4 | Markdown/HTML table | Markdown 또는 HTML 테이블 표기 |
| 5 | Interleaved table-text | 테이블과 패시지를 인터리빙 |
| 6 | Relation-explicit | 관계를 명시적으로 표현 |
| 7 | Compressed | 토큰 최소화 압축 포맷 |

### 6 Experiment Stages

1. **Stage 1**: Baseline — Structured JSON 직렬화 + zero-shot QA
2. **Stage 2**: Format Comparison — 7개 포맷 비교
3. **Stage 3**: Perturbation — 행/열 재배열, 구분자 변경, 디스트랙터 삽입
4. **Stage 4**: Cross-model — GPT-4o, Claude, Gemini 등 모델 간 비교
5. **Stage 5**: Breakdown Analysis — 테이블/패시지 유형, hop 수, 테이블 크기별 분석
6. **Stage 6**: Ablation — 포맷 구성요소별 기여도 분석

---

## HybridQA Data Schema

### 원본 데이터 구조

**released_data/train.json, dev.json, test.json**:
```json
{
  "question_id": "00153f694413a536",
  "question": "What is the middle name of the player with...",
  "table_id": "List_of_National_Football_League_rushing_yards_leaders_0",
  "answer-text": "Jerry",
  "question_postag": "WP VBZ DT JJ NN IN DT NN ..."
}
```

**released_data/train.traced.json, dev.traced.json** (traced 버전):
```json
{
  ...위 필드 + ...
  "answer-node": [
    ["Jerry", [2, 1], "/wiki/Jerry_Rice", "passage"]
  ]
}
```

**WikiTables-WithLinks/tables_tok/{table_id}.json**:
```json
{
  "header": [["Rank", []], ["Player", ["/wiki/Walter_Payton"]], ...],
  "data": [[["1", []], ["Walter Payton", ["/wiki/Walter_Payton"]], ...], ...],
  "title": "Table Title",
  "section_title": "Section",
  "uid": "table_id"
}
```

**WikiTables-WithLinks/request_tok/{table_id}.json**:
```json
{
  "/wiki/Walter_Payton": "Walter Jerry Payton was an American football running back...",
  "/wiki/Emmitt_Smith": "Emmitt James Smith III is a former American football...",
  ...
}
```

### 데이터 접근 패턴

```python
# 질문 로드
with open("released_data/dev.traced.json") as f:
    questions = json.load(f)

# 테이블 로드 (table_id 기반)
table_id = questions[0]["table_id"]
with open(f"WikiTables-WithLinks/tables_tok/{table_id}.json") as f:
    table = json.load(f)

# 패시지 로드 (같은 table_id)
with open(f"WikiTables-WithLinks/request_tok/{table_id}.json") as f:
    passages = json.load(f)
```

### dev_reference.json (평가용)

```json
{
  "reference": {"question_id": "answer_text", ...},
  "table": ["qid1", "qid2", ...],
  "passage": ["qid3", "qid4", ...]
}
```

---

## Architecture

```
serialization/
├── configs/           # YAML 설정 (경로, 포맷, 모델)
├── src/
│   ├── types.py       # 커스텀 타입 별칭
│   ├── data_loader/   # HybridQA + WikiTables 데이터 로드
│   ├── serializers/   # 7개 직렬화 포맷 (ABC + Registry)
│   ├── inference/     # LLM 추론 (이후 구현)
│   ├── evaluation/    # EM/F1 메트릭, 토큰 카운트, evidence 검증
│   └── perturbation/  # Stage 3 변형 실험
├── scripts/           # CLI 실행 스크립트
├── tests/             # pytest 테스트
├── outputs/           # 생성된 결과물 (gitignored)
└── notebooks/         # 탐색/분석용
```

### Module Responsibilities

| Module | Purpose |
|---|---|
| `src/types.py` | `TableID`, `QuestionID`, `WikiURL` 등 타입 별칭 |
| `src/data_loader/schema.py` | `Question`, `Table`, `Evidence`, `AnswerNode` 데이터클래스 |
| `src/data_loader/hybridqa_loader.py` | `released_data/*.json` 로드 + 스키마 변환 |
| `src/data_loader/wikitables_loader.py` | WikiTables-WithLinks 로드 + LRU 캐시 |
| `src/serializers/base.py` | `BaseSerializer` ABC (serialize + format_name) |
| `src/serializers/registry.py` | `@register` 데코레이터 + `get_serializer()` |
| `src/serializers/json_format.py` | Format 1: Structured JSON |
| `src/serializers/row_wise.py` | Format 2: Flattened row-wise text |
| `src/serializers/col_wise.py` | Format 3: Flattened column-wise text |
| `src/serializers/markdown_html.py` | Format 4: Markdown/HTML table |
| `src/serializers/interleaved.py` | Format 5: Interleaved table-text |
| `src/serializers/relation_explicit.py` | Format 6: Relation-explicit |
| `src/serializers/compressed.py` | Format 7: Compressed format |
| `src/evaluation/metrics.py` | EM/F1 (evaluate_script.py에서 포팅) |
| `src/evaluation/token_counter.py` | tiktoken 기반 토큰 카운트 |
| `src/evaluation/evidence_checker.py` | 포맷 간 evidence 동일성 검증 |
| `src/evaluation/analyzer.py` | 조건별 분석 (Stage 5) |
| `src/perturbation/` | 행/열 재배열, 구분자 변형, 디스트랙터 삽입, 공백 변형 |

---

## Coding Style & Patterns

### 1. 코드 언어

**모든 코드는 영어로 작성**: 변수명, 함수명, docstring, 주석, 로그 메시지 전부 영어.
CLAUDE.md와 Skills만 한국어로 작성.

### 2. Type Hints

모든 함수/메서드에 타입 힌트를 명시합니다.

```python
from serialization.src.types import TableID, QuestionID

def load_questions(split: str) -> list[Question]:
    ...
```

### 3. Private/Public Convention

- **Private 속성**: `self._cache`, `self._config`
- **Private 메서드**: `_parse_header()`, `_resolve_links()`
- **Public 접근**: `@property` 데코레이터 사용

### 4. Dataclass for Data Structures

모든 데이터 구조는 `@dataclass`로 정의합니다.

```python
@dataclass
class Question:
    question_id: str
    question: str
    table_id: str
    answer_text: str | None = None
```

### 5. ABC for Extensibility

직렬화 포맷은 `BaseSerializer` ABC를 상속합니다.

```python
class BaseSerializer(ABC):
    @abstractmethod
    def serialize(self, evidence: Evidence) -> str:
        pass

    @property
    @abstractmethod
    def format_name(self) -> str:
        pass
```

### 6. Registry Pattern

새 포맷 추가 시 `@register` 데코레이터 1줄로 등록 완료.

```python
@register("json")
class JSONSerializer(BaseSerializer):
    ...
```

### 7. Docstrings

`:param:`, `:return:` 형식으로 작성합니다.

```python
def serialize(self, evidence: Evidence) -> str:
    """Serialize table and passages into structured JSON.

    :param evidence: Evidence containing table, passages, and question.
    :return: Serialized string representation.
    """
```

---

## Data Flow

```
released_data/*.json          WikiTables-WithLinks/
       ↓                              ↓
  hybridqa_loader.py            wikitables_loader.py (LRU cached)
       ↓                              ↓
       └──────── schema.py ───────────┘
                    ↓
            Evidence dataclass
                    ↓
         serializers/ (7 formats)
                    ↓
           serialized text (str)
                    ↓
         inference/ (prompt + LLM)    ← 이후 구현
                    ↓
              predictions
                    ↓
         evaluation/ (EM, F1, tokens)
```

---

## Configuration

### `configs/base.yaml`

경로, split, 샘플링 설정. WikiTables-WithLinks는 미설치 시 경로만 지정.

```yaml
paths:
  hybridqa_data: "../released_data"
  wikitables: "../WikiTables-WithLinks"
  output_dir: "outputs"
```

### `configs/formats.yaml`

7개 직렬화 포맷 정의 + 포맷별 파라미터.

### `configs/models.yaml`

LLM 모델별 설정 (provider, name, temperature, max_tokens).

---

## Testing

```bash
cd /Users/casthood/codes/working/HybridQA
pytest serialization/tests/ -v
```

- `tests/conftest.py`: 공유 fixture (샘플 테이블, 질문, 패시지)
- `tests/test_loaders.py`: 데이터 로더 테스트
- `tests/test_serializers.py`: 직렬화 포맷 테스트
- `tests/test_evidence.py`: evidence 보존 검증 테스트
- `tests/test_metrics.py`: EM/F1 메트릭 테스트

---

## Common Tasks

### 새 직렬화 포맷 추가

1. `src/serializers/` 에 새 파일 생성 (예: `new_format.py`)
2. `BaseSerializer`를 상속하고 `serialize()`, `format_name` 구현
3. `@register("new_format")` 데코레이터 추가
4. `configs/formats.yaml`에 포맷 설정 추가
5. `tests/test_serializers.py`에 테스트 추가

### 새 데이터셋 추가

1. `src/data_loader/`에 새 로더 파일 생성
2. `schema.py`의 데이터클래스를 재사용 또는 확장
3. `configs/base.yaml`에 경로 추가

### 실험 실행 순서

1. WikiTables-WithLinks 설치 확인
2. `python scripts/run_preprocess.py` — 데이터 전처리
3. `python scripts/run_serialize.py --format all` — 직렬화
4. `python scripts/run_inference.py` — LLM 추론 (이후 구현)
5. `python scripts/run_evaluate.py` — 평가

---

## Skills

프로젝트 루트의 `.claude/skills/` 폴더에 개발 워크플로우 특화 스킬이 정의되어 있습니다.

- `/preprocess`: WikiTables 의존성 확인 → HybridQA + WikiTables 로드 → Schema 변환
- `/serialize`: 포맷별 직렬화 실행 + 토큰 카운트 + 결과 저장
- `/evaluate`: EM/F1 계산 + 비교 테이블 + 조건별 분석
- `/validate`: evidence 보존 검증 + 구조 검증 + 교차 포맷 검증
- `/debug`: 에러 분류 → 최소 수정 → pytest 검증
- `/test`: 모듈별/전체 pytest 실행 + 결과 요약

자세한 내용은 `.claude/skills/` 참고.

---

## External Dependencies

### WikiTables-WithLinks 설치

```bash
cd /Users/casthood/codes/working/HybridQA
git clone https://github.com/wenhuchen/WikiTables-WithLinks
```

설치 후 `configs/base.yaml`의 `paths.wikitables` 경로 확인.

### 주요 Python 패키지

- `pyyaml`: YAML 설정 파일 로드
- `tiktoken`: 토큰 카운트 (OpenAI 토크나이저)
- `tqdm`: 진행률 표시
- `pytest`: 테스트 프레임워크
- `ruff`: 린팅/포매팅

---

## Notes

- **Evidence 보존이 최우선**: 모든 직렬화 포맷은 원본 테이블과 패시지의 정보를 100% 보존해야 합니다. `evidence_checker.py`로 자동 검증.
- **토큰 효율성 추적**: 포맷별 토큰 카운트를 항상 기록하여 효율성 비교.
- **dev 먼저 개발**: 새 기능은 dev split으로 먼저 개발/검증 후 train/test에 적용.
- **evaluate_script.py 로직 재사용**: `metrics.py`는 기존 `evaluate_script.py`의 `normalize_answer`, `compute_exact`, `compute_f1`, `get_raw_scores`를 동일 로직으로 포팅. 원본 로직을 변경하지 않을 것.
- **inference/ 모듈은 이후 구현**: 디렉토리와 `__init__.py`만 생성. 내부 파일은 별도 단계에서 구현.
