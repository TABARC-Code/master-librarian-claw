-- Master Librarian catalogue schema v1. Foreign keys are enforced by the Python connection.
CREATE TABLE IF NOT EXISTS schema_version (
  version INTEGER PRIMARY KEY,
  applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS works (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL CHECK(length(trim(title)) > 0),
  kind TEXT NOT NULL DEFAULT 'unknown',
  description TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS editions (
  id TEXT PRIMARY KEY,
  work_id TEXT NOT NULL REFERENCES works(id) ON DELETE RESTRICT,
  edition_label TEXT,
  language TEXT,
  publisher TEXT,
  published_date TEXT,
  identifiers_json TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS ix_editions_work ON editions(work_id);
CREATE TABLE IF NOT EXISTS file_instances (
  id TEXT PRIMARY KEY,
  edition_id TEXT REFERENCES editions(id) ON DELETE RESTRICT,
  path TEXT NOT NULL UNIQUE,
  size_bytes INTEGER CHECK(size_bytes >= 0),
  sha256 TEXT CHECK(sha256 IS NULL OR length(sha256) = 64),
  observed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS authorities (
  id TEXT PRIMARY KEY,
  preferred_label TEXT NOT NULL,
  authority_type TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS relationships (
  id TEXT PRIMARY KEY,
  subject_id TEXT NOT NULL,
  subject_type TEXT NOT NULL,
  predicate TEXT NOT NULL,
  object_id TEXT NOT NULL,
  object_type TEXT NOT NULL,
  source_id TEXT,
  review_state TEXT NOT NULL DEFAULT 'proposed' CHECK(review_state IN ('proposed','verified','rejected','conflicted'))
);
CREATE INDEX IF NOT EXISTS ix_rel_subject ON relationships(subject_type,subject_id);
CREATE INDEX IF NOT EXISTS ix_rel_object ON relationships(object_type,object_id);
CREATE TABLE IF NOT EXISTS evidence (
  id TEXT PRIMARY KEY,
  entity_type TEXT NOT NULL,
  entity_id TEXT NOT NULL,
  field_name TEXT NOT NULL,
  claim TEXT,
  source_reference TEXT,
  status TEXT NOT NULL DEFAULT 'provisional' CHECK(status IN ('verified','corroborated','inferred','provisional','conflicted','rejected')),
  recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS audit_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  action TEXT NOT NULL,
  entity_type TEXT,
  entity_id TEXT,
  details_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
