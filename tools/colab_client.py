"""Secret-free client embedded in each hospital notebook; no fallback routes."""
import json
import math
import time
from datetime import datetime
from getpass import getpass
from uuid import uuid4

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


def result_contract(payload, request_id):
    require(isinstance(payload, dict) and set(payload) == RESULT_FIELDS, "POST 結果欄位不符合契約")
    require(isinstance(payload["request_id"], str) and payload["request_id"] == request_id, "request_id 不一致")
    polished = payload["polished_clinical_note"]
    require(isinstance(polished, str) and bool(polished.strip()), "整理後病歷為空或型別不符")
    require(" ".join(polished.split()).casefold() != " ".join(RAW_NOTE.split()).casefold(), "未觀察到病歷整理")
    codings = payload["snomed_codings"]
    require(isinstance(codings, list) and bool(codings), "編碼結果為空或型別不符")
    seen = set()
    for item in codings:
        require(isinstance(item, dict), "編碼項目必須是 object")
        require(CODING_FIELDS <= set(item) <= CODING_FIELDS | {"category", "tui", "code_name"}, "編碼項目欄位不符合現行 OpenAPI")
        concept_id = item["concept_id"]
        require(isinstance(concept_id, str) and concept_id.isdigit(), "concept_id 必須是數字字串")
        require(concept_id not in seen, "concept_id 重複")
        # This single synthetic fixture has one positive clinical finding.
        # Membership is checked against its known SNOMED CT concept, not guessed from digits.
        require(concept_id in KNOWN_SNOMED_FIXTURE, "回傳概念不在此合成測試的已知 SNOMED CT 集合")
        seen.add(concept_id)
        require(isinstance(item["term"], str) and bool(item["term"].strip()), "term 為空或型別不符")
        confidence = item["confidence"]
        require(type(confidence) in (int, float) and math.isfinite(confidence) and 0 < confidence <= 1, "confidence 型別或範圍錯誤")
        require(item["source"] == ["TXT_NER"], "編碼來源不符合 TXT_NER 契約")
        if "category" in item:
            require(item["category"] in ("finding", "disorder", "procedure"), "category 值不符")
        if "tui" in item:
            require(isinstance(item["tui"], str) and bool(item["tui"].strip()), "tui 型別或內容不符")
        if "code_name" in item:
            require(isinstance(item["code_name"], str) and bool(item["code_name"].strip()), "code_name 型別或內容不符")
    require(seen == set(KNOWN_SNOMED_FIXTURE), "未辨識胸痛；否認咳嗽不得產生陽性編碼")
    metadata = payload["processing_metadata"]
    require(isinstance(metadata, dict) and set(metadata) == METADATA_FIELDS, "處理 metadata 欄位不符")
    require(isinstance(metadata["polish_model"], str) and bool(metadata["polish_model"].strip()), "病歷整理 metadata 缺少模型標記")
    require(metadata["snomed_version"] == "2026-07-01", "SNOMED CT 版本不符")
    require(metadata["pipeline_version"] == "api-version-0.1.0|txt_ner", "完整術語流程版本不符")
    require(type(metadata["vote_attempts"]) is int and metadata["vote_attempts"] == 3, "NER 投票輪數必須是 3")
    require(metadata["confidence_method"] == "txt_ner_assertion_filtered_vote_support_min_2", "投票信心度方法不符")
    timestamp(metadata["timestamp"], "processing_metadata.timestamp")
    return codings


def get_contract(payload, request_id, post_payload):
    require(isinstance(payload, dict) and set(payload) == GET_FIELDS, "GET 結果欄位不符")
    require(isinstance(payload["request_id"], str) and payload["request_id"] == request_id, "GET request_id 不符")
    require(payload["status"] == "completed", "任務尚未完成")
    require(type(payload["status_code"]) is int and payload["status_code"] == 200, "儲存的任務狀態碼不符")
    require(type(payload["duration_ms"]) is int and payload["duration_ms"] >= 0, "duration_ms 不符")
    timestamp(payload["occurred_at"], "occurred_at")
    require(payload["error_detail"] is None, "GET 結果包含錯誤")
    result_contract(payload["response"], request_id)
    require(payload["response"] == post_payload, "GET 與 POST 完整結果不一致")


