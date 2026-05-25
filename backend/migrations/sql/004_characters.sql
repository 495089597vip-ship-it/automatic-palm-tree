ALTER TABLE characters
  ADD COLUMN IF NOT EXISTS description TEXT DEFAULT '',
  ADD COLUMN IF NOT EXISTS appearance TEXT DEFAULT '',
  ADD COLUMN IF NOT EXISTS personality TEXT DEFAULT '',
  ADD COLUMN IF NOT EXISTS reference_image_url TEXT DEFAULT '',
  ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW(),
  ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

UPDATE characters
SET description = COALESCE(description, profile, '')
WHERE COALESCE(description, '') = '';
