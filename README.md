

# 📑 辯論網站 SPEC v1.2（Python Flask 版）

## 1. 系統總覽

本網站為 **文字型 1v1 辯論平台**，玩家需透過 **Line 實名登入**。辯題由玩家申請、官方審核後上架。辯論流程採回合制，雙方以文章方式發表、提問與回應，每回合結束後開放限時投票，依規則決定勝負。
系統需保存辯論記錄，並提供排行榜與積分制度。

---

## 2. 使用者角色與權限

* **訪客**

  * 可瀏覽公開辯題與辯論紀錄
  * 不可投票、不可申請辯題

* **玩家（Line 實名登入）**

  * 可申請辯題（需官方審核）
  * 可參與辯論（僅支援 1v1）
  * 可投票
  * 擁有戰績與積分，參與排行榜

* **官方管理員**

  * 辯題審核
  * 管理辯論流程
  * 平局時可手動判定勝負

---

## 3. 辯題建立（申請審核制）

1. 玩家填寫申請表：

   * 辯題名稱
   * 辯題描述
   * 正方立場定義
   * 反方立場定義
   * 建議規則（時間/字數限制）
   * 是否公開

2. 官方審核狀態：

   * ✅ 通過 → 自動上架
   * ❌ 退回 → 附原因，玩家可修改後重送
   * ⏳ 暫緩 → 保留待審

3. 系統通知玩家結果（站內通知 / Email / Line Notify）

---

## 4. 辯論流程

### 單回合流程

1. 正方發表 → 發表主要論點（文字文章）
2. 反方提問 → 提出多個問題（文字）
3. 正方回應 → 統一回覆（文字文章）
4. 反方發表 → 發表主要論點（文字文章）
5. 正方提問 → 提問（文字）
6. 反方回應 → 回覆（文字文章）
7. 觀眾與裁判投票 → 限時（例如 24 小時內完成）

### 投票規則

* 玩家投票：每票 = 1 分
* 裁判投票：每票 = 10 分（固定加權）
* 判定條件：

  * 若單方得票率 ≥ 70% → 立即勝出
  * 否則進入下一回合
  * 最多 5 回合，若某方連續 3 回合勝出 → 勝利
  * 若五回合後仍平局 → 官方管理員手動判定

---

## 5. 投票機制

* 投票開放時間：回合結束後，限時 X 小時（可由官方設定）
* 投票結果：公開百分比（圓餅圖 / 長條圖）
* 防作弊機制：

  * 必須 Line 實名登入
  * 限制單人單票
  * 記錄 IP / 裝置指紋

---

## 6. 系統功能模組

1. **會員系統**

   * Line Login API + JWT
   * 玩家檔案（暱稱、頭像、戰績、積分）

2. **辯題管理**

   * 玩家申請辯題
   * 官方審核與上架
   * 辯題清單（搜尋、分類）

3. **辯論流程管理**

   * 僅支援 1v1
   * 全文字留言制，不提供即時聊天室
   * 系統控管回合數與流程進度
   * 官方管理員可介入處理

4. **投票系統**

   * 非即時（投票期內開放，截止後統計）
   * 玩家投票 + 裁判投票加權計算
   * 投票結果可視化（HTML Canvas 或 JS chart library）

5. **賽後管理**

   * 儲存逐字稿（玩家文章 / 問答內容）
   * 儲存投票數據與勝負結果
   * 玩家戰績更新（勝場、敗場、積分）

6. **排行榜與積分制度**

   * 排行榜依據：勝率 + 積分
   * 積分採 **Elo Rating** 方式計算

7. **後台管理**

   * 玩家管理（封鎖、權限設定）
   * 辯題審核
   * 辯論數據查詢
   * 平局手動判定

---

## 7. 技術需求

* **前端**

  * Native HTML + JavaScript
  * Tailwind CSS（樣式框架）

* **後端**

  * Python Flask
  * REST API 架構
  * 驗證使用 JWT

* **資料庫**

  * SQL Server（存放用戶、辯題、辯論、投票、積分紀錄）

* **部署**

  * Windows Server / Linux Server 均可
  * 使用 IIS 或 Nginx 作為反向代理

* **即時處理**

  * ❌ 不需要 WebSocket / Socket.IO
  * ✅ 投票採「開放一段時間後批量統計」