def run_hospital_test(base_url, slug, enabled, service_status):
    if not enabled:
        raise RuntimeError(f"{slug}：{service_status}。本 notebook 尚未啟用，不要求金鑰、不送 API 請求。")
    require(isinstance(base_url, str) and base_url.startswith("https://") and base_url.endswith("/" + slug), "正式 API 根網址未設定")
    code_url = base_url + "/api/v1/snomed/coding"
    result_root = base_url + "/api/v1/snomed/results/"
    with requests.Session() as session:
        health_url = base_url + "/healthz"
        health = session.get(health_url, timeout=20, allow_redirects=False)
        http(health, 200, health_url, "健康檢查")
        health_body = health.json()
        require(isinstance(health_body, dict) and health_body["status"] == "ok", "健康檢查內容不符")
        print("健康檢查：通過")

        for url, method in ((code_url, "POST"), (result_root + str(uuid4()), "GET")):
            preflight = session.options(url, headers={
                "Origin": COLAB_ORIGIN,
                "Access-Control-Request-Method": method,
                "Access-Control-Request-Headers": "content-type,x-api-key",
            }, timeout=20, allow_redirects=False)
            http(preflight, (200, 204), url, method + " CORS 預檢")
            cors(preflight)
            methods = {v.strip().upper() for v in preflight.headers["Access-Control-Allow-Methods"].split(",")}
            allowed_headers = {v.strip().lower() for v in preflight.headers["Access-Control-Allow-Headers"].split(",")}
            require(method in methods or "*" in methods, "CORS 未允許此 HTTP 方法")
            require({"content-type", "x-api-key"} <= allowed_headers or "*" in allowed_headers, "CORS 未允許必要 headers")
        print("Colab Origin 的 POST／GET 預檢：通過")

        unauthenticated = session.get(result_root + str(uuid4()), timeout=20, allow_redirects=False)
        http(unauthenticated, 401, unauthenticated.url, "無金鑰認證邊界")
        require(unauthenticated.url.startswith(result_root), "無金鑰測試路徑不符")
        print("無金鑰請求被拒絕：通過")

        api_key = getpass(f"請貼上 {slug} 的 API key（隱藏輸入）：").strip()
        require(bool(api_key), "未輸入金鑰，已停止")
        headers = {"Content-Type": "application/json; charset=utf-8", "X-API-Key": api_key, "Origin": COLAB_ORIGIN}
        request_id = str(uuid4())
        body = {"request_id": request_id, "raw_clinical_note": RAW_NOTE, "output_format": "simple"}
        started = time.perf_counter()
        post = session.post(code_url, headers=headers, json=body, timeout=240, allow_redirects=False)
        elapsed = round(time.perf_counter() - started, 2)
        http(post, 200, code_url, "POST 編碼")
        cors(post)
        post_payload = post.json()
        codings = result_contract(post_payload, request_id)
        get_url = result_root + request_id
        get_response = session.get(get_url, headers=headers, timeout=60, allow_redirects=False)
        http(get_response, 200, get_url, "GET 結果")
        cors(get_response)
        get_contract(get_response.json(), request_id, post_payload)
        # Only synthetic content and contract metadata are displayed; no secret/model identifiers.
        print(json.dumps({
            "request_id": request_id,
            "polished_clinical_note": post_payload["polished_clinical_note"],
            "snomed_codings": codings,
            "vote_attempts": post_payload["processing_metadata"]["vote_attempts"],
            "snomed_version": post_payload["processing_metadata"]["snomed_version"],
            "post_seconds": elapsed,
        }, ensure_ascii=False, indent=2))
        print(f"{slug}：合成病例完整流程測試通過（POST 200、GET 200、結果一致、CORS 通過）")
        return {"hospital_slug": slug, "passed": True, "post_seconds": elapsed, "coding_count": len(codings)}
