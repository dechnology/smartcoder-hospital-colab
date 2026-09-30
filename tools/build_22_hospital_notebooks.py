"""Build the 22 requested hospital notebooks from a secret-free status registry."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "colab/hospitals/hospitals_22_20260930.json"


def cell(kind, text):
    item = {"cell_type": kind, "metadata": {}, "source": text.splitlines(keepends=True)}
    if kind == "code":
        item.update(execution_count=None, outputs=[])
    return item


def colab_url(slug):
    return f"https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/{slug}_smartcoder_api.ipynb"


def build():
    hospitals = json.loads(REGISTRY.read_text())
    client = (ROOT / "tools/colab_client.py").read_text()
    table = ["| # | 院別／代碼 | 分區 | 正式 VM | API 根網址 | 公開測試狀態 | Colab |", "|---|---|---|---|---|---|---|"]
    for number, h in enumerate(hospitals, 1):
        slug = h["slug"]
        filename = f"{slug}_smartcoder_api.ipynb"
        base = h["base_url"]
        endpoint = f"`{base}`" if base else "尚未設定"
        target = base or f"預定網域：`smartcoder{h['region']}.itri-nlp.tw`；正式 API 根網址尚未配置。"
        title = f"""# {h['name']}（{slug}）SmartCoder API 測試

狀態日期：{h['status_date']}。分區：**{h['region']}**（n 北、m 中、s 南）。正式 VM：`{h['vm_ip']}`。

**目前狀態：{h['status']}**

API 根網址：{target}

## 操作步驟

1. 使用 Colab 的 Python 3／CPU 執行階段，選擇「執行階段 → 全部執行」。不需要 GPU。
2. 已啟用院別會先檢查健康、Colab Origin 預檢與無金鑰認證邊界，再要求隱藏輸入該院 API key。金鑰由管理者以私有管道提供；本 notebook 沒有內建金鑰。
3. 只送出內建合成病例：`患者胸痛持續兩週，否認咳嗽。`。請勿放入真實病歷或個人資料。
4. 看到「合成病例完整流程測試通過」才代表本次成功。失敗會停止；未啟用院別不會要求金鑰或發送請求。

## API 怎麼呼叫

本院只使用上述單一根網址。POST 路徑為 `{{BASE_URL}}/api/v1/snomed/coding`，GET 回查為 `{{BASE_URL}}/api/v1/snomed/results/{{request_id}}`。

認證 header 是 `X-API-Key`，JSON header 是 `Content-Type: application/json; charset=utf-8`。不需要 `X-Hospital-Slug`。POST body：

```json
{{
  "request_id": "每次產生的新 UUID",
  "raw_clinical_note": "患者胸痛持續兩週，否認咳嗽。",
  "output_format": "simple"
}}
```

程式會驗證病歷整理、3 輪 NER metadata、TXT_NER 編碼來源、此合成病例的已知胸痛 SNOMED CT 概念 `29857009`、否認咳嗽未產生陽性編碼，以及 POST／GET 完整結果一致性。

這是合成病例的可用性與契約測試；無法單靠 metadata 證明內部每輪推論，也不代表臨床準確性或院方整合驗收。Python requests 不受瀏覽器 CORS 限制；此 notebook 另外明確檢查 Colab Origin 的預檢與回應 headers，其他前端 Origin 需另外測試。
"""
        setup = f"HOSPITAL_SLUG = {slug!r}\nBASE_URL = {base!r}\nSERVICE_ENABLED = {h['enabled']!r}\nSERVICE_STATUS = {h['status']!r}\nprint(HOSPITAL_SLUG, SERVICE_STATUS)\n"
        run = "TEST_RESULT = run_hospital_test(BASE_URL, HOSPITAL_SLUG, SERVICE_ENABLED, SERVICE_STATUS)\n"
        notebook = {"cells": [cell("markdown", title), cell("code", setup), cell("code", client), cell("code", run)],
                    "metadata": {"colab": {"name": filename, "provenance": []}, "kernelspec": {"display_name": "Python 3", "name": "python3"}, "language_info": {"name": "python"}},
                    "nbformat": 4, "nbformat_minor": 5}
        for index, item in enumerate(notebook["cells"]):
            item["id"] = f"{slug}-{index}"
        (ROOT / "colab/hospitals" / filename).write_text(json.dumps(notebook, ensure_ascii=False, indent=2) + "\n")
        table.append(f"| {number} | {h['name']} `{slug}` | {h['region']} | `{h['vm_ip']}` | {endpoint} | {h['status']} | [開啟]({colab_url(slug)}) |")

    readme = """# SmartCoder 本次 22 院 Colab

依提供的 22 院表順序列出。公開完整流程驗證日期為 2026-10-01（Australia/Sydney）；逐院 UTC 時間記錄於 `hospitals_22_20260930.json` 的 `public_tested_at`。

22 院已部署到對應正式 VM。北區 n 使用 MMH `51.53.64.4`、中區 m 使用 CSH `51.53.64.0`、南區 s 使用 CGHH `51.53.64.5`；公開入口由 Gateway `51.53.64.2` 轉送。公開 HTTPS 與完整測試是否完成，依下表實測狀態判定。

## 執行方式與測試範圍

開啟下表 Colab → Python 3／CPU →「執行階段 → 全部執行」→ 在隱藏欄位輸入該院 API key。

Notebook 先檢查 `/healthz`、POST／GET 的 Colab Origin CORS 預檢與無金鑰 GET 401，再送出一筆內建合成病例。流程檢查病歷整理、3 輪 NER metadata、TXT_NER 來源、已知胸痛 SNOMED CT `29857009`，最後以相同 request_id 回查完整結果。測試通過不等於临床準確性或院方整合驗收；其他瀏覽器 Origin 需另外驗證。

API 認證使用 `X-API-Key`。POST 為 `<API 根網址>/api/v1/snomed/coding`，GET 為 `<API 根網址>/api/v1/snomed/results/<request_id>`。每本 notebook 內有完整 JSON body 與 Python 呼叫程式。沒有內建金鑰；請由管理者以私有管道提供，不要把金鑰貼在 GitHub 或分享連結中。

## 22 院連結

""" + "\n".join(table) + "\n\n`hlm` 是花蓮慈濟；`cmmc` 是奇美；中國附醫另用 `cmuh`，國泰另用 `cathay`。\n"
    (ROOT / "colab/hospitals/README_22_HOSPITALS_20260930.md").write_text(readme.replace("临床", "臨床"))
    print(f"Generated {len(hospitals)} notebooks; enabled={sum(h['enabled'] for h in hospitals)}")


if __name__ == "__main__":
    build()
