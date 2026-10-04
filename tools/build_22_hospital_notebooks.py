"""Build hospital-facing, independently executable API exercises."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'colab/hospitals/hospitals_22_20260930.json'


def cell(kind, text, *, form=False, tag=None):
    item = {'cell_type':kind, 'metadata':{}, 'source':text.strip().splitlines(keepends=True)}
    if kind == 'code':
        item.update(execution_count=None, outputs=[])
    if form:
        item['metadata']['cellView']='form'
    if tag:
        item['metadata']['test_id']=tag
    return item


def colab_url(slug):
    return f'https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/{slug}_smartcoder_api.ipynb'


def build():
    hospitals=json.loads(REGISTRY.read_text())
    client=(ROOT/'tools/colab_client.py').read_text()
    table=['| # | 醫院／院別代碼 | 分區 | 最新逐項重測 | 執行位置 | Colab 測試手冊 |','|---|---|---|---|---|---|']
    for number,h in enumerate(hospitals,1):
        slug=h['slug'];base=h['base_url'];features=h['interface'];stream=features['stream_supported']
        cells=[]
        def md(s): cells.append(cell('markdown',s))
        def code(s,tag=None,form=False): cells.append(cell('code',s,tag=tag,form=form))
        md(f'''# {h['name']}\n## SmartCoder API 介接與逐項測試

**院別：`{slug}`　｜　API 根網址：`{base}`**

本手冊供院方資訊室與 HIS 介接工程師使用。每項 API 都有參數、可執行範例、預期狀態碼及回應說明；按該區塊左側 **▶** 即可測試。

### 開始使用

1. 選擇 Python 3／CPU 執行階段，不需要 GPU。先執行「0. 初始化」與「金鑰設定」。
2. 依目錄逐項測試。編碼 POST 會產生 `request_id`；GET 用同一 ID 回查。也可選「執行階段 → 全部執行」。
3. 金鑰由計畫窗口透過私有管道提供，輸入時隱藏。不要把金鑰寫進程式、網址或儲存的輸出。
4. 預設案例是合成文字：`患者胸痛持續兩週，否認咳嗽。`。可調整參數測試其他合成案例；本公開 Colab 請勿輸入真實病歷或個資。

### API 功能索引

| 區塊 | 方法與路徑 | 用途 | 成功／預期 HTTP | 金鑰 |
|---|---|---|---|---|
| 1 | `GET /healthz` | 確認服務可連線 | 200 | 不需要 |
| 2 | `GET /openapi.json` | 查詢本院介面 schema | {'200' if features['openapi_available'] else '404（此院未公開此路徑）'} | 需要 |
| 3 | `POST /api/v1/snomed/coding` | 原始文字 → 整理 → SNOMED CT 編碼 | {'200；帶 ICD 時先回 202' if slug == 'yuanrung' else '200'} | 需要 |
| 4 | `GET /api/v1/snomed/results/{{request_id}}` | 以同一 ID 取得完整結果 | 200 | 需要 |
| 5 | 同一 POST，`output_format="fhir"` | 查看 FHIR 格式內容 | 200 | 需要 |
''' + ('''| 6 | 同一 POST，`stream=true` | 逐行讀取 NDJSON 進度與最終結果 | 200 | 需要 |
''' if stream else '') + '''| 錯誤測試 | POST／GET | 無金鑰、錯誤金鑰、查無 ID、參數錯誤 | 401／404／422 | 依案例 |
| CORS | POST／GET 的 `OPTIONS` | 檢查 Colab Origin 預檢 | 200 或 204 | 不需要 |

以下使用本院唯一根網址。`X-API-Key` 放在 header；不需要呼叫端另加 `X-Hospital-Slug`。管理頁面、稽核資料列表及服務內部回呼不屬於院方編碼介接功能，因此本手冊不呼叫這些路徑。
''')
        md('''## 0. 初始化

執行一次，載入連線與結果檢查工具。此區塊不送 API 請求；每項請求都寫在後續對應區塊中。重新執行初始化會清除本次記憶體內的測試紀錄。''')
        code(f"#@title 初始化與測試工具（執行一次）\nHOSPITAL_SLUG = {slug!r}\nBASE_URL = {base!r}\nREQUEST_FIELDS = {features['request_fields']!r}\nOPENAPI_AVAILABLE = {features['openapi_available']!r}\nSTREAM_SUPPORTED = {stream!r}\n"+client+"\nprint('已準備本院 API：', BASE_URL)\n",'setup',True)
        md('''### 金鑰設定

執行後貼上本院 API key。金鑰只保存在目前執行階段記憶體中；結束時可執行最後的清除區塊。''')
        code("API_KEY = getpass(f'請輸入 {HOSPITAL_SLUG} 的 API key（隱藏輸入）：').strip()\nrequire(bool(API_KEY), '尚未輸入金鑰')\nprint('本院金鑰已設定；內容不顯示。')",'authorize')
        md('''## 1. GET／健康檢查

**路徑：`/healthz`　｜　參數：無　｜　金鑰：不需要　｜　預期：HTTP 200**

`status="ok"` 表示 API 程序能回應；此檢查不會執行編碼。`service` 與 `version` 是服務識別及版本。''')
        code('''name = "健康檢查"
with test_case(name):
    health = request("GET", "/healthz", authenticated=False)
    checked(health, 200, name, check_cors=False)
    health_body = health.json()
    require(isinstance(health_body, dict) and health_body["status"] == "ok", "健康狀態不符")
    show_json(health)
''','health')
        md(f'''## 2. GET／查詢介面定義

**路徑：`/openapi.json`　｜　參數：無　｜　金鑰：需要**

{'此院已開放 OpenAPI。下方列出院方編碼功能與請求欄位，方便對照 Swagger 的 schema。' if features['openapi_available'] else '此院正式入口未開放 OpenAPI 路徑，預期回傳 404；這項測試確認目前公開範圍。請依本手冊的欄位表介接，404 不代表編碼功能故障。'}
''')
        code(f'''name = "OpenAPI 公開範圍"
with test_case(name):
    schema_response = request("GET", "/openapi.json")
    checked(schema_response, {200 if features['openapi_available'] else 404}, name, check_cors=False)
''' + ('''    schema = schema_response.json()
    for path, method in [("/healthz", "get"), ("/api/v1/snomed/coding", "post"), ("/api/v1/snomed/results/{request_id}", "get")]:
        require(method in schema["paths"][path], "OpenAPI 缺少院方介接功能")
    request_schema = schema["components"]["schemas"]["CodingRequest"]
    require(set(request_schema["properties"]) == set(REQUEST_FIELDS), "本院請求欄位已變動，請更新手冊")
    display(JSON({"request_fields": request_schema["properties"], "response_fields": schema["components"]["schemas"]["CodingResponse"]["properties"]}, expanded=True))
''' if features['openapi_available'] else '''    show_error(schema_response)
'''),'schema')
        md('''## 3. POST／病歷文字編碼

**路徑：`/api/v1/snomed/coding`　｜　金鑰：需要　｜　預期：HTTP 200、JSON**

### 請求參數

| 欄位 | 型別 | 本手冊預設／用途 |
|---|---|---|
| `request_id` | string | 每次 POST 產生新的 UUID，供 GET 回查 |
| `raw_clinical_note` | string | 原始合成病歷文字，不可空白 |
| `output_format` | string | `simple` 回傳編碼 JSON；`fhir` 額外回傳 `fhir_bundle` |
| `language` | string，可省略 | 輸入語言的紀錄資訊，例如 `zh-TW` |
| `encounter_type` | string，可省略 | 就醫類型紀錄資訊 |
| `department` | string，可省略或 null | 科別保留欄位，目前不影響編碼 |
| `threshold` | number，可省略或 null | 數值保留欄位，目前不影響信心值或篩選 |
| `SOAP` | string，可省略 | 區段標記，例如 `S`；不是病歷本文 |
| `tui` | array[string]，可省略 | 限定語意類型，例如 `["T184"]`；表單用逗號分隔 |
| `icd_codes` | array[object]，可省略 | 額外 ICD 證據；每項至少有 `code`，可加 `system`、`description` |

空白的選填欄位不會送出。預設只送 `request_id`、`raw_clinical_note`、`output_format`。`department` 可填科別文字；`threshold` 表單可填數值，例如 `0.5`，送出時轉為 JSON number。這兩個保留欄位目前不參與編碼、投票或篩選。`icd_codes` 表單接受 JSON array；例如 `[{"code":"R07.9","system":"http://hl7.org/fhir/sid/icd-10-cm"}]`，需要本院已配置對應表。

### 回應欄位

| 欄位 | 內容與判讀 |
|---|---|
| `request_id` | 必須等於本次送出的 ID |
| `polished_clinical_note` | 整理後文字 |
| `snomed_codings` | 編碼 array；每項有 `concept_id`、`term`、`confidence`、`source` |
| `concept_id`／`term` | SNOMED CT 概念碼與名稱 |
| `confidence` | 投票支持度；不能當成臨床準確率 |
| `source` | 原始文字編碼為 `["TXT_NER"]`；加 ICD 證據時可能包含其來源 |
| `processing_metadata` | 流程與術語版本、投票輪數、時間；顯示時遮蔽內部模型識別值 |
| `allowed_tui` | 有指定 TUI 時，回傳採用的篩選值 |

預設病例會檢查已知胸痛概念 `29857009`、否認咳嗽未產生陽性編碼、3 輪 NER metadata 及完整欄位。修改病例、TUI 或 ICD 證據後，程式檢查回應結構及 POST／GET 一致性；其他病例的編碼正確性須另由專業人員覆核。
'''+('本院另支援 `stream`；請使用第 6 節的串流測試。' if stream else '本院未支援 `stream` 欄位；請勿加入請求 body。'))
        code('''#@title POST／編碼參數與執行
raw_clinical_note = "患者胸痛持續兩週，否認咳嗽。" #@param {type:"string"}
output_format = "simple" #@param ["simple", "fhir"]
language = "" #@param {type:"string"}
encounter_type = "" #@param {type:"string"}
department = "" #@param {type:"string"}
threshold = "" #@param {type:"string"}
SOAP = "" #@param {type:"string"}
tui_csv = "" #@param {type:"string"}
icd_codes_json = "" #@param {type:"string"}
name = "POST 編碼"
with test_case(name):
    require(bool(raw_clinical_note.strip()), "合成病歷不可空白")
    request_id = str(uuid4())
    coding_body = {"request_id": request_id, "raw_clinical_note": raw_clinical_note, "output_format": output_format}
    for field, value in [("language", language), ("encounter_type", encounter_type), ("SOAP", SOAP), ("department", department)]:
        if value.strip():
            coding_body[field] = value.strip()
    if tui_csv.strip():
        coding_body["tui"] = [v.strip() for v in tui_csv.split(",") if v.strip()]
    if threshold.strip():
        try:
            coding_body["threshold"] = float(threshold)
        except ValueError:
            raise RuntimeError("threshold 請填數值，例如 0.5；留白表示不送出") from None
    if icd_codes_json.strip():
        coding_body["icd_codes"] = json.loads(icd_codes_json)
        require(isinstance(coding_body["icd_codes"], list), "icd_codes 必須是 JSON array")
    require(set(coding_body) <= set(REQUEST_FIELDS), "請求包含本院不支援的欄位")
    coding_response = request("POST", "/api/v1/snomed/coding", body=coding_body)
    POST_RESULT = completed_coding_response(coding_response, request_id, coding_body, name)
    result_contract(POST_RESULT, request_id, coding_body)
    remember(coding_body, POST_RESULT)
    LAST_REQUEST_ID = request_id
    display(JSON(public_view(POST_RESULT), expanded=True))
    print("回查用 request_id：", LAST_REQUEST_ID)
''','coding',True)
        md('''## 4. GET／回查編碼結果

**路徑：`/api/v1/snomed/results/{request_id}`　｜　金鑰：需要　｜　預期：HTTP 200**

表單留白會使用上一個 POST 的 ID；也可以填入本院已完成的 ID。每次執行都會重新發送 GET。

| 欄位 | 用途 |
|---|---|
| `request_id` | 本次查詢的 ID |
| `status`／`status_code` | 已完成結果為 `completed`／`200`；其他狀態需依回傳內容處理 |
| `occurred_at` | 含時區的紀錄時間 |
| `duration_ms` | 伺服器記錄的處理時間，單位毫秒 |
| `response` | 與 POST 相同的完整編碼結果 |
| `error_detail` | 成功時為 `null` |

查詢本 notebook 送出的 ID 時，會比對 POST 與 GET 完整 JSON 一致；查詢其他 ID 時，會檢查已完成結果的欄位，無法比對先前 POST。''')
        code('''#@title GET／回查參數與執行
lookup_request_id = "" #@param {type:"string"}
name = "GET 結果回查"
with test_case(name):
    selected_id = lookup_request_id.strip() or globals().get("LAST_REQUEST_ID")
    require(bool(selected_id), "請先完成 POST 編碼，或填入已有的 request_id")
    require(str(UUID(selected_id)) == selected_id, "request_id 必須是 UUID")
    GET_RESULT = lookup_completed(selected_id, name)
''','lookup',True)
        md('''## 5. POST／FHIR 輸出

**同一編碼路徑，設定 `output_format="fhir"`。** 此區塊可單獨執行，不需先執行第 3 節。

使用新的 ID 與相同合成病例，檢查 `fhir_bundle.entry` 的 `Composition` 與 `Observation`，再以 GET 確認保存結果。`Observation.code.coding` 的 `system` 為 `http://snomed.info/sct`，`code`、`display` 必須與 SNOMED 編碼一致。

目前 `fhir_bundle` 是含 `entry` 的 API 包裝物件，沒有頂層 `resourceType="Bundle"`、`type`、病人或就醫資料；直接寫入院方 FHIR Server 前，需要依院方資源規格組裝。''')
        code('''name = "FHIR 輸出與回查"
with test_case(name):
    fhir_id = str(uuid4())
    fhir_body = {"request_id": fhir_id, "raw_clinical_note": RAW_NOTE, "output_format": "fhir"}
    fhir_response = request("POST", "/api/v1/snomed/coding", body=fhir_body)
    checked(fhir_response, 200, name)
    FHIR_RESULT = fhir_response.json()
    result_contract(FHIR_RESULT, fhir_id, fhir_body)
    remember(fhir_body, FHIR_RESULT)
    show_json(fhir_response)
    FHIR_GET_RESULT = lookup_completed(fhir_id, name)
''','fhir')
        if slug == 'yuanrung':
            md('''## 5a. POST／ICD-10 對照與結果回查

員榮已提供 ICD-10-CM 對照。此測項同時送出合成文字與 `icd_codes=[{"system":"ICD-10-CM","code":"E11.9"}]`，確認預期 SNOMED `44054006` 與完整文字分析。院方仍使用 `code`／`system` 欄位。

**HTTP 202 是初步結果**：程式會使用同一 `request_id` 回查，等待 `completed` 後才判定通過。對照項目沒有模型投票支持度時，`confidence` 可能為空或省略；不要填入推估分數。這項已知對照不代表所有 ICD 均有結果，也不代表 OMOP CDM 匯出。
''')
            code('''name = "ICD-10 對照與結果回查"
with test_case(name):
    icd_id = str(uuid4())
    icd_body = {"request_id": icd_id, "raw_clinical_note": RAW_NOTE, "output_format": "simple",
                "icd_codes": [{"system": "ICD-10-CM", "code": "E11.9"}]}
    icd_response = request("POST", "/api/v1/snomed/coding", body=icd_body)
    ICD_RESULT = completed_coding_response(icd_response, icd_id, icd_body, name)
    result_contract(ICD_RESULT, icd_id, icd_body)
    require(any(row["concept_id"] == "44054006" and row["source"] != ["TXT_NER"] for row in ICD_RESULT["snomed_codings"]), "未取得 E11.9 的預期 SNOMED 對照來源")
    remember(icd_body, ICD_RESULT)
    display(JSON(public_view(ICD_RESULT), expanded=True))
    ICD_GET_RESULT = lookup_completed(icd_id, name)
''','icd_mapping')
        if stream:
            md('''## 6. POST／串流進度與最終結果

**同一編碼路徑，設定 `stream=true`、`output_format="simple"`。** 此區塊可單獨執行。

HTTP 200 的內容為 `application/x-ndjson`，每一行是一個 JSON 事件。程式逐行列出事件種類、順序與時間；只在 `pipeline.completed` 收到最終結果後判定成功。`coding.provisional` 是暫定結果，不能先視為最終編碼。串流內的 `pipeline.error` 仍表示失敗，即使 HTTP 已是 200。

最後以 GET 比對保存的完整結果。''')
            code('''name = "串流與最終結果回查"
with test_case(name):
    require(STREAM_SUPPORTED, "本院未支援串流")
    stream_id = str(uuid4())
    stream_body = {"request_id": stream_id, "raw_clinical_note": RAW_NOTE, "output_format": "simple", "stream": True}
    stream_response = request("POST", "/api/v1/snomed/coding", body=stream_body, stream=True)
    checked(stream_response, 200, name)
    require(stream_response.headers["Content-Type"].split(";")[0] == "application/x-ndjson", "Content-Type 不是 NDJSON")
    STREAM_RESULT = None
    sequence = 0
    with stream_response:
        for line in stream_response.iter_lines():
            if not line:
                continue
            event = json.loads(line)
            require(event["request_id"] == stream_id, "事件 request_id 不符")
            require(type(event["seq"]) is int and event["seq"] == sequence + 1, "事件順序不符")
            sequence = event["seq"]
            require(type(event["elapsed_ms"]) is int and event["elapsed_ms"] >= 0, "事件時間不符")
            require(event["type"] != "pipeline.error", "串流回報處理失敗")
            print({"seq": sequence, "type": event["type"], "elapsed_ms": event["elapsed_ms"]})
            if event["type"] == "pipeline.completed":
                require(STREAM_RESULT is None, "重複最終結果事件")
                STREAM_RESULT = event["result"]
    require(STREAM_RESULT is not None, "串流缺少最終結果")
    result_contract(STREAM_RESULT, stream_id, stream_body)
    remember(stream_body, STREAM_RESULT)
    display(JSON(public_view(STREAM_RESULT), expanded=True))
    STREAM_GET_RESULT = lookup_completed(stream_id, name)
''','stream')
        md('''## 錯誤處理／逐項測試

以下故意發送無效請求。**顯示預期的 401、404、422 才是該測試通過**，不會執行有效病例編碼。

| HTTP | HIS 端處理方式 |
|---|---|
| 401 | 核對本院金鑰與 `X-API-Key`；不要自動改用其他院別 |
| 404 | 核對院別根網址及 `request_id`；未開放的路徑也會回 404 |
| 422 | 修正欄位名稱、型別或列舉值後再送出 |
| 502／503／504 | 記錄 HTTP、request_id、時間並提供給計畫維運窗口；本手冊不把這些狀態判為通過 |

實際錯誤的 `detail` 可能含服務內部資訊；此手冊僅顯示狀態及驗證欄位，不轉印內部來源。''')
        for tag,name,method,path,body,kwargs,description in [
            ('no_key_post','POST 無金鑰','POST','/api/v1/snomed/coding','{"request_id": str(uuid4()), "raw_clinical_note": RAW_NOTE, "output_format": "simple"}','authenticated=False','省略 X-API-Key，預期 HTTP 401。'),
            ('no_key_get','GET 無金鑰','GET','/api/v1/snomed/results/" + str(uuid4()) + "',None,'authenticated=False','省略 X-API-Key，預期 HTTP 401。'),
            ('invalid_key','錯誤金鑰','GET','/api/v1/snomed/results/" + str(uuid4()) + "',None,'authenticated=False, headers={"X-API-Key": "invalid-test-token", "Origin": COLAB_ORIGIN}','使用明確無效的測試字串，預期 HTTP 401。'),
            ('missing_result','查無 request_id','GET','/api/v1/snomed/results/" + str(uuid4()) + "',None,'','使用本院有效金鑰與新的隨機 UUID，預期 HTTP 404。'),
            ('unknown_field','額外欄位相容','POST','/api/v1/snomed/coding','{"request_id": str(uuid4()), "raw_clinical_note": RAW_NOTE, "output_format": "simple", "unknown_field": True}','','額外欄位會被忽略，不改變編碼流程；有效病歷仍回 HTTP 200。'),
            ('invalid_format','錯誤 output_format','POST','/api/v1/snomed/coding','{"request_id": str(uuid4()), "raw_clinical_note": RAW_NOTE, "output_format": "invalid"}','','設定無效列舉值，預期 HTTP 422。')]:
            status=404 if tag=='missing_result' else (422 if tag=='invalid_format' else (200 if tag=='unknown_field' else 401))
            md('### '+name+'\n\n'+description)
            args=(f', body={body}' if body else '') + (', '+kwargs if kwargs else '')
            if tag=='unknown_field':
                code(f'''name = {name!r}
with test_case(name):
    compatibility_body = {body}
    compatibility_response = request({method!r}, "{path}", body=compatibility_body)
    checked(compatibility_response, 200, name)
    result_contract(compatibility_response.json(), compatibility_body["request_id"], compatibility_body)
    show_json(compatibility_response)
''',tag)
                continue
            code(f'''name = {name!r}
with test_case(name):
    error_response = request({method!r}, "{path}"{args})
    checked(error_response, {status}, name)
    show_error(error_response)
''',tag)
        md('''## CORS／瀏覽器預檢

`OPTIONS` 不帶金鑰，檢查是否允許 Colab Origin、對應方法與 `content-type,x-api-key`。前面的成功 POST／GET 和錯誤回應也會檢查 `Access-Control-Allow-Origin`。

Python `requests` 本身不受瀏覽器 CORS 限制。以下通過代表已檢查 **`https://colab.research.google.com`** 的 headers；院方自己的網頁 Origin 仍需另行驗證。''')
        for method,path,tag in [('POST','"/api/v1/snomed/coding"','cors_post'),('GET','"/api/v1/snomed/results/" + str(uuid4())','cors_get')]:
            md(f'### {method} 預檢')
            code(f'name = "{method} CORS 預檢"\nwith test_case(name):\n    preflight({path}, "{method}", name)\n',tag)
        md('''## 本次測試總表

只列出**這次執行階段實際跑過**的結果。尚未執行不會算通過。可依表格找出需要重跑的區塊。這些是 API 可用性、格式及合成病例檢查，不等於臨床準確率或院方整合驗收。''')
        tags=[c['metadata']['test_id'] for c in cells if c['cell_type']=='code' and c['metadata']['test_id'] not in ['setup','authorize']]
        code('''EXPECTED_TEST_NAMES = '''+repr(['健康檢查','OpenAPI 公開範圍','POST 編碼','GET 結果回查','FHIR 輸出與回查']+(['串流與最終結果回查'] if stream else [])+['POST 無金鑰','GET 無金鑰','錯誤金鑰','查無 request_id','不支援的欄位','錯誤 output_format','POST CORS 預檢','GET CORS 預檢'])+'''
rows = [TESTS[name] if name in TESTS else {"項目": name, "結果": "未執行", "HTTP": "", "秒數": ""} for name in EXPECTED_TEST_NAMES]
show_table(rows)
passed = sum(row["結果"] == "通過" for row in rows)
print(f"本次 {passed}/{len(rows)} 項通過。")
''','summary')
        md(f'''## HIS 呼叫範例

正式 POST URL：`{base}/api/v1/snomed/coding`。請在院方程式中配置本院金鑰，不要將它寫入原始碼。

```python
import os, uuid, requests
base_url = "{base}"
headers = {{"X-API-Key": os.environ["SMARTCODER_API_KEY"]}}
body = {{"request_id": str(uuid.uuid4()), "raw_clinical_note": "患者胸痛持續兩週，否認咳嗽。", "output_format": "simple"}}
r = requests.post(base_url + "/api/v1/snomed/coding", headers=headers, json=body, timeout=240)
r.raise_for_status()
result = r.json()
saved = requests.get(base_url + "/api/v1/snomed/results/" + result["request_id"], headers=headers, timeout=60)
saved.raise_for_status()
```

此範例供院內程式配置使用；Colab 的金鑰取得方式仍是前面的隱藏輸入。若在瀏覽器前端呼叫，請先確認院方 Origin 已被允許，並避免把院級金鑰散發到公開前端。

### 使用完畢／清除金鑰

清除目前記憶體中的連線、金鑰與 API 結果。分享 notebook 前，另選「編輯 → 清除所有輸出」，或以原始公開連結提供給其他人。''')
        code('''API_KEY = ""
COMPLETED.clear()
for variable_name in ["POST_RESULT", "GET_RESULT", "FHIR_RESULT", "FHIR_GET_RESULT", "STREAM_RESULT", "STREAM_GET_RESULT", "ICD_RESULT", "ICD_GET_RESULT", "LAST_REQUEST_ID", "coding_response", "icd_response", "fhir_response", "stream_response", "schema_response", "error_response", "event", "original", "payload"]:
    globals().pop(variable_name, None)
SESSION.close()
print("已移除金鑰變數並關閉連線。需要再測試時，請重跑初始化及金鑰設定。")
''','cleanup')
        for index,c in enumerate(cells):c['id']=f'{slug}-{index}'
        filename=slug+'_smartcoder_api.ipynb'
        notebook={'cells':cells,'metadata':{'colab':{'name':filename,'provenance':[],'toc_visible':True},'kernelspec':{'display_name':'Python 3','name':'python3'},'language_info':{'name':'python'}},'nbformat':4,'nbformat_minor':5}
        (ROOT/'colab/hospitals'/filename).write_text(json.dumps(notebook,ensure_ascii=False,indent=2)+'\n')
        if h.get('function_contract_passed') is True:
            tested = f'{h["function_checks"]}/{h["function_checks"]} 通過'
        elif h.get('function_contract_passed') is False:
            tested = f'{h["function_passed_checks"]}/{h["function_checks"]}；未通過'
        else:
            tested = '待驗證'
        execution_client = {'operator_mac_public_https':'Mac → 公開 HTTPS','formal_vm_public_https':'正式 VM → 公開 HTTPS'}.get(h.get('function_test_client'), '正式 VM → 公開 HTTPS')
        table.append(f'| {number} | {h["name"]} `{slug}` | {h["region"]} | {tested} | {execution_client} | [開啟]({colab_url(slug)}) |')
    readme='''# SmartCoder 22 院 API 介接與 Colab 測試手冊

供院方資訊室與 HIS 介接工程師使用。依院別開啟下表 Colab，先執行初始化與隱藏金鑰設定，再按各功能區塊的 ▶。也可選 Python 3／CPU →「執行階段 → 全部執行」。不需要 GPU。

每本手冊包含參數表、POST／GET 呼叫程式、實際 HTTP 狀態與 JSON 顯示、FHIR 輸出、401／404／422 錯誤測試、Colab Origin 的 CORS 預檢，以及本次逐項測試總表。中山醫與員榮另有 NDJSON 串流測試；其餘院別不提供未支援的 stream 開關。各院 API 根網址固定於自己的 notebook。

金鑰由計畫窗口以私有管道提供；公開 notebook 沒有內建金鑰，也沒有儲存任何執行輸出。預設使用合成病例，請勿在本公開 Colab 輸入真實病歷或個資。自訂病例可驗證 API 格式；其編碼正確性須由專業人員覆核。

## 最新重測狀態（2026-10-01）

### 新增保留參數

22 院的編碼 POST 已接受選填 `department`（string）與 `threshold`（number）；可省略或傳 null。兩者目前不參與編碼、投票或篩選。各院 Colab 第 3 節已加入表單；`threshold` 留白不送出，填入數值時轉為 JSON number。

22/22 院已由各自正式 VM→公開 HTTPS 驗證新欄位編碼、結果回查與 CORS；CSH 與員榮的新版 Colab 分別通過 14/14、15/15 項。此輪測試的來源是正式 VM。[新參數驗證紀錄](../../verification/reserved_parameters_20261001.json)。

北、南區從 Mac 取用已發布 notebook 的程式進行完整逐項重測，16 院中 9 院通過、7 院未通過；部分 POST 在約 60–62 秒後連線中斷。中區六院在正式 VM 重測通過，尚不能當成中區外部完整驗收。下表標示每院的實際執行位置與結果。

Mac 與 Google Colab 執行階段均完成 22/22 院的健康、預檢及無金鑰回應檢查；Google 帶金鑰完整編碼尚未執行。斷線原因仍在定位，目前不宣稱全部可供外部完整使用。詳見 [本次重測紀錄](../../verification/external_clients_22_20261001.json)。

## 院別連結

### 員榮 ICD 對照修復（2026-10-01）

員榮後端查詢參數已修正。新版手冊新增 ICD-10-CM E11.9 → SNOMED 44054006 測項，正式 VM→公開 HTTPS 15/15 項通過。帶 ICD 的 POST 先回 202，程式會回查到 completed；對照項目缺少模型 confidence 時，不填入推估分數。院方仍使用 icd_codes 內的 code／system。其他院別的 OMOP 接入不能由此推論；OMOP CDM 匯出不在此測項範圍。[員榮驗證紀錄](../../verification/yuanrung_icd_acceptance_20261001.json)。

先前外部未通過的七院，在各自正式 VM→公開 HTTPS 的後續重測共 91/91 項通過。外部 Mac／Google 完整編碼的斷線仍未完成定位，下表保留原外部結果，沒有改標全部通過。

'''+'\n'.join(table)+'''

n＝北區、m＝中區、s＝南區。`hlm` 為花蓮慈濟、`cmmc` 為奇美、`cmuh` 為中國附醫、`cathay` 為國泰。

## 功能與驗證範圍

公開院方介接功能為 `GET /healthz`、`POST /api/v1/snomed/coding`、`GET /api/v1/snomed/results/{request_id}`。POST 的輸出格式為 `simple` 或 `fhir`。目前 fhir_bundle 是含 entry 的 API 包裝物件，不是可以直接寫入 FHIR Server 的完整 Bundle。

中山醫、員榮、林口長庚、臺中榮總已公開需金鑰的 `/openapi.json`；其餘院別此路徑預期 404。各手冊依實際配置檢查，404 不等於編碼功能故障。管理／稽核路徑及內部回呼不屬於此院方介接手冊。

預設合成病例檢查胸痛概念 29857009、否認咳嗽、整理後文字、3 輪 NER metadata、TXT_NER 來源、FHIR 對應及 POST／GET 完整 JSON 一致。CORS 驗證 Origin 為 https://colab.research.google.com；院方自己的 Origin 仍需另外驗證。測試通過不等於臨床準確率或院方整合驗收。

逐院介面配置與測試日期見 [院別登錄表](hospitals_22_20260930.json)。Notebook 自己的總表只代表當次實際執行結果。
'''
    readme=readme.replace('实际','實際')
    evidence=ROOT/'verification/functions_22_20261001.json'
    if evidence.exists():
        report=json.loads(evidence.read_text())
        readme += f'\n歷史批次紀錄：先前正式 VM 的逐項測試為 {report["passed"]}/{report["hospital_count"]} 院、共 {report["function_checks"]} 項通過。該紀錄保留實際日期與執行位置，已由上方最新重測更新目前狀態，不能替代目前的外部完整驗收，也不代表任意參數組合或臨床準確率已驗證。逐項 HTTP 與時間見 [歷史驗證紀錄](../../verification/functions_22_20261001.json)。\n'
    (ROOT/'colab/hospitals/README_22_HOSPITALS_20260930.md').write_text(readme)
    (ROOT/'README.md').write_text(readme.replace('(hospitals_22_20260930.json)','(colab/hospitals/hospitals_22_20260930.json)').replace('(../../verification/','(verification/'))
    print('Generated',len(hospitals),'hospital API manuals')


if __name__=='__main__':build()