---

## 8. 資料表（建議設計）

1. **Users**

   * user_id, line_id, nickname, avatar, join_date, rating, wins, losses

2. **DebateTopics**

   * topic_id, title, description, side_pros, side_cons, status (pending/approved/rejected), created_by, created_at

3. **Debates**

   * debate_id, topic_id, user_pros_id, user_cons_id, status (ongoing/finished), round_count, winner_id

4. **Rounds**

   * round_id, debate_id, round_number, pros_statement, cons_questions, pros_reply, cons_statement, pros_questions, cons_reply, status

5. **Votes**

   * vote_id, round_id, voter_id, side_voted (pros/cons), is_judge (boolean), weight

6. **JudgeAssignments**

   * judge_id, debate_id, user_id

---



---

# 📡 Debate Website API 規格 (Draft v1.0)

## 1. 認證與使用者 (Users)

### 🔹 登入 / 註冊

* `POST /api/auth/login`

  * 描述：使用 **Line Login** 登入
  * 輸入：Line OAuth token
  * 輸出：

    ```json
    {
      "user_id": 1,
      "nickname": "Alice",
      "avatar": "https://...",
      "token": "jwt-token"
    }
    ```

### 🔹 使用者資料

* `GET /api/users/me`

  * 描述：取得目前登入者的資料
  * 驗證：JWT
  * 輸出：

    ```json
    {
      "user_id": 1,
      "nickname": "Alice",
      "rating": 1500,
      "wins": 10,
      "losses": 5
    }
    ```

* `GET /api/users/{id}`

  * 描述：查看其他使用者的公開資料

---

## 2. 辯題 (Debate Topics)

### 🔹 申請辯題

* `POST /api/topics/apply`

  * 描述：玩家提交辯題申請
  * 驗證：JWT
  * 輸入：

    ```json
    {
      "title": "AI 是否會取代人類工作？",
      "description": "討論人工智慧對就業的影響",
      "side_pros": "AI 將取代大部分人類工作",
      "side_cons": "AI 不會取代大部分人類工作",
      "rules": {
        "word_limit": 500,
        "time_limit_hours": 24
      },
      "is_public": true
    }
    ```
  * 輸出：`{ "topic_id": 12, "status": "pending" }`

### 🔹 查詢辯題清單

* `GET /api/topics`

  * 支援參數：`status` (pending / approved / rejected)
  * 輸出：

    ```json
    [
      {
        "topic_id": 12,
        "title": "AI 是否會取代人類工作？",
        "status": "approved",
        "created_by": "Alice",
        "created_at": "2025-10-01"
      }
    ]
    ```

---

## 3. 辯論 (Debates)

### 🔹 建立辯論

* `POST /api/debates/create`

  * 描述：由官方管理員建立一場辯論，分配正反方玩家
  * 驗證：Admin
  * 輸入：

    ```json
    {
      "topic_id": 12,
      "pros_user_id": 1,
      "cons_user_id": 2
    }
    ```
  * 輸出：`{ "debate_id": 100, "status": "ongoing" }`

### 🔹 取得辯論資訊

* `GET /api/debates/{id}`

  * 描述：取得辯論基本資料（含回合數、狀態、參與者）
  * 輸出：

    ```json
    {
      "debate_id": 100,
      "topic_id": 12,
      "rounds_played": 2,
      "status": "ongoing",
      "pros": { "user_id": 1, "nickname": "Alice" },
      "cons": { "user_id": 2, "nickname": "Bob" }
    }
    ```

---

## 4. 回合流程 (Rounds)

### 🔹 發表 / 提問 / 回應

* `POST /api/rounds/{round_id}/pros_statement`

  * 輸入：

    ```json
    { "content": "AI 的效率與精準度將取代許多工作..." }
    ```
* `POST /api/rounds/{round_id}/cons_questions`

  * 輸入：

    ```json
    { "questions": ["AI 是否能處理創造性工作？", "AI 是否能理解倫理？"] }
    ```
* `POST /api/rounds/{round_id}/pros_reply`

  * 輸入：

    ```json
    { "content": "AI 雖然能自動化許多任務，但在倫理與創造性..." }
    ```
* `POST /api/rounds/{round_id}/cons_statement`
* `POST /api/rounds/{round_id}/pros_questions`
* `POST /api/rounds/{round_id}/cons_reply`

