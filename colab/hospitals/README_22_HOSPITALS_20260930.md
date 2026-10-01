# SmartCoder 22 院 API 介接與 Colab 測試手冊

供院方資訊室與 HIS 介接工程師使用。依院別開啟下表 Colab，先執行初始化與隱藏金鑰設定，再按各功能區塊的 ▶。也可選 Python 3／CPU →「執行階段 → 全部執行」。不需要 GPU。

每本手冊包含參數表、POST／GET 呼叫程式、實際 HTTP 狀態與 JSON 顯示、FHIR 輸出、401／404／422 錯誤測試、Colab Origin 的 CORS 預檢，以及本次逐項測試總表。中山醫與員榮另有 NDJSON 串流測試；其餘院別不提供未支援的 stream 開關。各院 API 根網址固定於自己的 notebook。

金鑰由計畫窗口以私有管道提供；公開 notebook 沒有內建金鑰，也沒有儲存任何執行輸出。預設使用合成病例，請勿在本公開 Colab 輸入真實病歷或個資。自訂病例可驗證 API 格式；其編碼正確性須由專業人員覆核。

## 院別連結

| # | 醫院／院別代碼 | 分區 | 新版逐項測試 | Colab 測試手冊 |
|---|---|---|---|---|
| 1 | 林口長庚紀念醫院 `cgmhlnk` | m | 13/13 通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/cgmhlnk_smartcoder_api.ipynb) |
| 2 | 中山醫學大學附設醫院 `csh` | m | 14/14 通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/csh_smartcoder_api.ipynb) |
| 3 | 台灣基督長老教會馬偕醫療財團法人馬偕紀念醫院（台北院區） `tpmmh` | n | 13/13 通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/tpmmh_smartcoder_api.ipynb) |
| 4 | 國立成功大學醫學院附設醫院 `nckuh` | s | 13/13 通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/nckuh_smartcoder_api.ipynb) |
| 5 | 財團法人私立高雄醫學大學附設中和紀念醫院 `kmuh` | s | 13/13 通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/kmuh_smartcoder_api.ipynb) |
| 6 | 佛教慈濟醫療財團法人花蓮慈濟醫院 `hlm` | s | 13/13 通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/hlm_smartcoder_api.ipynb) |
| 7 | 奇美醫療財團法人奇美醫院 `cmmc` | s | 13/13 通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/cmmc_smartcoder_api.ipynb) |
| 8 | 臺中榮民總醫院 `tcvgh` | m | 13/13 通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/tcvgh_smartcoder_api.ipynb) |
| 9 | 國立臺灣大學醫學院附設醫院 `ntuh` | n | 13/13 通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/ntuh_smartcoder_api.ipynb) |
| 10 | 臺北榮民總醫院 `tvgh` | n | 13/13 通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/tvgh_smartcoder_api.ipynb) |
| 11 | 員榮醫療社團法人員榮醫院 `yuanrung` | m | 14/14 通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/yuanrung_smartcoder_api.ipynb) |
| 12 | 衛生福利部臺北醫院 `tph` | n | 13/13 通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/tph_smartcoder_api.ipynb) |
| 13 | 新光醫療財團法人新光吳火獅紀念醫院 `skh` | n | 13/13 通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/skh_smartcoder_api.ipynb) |
| 14 | 國防醫學大學三軍總醫院 `tsgh` | n | 13/13 通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/tsgh_smartcoder_api.ipynb) |
| 15 | 臺北市立萬芳醫院－委託臺北醫學大學辦理 `wfh` | n | 13/13 通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/wfh_smartcoder_api.ipynb) |
| 16 | 高雄榮民總醫院 `ksvgh` | s | 13/13 通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/ksvgh_smartcoder_api.ipynb) |
| 17 | 醫療財團法人徐元智先生醫藥基金會亞東紀念醫院 `femh` | n | 13/13 通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/femh_smartcoder_api.ipynb) |
| 18 | 中國醫藥大學附設醫院 `cmuh` | m | 13/13 通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/cmuh_smartcoder_api.ipynb) |
| 19 | 佛教慈濟醫療財團法人台北慈濟醫院 `ttch` | n | 13/13 通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/ttch_smartcoder_api.ipynb) |
| 20 | 國泰醫療財團法人國泰綜合醫院 `cathay` | n | 13/13 通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/cathay_smartcoder_api.ipynb) |
| 21 | 義大醫療財團法人義大醫院 `edah` | s | 13/13 通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/edah_smartcoder_api.ipynb) |
| 22 | 彰化基督教醫療財團法人彰化基督教醫院 `cch` | m | 13/13 通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/cch_smartcoder_api.ipynb) |

n＝北區、m＝中區、s＝南區。`hlm` 為花蓮慈濟、`cmmc` 為奇美、`cmuh` 為中國附醫、`cathay` 為國泰。

## 功能與驗證範圍

公開院方介接功能為 `GET /healthz`、`POST /api/v1/snomed/coding`、`GET /api/v1/snomed/results/{request_id}`。POST 的輸出格式為 `simple` 或 `fhir`。目前 fhir_bundle 是含 entry 的 API 包裝物件，不是可以直接寫入 FHIR Server 的完整 Bundle。

中山醫、員榮、林口長庚、臺中榮總已公開需金鑰的 `/openapi.json`；其餘院別此路徑預期 404。各手冊依實際配置檢查，404 不等於編碼功能故障。管理／稽核路徑及內部回呼不屬於此院方介接手冊。

預設合成病例檢查胸痛概念 29857009、否認咳嗽、整理後文字、3 輪 NER metadata、TXT_NER 來源、FHIR 對應及 POST／GET 完整 JSON 一致。CORS 驗證 Origin 為 https://colab.research.google.com；院方自己的 Origin 仍需另外驗證。測試通過不等於臨床準確率或院方整合驗收。

逐院介面配置與測試日期見 [院別登錄表](hospitals_22_20260930.json)。Notebook 自己的總表只代表當次實際執行結果。

新版預設逐項測試：22/22 院、共 288 項通過。實際 notebook 程式在正式 VM 執行，連至各院公開 HTTPS 入口；此紀錄不宣稱全部已在 Google Colab 執行階段跑過，也不代表任意參數組合或臨床準確率已驗證。逐項 HTTP 與時間見 [驗證紀錄](../../verification/functions_22_20261001.json)。
