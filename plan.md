⏺ 계획이 완성되었습니다. 요약하면:                                                                                  
                                                                                                                    
  이번 구현 범위:                                                                                                   
  - serialization/ 작업공간 (data_loader + serializers 7개 + evaluation + tests)                                    
  - CLAUDE.md (한국어, 코드는 전부 영어)
  - .claude/skills/ 6개 (preprocess, serialize, evaluate, validate, debug, test)                                    
  - inference/ 모듈은 디렉토리만 생성, 내부 구현은 이후로                                                         

  핵심 설계:
  - ABC + Registry 패턴으로 serializer 확장성 확보
  - YAML config로 실험 매트릭스 관리
  - WikiTables-WithLinks는 미설치 상태를 기본으로, setup 안내 포함
  - 기존 evaluate_script.py의 EM/F1 로직을 그대로 포팅

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 Ready to code?                                        

 Here is Claude's plan:                                                                                             
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
 Plan: HybridQA Serialization 작업공간 구축 + CLAUDE.md + Skills                                                    
                                                                                                                  
 Context

 연구 프로젝트 "How Input Serialization Shapes Hybrid Table–Text QA" (EMNLP 2026 목표)의 실험 코드 기반을 마련한다.
  HybridQA 데이터셋(70K+ QA pairs)을 7가지 직렬화 포맷으로 변환하고, LLM 추론 및 평가까지 이어지는 파이프라인을
 구축해야 한다. 이를 위해:

 1. HybridQA 폴더 내에 serialization/ 작업공간을 생성
 2. 프로젝트 루트에 CLAUDE.md를 작성하여 Claude Code가 프로젝트를 효과적으로 이해하도록 함
 3. .claude/skills/에 전처리·직렬화·평가·검증·디버그·테스트 스킬을 정의

 결정 사항:
 - 코드 언어: 전부 영어 (변수명, docstring, 주석, 로그 메시지)
 - WikiTables-WithLinks: 아직 미설치. configs/base.yaml에서 경로 설정 + setup 안내 포함
 - 구현 범위: data_loader + serializers + evaluation + tests 우선. inference/ 모듈은 이후 별도 구현

 참조 문서:
 - paper_strategy/experiments/plans/experiments_plan.tex — 실험 계획 (7 포맷, 6 스테이지)
 - paper_strategy/paper_archive/01_data_form_benchmarks/@ChenEtAl2020.md — HybridQA 논문 리뷰
 - paper_strategy/paper_archive/03_survey/JY_Dataset.md — 데이터셋 비교표
 - paper_strategy/writing/paper/abstract.tex — 논문 초록 (연구 방향)
 - Tuesday_Morning_Trading/CLAUDE.md + .claude/skills/ — 기존 Claude Code 패턴 참고

 ---
 Step 1: serialization/ 디렉토리 구조 생성

 경로: /Users/casthood/codes/working/HybridQA/serialization/

 serialization/
 ├── __init__.py
 ├── configs/
 │   ├── base.yaml              # 경로, split, 샘플링 설정
 │   ├── formats.yaml           # 7개 직렬화 포맷 정의 + 파라미터
 │   └── models.yaml            # LLM 모델별 설정 (Stage 4용)
 ├── src/
 │   ├── __init__.py
 │   ├── types.py               # 커스텀 타입 (TableID, QuestionID 등)
 │   ├── data_loader/
 │   │   ├── __init__.py
 │   │   ├── hybridqa_loader.py # released_data/*.json 로드
 │   │   ├── wikitables_loader.py # WikiTables-WithLinks 로드 + LRU 캐시
 │   │   └── schema.py          # @dataclass: Question, Table, Passage, AnswerNode
 │   ├── serializers/
 │   │   ├── __init__.py
 │   │   ├── base.py            # ABC: BaseSerializer (serialize + format_name)
 │   │   ├── registry.py        # @register 데코레이터 + get_serializer()
 │   │   ├── json_format.py     # Format 1: Structured JSON
 │   │   ├── row_wise.py        # Format 2: Flattened row-wise text
 │   │   ├── col_wise.py        # Format 3: Flattened column-wise text
 │   │   ├── markdown_html.py   # Format 4: Markdown/HTML table
 │   │   ├── interleaved.py     # Format 5: Interleaved table-text
 │   │   ├── relation_explicit.py # Format 6: Relation-explicit
 │   │   └── compressed.py      # Format 7: Compressed format
 │   ├── inference/             # (이후 구현 예정 - 이번 범위 외)
 │   │   ├── __init__.py
 │   │   ├── prompt_builder.py  # 직렬화 텍스트 + 질문 → 프롬프트
 │   │   ├── llm_client.py      # ABC + OpenAI/Anthropic 구현
 │   │   └── runner.py          # 배치 추론 + rate limiting + 재개 지원
 │   ├── evaluation/
 │   │   ├── __init__.py
 │   │   ├── metrics.py         # EM, F1 (기존 evaluate_script.py에서 포팅)
 │   │   ├── token_counter.py   # tiktoken 기반 토큰 카운트
 │   │   ├── evidence_checker.py # 포맷 간 evidence 동일성 검증
 │   │   └── analyzer.py        # 조건별 분석 (Stage 5)
 │   └── perturbation/
 │       ├── __init__.py
 │       ├── row_reorder.py     # 행/열 재배열
 │       ├── separator_swap.py  # 구분자/필드명 변형
 │       ├── distractor.py      # 디스트랙터 패시지/행 삽입
 │       └── whitespace.py      # 공백/들여쓰기 변형
 ├── scripts/
 │   ├── run_preprocess.py      # 전처리 파이프라인
 │   ├── run_serialize.py       # 직렬화 실행 (전 포맷 / 단일 포맷)
 │   ├── run_inference.py       # LLM 추론 실행
 │   └── run_evaluate.py        # 메트릭 계산 + 비교 테이블
 ├── tests/
 │   ├── __init__.py
 │   ├── conftest.py            # 공유 fixture (샘플 테이블/질문/패시지)
 │   ├── test_loaders.py
 │   ├── test_serializers.py
 │   ├── test_evidence.py
 │   └── test_metrics.py
 ├── outputs/                   # gitignored
 │   ├── serialized/            # {format}/{split}/data.jsonl
 │   ├── predictions/           # {model}/{format}/{split}/*.jsonl
 │   └── results/               # {experiment}/metrics.json
 ├── notebooks/
 │   └── .gitkeep
 ├── requirements.txt
 └── pyproject.toml             # ruff, pytest 설정

 핵심 설계 결정:
 - ABC + Registry 패턴: 기존 Tuesday_Morning_Trading 패턴을 따름. 새 포맷 추가 시 파일 1개 + 데코레이터 1줄로 완료
 - YAML 기반 설정: 경로·포맷·모델 설정을 분리하여 실험 매트릭스 관리
 - WikiTables LRU 캐싱: 동일 table_id를 여러 질문이 참조하므로 lazy loading + 캐시
 - evidence 보존 검증: evidence_checker.py로 모든 포맷이 동일한 정보를 포함하는지 자동 검증

 ---
 Step 2: CLAUDE.md 작성

 경로: /Users/casthood/codes/working/HybridQA/CLAUDE.md

 한국어로 작성. 포함 섹션:

 ┌───────────────────────┬────────────────────────────────────────────────────────────────────────────────────┐
 │         섹션          │                                        내용                                        │
 ├───────────────────────┼────────────────────────────────────────────────────────────────────────────────────┤
 │ Project Overview      │ 연구 목표, RQ, 타겟 학회, 7가지 직렬화 포맷, 6 실험 단계                           │
 ├───────────────────────┼────────────────────────────────────────────────────────────────────────────────────┤
 │ HybridQA Data Schema  │ 원본 데이터 스키마, answer-node 구조, WikiTables 구조, 데이터 접근 패턴 코드 예시  │
 ├───────────────────────┼────────────────────────────────────────────────────────────────────────────────────┤
 │ Architecture          │ serialization/ 디렉토리 구조, 모듈별 역할 테이블                                   │
 ├───────────────────────┼────────────────────────────────────────────────────────────────────────────────────┤
 │ Coding Style          │ Type hints 필수, @dataclass, ABC 상속, private/public 규약, docstring 포맷         │
 ├───────────────────────┼────────────────────────────────────────────────────────────────────────────────────┤
 │ Data Flow             │ 전체 파이프라인 다이어그램 (raw → loader → schema → serializer → inference → eval) │
 ├───────────────────────┼────────────────────────────────────────────────────────────────────────────────────┤
 │ Configuration         │ base.yaml, formats.yaml, models.yaml 구조 설명                                     │
 ├───────────────────────┼────────────────────────────────────────────────────────────────────────────────────┤
 │ Testing               │ pytest 실행법, fixture 설명                                                        │
 ├───────────────────────┼────────────────────────────────────────────────────────────────────────────────────┤
 │ Common Tasks          │ 새 포맷 추가, 새 데이터셋 추가, 실험 실행 순서                                     │
 ├───────────────────────┼────────────────────────────────────────────────────────────────────────────────────┤
 │ Skills                │ 사용 가능한 6개 스킬 목록 + 간단 설명                                              │
 ├───────────────────────┼────────────────────────────────────────────────────────────────────────────────────┤
 │ External Dependencies │ WikiTables-WithLinks 설치법, 실험 서버 정보                                        │
 ├───────────────────────┼────────────────────────────────────────────────────────────────────────────────────┤
 │ Notes                 │ evidence 보존 최우선, 토큰 효율성 추적, dev 먼저 개발                              │
 └───────────────────────┴────────────────────────────────────────────────────────────────────────────────────┘

 기존 evaluate_script.py의 normalize_answer, compute_exact, compute_f1 함수를 metrics.py에서 재사용해야 한다는 점을
  명시.

 ---
 Step 3: .claude/skills/ 작성

 경로: /Users/casthood/codes/working/HybridQA/.claude/skills/

 6개 스킬 파일, 각각 Korean + 기존 패턴(Usage, Behavior, Rules, Example):

 스킬: /preprocess
 파일: preprocess.md
 용도: WikiTables 의존성 확인 → HybridQA JSON + WikiTables 로드 → Schema 변환 → 요약 출력
 ────────────────────────────────────────
 스킬: /serialize
 파일: serialize.md
 용도: --format, --split, --sample, --dry-run 옵션. 포맷별 직렬화 + 토큰 카운트 + 결과 저장
 ────────────────────────────────────────
 스킬: /evaluate
 파일: evaluate.md
 용도: 예측 결과 EM/F1 계산, --compare로 전체 비교 테이블, --breakdown으로 조건별 분석
 ────────────────────────────────────────
 스킬: /validate
 파일: validate.md
 용도: evidence 보존 검증, 구조 검증, 교차 포맷 검증. 실패 시 diff 표시
 ────────────────────────────────────────
 스킬: /debug
 파일: debug.md
 용도: 에러 분류(Import/Type/Data/API/Serialization) → 최소 수정 → pytest 검증
 ────────────────────────────────────────
 스킬: /test
 파일: test.md
 용도: 모듈별/전체 pytest 실행 → 결과 요약 → 실패 시 /debug 연계 제안

 ---
 Step 4: 설정 파일 (configs/)

 base.yaml

 - paths.hybridqa_data: "../released_data"
 - paths.wikitables: "../WikiTables-WithLinks" (또는 절대경로)
 - paths.output_dir: "outputs"
 - splits: [train, dev, test]
 - sampling.dev_sample_size: null (전체) 또는 숫자
 - sampling.random_seed: 42

 formats.yaml

 - 7개 포맷 각각: class (serializer 클래스명), params (포맷별 파라미터)

 models.yaml

 - provider, name, params (temperature, max_tokens) per model

 ---
 Step 5: 기반 Python 파일

 pyproject.toml

 - ruff: line-length = 100, target-version = "py310"
 - pytest: testpaths = ["tests"]

 requirements.txt

 - pyyaml, tiktoken, tqdm, openai, anthropic
 - pytest, ruff (dev)

 src/data_loader/schema.py — 핵심 데이터클래스

 @dataclass
 class AnswerNode:
     text: str
     position: tuple[int, int]  # (row_idx, col_idx)
     wiki_link: str | None = None
     source: str = "table"  # "table" | "passage"

 @dataclass
 class Question:
     question_id: str
     question: str
     table_id: str
     answer_text: str | None = None
     answer_nodes: list[AnswerNode] = field(default_factory=list)

 @dataclass
 class Table:
     table_id: str
     header: list[tuple[str, list[str]]]  # [(cell_text, [wiki_urls]), ...]
     data: list[list[tuple[str, list[str]]]]  # rows × cols

 @dataclass
 class Evidence:
     table: Table
     passages: dict[str, str]  # wiki_url → passage_text
     question: Question

 src/serializers/base.py — ABC

 - serialize(table, passages, question) -> str (추상)
 - format_name property (추상)
 - get_evidence_set(table, passages) -> set (구체, 검증용)

 src/serializers/registry.py — Registry

 - @register(name) 데코레이터
 - get_serializer(name, config) -> BaseSerializer
 - list_formats() -> list[str]

 src/evaluation/metrics.py

 - 기존 evaluate_script.py에서 normalize_answer, compute_exact, compute_f1, get_raw_scores 함수를 포팅 (동일 로직
 유지)

 ---
 Step 6: .gitignore 업데이트

 serialization/outputs/ 디렉토리를 gitignore에 추가.

 ---
 구현 순서 (권장)

 inference/ 모듈은 이번 범위에서 제외. 디렉토리와 __init__.py만 생성해두고, 내부 파일은 이후 구현.

 1. 디렉토리 구조 생성 + __init__.py 파일들
 2. CLAUDE.md 작성 (전부 영어 코딩 스타일 반영, WikiTables setup 안내 포함)
 3. .claude/skills/ 6개 파일 작성
 4. configs/ YAML 3개 파일 (base.yaml에 WikiTables 미설치 상태 기본값)
 5. pyproject.toml + requirements.txt
 6. src/types.py + src/data_loader/schema.py
 7. src/data_loader/hybridqa_loader.py + wikitables_loader.py
 8. src/serializers/base.py + registry.py
 9. src/serializers/json_format.py (Stage 1 베이스라인)
 10. src/evaluation/metrics.py (기존 evaluate_script.py에서 포팅)
 11. src/evaluation/token_counter.py + evidence_checker.py
 12. tests/conftest.py + 기본 테스트들
 13. 나머지 6개 serializer 포맷 (Stage 2)

 ---
 Verification

 1. 구조 검증: tree serialization/ 으로 디렉토리 구조 확인
 2. import 검증: python -c "from serialization.src.serializers.registry import list_formats; print(list_formats())"
  실행
 3. CLAUDE.md 확인: Claude Code 새 세션에서 HybridQA 폴더 진입 시 자동 로드 확인
 4. Skills 확인: /preprocess, /serialize 등 스킬 호출 가능 여부 확인
 5. 테스트 실행: cd /Users/casthood/codes/working/HybridQA && pytest serialization/tests/ -v
 6. JSON 포맷 직렬화 e2e: 샘플 데이터로 json_format serializer 동작 확인