### 🔹 查詢回合內容

* `GET /api/rounds/{round_id}`

  * 輸出：

    ```json
    {
      "round_id": 5,
      "round_number": 2,
      "pros_statement": "AI 將取代...",
      "cons_questions": ["問題1", "問題2"],
      "pros_reply": "回覆內容",
      "cons_statement": "反方論述",
      "pros_questions": ["問題A"],
      "cons_reply": "反方回覆",
      "status": "completed"
    }
    ```

---

## 5. 投票 (Votes)

### 🔹 投票

* `POST /api/rounds/{round_id}/vote`

  * 驗證：JWT
  * 輸入：

    ```json
    {
      "side_voted": "pros",   // or "cons"
      "is_judge": false
    }
    ```
  * 系統會自動計算 `weight`（一般玩家 = 1，裁判 = 10）

### 🔹 查詢投票結果

* `GET /api/rounds/{round_id}/results`

  * 輸出：

    ```json
    {
      "pros_votes": 70,
      "cons_votes": 30,
      "pros_percentage": 70,
      "cons_percentage": 30,
      "winner": "pros"
    }
    ```

---

## 6. 排行榜 (Ranking)

* `GET /api/ranking`

  * 描述：依據 **Elo Rating + 勝率** 排行
  * 輸出：

    ```json
    [
      { "user_id": 1, "nickname": "Alice", "rating": 1600, "wins": 15, "losses": 5 },
      { "user_id": 2, "nickname": "Bob", "rating": 1550, "wins": 12, "losses": 6 }
    ]
    ```

---

## 7. 後台管理 (Admin)

* `GET /api/admin/topics/pending`

  * 取得待審辯題清單
* `POST /api/admin/topics/{id}/approve`
* `POST /api/admin/topics/{id}/reject`
* `POST /api/admin/debates/{id}/force_end`

  * 管理員在平局或異常情況下手動結束辯論

---

# 📌 備註

* 所有需要登入的 API 都必須帶 JWT token (`Authorization: Bearer xxx`)
* 所有投票、辯論參與操作必須驗證使用者身份（Line Login）
* 投票不需即時統計，系統在投票截止時間統計並公布結果

---

👉 這份 API 規格可以讓前後端工程師直接開工：

* **前端** 負責呼叫 API、呈現 UI、顯示投票結果
* **後端 (Flask)** 負責驗證、流程控制、資料儲存
* **資料庫 (SQL Server)** 儲存所有辯題、辯論、回合與投票紀錄

---




---

# 📑 SQL Server 資料表設計 (DDL v1.0)

