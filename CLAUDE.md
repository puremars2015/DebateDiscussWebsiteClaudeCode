# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **1v1 text-based debate platform** where users authenticate via Line Login. The platform supports topic submission (with official approval), round-based debates, weighted voting, and an Elo-based ranking system.

**Tech Stack:**
- Backend: Python Flask (REST API)
- Frontend: Native HTML + JavaScript with Tailwind CSS
- Database: SQL Server
- Authentication: Line Login + JWT
- Deployment: Windows/Linux Server with IIS or Nginx

## Core Architecture

### User Roles
- **Guests**: View public debates and records (no voting/topic submission)
- **Players**: Line-authenticated users who can submit topics, participate in 1v1 debates, vote, and earn ratings
- **Admins**: Review topics, manage debates, and make manual judgments in tie situations

### Debate Flow State Machine

Each debate follows a strict state progression:

**Debate States**: `NEW` → `ONGOING` → `FINISHED`

**Round States** (per round):
1. `WAIT_PROS_STATEMENT` - Pro side publishes main argument
2. `WAIT_CONS_QUESTIONS` - Con side asks questions
3. `WAIT_PROS_REPLY` - Pro side responds
4. `WAIT_CONS_STATEMENT` - Con side publishes main argument
5. `WAIT_PROS_QUESTIONS` - Pro side asks questions
6. `WAIT_CONS_REPLY` - Con side responds
7. `WAIT_VOTING` - Open voting period (time-limited, e.g., 24 hours)
8. `VOTING_CLOSED` - System tallies votes
9. `ROUND_RESULT` - Determine winner and check end conditions

### Victory Conditions
- **Instant win**: ≥70% of weighted votes in any round
- **Consecutive wins**: 3 rounds in a row
- **Maximum rounds**: 5 rounds (admin manually decides if still tied)

### Voting System
- Regular player vote: weight = 1
- Judge vote: weight = 10
- Voting is NOT real-time; votes are tallied after time window closes
- One vote per user per round (enforced by `UNIQUE` constraint)

### Rating System
Uses **Elo Rating** algorithm:
```
R_new = R_old + K * (S - E)
```
- `K` = 32 (adjustment factor)
- `S` = actual result (win=1, draw=0.5, loss=0)
- `E` = expected win rate = 1 / (1 + 10^((R_opponent - R_self) / 400))

Initial rating: 1500

## Database Schema

### Key Tables
- **Users**: `user_id`, `line_id` (unique), `nickname`, `avatar`, `rating`, `wins`, `losses`, `is_admin`
- **DebateTopics**: `topic_id`, `title`, `description`, `side_pros`, `side_cons`, `rules` (JSON), `status` (pending/approved/rejected), `created_by`
- **Debates**: `debate_id`, `topic_id`, `pros_user_id`, `cons_user_id`, `status`, `round_count`, `winner_id`
- **Rounds**: `round_id`, `debate_id`, `round_number`, `pros_statement`, `cons_questions` (JSON array), `pros_reply`, `cons_statement`, `pros_questions`, `cons_reply`, `status`
- **Votes**: `vote_id`, `round_id`, `voter_id`, `side_voted`, `is_judge`, `weight` - with `UNIQUE(round_id, voter_id)` constraint
- **JudgeAssignments**: `judge_id`, `debate_id`, `user_id`
- **MatchHistory**: `match_id`, `debate_id`, `user_id`, `result`, `rating_before`, `rating_after`

### Important Constraints
- Questions stored as JSON arrays in `cons_questions` and `pros_questions` fields
- Rules stored as JSON in `DebateTopics.rules` (e.g., `{"word_limit": 500, "time_limit_hours": 24}`)
- One vote per user per round enforced via unique constraint

## API Structure

All authenticated endpoints require JWT token: `Authorization: Bearer <token>`

### Authentication
- `POST /api/auth/login` - Line OAuth login, returns JWT

### Users
- `GET /api/users/me` - Current user profile
- `GET /api/users/{id}` - Public user profile

### Topics
- `POST /api/topics/apply` - Submit topic for approval
- `GET /api/topics` - List topics (filter by status)

### Debates
- `POST /api/debates/create` - Admin creates debate and assigns players
- `GET /api/debates/{id}` - Get debate info

### Rounds
- `POST /api/rounds/{round_id}/pros_statement` - Pro publishes statement
- `POST /api/rounds/{round_id}/cons_questions` - Con submits questions
- `POST /api/rounds/{round_id}/pros_reply` - Pro responds
- `POST /api/rounds/{round_id}/cons_statement` - Con publishes statement
- `POST /api/rounds/{round_id}/pros_questions` - Pro submits questions
- `POST /api/rounds/{round_id}/cons_reply` - Con responds
- `GET /api/rounds/{round_id}` - Get round content

### Voting
- `POST /api/rounds/{round_id}/vote` - Submit vote (system auto-calculates weight)
- `GET /api/rounds/{round_id}/results` - Get voting results with percentages

### Ranking
- `GET /api/ranking` - Leaderboard by Elo rating + win rate

### Admin
- `GET /api/admin/topics/pending` - List pending topics
- `POST /api/admin/topics/{id}/approve` - Approve topic
- `POST /api/admin/topics/{id}/reject` - Reject topic
- `POST /api/admin/debates/{id}/force_end` - Manual debate termination

## Development Notes

### Elo Calculation Example (Python)
```python
def calculate_elo(rating_a, rating_b, score_a, score_b, k=32):
    expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    expected_b = 1 / (1 + 10 ** ((rating_a - rating_b) / 400))

    new_a = rating_a + k * (score_a - expected_a)
    new_b = rating_b + k * (score_b - expected_b)

    return round(new_a), round(new_b)
```

### Vote Tallying (SQL Server)
```sql
SELECT
    side_voted,
    SUM(weight) AS total_votes
FROM Votes
WHERE round_id = @round_id
GROUP BY side_voted;
```

### State Transitions
- System must automatically advance states after each action
- Use scheduled tasks (cron/scheduler) to check voting deadlines
- Track consecutive wins to detect 3-win victory condition
- Maximum 5 rounds enforced before requiring admin intervention

### Anti-Cheating Measures
- Line Login required (real-name authentication)
- One vote per user per round (database constraint)
- IP and device fingerprint tracking recommended

## No Real-Time Requirements
- ❌ No WebSocket or Socket.IO needed
- ✅ Voting is batch-processed after time window closes
- ✅ Debate proceeds in asynchronous turns (not live chat)
