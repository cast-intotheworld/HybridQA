# Serialize Skill

Evidence 데이터를 지정된 직렬화 포맷으로 변환합니다.

## Usage

```
/serialize                           # 전체 포맷, dev split
/serialize --format json             # JSON 포맷만
/serialize --format all --split dev  # 전체 포맷, dev split
/serialize --sample 100              # 100개 샘플만
/serialize --dry-run                 # 저장 없이 1개 샘플 출력
```

## Behavior

1. **설정 로드**: `configs/base.yaml` + `configs/formats.yaml`에서 포맷 정의 확인
2. **데이터 로드**: 전처리된 Evidence 데이터 로드 (또는 즉석 로드)
3. **직렬화 실행**: Registry에서 포맷별 Serializer 가져와 `serialize()` 호출
4. **토큰 카운트**: tiktoken으로 각 직렬화 결과의 토큰 수 계산
5. **결과 저장**: `outputs/serialized/{format}/{split}/data.jsonl`
6. **요약 출력**: 포맷별 평균 토큰 수, 최소/최대 토큰 수, 저장 경로

## Options

| Option | Description |
|--------|-------------|
| `--format` | 포맷 이름 또는 `all` (기본: `all`) |
| `--split` | `train`, `dev`, `test` (기본: `dev`) |
| `--sample` | 샘플 수 (기본: 전체) |
| `--dry-run` | 1개 샘플만 출력, 파일 저장 안 함 |

## Rules

- 직렬화 전 evidence_checker로 정보 보존 검증할 것
- JSONL 형식: 한 줄에 하나의 JSON 객체 (question_id, format, serialized_text, token_count)
- 기존 출력 파일이 있으면 덮어쓰기 전 확인
- `--dry-run` 시에도 토큰 카운트는 계산하여 출력

## Example

```
/serialize --format json --split dev --sample 10
```

→ JSON 포맷으로 dev split 10개 샘플 직렬화 → 토큰 통계 출력 → `outputs/serialized/json/dev/data.jsonl` 저장.