⏺ All tasks complete. Here's a summary of everything implemented: 
                                                                    
  Summary                                            
                                                                                                                    
  Files Created (44 files total)             
                                                                                                                    
  Directory Structure — serialization/ with all subdirectories:                                                     
  - configs/ (3 YAML files), src/ (4 subpackages), scripts/ (4 runners), tests/ (5 files), outputs/, notebooks/     
                                                                                                                    
  CLAUDE.md — Comprehensive project documentation in Korean covering:                                               
  - Project overview, research questions, 7 formats, 6 stages                                                       
  - HybridQA data schema with code examples                                                                         
  - Architecture, coding style, data flow, configuration
  - Testing, common tasks, skills, external dependencies

  Skills (.claude/skills/) — 6 skill files:
  - /preprocess, /serialize, /evaluate, /validate, /debug, /test

  Config — 3 YAML + pyproject.toml + requirements.txt:
  - base.yaml (paths, splits, sampling), formats.yaml (7 format definitions), models.yaml (LLM configs)

  Core Python Modules:
  - types.py — Custom type aliases (TableID, QuestionID, etc.)
  - data_loader/ — schema.py (4 dataclasses), hybridqa_loader.py, wikitables_loader.py (LRU cached)
  - serializers/ — base.py (ABC), registry.py (@register pattern), + 7 format implementations
  - evaluation/ — metrics.py (ported from evaluate_script.py), token_counter.py, evidence_checker.py, analyzer.py
  - perturbation/ — row_reorder.py, separator_swap.py, distractor.py, whitespace.py
  - inference/ — __init__.py only (placeholder for later)

  Tests — 61 tests, all passing:
  - test_loaders.py (10 tests), test_serializers.py (31 tests incl. parametrized evidence preservation),
  test_evidence.py (3 tests), test_metrics.py (17 tests)

  Verification:
  - list_formats() returns all 7 registered formats
  - All 61 tests pass in 0.07s
  - Evidence preservation verified across all 7 formats

 원본 HybridQA 모델 (2020년, 작은 모델 시대):
  질문 → linking(TF-IDF/string match) → 관련 행/패시지 필터링 → 셀 선택 → 정답 추출                
  작은 모델은 전체 테이블+패시지를 한번에 처리할 수 없어서 linking으로 범위를 좁히는 것이          
  필수였습니다.                                                                                    
                                                                                                   
  우리 프로젝트 (2026년, LLM 시대):                                                                
  질문 + 전체 테이블+패시지(직렬화) → LLM → 정답
  GPT-4o, Claude 같은 LLM은 긴 컨텍스트를 직접 처리하므로 linking 없이 end-to-end로 답을 찾습니다.

  이게 의미 있는 이유:

  1. 같은 데이터셋, 같은 평가지표 (EM/F1) — HybridQA 벤치마크 위에서 비교 가능
  2. 연구 초점이 다름 — 원본은 "어떤 모델 아키텍처가 좋은가", 우리는 "같은 LLM에 어떤 포맷으로
  주느냐가 성능에 영향을 주는가"
  3. 최근 연구 트렌드와 일치 — 2024~2025 테이블 QA 논문들도 대부분 linking 없이 LLM에 직접 입력하는
   방식

  다만 고려할 점이 하나 있습니다: 테이블에 연결된 패시지가 수십 개일 경우 토큰 한도를 초과할 수
  있습니다. 이건 linking이 아니라 토큰 예산 관리 차원에서 나중에 처리하면 됩니다 (예: 패시지
  truncation, 요약 등).

  결론적으로, preprocessing.py의 linking 과정은 우리 파이프라인에서 불필요하고, 이는 연구 설계상
  의도된 것입니다.
