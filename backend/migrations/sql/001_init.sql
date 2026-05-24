CREATE TABLE IF NOT EXISTS projects (
  id SERIAL PRIMARY KEY,
  name VARCHAR(120) UNIQUE NOT NULL,
  description TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS characters (
  id SERIAL PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  profile TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS scenes (
  id SERIAL PRIMARY KEY,
  title VARCHAR(120) NOT NULL,
  summary TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS shots (
  id SERIAL PRIMARY KEY,
  episode INTEGER NOT NULL,
  scene_no VARCHAR(50) NOT NULL,
  shot_no VARCHAR(50) NOT NULL,
  duration_sec INTEGER NOT NULL,
  aspect_ratio VARCHAR(30) NOT NULL,
  shot_size VARCHAR(30) NOT NULL,
  camera_angle VARCHAR(30) NOT NULL,
  action TEXT DEFAULT '',
  dialogue TEXT DEFAULT '',
  visual_requirements TEXT DEFAULT '',
  negative_prompt TEXT DEFAULT '',
  status VARCHAR(30) DEFAULT 'draft'
);

CREATE TABLE IF NOT EXISTS prompt_templates (
  id SERIAL PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  content TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS generation_tasks (
  id SERIAL PRIMARY KEY,
  task_type VARCHAR(60) NOT NULL,
  payload TEXT NOT NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'queued',
  result TEXT DEFAULT '',
  provider VARCHAR(40) DEFAULT 'mock',
  request_params TEXT DEFAULT '',
  response_payload TEXT DEFAULT '',
  cost_estimate NUMERIC(12,6) DEFAULT 0,
  error_reason TEXT DEFAULT '',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS assets (
  id SERIAL PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  file_type VARCHAR(30) DEFAULT 'image',
  object_key VARCHAR(255) UNIQUE NOT NULL
);
