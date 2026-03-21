# Evaluate Skill

예측 결과에 대한 EM/F1 메트릭을 계산하고 비교 테이블을 생성합니다.

## Usage

```
/evaluate predictions.jsonl                       # 단일 파일 평가
/evaluate --compare                               # 전체 포맷 비교 테이블
/evaluate --breakdown                             # 조건별 분석 (table/passage)
/evaluate predictions.jsonl --ref dev_reference.json  # 커스텀 reference
```

## Behavior

1. **예측 파일 로드**: JSONL (question_id, pred) 또는 JSON 리스트 형식
2. **Reference 로드**: `released_data/dev_reference.json` (기본)
3. **메트릭 계산**: EM, F1 (evaluate_script.py 동일 로직)
4. **결과 분류**: table exact, table f1, passage exact, passage f1, total exact, total f1
5. **비교 테이블**: `--compare` 시 `outputs/results/` 내 모든 결과를 모아 비교 테이블 생성
6. **조건별 분석**: `--breakdown` 시 테이블 크기, hop 수, answer source별 분석

## Rules

- 메트릭 로직은 기존 `evaluate_script.py`와 **동일해야** 함
- `normalize_answer()`의 동작을 절대 변경하지 않을 것
- 비교 테이블은 Markdown 형식으로 출력
- 결과는 `outputs/results/{experiment}/metrics.json`에도 저장

## Example

```
/evaluate --compare
```

→ outputs/results/ 내 모든 실험 결과 수집 → 포맷별 EM/F1 비교 테이블 출력:

```
| Format      | Table EM | Table F1 | Pass EM | Pass F1 | Total EM | Total F1 |
|-------------|----------|----------|---------|---------|----------|----------|
| json        | 45.2     | 52.1     | 38.7    | 46.3    | 42.0     | 49.2     |
| markdown    | ...      | ...      | ...     | ...     | ...      | ...      |
| html        | ...      | ...      | ...     | ...     | ...      | ...      |
| latex       | ...      | ...      | ...     | ...     | ...      | ...      |
| csv         | ...      | ...      | ...     | ...     | ...      | ...      |
```
