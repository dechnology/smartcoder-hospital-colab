# SmartCoder 本次 22 院 Colab

依提供的 22 院表順序列出。公開完整流程驗證日期為 2026-10-01（Australia/Sydney）；逐院 UTC 時間記錄於 `hospitals_22_20260930.json` 的 `public_tested_at`。

22 院已部署到對應正式 VM。北區 n 使用 MMH `51.53.64.4`、中區 m 使用 CSH `51.53.64.0`、南區 s 使用 CGHH `51.53.64.5`；公開入口由 Gateway `51.53.64.2` 轉送。公開 HTTPS 與完整測試是否完成，依下表實測狀態判定。

## 執行方式與測試範圍

開啟下表 Colab → Python 3／CPU →「執行階段 → 全部執行」→ 在隱藏欄位輸入該院 API key。

Notebook 先檢查 `/healthz`、POST／GET 的 Colab Origin CORS 預檢與無金鑰 GET 401，再送出一筆內建合成病例。流程檢查病歷整理、3 輪 NER metadata、TXT_NER 來源、已知胸痛 SNOMED CT `29857009`，最後以相同 request_id 回查完整結果。測試通過不等於臨床準確性或院方整合驗收；其他瀏覽器 Origin 需另外驗證。

API 認證使用 `X-API-Key`。POST 為 `<API 根網址>/api/v1/snomed/coding`，GET 為 `<API 根網址>/api/v1/snomed/results/<request_id>`。每本 notebook 內有完整 JSON body 與 Python 呼叫程式。沒有內建金鑰；請由管理者以私有管道提供，不要把金鑰貼在 GitHub 或分享連結中。

## 22 院連結

