# Test Skill

특정 모듈 또는 전체 테스트를 실행하고 결과를 요약합니다.

## Usage

```
/test                    # 전체 테스트 실행
/test loaders            # data_loader 관련 테스트만
/test serializers        # serializers 관련 테스트만
/test metrics            # metrics 관련 테스트만
/test evidence           # evidence 관련 테스트만
/test [file_path]        # 특정 테스트 파일 실행
```

## Behavior

1. **테스트 대상 결정**: 인자가 없으면 전체, 있으면 매칭되는 테스트 파일을 Glob으로 탐색
2. **실행**: `pytest serialization/tests/ -v` 또는 특정 파일 실행
3. **결과 요약**:
   - 통과/실패 개수
   - 실패한 테스트의 에러 메시지와 위치
   - 실패 원인에 대한 간단한 분석
4. **실패 시 후속 조치**: `/debug` 스킬로 이어서 원인 분석 제안

## Module Mapping

| 인자 | 테스트 파일 |
|------|------------|
| `loaders` | `tests/test_loaders.py` |
| `serializers` | `tests/test_serializers.py` |
| `metrics` | `tests/test_metrics.py` |
| `evidence` | `tests/test_evidence.py` |

## Rules

- 테스트 실행 전 현재 working directory가 `HybridQA/`인지 확인
- conftest.py의 fixture를 활용하여 실제 데이터 파일 의존성을 최소화
- WikiTables 미설치 시 관련 테스트는 skip 처리
- 새 기능 추가 시 테스트도 함께 작성할 것을 제안

## Example

```
/test serializers
```

→ `pytest serialization/tests/test_serializers.py -v` 실행 → 7개 포맷 테스트 결과 요약.
