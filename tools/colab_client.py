"""Secret-free client embedded in each hospital notebook; no fallback routes."""
import json
import math
import time
from datetime import datetime
from getpass import getpass
from contextlib import contextmanager
from html import escape

try:
    from IPython.display import display, JSON, HTML
except ImportError:
    # The same request cells can also run in a plain Python verification process.
    def JSON(value, expanded=True):
        return json.dumps(value, ensure_ascii=False, indent=2)
    def HTML(value):
        return value
    def display(value):
        print(value)
from uuid import UUID, uuid4

import requests

COLAB_ORIGIN = "https://colab.research.google.com"
RAW_NOTE = "患者胸痛持續兩週，否認咳嗽。"
KNOWN_SNOMED_FIXTURE = {"29857009": "Chest pain"}
RESULT_FIELDS = {"request_id", "polished_clinical_note", "snomed_codings", "processing_metadata"}
CODING_FIELDS = {"concept_id", "term", "confidence", "source"}
METADATA_FIELDS = {"polish_model", "snomed_version", "pipeline_version", "vote_attempts", "confidence_method", "timestamp"}
GET_FIELDS = {"request_id", "status", "status_code", "occurred_at", "duration_ms", "response", "error_detail"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def timestamp(value, field):
    require(isinstance(value, str) and bool(value.strip()), f"{field} 必須是時間字串")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(parsed.tzinfo is not None and parsed.utcoffset() is not None, f"{field} 缺少時區")


def cors(response):
    actual = response.headers["Access-Control-Allow-Origin"]
    require(actual in (COLAB_ORIGIN, "*"), "回應未允許 Colab Origin")


def http(response, expected_status, expected_url, label):
    # Do not print error bodies: they may contain internal service details.
    acceptable = (expected_status,) if isinstance(expected_status, int) else expected_status
    require(response.status_code in acceptable,
            f"{label} HTTP {response.status_code}；預期 {expected_status}，已停止")
    require(response.url == expected_url and not response.history, f"{label} 不接受網址轉向")


def result_contract(payload, request_id, body=None):
    known_body = body is not None
    fixture = known_body and body["raw_clinical_note"] == RAW_NOTE and not body.get("tui") and not body.get("icd_codes")
    allowed_fields = RESULT_FIELDS | {"allowed_tui", "fhir_bundle"}
    require(isinstance(payload, dict) and RESULT_FIELDS <= set(payload) <= allowed_fields, "POST 結果欄位不符合契約")
    require(isinstance(payload["request_id"], str) and payload["request_id"] == request_id, "request_id 不一致")
    polished = payload["polished_clinical_note"]
    require(isinstance(polished, str) and bool(polished.strip()), "整理後病歷為空或型別不符")
    if fixture:
        require(" ".join(polished.split()).casefold() != " ".join(body["raw_clinical_note"].split()).casefold(), "未觀察到病歷整理")
    codings = payload["snomed_codings"]
    require(isinstance(codings, list) and (bool(codings) or not fixture), "編碼結果為空或型別不符")
    seen = set()
    for item in codings:
        require(isinstance(item, dict), "編碼項目必須是 object")
        require(CODING_FIELDS <= set(item) <= CODING_FIELDS | {"category", "tui", "code_name"}, "編碼項目欄位不符合現行 OpenAPI")
        concept_id = item["concept_id"]
        require(isinstance(concept_id, str) and concept_id.isdigit(), "concept_id 必須是數字字串")
        require(concept_id not in seen, "concept_id 重複")
        # This single synthetic fixture has one positive clinical finding.
        # Membership is checked against its known SNOMED CT concept, not guessed from digits.
        require(not fixture or concept_id in KNOWN_SNOMED_FIXTURE, "回傳概念不在此合成測試的已知 SNOMED CT 集合")
        seen.add(concept_id)
        require(isinstance(item["term"], str) and bool(item["term"].strip()), "term 為空或型別不符")
        confidence = item["confidence"]
        if confidence is None:
            require("ICD10_CROSSWALK" in item["source"], "只有 ICD 對照項目可缺少投票支持度")
        else:
            require(type(confidence) in (int, float) and math.isfinite(confidence) and 0 < confidence <= 1, "confidence 型別或範圍錯誤")
        require(isinstance(item["source"], list) and bool(item["source"]), "source 必須是非空 array")
        require(all(isinstance(v, str) and bool(v) for v in item["source"]), "source 項目型別不符")
        if known_body and not body.get("icd_codes"):
            require(item["source"] == ["TXT_NER"], "編碼來源不符合 TXT_NER 契約")
        if "category" in item:
            require(item["category"] in ("finding", "disorder", "procedure"), "category 值不符")
        if "tui" in item:
            require(isinstance(item["tui"], str) and bool(item["tui"].strip()), "tui 型別或內容不符")
        if "code_name" in item:
            require(isinstance(item["code_name"], str) and bool(item["code_name"].strip()), "code_name 型別或內容不符")
    require(not fixture or seen == set(KNOWN_SNOMED_FIXTURE), "未辨識胸痛；否認咳嗽不得產生陽性編碼")
    metadata = payload["processing_metadata"]
    require(isinstance(metadata, dict) and set(metadata) == METADATA_FIELDS, "處理 metadata 欄位不符")
    require(isinstance(metadata["polish_model"], str) and bool(metadata["polish_model"].strip()), "病歷整理 metadata 缺少模型標記")
    require(metadata["snomed_version"] == "2026-07-01", "SNOMED CT 版本不符")
    require(metadata["pipeline_version"] == "api-version-0.1.0|txt_ner", "完整術語流程版本不符")
    require(type(metadata["vote_attempts"]) is int and metadata["vote_attempts"] == 3, "NER 投票輪數必須是 3")
    require(metadata["confidence_method"] == "txt_ner_assertion_filtered_vote_support_min_2", "投票信心度方法不符")
    timestamp(metadata["timestamp"], "processing_metadata.timestamp")
    if known_body and body.get("tui"):
        require(payload["allowed_tui"] == body["tui"], "allowed_tui 與請求不同")
    if (known_body and body["output_format"] == "fhir") or (not known_body and "fhir_bundle" in payload):
        fhir_contract(payload)
    else:
        require("fhir_bundle" not in payload, "simple 不應包含 fhir_bundle")
    return codings


def get_contract(payload, request_id, post_payload=None, body=None):
    require(isinstance(payload, dict) and set(payload) == GET_FIELDS, "GET 結果欄位不符")
    require(isinstance(payload["request_id"], str) and payload["request_id"] == request_id, "GET request_id 不符")
    require(payload["status"] == "completed", "任務尚未完成")
    require(type(payload["status_code"]) is int and payload["status_code"] == 200, "儲存的任務狀態碼不符")
    require(type(payload["duration_ms"]) is int and payload["duration_ms"] >= 0, "duration_ms 不符")
    timestamp(payload["occurred_at"], "occurred_at")
    require(payload["error_detail"] is None, "GET 結果包含錯誤")
    result_contract(payload["response"], request_id, body)
    if post_payload is not None:
        require(payload["response"] == post_payload, "GET 與 POST 完整結果不一致")


def fhir_contract(payload):
    bundle = payload["fhir_bundle"]
    require(isinstance(bundle, dict) and set(bundle) == {"entry"}, "fhir_bundle 結構不符")
    entries = bundle["entry"]
    require(isinstance(entries, list) and len(entries) == len(payload["snomed_codings"]) + 1, "FHIR entry 數量不符")
    composition = entries[0]["resource"]
    require(composition["resourceType"] == "Composition", "FHIR 首筆必須是 Composition")
    sections = composition["section"]
    require(isinstance(sections, list) and len(sections) == 1, "Composition section 不符")
    require(sections[0]["text"]["status"] == "generated", "Composition text.status 不符")
    require(isinstance(sections[0]["text"]["div"], str) and payload["polished_clinical_note"] in sections[0]["text"]["div"], "Composition 病歷內容不符")
    for entry, coding in zip(entries[1:], payload["snomed_codings"]):
        resource = entry["resource"]
        require(resource["resourceType"] == "Observation", "編碼 resource 必須是 Observation")
        fhir_coding = resource["code"]["coding"]
        require(isinstance(fhir_coding, list) and len(fhir_coding) == 1, "Observation coding 不符")
        require(fhir_coding[0] == {"system": "http://snomed.info/sct", "code": coding["concept_id"], "display": coding["term"]}, "FHIR 與 SNOMED 編碼不一致")


# Helpers only prepare requests, display results, and check response contracts.
# Every API operation is called explicitly in its own notebook cell below.
SESSION = requests.Session()
TESTS = {}
COMPLETED = {}


def show_table(rows):
    columns = ["項目", "結果", "HTTP", "秒數"]
    head = "".join("<th>" + escape(v) + "</th>" for v in columns)
    body = "".join("<tr>" + "".join("<td>" + escape(str(row[k])) + "</td>" for k in columns) + "</tr>" for row in rows)
    display(HTML("<table><thead><tr>" + head + "</tr></thead><tbody>" + body + "</tbody></table>"))


@contextmanager
def test_case(name):
    TESTS[name] = {"項目": name, "結果": "執行中", "HTTP": "", "秒數": ""}
    started = time.perf_counter()
    try:
        yield
    except Exception as exc:
        TESTS[name]["結果"] = "失敗"
        # Original server bodies and third-party exceptions are not printed.
        print(f"{name}：失敗；請核對 HTTP 狀態、參數與本院金鑰後重跑此項。")
        reason = str(exc) if type(exc) is ValueError else type(exc).__name__
        raise RuntimeError(f"{name} 未通過：{reason}") from None
    else:
        TESTS[name]["結果"] = "通過"
        print(name + "：通過")
    finally:
        TESTS[name]["秒數"] = round(time.perf_counter() - started, 2)
        print("本項耗時：", TESTS[name]["秒數"], "秒")


def auth_headers():
    require("API_KEY" in globals() and isinstance(API_KEY, str) and bool(API_KEY), "請先執行金鑰設定")
    return {"X-API-Key": API_KEY, "Content-Type": "application/json; charset=utf-8", "Origin": COLAB_ORIGIN}


def request(method, path, *, body=None, authenticated=True, headers=None, stream=False):
    require(path.startswith("/") and "://" not in path and ".." not in path, "請使用本院相對路徑")
    url = BASE_URL + path
    actual_headers = auth_headers() if authenticated else {"Origin": COLAB_ORIGIN}
    if headers is not None:
        actual_headers = headers
    print(f"{method} {url}")
    print("X-API-Key：已設定（隱藏）" if "X-API-Key" in actual_headers else "X-API-Key：未提供")
    if body is not None:
        display(JSON(body, expanded=True))
    return SESSION.request(method, url, headers=actual_headers, json=body,
                           timeout=(20, 240), allow_redirects=False, stream=stream)


def checked(response, expected, name, *, check_cors=True):
    print("HTTP", response.status_code)
    TESTS[name]["HTTP"] = response.status_code
    http(response, expected, response.request.url, name)
    if check_cors:
        cors(response)


def public_view(value):
    # The API field remains in memory for validation; the displayed identifier is masked.
    if isinstance(value, dict):
        return {k: ("external AI capacity" if k == "polish_model" else public_view(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [public_view(v) for v in value]
    return value


def show_json(response):
    display(JSON(public_view(response.json()), expanded=True))


def show_error(response):
    payload = response.json()
    require(isinstance(payload, dict) and "detail" in payload, "錯誤回應缺少 detail")
    if isinstance(payload["detail"], list):
        # Do not echo rejected input values.
        display(JSON({"detail": [{"loc": e["loc"], "type": e["type"]} for e in payload["detail"]]}, expanded=True))
    else:
        require(isinstance(payload["detail"], str) and bool(payload["detail"]), "detail 型別不符")
        print("detail：服務已拒絕此請求")


def preflight(path, method, name):
    response = request("OPTIONS", path, authenticated=False, headers={
        "Origin": COLAB_ORIGIN, "Access-Control-Request-Method": method,
        "Access-Control-Request-Headers": "content-type,x-api-key"})
    checked(response, (200, 204), name)
    methods = {v.strip().upper() for v in response.headers["Access-Control-Allow-Methods"].split(",")}
    allowed = {v.strip().lower() for v in response.headers["Access-Control-Allow-Headers"].split(",")}
    require(method in methods or "*" in methods, "CORS 未允許此方法")
    require({"content-type", "x-api-key"} <= allowed or "*" in allowed, "CORS 未允許必要 headers")
    display(JSON({k: response.headers[k] for k in ["Access-Control-Allow-Origin", "Access-Control-Allow-Methods", "Access-Control-Allow-Headers"]}, expanded=True))


def remember(body, payload):
    COMPLETED[body["request_id"]] = {"body": body, "response": payload}


def lookup_completed(request_id, name):
    response = request("GET", "/api/v1/snomed/results/" + request_id)
    checked(response, 200, name)
    payload = response.json()
    if request_id in COMPLETED:
        original = COMPLETED[request_id]
        get_contract(payload, request_id, original["response"], original["body"])
        print("GET 與本次 POST 完整 JSON 一致。")
    else:
        get_contract(payload, request_id)
        print("此 ID 未由本次 notebook 送出；已檢查回應欄位，未比對先前 POST。")
    show_json(response)
    return payload