```sql
-- 使用者資料
CREATE TABLE Users (
    user_id INT IDENTITY(1,1) PRIMARY KEY,
    line_id NVARCHAR(100) UNIQUE NOT NULL,   -- Line 實名登入 ID
    nickname NVARCHAR(50) NOT NULL,
    avatar NVARCHAR(255) NULL,
    join_date DATETIME DEFAULT GETDATE(),
    rating INT DEFAULT 1500,                 -- Elo 初始分數
    wins INT DEFAULT 0,
    losses INT DEFAULT 0,
    is_admin BIT DEFAULT 0                   -- 管理員標記
);

-- 辯題 (玩家申請 + 官方審核)
CREATE TABLE DebateTopics (
    topic_id INT IDENTITY(1,1) PRIMARY KEY,
    title NVARCHAR(200) NOT NULL,
    description NVARCHAR(MAX) NULL,
    side_pros NVARCHAR(500) NOT NULL,
    side_cons NVARCHAR(500) NOT NULL,
    rules NVARCHAR(MAX) NULL,                -- JSON 格式存字數/時間限制
    is_public BIT DEFAULT 1,
    status NVARCHAR(20) DEFAULT 'pending',   -- pending / approved / rejected
    created_by INT FOREIGN KEY REFERENCES Users(user_id),
    created_at DATETIME DEFAULT GETDATE(),
    reviewed_by INT NULL FOREIGN KEY REFERENCES Users(user_id),
    reviewed_at DATETIME NULL
);

-- 辯論對戰
CREATE TABLE Debates (
    debate_id INT IDENTITY(1,1) PRIMARY KEY,
    topic_id INT NOT NULL FOREIGN KEY REFERENCES DebateTopics(topic_id),
    pros_user_id INT NOT NULL FOREIGN KEY REFERENCES Users(user_id),
    cons_user_id INT NOT NULL FOREIGN KEY REFERENCES Users(user_id),
    status NVARCHAR(20) DEFAULT 'ongoing',   -- ongoing / finished
    round_count INT DEFAULT 0,
    winner_id INT NULL FOREIGN KEY REFERENCES Users(user_id),
    created_at DATETIME DEFAULT GETDATE(),
    finished_at DATETIME NULL
);

-- 辯論回合內容
CREATE TABLE Rounds (
    round_id INT IDENTITY(1,1) PRIMARY KEY,
    debate_id INT NOT NULL FOREIGN KEY REFERENCES Debates(debate_id),
    round_number INT NOT NULL,
    pros_statement NVARCHAR(MAX) NULL,
    cons_questions NVARCHAR(MAX) NULL,       -- JSON 陣列存放多題
    pros_reply NVARCHAR(MAX) NULL,
    cons_statement NVARCHAR(MAX) NULL,
    pros_questions NVARCHAR(MAX) NULL,
    cons_reply NVARCHAR(MAX) NULL,
    status NVARCHAR(20) DEFAULT 'in_progress', -- in_progress / completed
    created_at DATETIME DEFAULT GETDATE()
);

-- 投票記錄
CREATE TABLE Votes (
    vote_id INT IDENTITY(1,1) PRIMARY KEY,
    round_id INT NOT NULL FOREIGN KEY REFERENCES Rounds(round_id),
    voter_id INT NOT NULL FOREIGN KEY REFERENCES Users(user_id),
    side_voted NVARCHAR(10) NOT NULL,        -- 'pros' / 'cons'
    is_judge BIT DEFAULT 0,
    weight INT DEFAULT 1,                    -- 系統自動計算 (一般=1, 裁判=10)
    created_at DATETIME DEFAULT GETDATE(),
    CONSTRAINT UQ_Vote UNIQUE (round_id, voter_id) -- 每人每回合僅能投一次
);

-- 裁判分派 (可選)
CREATE TABLE JudgeAssignments (
    judge_id INT IDENTITY(1,1) PRIMARY KEY,
    debate_id INT NOT NULL FOREIGN KEY REFERENCES Debates(debate_id),
    user_id INT NOT NULL FOREIGN KEY REFERENCES Users(user_id)
);

-- 戰績紀錄 (歷史比賽結果保存)
CREATE TABLE MatchHistory (
    match_id INT IDENTITY(1,1) PRIMARY KEY,
    debate_id INT NOT NULL FOREIGN KEY REFERENCES Debates(debate_id),
    user_id INT NOT NULL FOREIGN KEY REFERENCES Users(user_id),
    result NVARCHAR(10) NOT NULL,            -- 'win' / 'loss' / 'draw'
    rating_before INT NOT NULL,
    rating_after INT NOT NULL,
    created_at DATETIME DEFAULT GETDATE()
);
```

---

# 📌 設計重點說明

1. **Users**

   * 使用 Line ID 做唯一識別
   * rating 用於 Elo 排名系統
   * is_admin 區分管理員

2. **DebateTopics**

   * 玩家申請，需官方審核
   * status 控制 `pending/approved/rejected`
   * rules 欄位可存 JSON（例如：`{"word_limit":500,"time_limit_hours":24}`）

3. **Debates + Rounds**

   * 一個 Debate 對應多個 Round
   * Rounds 裡存放發言、提問與回覆，提問存成 JSON 陣列

4. **Votes**

   * 每個玩家每回合只能投一次（透過 `UQ_Vote` constraint 保證）
   * is_judge = 1 → weight=10，自動計算投票比重

5. **MatchHistory**

   * 紀錄 Elo 演算法前後的分數
   * 方便排行榜更新

---


好，我幫你把 **勝負判定流程 + Elo 算法** 梳理成 **SQL + 程式邏輯**，工程師可以直接照這個來做。

---

# ⚖️ 勝負判定與 Elo 計算規格

## 1. 投票統計邏輯

每回合投票結束後，系統需統計：

