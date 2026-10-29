-- Coordinated tasks and bidirectional referrals, schema v2
CREATE TABLE IF NOT EXISTS agent_tasks (
 id TEXT PRIMARY KEY, title TEXT NOT NULL CHECK(length(trim(title))>0),
 owner TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'queued'
 CHECK(status IN ('queued','claimed','review','completed','failed','cancelled')),
 claimed_by TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_agent_tasks_status ON agent_tasks(status,created_at);
CREATE TABLE IF NOT EXISTS agent_referrals (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 task_id TEXT NOT NULL REFERENCES agent_tasks(id) ON DELETE RESTRICT,
 source TEXT NOT NULL,target TEXT NOT NULL,
 question TEXT NOT NULL CHECK(length(trim(question))>0),question_key TEXT NOT NULL,
 response TEXT,response_status TEXT NOT NULL DEFAULT 'pending'
 CHECK(response_status IN ('pending','answered','blocked')),
 created_at TEXT DEFAULT CURRENT_TIMESTAMP,
 UNIQUE(task_id,source,target,question_key)
);
CREATE INDEX IF NOT EXISTS ix_agent_referrals_task ON agent_referrals(task_id,id);
CREATE TABLE IF NOT EXISTS agent_events (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 task_id TEXT NOT NULL REFERENCES agent_tasks(id) ON DELETE RESTRICT,
 action TEXT NOT NULL,actor TEXT NOT NULL,details_json TEXT NOT NULL DEFAULT '{}',
 created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
