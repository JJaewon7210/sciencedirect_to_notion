## 개요 ✨

이 저장소는 다음과 같은 순서의 파이프라인을 통해 작동합니다:

1. **ScienceDirect**에서 연세대학교 도서관을 통해 **논문 내용**을 수집 .
2. **Gemini**를 사용해 **구조화된 요약** 생성 .
3. **Notion**에 해당 요약을 **포맷된 페이지**로 업로드 .

모든 설정값과 자격 정보는 `config.yaml` 파일에 저장되어 있습니다. ⚙️

![image](https://github.com/user-attachments/assets/cd107334-cbdd-4295-ab9b-79599716a972)
![image](https://github.com/user-attachments/assets/07e2eef1-d6ac-4df8-a9c7-d73a3a84b895)


---

## 디렉터리 구조 

```
.
├── config.yaml             # Configuration file ⚙️
├── data/
│   ├── scrap/              # Raw article data 
│   └── summary/            # Processed summaries 
└── script/
    ├── scrap.py            # Scraping module ️
    ├── gemini.py           # AI analysis module 
    ├── prompt.py           # Prompt engineering 
    └── notion.py           # Notion integration ️
```

- **`script/scrap.py`** ️
    - `elsapy`를 이용해 Elsevier Scopus 검색 결과를 받아오고, Selenium을 통해 연세대 도서관에 로그인 후 ScienceDirect에 접속해 논문을 수집합니다. ️
    - 수집한 내용은 `.txt` 파일로 저장됩니다. 

- **`script/gemini.py`** 
    - 수집 결과(`.txt` 파일)를 읽어 `prompt.py`에서 정의한 템플릿에 따라 **Gemini**에 요약을 요청합니다. 
    - 가져온 요약 결과를 **JSON 형식**으로 저장합니다. ️

- **`script/prompt.py`** 
    - 어떤 내용을 추출하고 구조화할지 정의한 프롬프트 텍스트와 응답 스키마를 담고 있습니다. 

- **`script/notion.py`** ️
    - Gemini로부터 생성된 **JSON 요약**을 읽어 Notion Database에 페이지로 추가합니다. ➕
    - 새 데이터베이스를 생성하거나, 기존 데이터베이스를 사용해 페이지를 업로드할 수 있습니다. ✅

---

## 요구 사항 ✅

1. **Python 3.9+** 
2. **필수 라이브러리** (예: `pip install <패키지명>`):
    - `selenium`
    - `beautifulsoup4`
    - `pyyaml`
    - `elsapy`
    - `google-generativeai`
    - `notion-client`

Chrome 브라우저를 사용하며, 다른 브라우저를 사용할 경우 코드 일부 수정이 필요할 수 있습니다. 

---

## 설정 (`config.yaml`) ⚙️

`config.yaml` 파일에는 사용자별 자격 정보와 검색 조건, 경로가 정의되어 있습니다. 주요 항목은 아래와 같습니다:

- ⚠️ 현재 ScienceDirect에 등재된 저널에만 작동하도록 처리하였습니다. 
- ⚠️ **elsevier_query**에서 꼭 cienceDirect에 등재된 저널만 포함되도록 SRCTITLE을 설정해주세요!

```yaml
yonsei_username: # 연세대 포탈 계정 🆔
yonsei_password: # 연세대 포탈 비밀번호 

elsevier_apikey: # Elsevier API 키 ️
elsevier_query: > # Scopus 고급 검색 쿼리 
  TITLE-ABS-KEY("digital twin" AND ...)
  ...

chrome_user_agent: # Chrome User-Agent 문자열 
scrap_output_folder: data/scrap/... 

gemini_apikey: # Google Generative AI API 키 ️
gemini_model: gemini-2.0-flash-exp
gemini_output_folder: data/summary/... 

notion_api_token: # Notion 통합 토큰 
parent_page_id: # 새 데이터베이스 생성 시 부모 페이지의 ID 🆔
database_id: "" # 기존 DB 사용 시 ID 기입, 없으면 자동 생성 ️
new_database_title: "250121 디지털 트윈" # 새 DB 생성 시 제목 ️
```

- ⚠️ 최초 실행 시에는 `database_id`를 ""으로 설정해주세요!
- `database_id`가 비어 있으면 `parent_page_id` 아래에 새 데이터베이스가 생성됩니다. ➕
- 이미 Notion 데이터베이스가 있다면 해당 ID를 넣고 사용합니다. ️

---

## 사용 방법 

1. **개발 환경 설정** 
    - 가상환경을 만들고(예: `python -m venv venv`) 활성화하십시오. ⚙️
    - 필요한 라이브러리를 설치합니다. 

2. **`config.yaml` 수정** ✏️
    - 연세대 포탈 계정, Elsevier API 키, Google Generative AI 키, Notion 토큰 등을 실제 값으로 기입합니다. 
    - 수집 결과 폴더(`scrap_output_folder`), 요약 결과 폴더(`gemini_output_folder`) 등을 원하는 경로로 설정합니다. 

3. **`prompt.py` 수정** 
    - Gemini를 이용해서 어떤 정보를 추출할지 prompt를 작성합니다. 

4. **수집(`scrap.py`) 실행** ️

    ```bash
    python script/scrap.py
    ```

    - 연세대 도서관 로그인 후 Scopus 검색 결과를 바탕으로 ScienceDirect에서 논문 HTML을 가져옵니다. ️
    - 가져온 내용을 `.txt`로 저장합니다. 

5. **수집 결과 확인** 
    - 몇몇 논문들은 수집이 불완전하게 될 수 있습니다. ⚠️
    - 크기 순으로 파일을 정렬한 다음 직접 내용을 붙여넣을 수 있습니다. ✂️

6. **요약(`gemini.py`) 실행** 

    ```bash
    python script/gemini.py
    ```

    - 수집된 `.txt`를 읽어, Gemini 모델에 요약을 요청하고, 구조화된 JSON 형태로 결과를 저장합니다. ️

7. **Notion 업로드(`notion.py`) 실행** ️

    ```bash
    python script/notion.py
    ```

    - Gemini가 생성한 JSON 요약 파일을 읽어 Notion Database에 페이지로 업로드합니다. 
    - `database_id`가 비어 있으면 `parent_page_id` 페이지 아래 새 DB를 생성하고 업로드하며, DB ID가 있는 경우 해당 DB에 업로드합니다. ➕️

---

## 팁 

- **속도 제한**: ⏳
    - `scrap.py` 실행 시, html을 로드하는 시간을 준수하기 위해 약 7초 간격으로 각 논문의 정보를 수집합니다.
    - `gemini.py`는 API 호출에 대한 속도 제한을 고려해 구현되어 있습니다. 
    - 대량의 파일을 처리 시, 적절히 대기 시간을 조정하십시오. ⏱️
