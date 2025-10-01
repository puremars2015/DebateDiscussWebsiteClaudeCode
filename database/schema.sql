-- 辯論平台數據庫 Schema
-- SQL Server 版本

-- 創建數據庫（如需要）
-- CREATE DATABASE DebatePlatform;
-- GO
-- USE DebatePlatform;
-- GO

-- 用戶表
CREATE TABLE Users (
    user_id INT PRIMARY KEY IDENTITY(1,1),
    line_id NVARCHAR(255) NOT NULL UNIQUE,
    nickname NVARCHAR(100) NOT NULL,
    avatar NVARCHAR(500),
    rating INT NOT NULL DEFAULT 1500,
    wins INT NOT NULL DEFAULT 0,
    losses INT NOT NULL DEFAULT 0,
    draws INT NOT NULL DEFAULT 0,
    is_admin BIT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME NOT NULL DEFAULT GETDATE()
);

-- 辯論話題表
CREATE TABLE DebateTopics (
    topic_id INT PRIMARY KEY IDENTITY(1,1),
    title NVARCHAR(200) NOT NULL,
    description NVARCHAR(MAX) NOT NULL,
    side_pros NVARCHAR(100) NOT NULL,  -- 正方立場名稱
    side_cons NVARCHAR(100) NOT NULL,  -- 反方立場名稱
    rules NVARCHAR(MAX),  -- JSON 格式存儲規則 {"word_limit": 500, "time_limit_hours": 24}
    status NVARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending, approved, rejected
    created_by INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (created_by) REFERENCES Users(user_id)
);

-- 辯論表
CREATE TABLE Debates (
    debate_id INT PRIMARY KEY IDENTITY(1,1),
    topic_id INT NOT NULL,
    pros_user_id INT NOT NULL,
    cons_user_id INT NOT NULL,
    status NVARCHAR(20) NOT NULL DEFAULT 'NEW',  -- NEW, ONGOING, FINISHED
    round_count INT NOT NULL DEFAULT 0,
    winner_id INT,
    pros_consecutive_wins INT NOT NULL DEFAULT 0,
    cons_consecutive_wins INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (topic_id) REFERENCES DebateTopics(topic_id),
    FOREIGN KEY (pros_user_id) REFERENCES Users(user_id),
    FOREIGN KEY (cons_user_id) REFERENCES Users(user_id),
    FOREIGN KEY (winner_id) REFERENCES Users(user_id)
);

-- 回合表
CREATE TABLE Rounds (
    round_id INT PRIMARY KEY IDENTITY(1,1),
    debate_id INT NOT NULL,
    round_number INT NOT NULL,
    pros_statement NVARCHAR(MAX),
    cons_questions NVARCHAR(MAX),  -- JSON 數組
    pros_reply NVARCHAR(MAX),
    cons_statement NVARCHAR(MAX),
    pros_questions NVARCHAR(MAX),  -- JSON 數組
    cons_reply NVARCHAR(MAX),
    status NVARCHAR(30) NOT NULL DEFAULT 'WAIT_PROS_STATEMENT',
    -- 狀態: WAIT_PROS_STATEMENT, WAIT_CONS_QUESTIONS, WAIT_PROS_REPLY,
    --       WAIT_CONS_STATEMENT, WAIT_PROS_QUESTIONS, WAIT_CONS_REPLY,
    --       WAIT_VOTING, VOTING_CLOSED, ROUND_RESULT
    winner_side NVARCHAR(10),  -- pros, cons, draw
    voting_deadline DATETIME,
    created_at DATETIME NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (debate_id) REFERENCES Debates(debate_id),
    CONSTRAINT UQ_Round_Per_Debate UNIQUE (debate_id, round_number)
);

-- 投票表
CREATE TABLE Votes (
    vote_id INT PRIMARY KEY IDENTITY(1,1),
    round_id INT NOT NULL,
    voter_id INT NOT NULL,
    side_voted NVARCHAR(10) NOT NULL,  -- pros, cons
    is_judge BIT NOT NULL DEFAULT 0,
    weight INT NOT NULL DEFAULT 1,  -- 普通用戶 1，法官 10
    created_at DATETIME NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (round_id) REFERENCES Rounds(round_id),
    FOREIGN KEY (voter_id) REFERENCES Users(user_id),
    CONSTRAINT UQ_Vote_Per_Round UNIQUE (round_id, voter_id)
);

-- 法官分配表
CREATE TABLE JudgeAssignments (
    judge_id INT PRIMARY KEY IDENTITY(1,1),
    debate_id INT NOT NULL,
    user_id INT NOT NULL,
    assigned_at DATETIME NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (debate_id) REFERENCES Debates(debate_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    CONSTRAINT UQ_Judge_Per_Debate UNIQUE (debate_id, user_id)
);

-- 比賽歷史表
CREATE TABLE MatchHistory (
    match_id INT PRIMARY KEY IDENTITY(1,1),
    debate_id INT NOT NULL,
    user_id INT NOT NULL,
    result NVARCHAR(10) NOT NULL,  -- win, loss, draw
    rating_before INT NOT NULL,
    rating_after INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (debate_id) REFERENCES Debates(debate_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- 創建索引以提升查詢性能
CREATE INDEX IDX_Users_Rating ON Users(rating DESC);
CREATE INDEX IDX_DebateTopics_Status ON DebateTopics(status);
CREATE INDEX IDX_Debates_Status ON Debates(status);
CREATE INDEX IDX_Rounds_Status ON Rounds(status);
CREATE INDEX IDX_Votes_Round ON Votes(round_id);
CREATE INDEX IDX_JudgeAssignments_Debate ON JudgeAssignments(debate_id);
CREATE INDEX IDX_MatchHistory_User ON MatchHistory(user_id);
