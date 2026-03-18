# Preprocess Skill

HybridQA + WikiTables 데이터를 로드하고 Schema 데이터클래스로 변환합니다.

## Usage

```
/preprocess                  # 전체 전처리 파이프라인
/preprocess --split dev      # 특정 split만
/preprocess --check          # WikiTables 의존성 확인만
```

## Behavior

1. **의존성 확인**: WikiTables-WithLinks 디렉토리 존재 여부 확인
   - 미설치 시: `git clone https://github.com/wenhuchen/WikiTables-WithLinks` 안내 출력
   - `configs/base.yaml`의 `paths.wikitables` 경로 확인
2. **HybridQA JSON 로드**: `released_data/{split}.traced.json` 파일 로드
3. **WikiTables 로드**: `tables_tok/{table_id}.json` + `request_tok/{table_id}.json` 로드
4. **Schema 변환**: `Question`, `Table`, `Evidence` 데이터클래스로 변환
5. **요약 출력**: split별 질문 수, 고유 테이블 수, 평균 패시지 수

## Rules

- WikiTables가 없으면 전처리를 중단하고 설치 안내를 출력할 것
- traced 버전(answer-node 포함)을 우선 사용할 것 (train.traced.json, dev.traced.json)
- test.json은 answer-text가 없으므로 answer_text=None으로 처리
- 대용량 파일 로드 시 tqdm으로 진행률 표시

## Example

```
/preprocess --split dev --check
```

→ WikiTables 경로 확인 → dev.traced.json 로드 → Schema 변환 → "dev: 3,466 questions, 1,023 tables" 출력.
