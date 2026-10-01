# 22 院正式前端 CORS 修復與重測

日期：2026-10-01。前端維持 v0.9.0／`39d48b6ba5fbbaba0de672bf9ce4b45c25372ef4`；本次修改三台正式 VM 的 Nginx CORS，未重建 API／worker、變更院別路由或輪替金鑰。

## 原因與修正

先前錯誤回應修補將 `Access-Control-Allow-Origin` 寫死為 Colab，並隱藏 API 原有 header。因此 19 院即使 POST 已完成，正式院方頁面的 Origin 仍與回應不符，瀏覽器會阻擋讀取。這是本次操作前已確認的 Nginx 設定錯誤；先前 Colab Origin 通過不能代替院方 Origin 驗收。

經使用者明確授權，22 院現有 coding、results、health 與 OpenAPI location 改用依院別路徑比對的精確 Origin 清單：各院自己的 `https://<代碼>.mohw-smart.itri-nlp.tw` 及既有 Colab。OPTIONS 回 204；成功與認證錯誤回應均回單一合法 Origin，附 `Vary: Origin`。陌生網站及其他院別 Origin 均不放行。

## 逐院結果

每院 18 項，共 **396/396 通過**。帶金鑰測試從各院原正式 VM 走公開 HTTPS，明確送出正式頁面 Origin；TLS 驗證開啟，金鑰僅在原 VM 記憶體使用。每院以獨立 UUID 送合成病例，含 `department=MOHW_INTERNAL_MEDICINE`、`threshold=0.5`，確認整理後文字、非空 SNOMED CT、POST 200、GET completed 與結果一致。兩個新參數目前沒有篩選或分析功能。

| 院別 | 分區 | API | 金鑰狀態 | POST／GET | 模式 | 正式 Origin／Colab CORS |
|---|---|---|---|---|---|---|
| 林口長庚紀念醫院 `cgmhlnk` | m | https://smartcoderm.itri-nlp.tw/cgmhlnk | 已配置、驗證通過 | 200／200 completed | JSON | 通過／通過 |
| 中山醫學大學附設醫院 `csh` | m | https://smartcoderm.itri-nlp.tw/csh | 已配置、驗證通過 | 200／200 completed | NDJSON | 通過／通過 |
| 台灣基督長老教會馬偕醫療財團法人馬偕紀念醫院（台北院區） `tpmmh` | n | https://smartcodern.itri-nlp.tw/tpmmh | 已配置、驗證通過 | 200／200 completed | JSON | 通過／通過 |
| 國立成功大學醫學院附設醫院 `nckuh` | s | https://smartcoders.itri-nlp.tw/nckuh | 已配置、驗證通過 | 200／200 completed | JSON | 通過／通過 |
| 財團法人私立高雄醫學大學附設中和紀念醫院 `kmuh` | s | https://smartcoders.itri-nlp.tw/kmuh | 已配置、驗證通過 | 200／200 completed | JSON | 通過／通過 |
| 佛教慈濟醫療財團法人花蓮慈濟醫院 `hlm` | s | https://smartcoders.itri-nlp.tw/hlm | 已配置、驗證通過 | 200／200 completed | JSON | 通過／通過 |
| 奇美醫療財團法人奇美醫院 `cmmc` | s | https://smartcoders.itri-nlp.tw/cmmc | 已配置、驗證通過 | 200／200 completed | JSON | 通過／通過 |
| 臺中榮民總醫院 `tcvgh` | m | https://smartcoderm.itri-nlp.tw/tcvgh | 已配置、驗證通過 | 200／200 completed | JSON | 通過／通過 |
| 國立臺灣大學醫學院附設醫院 `ntuh` | n | https://smartcodern.itri-nlp.tw/ntuh | 已配置、驗證通過 | 200／200 completed | JSON | 通過／通過 |
| 臺北榮民總醫院 `tvgh` | n | https://smartcodern.itri-nlp.tw/tvgh | 已配置、驗證通過 | 200／200 completed | JSON | 通過／通過 |
| 員榮醫療社團法人員榮醫院 `yuanrung` | m | https://smartcoderm.itri-nlp.tw/yuanrung | 已配置、驗證通過 | 200／200 completed | NDJSON | 通過／通過 |
| 衛生福利部臺北醫院 `tph` | n | https://smartcodern.itri-nlp.tw/tph | 已配置、驗證通過 | 200／200 completed | JSON | 通過／通過 |
| 新光醫療財團法人新光吳火獅紀念醫院 `skh` | n | https://smartcodern.itri-nlp.tw/skh | 已配置、驗證通過 | 200／200 completed | JSON | 通過／通過 |
| 國防醫學大學三軍總醫院 `tsgh` | n | https://smartcodern.itri-nlp.tw/tsgh | 已配置、驗證通過 | 200／200 completed | JSON | 通過／通過 |
| 臺北市立萬芳醫院－委託臺北醫學大學辦理 `wfh` | n | https://smartcodern.itri-nlp.tw/wfh | 已配置、驗證通過 | 200／200 completed | JSON | 通過／通過 |
| 高雄榮民總醫院 `ksvgh` | s | https://smartcoders.itri-nlp.tw/ksvgh | 已配置、驗證通過 | 200／200 completed | JSON | 通過／通過 |
| 醫療財團法人徐元智先生醫藥基金會亞東紀念醫院 `femh` | n | https://smartcodern.itri-nlp.tw/femh | 已配置、驗證通過 | 200／200 completed | JSON | 通過／通過 |
| 中國醫藥大學附設醫院 `cmuh` | m | https://smartcoderm.itri-nlp.tw/cmuh | 已配置、驗證通過 | 200／200 completed | JSON | 通過／通過 |
| 佛教慈濟醫療財團法人台北慈濟醫院 `ttch` | n | https://smartcodern.itri-nlp.tw/ttch | 已配置、驗證通過 | 200／200 completed | JSON | 通過／通過 |
| 國泰醫療財團法人國泰綜合醫院 `cathay` | n | https://smartcodern.itri-nlp.tw/cathay | 已配置、驗證通過 | 200／200 completed | JSON | 通過／通過 |
| 義大醫療財團法人義大醫院 `edah` | s | https://smartcoders.itri-nlp.tw/edah | 已配置、驗證通過 | 200／200 completed | JSON | 通過／通過 |
| 彰化基督教醫療財團法人彰化基督教醫院 `cch` | m | https://smartcoderm.itri-nlp.tw/cch | 已配置、驗證通過 | 200／200 completed | JSON | 通過／通過 |

