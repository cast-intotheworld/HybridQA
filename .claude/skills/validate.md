# Validate Skill

직렬화 결과의 evidence 보존 및 구조적 정합성을 검증합니다.

## Usage

```
/validate                              # 전체 포맷 evidence 보존 검증
/validate --format json                # 특정 포맷만 검증
/validate --cross                      # 교차 포맷 검증 (모든 포맷 간 비교)
/validate --structure                  # 출력 파일 구조 검증
```

## Behavior

1. **Evidence 보존 검증**: 각 직렬화 결과에서 원본 테이블의 모든 셀 값과 패시지 텍스트가 포함되는지 확인
   - 셀 값 누락 검출
   - 패시지 텍스트 누락 검출
   - 위키 링크 대응 관계 검증
2. **구조 검증**: JSONL 파일 형식, 필수 필드, JSON 파싱 가능 여부
3. **교차 포맷 검증**: 동일 question_id에 대해 모든 포맷이 같은 evidence set을 포함하는지
4. **실패 시 diff 표시**: 누락/초과된 evidence 항목을 diff 형태로 출력

## Rules

- evidence 보존은 **최우선 검증 항목** — 하나라도 누락되면 FAIL
- 검증은 직렬화 결과의 텍스트 내에서 원본 값의 존재 여부를 확인 (정규화 후 비교)
- 대용량 데이터에서는 랜덤 샘플링(기본 100개)으로 검증, `--all` 옵션으로 전체 검증
- 검증 결과를 `outputs/results/validation_report.json`에 저장

## Example

```
/validate --format json --cross
```

→ JSON 포맷 evidence 보존 확인 → 다른 포맷과 교차 비교 → 결과 요약:

```
[PASS] json: 100/100 samples — all evidence preserved
[PASS] Cross-format: json vs html — evidence sets match
[FAIL] Cross-format: json vs latex — 3 samples with missing cell values
  - question_id: abc123 — missing: "Walter Payton" in latex output
```