```sql
SELECT 
    side_voted,
    SUM(weight) AS total_votes
FROM Votes
WHERE round_id = @round_id
GROUP BY side_voted;
```

輸出範例：

| side_voted | total_votes |
| ---------- | ----------- |
| pros       | 70          |
| cons       | 30          |

然後計算百分比：

```sql
pros_percentage = pros_votes * 100 / (pros_votes + cons_votes)
cons_percentage = cons_votes * 100 / (pros_votes + cons_votes)
```

---

## 2. 勝負判定邏輯

1. **單回合直接勝出**：

   * 若 `pros_percentage >= 70` → Pros 勝
   * 若 `cons_percentage >= 70` → Cons 勝

2. **連勝三回合**：

   * 系統需追蹤玩家連勝次數：

   ```sql
   SELECT user_id, COUNT(*) AS consecutive_wins
   FROM MatchHistory
   WHERE debate_id = @debate_id
     AND result = 'win'
   GROUP BY user_id;
   ```

   * 若某方連續 3 回合勝出 → 宣布勝利

3. **最多 5 回合**：

   * 若五回合結束仍平局 → 管理員手動決定勝負

---

## 3. Elo 算法 (玩家積分計算)

Elo 計算公式：

```
R_new = R_old + K * (S - E)
```

* `R_old` = 玩家原本積分
* `R_new` = 更新後積分
* `K` = 調整係數（建議 32）
* `S` = 比賽實際結果 (勝=1，平=0.5，敗=0)
* `E` = 預期勝率 = 1 / (1 + 10 ^ ((R_opponent - R_self) / 400))

### 計算範例

* Alice：1500 分

* Bob：1600 分

* 預期勝率：

  * Alice: `1 / (1 + 10^((1600-1500)/400)) ≈ 0.36`
  * Bob:   `1 / (1 + 10^((1500-1600)/400)) ≈ 0.64`

* 若 Alice 勝出：

  * Alice: `1500 + 32 * (1 - 0.36) = 1520.5 ≈ 1521`
  * Bob:   `1600 + 32 * (0 - 0.64) = 1579.5 ≈ 1580`

---

## 4. SQL Server 儲存過程範例

```sql
CREATE PROCEDURE SP_CalculateRoundResult
    @round_id INT
AS
BEGIN
    DECLARE @pros_votes INT, @cons_votes INT, @pros_pct FLOAT, @cons_pct FLOAT;
    DECLARE @debate_id INT, @pros_user_id INT, @cons_user_id INT;
    DECLARE @winner_id INT = NULL;

    -- 抓回合投票數
    SELECT 
        @pros_votes = SUM(CASE WHEN side_voted = 'pros' THEN weight ELSE 0 END),
        @cons_votes = SUM(CASE WHEN side_voted = 'cons' THEN weight ELSE 0 END)
    FROM Votes
    WHERE round_id = @round_id;

    -- 計算百分比
    SET @pros_pct = (@pros_votes * 100.0) / NULLIF(@pros_votes + @cons_votes,0);
    SET @cons_pct = (@cons_votes * 100.0) / NULLIF(@pros_votes + @cons_votes,0);

    -- 找該場比賽玩家
    SELECT @debate_id = debate_id FROM Rounds WHERE round_id = @round_id;
    SELECT @pros_user_id = pros_user_id, @cons_user_id = cons_user_id
    FROM Debates WHERE debate_id = @debate_id;

    -- 判斷勝利
    IF @pros_pct >= 70
        SET @winner_id = @pros_user_id;
    ELSE IF @cons_pct >= 70
        SET @winner_id = @cons_user_id;

    -- 寫入回合勝負紀錄
    IF @winner_id IS NOT NULL
    BEGIN
        INSERT INTO MatchHistory(debate_id, user_id, result, rating_before, rating_after)
        VALUES(@debate_id, @winner_id, 'win', 0, 0); -- rating 稍後由 Elo 更新
    END
END
```

---

## 5. Elo 計算 (Flask 後端邏輯)

```python
def calculate_elo(rating_a, rating_b, score_a, score_b, k=32):
    # score_a = 1 if A勝, 0 if A敗, 0.5 if 平
    expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    expected_b = 1 / (1 + 10 ** ((rating_a - rating_b) / 400))

    new_a = rating_a + k * (score_a - expected_a)
    new_b = rating_b + k * (score_b - expected_b)

    return round(new_a), round(new_b)
```

