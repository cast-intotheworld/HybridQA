# Debug Skill

에러 로그를 분석하고, 원인을 추적하여 수정안을 제시합니다.

## Usage

```
/debug [error message or module name]
/debug "KeyError: 'answer-node'"
/debug serializers
```

## Behavior

1. **에러 파악**: 전달된 에러 메시지 또는 모듈명을 기반으로 관련 파일을 Read로 확인
2. **스택 트레이스 분석**: 라인 번호 → 해당 소스 코드 확인 → import/의존성 체크
3. **원인 분류**:
   - **Import 에러**: 경로, 패키지 누락, 순환 import
   - **Type 에러**: 타입 힌트 불일치, None 처리, 데이터클래스 필드
   - **Data 에러**: JSON 스키마 불일치, 누락 필드, 파일 경로
   - **API 에러**: OpenAI/Anthropic API 응답, rate limit, 인증
   - **Serialization 에러**: 포맷 변환 실패, evidence 누락, 인코딩
4. **수정 적용**: Edit 도구로 최소한의 변경을 적용
5. **검증**: `pytest serialization/tests/ -v` 실행하여 기존 테스트 통과 확인

## Rules

- 수정 전에 반드시 해당 파일을 Read로 읽을 것
- 한 번에 하나의 원인만 수정하고 검증할 것
- 수정 범위를 최소화할 것 — 관련 없는 코드를 건드리지 않기
- WikiTables 경로 관련 에러는 `configs/base.yaml` 설정을 먼저 확인

## Example

```
/debug "FileNotFoundError: WikiTables-WithLinks/tables_tok/..."
```

→ base.yaml 경로 설정 확인 → WikiTables 설치 여부 확인 → 경로 수정 또는 설치 안내.