18 項包含：兩個允許 Origin 各自的 POST／GET 預檢、無金鑰 401、錯誤金鑰 401、有效原金鑰查無 UUID 404；陌生 Origin 與其他院別 Origin 的預檢及 401 均無 ACAO；health；公開 OpenAPI 回應 CORS；合成 coding；completed results。中山與員榮只在收到 `pipeline.completed` 且同案 GET 完整一致後列為通過。

中山、員榮、林口長庚、臺中榮總的公開 OpenAPI 回 200；其餘 18 院既有配置為 404。這 18 個 404 不計成編碼故障，也沒有新增公開 OpenAPI 路由。

另將已審查的 CSH notebook 與公開 commit 14bf54f099a6fb2b08fe7deb1ed0371c48dac19f 逐位元組核對，再於原 CSH VM 執行已發布程式，14/14 項通過，含 simple、FHIR、串流、結果回查與 Colab CORS。此數字另計，不併入上方 396 項。

## 瀏覽器與驗收界線

實際瀏覽器從台北馬偕正式 host-test.html，以假測試金鑰送跨網域 GET；預檢後可讀到 HTTP 401 的 JSON detail，沒有 CORS 阻擋。此測試證明正式 Origin 在瀏覽器可讀認證錯誤。22 院帶正式金鑰完成分析的紀錄則來自原正式 VM；未執行 22 院瀏覽器帶金鑰的 HIS 嵌入／回傳驗收。

台北馬偕本次使用機台原有院別金鑰，POST 200、GET 200 completed；錯誤金鑰仍回 401。後續操作人員提供私有 TXT 來源，本機金鑰與正式 MMH 機台核對一致，以該 TXT 金鑰送公開 results 的不存在合成 UUID 回 404，證明認證通過；無金鑰控制組回 401，正式 Origin CORS 正常。來源檔案權限 0600，金鑰未印出或搬到別台 VM。先前 v0.9.0 那次 401 的實際 request header 未取得，尚未重現，不能宣稱已確認其原因或修復呼叫端設定。

先前 Mac／Google 完整測試約 60 秒斷線的問題沒有因這次 CORS 通過而被定位，MOHW-TRB-119 保留 Investigating。此表只涵蓋列出的 22 院，不是 39 院或三個共用入口的完整介接驗收。

