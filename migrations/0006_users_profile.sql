-- CL-UI-57: member profile editing. One optional JSON column holds the
-- member-editable profile fields (experience / region / bio); display_name
-- stays the single editable "nickname" surface (PATCH /api/v1/auth/profile).
ALTER TABLE users ADD COLUMN profile_json TEXT;
