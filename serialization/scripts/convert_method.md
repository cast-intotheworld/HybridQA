# Serialization Format — Conversion Method Reference

각 직렬화 포맷이 사용하는 변환 방식, 모듈, 이스케이프 처리를 정리한 문서입니다.

---

## Summary

| Format   | Module / Library          | Source           | Escaping                             |
|----------|---------------------------|------------------|--------------------------------------|
| JSON     | `json` (stdlib)           | Python 표준 라이브러리 | `json.dumps()` 자동 처리             |
| YAML     | `pyyaml` (pip)            | PyPI 패키지        | `yaml.dump()` 자동 처리              |
| XML      | `xml.etree.ElementTree` (stdlib) | Python 표준 라이브러리 | ElementTree 자동 이스케이프 (`<>&"'`)  |
| Markdown | 직접 문자열 조합              | 외부 의존성 없음      | 없음 (plain text 삽입)                |
| HTML     | `html.escape()` (stdlib)  | Python 표준 라이브러리 | `html.escape()` (`<>&"`) 처리         |
| LaTeX    | 직접 문자열 조합 + 커스텀 이스케이프 | 외부 의존성 없음      | `_escape_latex()` (`& % $ # _ { } ~ ^ \`) |
| CSV      | `csv` (stdlib)            | Python 표준 라이브러리 | `csv.writer` RFC 4180 자동 quoting    |

---

## Format Details

### 1. JSON — `json_format.py`

- **모듈**: `json` (Python 표준 라이브러리)
- **방식**: `json.dumps(output, ensure_ascii=False, indent=2)`
- **이스케이프**: `json.dumps()`가 문자열 내 `"`, `\`, 제어 문자 등을 자동 이스케이프
- **구조**: `{"table": {"columns": [...], "rows": [...]}, "passages": {...}}`
- **비고**: 구조화된 데이터 포맷. JSON은 사실상 모든 프로그래밍 언어에서 네이티브 지원

### 2. YAML — `yaml_format.py`

- **모듈**: `pyyaml` (PyPI: `pip install pyyaml`)
- **방식**: `yaml.dump(output, allow_unicode=True, default_flow_style=False, width=2147483647)`
- **이스케이프**: `yaml.dump()`가 특수문자 포함 문자열을 자동으로 따옴표 처리
- **구조**: JSON과 동일한 계층 구조를 YAML 문법으로 표현
- **비고**: `width=2147483647`로 긴 패시지 텍스트의 자동 줄바꿈 방지. 유일한 외부(pip) 의존성

### 3. XML — `xml_format.py`

- **모듈**: `xml.etree.ElementTree` (Python 표준 라이브러리)
- **방식**: ElementTree로 트리를 빌드한 뒤 `ET.tostring(root, encoding='unicode', xml_declaration=True)`로 직렬화
- **이스케이프**: ElementTree가 텍스트 노드와 속성 값의 `<`, `>`, `&`, `"`, `'`를 자동 이스케이프
- **정렬(indent)**: `ET.indent(root, space="  ")` (Python 3.9+)
- **태그 변환**: 컬럼명 → XML 태그명 변환 시 `_to_tag_name()` 헬퍼 사용 (공백/특수문자 → `_`)
- **구조**: `<evidence><table>...</table><passages>...</passages></evidence>`
- **비고**: 수동 문자열 조합 대신 stdlib 트리 빌더 사용으로 well-formed XML 보장

### 4. Markdown — `markdown.py`

- **모듈**: 없음 (직접 문자열 조합)
- **방식**: `| col1 | col2 |` 형식의 GFM(GitHub Flavored Markdown) 테이블 문법을 직접 조합
- **이스케이프**: 별도 이스케이프 없음. 셀 값에 `|`가 포함되면 테이블이 깨질 수 있음 (HybridQA 데이터에서는 미발생)
- **구조**: `## Title` + `| header |` + `| --- |` + `| data |` + `### Passages` + `**name**: text`
- **비고**: Markdown 생성 전용 표준 모듈이 Python에 존재하지 않음. 파싱 라이브러리(`markdown`, `mistune`)는 있으나 생성용이 아님

### 5. HTML — `html.py`

- **모듈**: `html.escape()` (Python 표준 라이브러리 `html` 모듈)
- **방식**: HTML 태그는 직접 조합, 셀 값과 패시지 텍스트는 `html.escape()`로 이스케이프 후 삽입
- **이스케이프**: `html.escape()`가 `<`, `>`, `&`, `"` 를 HTML 엔티티(`&lt;`, `&gt;`, `&amp;`, `&quot;`)로 변환
- **구조**: `<table><thead>...</thead><tbody>...</tbody></table>` + `<h3>Passages</h3><p>...</p>`
- **비고**: HTML 생성 전용 stdlib은 없으나, `html.escape()`로 XSS 등 안전성 확보. 구조 자체는 단순하여 직접 조합이 적절

### 6. LaTeX — `latex.py`

- **모듈**: 없음 (직접 문자열 조합 + 커스텀 이스케이프 함수)
- **방식**: `\begin{tabular}{lll...}` + `\hline` + `&` 구분자로 LaTeX 테이블 문법 직접 조합
- **이스케이프**: `_escape_latex()` 정적 메서드가 LaTeX 특수문자 10종 처리:
  - `\` → `\textbackslash{}`
  - `& % $ # _ { }` → `\&`, `\%`, `\$`, `\#`, `\_`, `\{`, `\}`
  - `~` → `\textasciitilde{}`, `^` → `\textasciicircum{}`
- **구조**: `\begin{table}\begin{tabular}...\end{tabular}\end{table}` + `\paragraph{Passages}\textbf{name}: text`
- **비고**: LaTeX 생성 전용 Python stdlib 없음. 출력은 LaTeX 문법이지만 컴파일 대상이 아닌 LLM 입력용 텍스트

### 7. CSV — `csv_format.py`

- **모듈**: `csv` (Python 표준 라이브러리)
- **방식**: `csv.writer(output, delimiter=',', quoting=csv.QUOTE_ALL)`
- **이스케이프**: `csv.writer`가 RFC 4180에 따라 모든 셀을 쌍따옴표로 감쌈. 셀 내부의 `"` → `""` 자동 이스케이프
- **구조**: 타이틀, 헤더, 데이터 행, 빈 행, "Passages" 라벨 행, 패시지 행 — 전부 동일 컬럼 수의 CSV 행
- **비고**: 패시지도 CSV 행으로 출력 (첫 번째 셀에 텍스트, 나머지 빈 셀). 전체 출력이 `csv.reader`로 파싱 가능

---

## Design Principles

1. **stdlib 우선**: Python 표준 라이브러리에 공식 모듈이 있으면 그것을 사용 (json, csv, xml.etree, html.escape)
2. **de facto 표준 허용**: YAML처럼 stdlib에 없지만 사실상 표준인 패키지(`pyyaml`)는 사용
3. **이스케이프 필수**: 각 포맷의 특수문자를 해당 포맷 규격에 맞게 이스케이프하여 구조 손상 방지
4. **직접 조합은 최후 수단**: Markdown, LaTeX처럼 생성 전용 표준 모듈이 없는 경우에만 문자열 직접 조합
