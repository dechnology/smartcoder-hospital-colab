# SmartCoder 正式服務 Colab

這 13 份 notebook 固定呼叫各院設定的服務入口。每份請求只包含 `request_id`、同一筆合成原始病歷與 `output_format=simple`，不帶 SNOMED CT 或 ICD-10 參考碼，並檢查完整病例整理、3 輪 NER、術語連結、results GET 與 Colab CORS。

每本 notebook 只呼叫表中的單一 API base URL，不在錯誤後改呼叫其他網址、改讀另一組憑證或縮短流程。回應缺少欄位、型別不符或值不符時立即停止，不以空字典、空陣列或預設值補齊。

所有 base URL 統一為 `https://<該院目前公開機台網域>/<hospital-slug>`。Notebook 只在後面組上固定的 `/api/v1/snomed/coding` 與 `/api/v1/snomed/results/{request_id}`。
院別由 base URL 的 `<hospital-slug>` 確定；Notebook 不傳送 `X-Hospital-Slug`，服務端會依該路徑固定院別，避免路徑與 header 出現兩種院別。

公開版本固定存放在 `dechnology/smartcoder-hospital-colab` 的 `main` branch。中山醫 notebook 已配置一組刻意公開、可撤換的 Colab access token，可直接執行；其他院別不含非公開 API key。

## 中山醫正式入口

中山醫已使用統一正式路徑。單筆合成病歷完整流程已驗證；全案驗收尚未全數通過，因此不標示為全案驗收完成。

| 院別 | API base URL | Colab |
|---|---|---|
| 中山醫 `csh` | `https://fhircsh.itri-nlp.tw/csh` | [開啟 Colab](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/csh_smartcoder_api.ipynb) |

## 正式入口已設定，完整流程待驗證

以下入口的 health、OpenAPI 與認證邊界已驗證。尚未用目前 notebook「只送原始病歷」的條件完成本輪全案驗收，因此不標示為完整流程驗收通過。

| 院別／入口 | API base URL | Colab |
|---|---|---|
| 臺北榮總 `tvgh` | `https://fhircsh.itri-nlp.tw/tvgh` | [開啟 Colab](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/tvgh_smartcoder_api.ipynb) |
| 部立臺北醫院 `tph` | `https://fhircsh.itri-nlp.tw/tph` | [開啟 Colab](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/tph_smartcoder_api.ipynb) |
| 花蓮門諾 `hlm` | `https://fhirdevaz.itri-nlp.tw/hlm` | [開啟 Colab](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/hlm_smartcoder_api.ipynb) |
| 中國醫藥大學附設醫院 `cmmc` | `https://fhirdevaz.itri-nlp.tw/cmmc` | [開啟 Colab](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/cmmc_smartcoder_api.ipynb) |
| 臺中榮總 `tcvgh` | `https://fhirdevazure.itri-nlp.tw/tcvgh` | [開啟 Colab](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/tcvgh_smartcoder_api.ipynb) |
| 臺大 `ntuh` | `https://fhirdevazure.itri-nlp.tw/ntuh` | [開啟 Colab](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/ntuh_smartcoder_api.ipynb) |
| 員榮 `yuanrung` | `https://fhirdevaz.itri-nlp.tw/yuanrung` | [開啟 Colab](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/yuanrung_smartcoder_api.ipynb) |
| UCC `ucc` | `https://fhirdevaz.itri-nlp.tw/ucc` | [開啟 Colab](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/ucc_smartcoder_api.ipynb) |
| 長庚醫療體系 `cgh` | `https://fhirdevazure.itri-nlp.tw/cgh` | [開啟 Colab](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/cgh_smartcoder_api.ipynb) |
| 成大 `nckuh` | `https://fhircgh.itri-nlp.tw/nckuh` | [開啟 Colab](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/nckuh_smartcoder_api.ipynb) |
| 高醫 `kmuh` | `https://fhircgh.itri-nlp.tw/kmuh` | [開啟 Colab](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/kmuh_smartcoder_api.ipynb) |

## 正式入口已設定，服務目前無法連線

馬偕 notebook 保留正式網址與完整驗收條件。服務恢復前，notebook 會顯示目前狀態並停止，不會把未完成流程標成通過。

| 院別／入口 | API base URL | 目前狀態 | Colab |
|---|---|---|---|
| 馬偕醫療體系 `mmh` | `https://fhirmmh.itri-nlp.tw/mmh` | 公開服務目前回傳 502 | [開啟 Colab](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/mmh_smartcoder_api.ipynb) |

## Notebook 會檢查什麼

每份 notebook 都會確認：

- POST 與 GET 皆直接回傳 HTTP 200，不接受網址轉向，並檢查 Colab CORS。
- `polished_clinical_note` 不為空，且整理後內容不得與原始病歷相同。
- 處理 metadata 必須只含契約欄位，SNOMED CT 版本、完整流程版本、3 輪投票、信心度方法與時區時間均需符合鎖定值。
- 每筆編碼的 `concept_id`、`term`、`category`、`confidence` 與 `source` 都必須完整，來源固定為 `TXT_NER`，且 concept 不得重複。
- 回應包含胸痛 SNOMED CT concept `29857009`。
- results GET 狀態為 `completed`，且完整結果與 POST 回應逐欄相同。
- 所有必要欄位的型別與內容都符合契約；任一欄位缺少就停止。

看到 `正式流程驗收通過`，才代表該次執行完成全部檢查。

## API key

- 中山醫：直接執行，不需輸入 key。Notebook 使用可公開、可撤換的 Colab access token。
- 其他已啟用入口：第一個程式區塊只會透過隱藏輸入欄要求該院 API key，不讀取環境變數。
- 服務目前不可用的入口：Notebook 會顯示目前狀態並停止；服務恢復後才會顯示隱藏輸入欄。

不要把其他院別的非公開 key 寫入 notebook、Google Drive 或 GitHub。

## 維護方式

在 repository 根目錄產生 notebook：

```bash
python3 tools/generate_hospital_colab_notebooks.py
```

檢查 notebook 是否與產生器一致：

```bash
python3 tools/generate_hospital_colab_notebooks.py --check
```