使用方式：

```python
# Alice vs Bob
alice_rating, bob_rating = 1500, 1600
new_alice, new_bob = calculate_elo(alice_rating, bob_rating, 1, 0)  # Alice 勝
print(new_alice, new_bob)  # 1521, 1580
```

---

✅ 這樣工程師就能做到：

1. **每回合投票統計**（判定勝負）
2. **寫入 MatchHistory**
3. **賽事結束時計算 Elo 分數並更新 Users.rating**

---


太好了 🙌
我來幫你把 **辯論流程狀態機 (State Machine)** 規劃出來。這份設計能讓工程師明確知道：

* 每一個辯論回合 (Round) 有哪些狀態
* 狀態之間如何轉移
* 在什麼條件下結束辯論並判定勝負

---

# ⚖️ 辯論流程狀態機 (State Machine v1.0)

## 1. 整體辯論流程 (Debate)

```
NEW → ONGOING → FINISHED
```

* **NEW**：辯題已建立，但辯論尚未開始（等待官方分配雙方玩家）
* **ONGOING**：辯論進行中（包含多個回合）
* **FINISHED**：比賽結束（由 70% 投票規則 / 連勝 3 回合 / 最多 5 回合 / 管理員手動裁定決定）

---

## 2. 單回合流程 (Round)

```
WAIT_PROS_STATEMENT
    ↓
WAIT_CONS_QUESTIONS
    ↓
WAIT_PROS_REPLY
    ↓
WAIT_CONS_STATEMENT
    ↓
WAIT_PROS_QUESTIONS
    ↓
WAIT_CONS_REPLY
    ↓
WAIT_VOTING
    ↓
VOTING_CLOSED
    ↓
ROUND_RESULT
```

### 狀態描述

1. **WAIT_PROS_STATEMENT**

   * 正方發表主要論點（文字文章）
   * 限制字數 / 時間

2. **WAIT_CONS_QUESTIONS**

   * 反方提問（可多題，JSON 陣列存）

3. **WAIT_PROS_REPLY**

   * 正方統一回應反方的提問

4. **WAIT_CONS_STATEMENT**

   * 反方發表主要論點

5. **WAIT_PROS_QUESTIONS**

   * 正方提問

6. **WAIT_CONS_REPLY**

   * 反方統一回覆

7. **WAIT_VOTING**

   * 開放投票（觀眾 + 裁判）
   * 設定截止時間（例如 24 小時）

8. **VOTING_CLOSED**

   * 投票截止，系統統計票數

9. **ROUND_RESULT**

   * 判斷勝負（≥70% 或平局）
   * 更新勝利者連勝數
   * 判斷是否結束比賽，或進入下一回合

---

## 3. 勝負判定邏輯

* 單回合結束後：

  * 若任一方得票率 ≥ 70% → 該方勝出，比賽直接結束 (Debate → FINISHED)
  * 否則：

    * 更新連勝次數
    * 若某方連勝 3 回合 → 該方勝出，比賽結束
    * 若尚未達 3 連勝，且回合數 < 5 → 開啟下一回合
    * 若已達 5 回合 → 管理員介入裁定 (Debate → FINISHED)

---

## 4. 狀態機示意圖 (簡化版)

```
[Debate: NEW]
        ↓ (開始)
[Debate: ONGOING]
        ↓
[Round 1: WAIT_PROS_STATEMENT] → ... → [ROUND_RESULT]
        ↓ (若比賽尚未結束)
[Round 2: WAIT_PROS_STATEMENT] → ... → [ROUND_RESULT]
        ↓
   ...
        ↓
[Debate: FINISHED]
```

---

## 5. 系統自動控制需求

* **自動跳轉**：每個狀態完成後，自動切換到下一狀態
* **時間限制**：若玩家逾時未提交 → 系統可：

  * 自動結束該回合並判對方勝利（可選規則）
* **投票結束**：系統需定時任務 (Scheduler / Cron job) 判斷投票是否截止，並統計結果
* **勝負決定**：在 `ROUND_RESULT` 狀態檢查條件，若符合立即結束比賽

---

✅ 有了這個狀態機，工程師就能照著實作「每個狀態 → 下一步」的流程控制，避免混亂。

---