| # | 院別／代碼 | 分區 | 正式 VM | API 根網址 | 公開測試狀態 | Colab |
|---|---|---|---|---|---|---|
| 1 | 林口長庚紀念醫院 `cgmhlnk` | m | `51.53.64.0` | `https://smartcoderm.itri-nlp.tw/cgmhlnk` | 公開 HTTPS 完整合成流程通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/cgmhlnk_smartcoder_api.ipynb) |
| 2 | 中山醫學大學附設醫院 `csh` | m | `51.53.64.0` | `https://smartcoderm.itri-nlp.tw/csh` | 公開 HTTPS 完整合成流程通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/csh_smartcoder_api.ipynb) |
| 3 | 台灣基督長老教會馬偕醫療財團法人馬偕紀念醫院（台北院區） `tpmmh` | n | `51.53.64.4` | `https://smartcodern.itri-nlp.tw/tpmmh` | 公開 HTTPS 完整合成流程通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/tpmmh_smartcoder_api.ipynb) |
| 4 | 國立成功大學醫學院附設醫院 `nckuh` | s | `51.53.64.5` | `https://smartcoders.itri-nlp.tw/nckuh` | 公開 HTTPS 完整合成流程通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/nckuh_smartcoder_api.ipynb) |
| 5 | 財團法人私立高雄醫學大學附設中和紀念醫院 `kmuh` | s | `51.53.64.5` | `https://smartcoders.itri-nlp.tw/kmuh` | 公開 HTTPS 完整合成流程通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/kmuh_smartcoder_api.ipynb) |
| 6 | 佛教慈濟醫療財團法人花蓮慈濟醫院 `hlm` | s | `51.53.64.5` | `https://smartcoders.itri-nlp.tw/hlm` | 公開 HTTPS 完整合成流程通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/hlm_smartcoder_api.ipynb) |
| 7 | 奇美醫療財團法人奇美醫院 `cmmc` | s | `51.53.64.5` | `https://smartcoders.itri-nlp.tw/cmmc` | 公開 HTTPS 完整合成流程通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/cmmc_smartcoder_api.ipynb) |
| 8 | 臺中榮民總醫院 `tcvgh` | m | `51.53.64.0` | `https://smartcoderm.itri-nlp.tw/tcvgh` | 公開 HTTPS 完整合成流程通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/tcvgh_smartcoder_api.ipynb) |
| 9 | 國立臺灣大學醫學院附設醫院 `ntuh` | n | `51.53.64.4` | `https://smartcodern.itri-nlp.tw/ntuh` | 公開 HTTPS 完整合成流程通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/ntuh_smartcoder_api.ipynb) |
| 10 | 臺北榮民總醫院 `tvgh` | n | `51.53.64.4` | `https://smartcodern.itri-nlp.tw/tvgh` | 公開 HTTPS 完整合成流程通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/tvgh_smartcoder_api.ipynb) |
| 11 | 員榮醫療社團法人員榮醫院 `yuanrung` | m | `51.53.64.0` | `https://smartcoderm.itri-nlp.tw/yuanrung` | 公開 HTTPS 完整合成流程通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/yuanrung_smartcoder_api.ipynb) |
| 12 | 衛生福利部臺北醫院 `tph` | n | `51.53.64.4` | `https://smartcodern.itri-nlp.tw/tph` | 公開 HTTPS 完整合成流程通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/tph_smartcoder_api.ipynb) |
| 13 | 新光醫療財團法人新光吳火獅紀念醫院 `skh` | n | `51.53.64.4` | `https://smartcodern.itri-nlp.tw/skh` | 公開 HTTPS 完整合成流程通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/skh_smartcoder_api.ipynb) |
| 14 | 國防醫學大學三軍總醫院 `tsgh` | n | `51.53.64.4` | `https://smartcodern.itri-nlp.tw/tsgh` | 公開 HTTPS 完整合成流程通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/tsgh_smartcoder_api.ipynb) |
| 15 | 臺北市立萬芳醫院－委託臺北醫學大學辦理 `wfh` | n | `51.53.64.4` | `https://smartcodern.itri-nlp.tw/wfh` | 公開 HTTPS 完整合成流程通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/wfh_smartcoder_api.ipynb) |
| 16 | 高雄榮民總醫院 `ksvgh` | s | `51.53.64.5` | `https://smartcoders.itri-nlp.tw/ksvgh` | 公開 HTTPS 完整合成流程通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/ksvgh_smartcoder_api.ipynb) |
| 17 | 醫療財團法人徐元智先生醫藥基金會亞東紀念醫院 `femh` | n | `51.53.64.4` | `https://smartcodern.itri-nlp.tw/femh` | 公開 HTTPS 完整合成流程通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/femh_smartcoder_api.ipynb) |
| 18 | 中國醫藥大學附設醫院 `cmuh` | m | `51.53.64.0` | `https://smartcoderm.itri-nlp.tw/cmuh` | 公開 HTTPS 完整合成流程通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/cmuh_smartcoder_api.ipynb) |
| 19 | 佛教慈濟醫療財團法人台北慈濟醫院 `ttch` | n | `51.53.64.4` | `https://smartcodern.itri-nlp.tw/ttch` | 公開 HTTPS 完整合成流程通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/ttch_smartcoder_api.ipynb) |
| 20 | 國泰醫療財團法人國泰綜合醫院 `cathay` | n | `51.53.64.4` | `https://smartcodern.itri-nlp.tw/cathay` | 公開 HTTPS 完整合成流程通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/cathay_smartcoder_api.ipynb) |
| 21 | 義大醫療財團法人義大醫院 `edah` | s | `51.53.64.5` | `https://smartcoders.itri-nlp.tw/edah` | 公開 HTTPS 完整合成流程通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/edah_smartcoder_api.ipynb) |
| 22 | 彰化基督教醫療財團法人彰化基督教醫院 `cch` | m | `51.53.64.0` | `https://smartcoderm.itri-nlp.tw/cch` | 公開 HTTPS 完整合成流程通過 | [開啟](https://colab.research.google.com/github/dechnology/smartcoder-hospital-colab/blob/main/colab/hospitals/cch_smartcoder_api.ipynb) |

`hlm` 是花蓮慈濟；`cmmc` 是奇美；中國附醫另用 `cmuh`，國泰另用 `cathay`。
