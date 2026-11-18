# MRO Face Recognition Desktop App — Plan

## Purpose
Used only by Mon Refugee Organization (MRO) staff, in the office, to:
1. **Find a member** among existing member records (1:N search)
2. **Verify identity during aid distribution** (1:1 check; identity only, no aid records)
3. **Prevent duplicate registration** (search all records when someone registers)

Faces come from a live camera when the person is in the office, or from a passport-size portrait they send in.

## Environment
- One main computer: **macOS** (built and tested first); Windows build follows
- No multi-device sync
- Thousands of members/photos
- Live camera in the MVP
- Existing data: Excel member list + OneDrive `Photos` folder
- Some members have more than one photo (`12345_1.jpg`, `12345_2.jpg`)

## Existing data and import

### Excel columns
| Excel column | App field | Use |
|---|---|---|
| MRO Status number | `member_code` | Primary ID, normalised to `MRO-12345` |
| Name | `full_name` | Display, search |
| Gender | `gender` | Display |
| DOB | `date_of_birth` | Tell family members apart; age shown on match cards |
| Date of Issue | `issue_date` | Approximate photo date |
| Renewal Date | `renewal_date` | Status badge: Active / Due soon / Expired |
| Photos (File Paths) | `photo_path` | Primary photo location |

### Photo matching
All of these are linked to `MRO-12345`:
- `12345.jpg`, `12345_1.jpg`, `12345_2.png`, `12345_3.jpeg` (any `_n` suffix, extensions case-insensitive)

Finding files:
1. Use the path in "Photos (File Paths)" if it exists on this computer
2. If the path is from another computer or broken, look for the same file name inside the chosen Photos folder
3. Also collect every `12345` / `12345_n` file in the Photos folder
4. If none found, report "photo not found"

Primary photo (shown on cards):
1. The file in the Excel path, if valid
2. Otherwise `12345` without suffix
3. Otherwise the lowest `_n`
4. Skipped if it fails the quality check; the next best photo becomes primary

Every photo that passes the quality check is stored as a face template for that member.

### ID normalisation
`12345`, `MRO12345`, `MRO-12345`, `mro - 12345` → `MRO-12345`

### Import behaviour
- Excel read with openpyxl/pandas; header row detected, column mapping pre-filled and editable
- Dates parsed from Excel date cells or common text formats (dd/mm/yyyy)
- Runs on a background thread with progress and cancel
- Repeatable: only new or changed rows/photos are processed (hash check)
- The OneDrive source folder is read-only to the app

### Import report
- Excel rows with no photo found
- Photos in the folder with no Excel row
- Duplicate member IDs inside the Excel file
- Invalid or missing dates
- Photos with no face, more than one face, or low quality
- **Photos under the same ID that do not look like the same person** (possible wrong file naming)
- Possible duplicate people across different IDs (every face searched against all others)

## Status and age rules
- Renewal Date drives the member status badge on Find and Verify results
- Expired status is a warning only; the app does not block anything
- Members whose newest photo is old relative to their age (for example, children with an old Date of Issue) are flagged "Photo update recommended"

## OneDrive usage
- The live encrypted database stays in the app's local data folder (`~/Library/Application Support/MRO Face` on macOS), not inside OneDrive
- Encrypted backup file written to a chosen OneDrive folder on demand or on a schedule
- Restore from backup in Settings

## Tech stack
| Layer | Choice |
|---|---|
| Language | Python 3.11+ |
| UI | PySide6 (Qt 6) |
| Detection | YuNet (OpenCV Model Zoo, MIT) |
| Recognition | SFace (OpenCV Model Zoo, Apache 2.0) |
| Runtime | OpenCV DNN (ONNX models) |
| Camera | OpenCV VideoCapture (AVFoundation on macOS) on a QThread |
| Database | SQLCipher (encrypted SQLite) via SQLAlchemy |
| Photo storage | Encrypted thumbnails (Fernet/AES) |
| Key storage | macOS Keychain / Windows Credential Manager via `keyring`, unlocked by app password |
| Excel import | openpyxl / pandas |
| Matching | In-memory NumPy cosine similarity |
| Packaging | PyInstaller; macOS `.app` signed + notarized with camera permission (NSCameraUsageDescription); Windows `.exe` via GitHub Actions |
| Tests | pytest, pytest-qt |

InsightFace pretrained models are not used because their license is non-commercial research only. The engine stays swappable.

## Core workflows

### 1. Register a new member (with duplicate check)
1. Staff enters Name, Gender, DOB, Date of Issue, Renewal Date and records consent
2. App suggests the next free `MRO-xxxxx` ID (editable by admin)
3. Capture face live (several frames, best ones kept) or upload the passport photo
4. Quality check: one face, size, sharpness, frontal pose, lighting
5. Search all existing faces
6. Matches above the duplicate threshold shown side by side (photo, name, DOB, ID) for staff review
7. Staff chooses: new member / existing member / cancel
8. Save encrypted templates + thumbnail; write to the audit log

### 2. Verify identity at aid distribution (1:1)
1. Staff types the member ID (`12345` or `MRO-12345`)
2. Member card shows primary photo, name, gender, age, renewal status
3. Live capture only (no sent-in photos)
4. Compare against **all** of that member's templates; best score used, strict threshold
5. Result: Verified / Not verified / Needs review; staff confirms
6. Only an audit entry is kept (staff, member ID, result, time); no aid details

### 3. Find a member (1:N)
1. Live capture or upload
2. Each member scored by their best-matching template
3. Top 5 members with score, thumbnail, ID, name, age, status
4. Staff opens the profile to confirm

### 4. Add or update a member's photo
1. From the member profile, capture a new live photo
2. App checks it matches the member's existing photos before saving (or admin override)
3. Admin can set any photo as primary or remove a bad photo

## Matching rules
- Separate thresholds: duplicate check (lenient), find (medium), verification (strict)
- Member score = best score across all their photos
- Below threshold = "Unknown"; never force a match
- A human confirms every decision; the app only suggests
- Family resemblance goes to review, never auto-match; DOB and gender shown to help staff decide

## Screens
1. Login
2. Dashboard
3. Import wizard (Excel + Photos folder, column mapping, progress, report)
4. Register member
5. Verify
6. Find member
7. Members library and member profile (photo gallery per member)
8. Duplicate review queue
9. Audit log (admin)
10. Settings, backup/restore, users (admin)

## Data model
- `users`: id, username, password_hash (argon2), role, active
- `members`: id, member_code (`MRO-12345`, unique), full_name, gender, date_of_birth, issue_date, renewal_date, consent_date, consent_by_user_id, created_at, updated_at
- `face_templates`: id, member_id, embedding (BLOB), thumbnail (encrypted), quality_score, source (import/live/upload), source_file_name, source_hash, is_primary, created_at
- `duplicate_reviews`: id, member_a_id, member_b_id, score, decision, decided_by, timestamp
- `audit_logs`: id, user_id, action, target, result, score, timestamp
- `import_runs`: id, started_at, finished_at, counts, report

## Security and data protection
- Offline operation; no network calls from the app
- Encrypted database and thumbnails; password unlock at app start
- macOS FileVault should be on for the main computer
- Roles: admin (import/edit/delete/settings/backup), staff (find/verify/register)
- Auto-lock after idle time; one-click lock
- Audit log of every action
- Consent recorded per member; deletion on request
- Encrypted backups only
- The original Excel file and Photos folder on OneDrive are unencrypted cloud storage; review who has access to them
- Written data-protection policy approved by MRO leadership before go-live (PDPA)

## Build phases
| Phase | Work |
|---|---|
| 0 | Repo, structure, macOS dev environment, CI builds (macOS first, then Windows) |
| 1 | Recognition engine + quality checks + threshold tuning on a sample of real photos (including `_n` photo sets) |
| 2 | Encrypted storage, users/roles, audit log |
| 3 | Import wizard (Excel + Photos) with report and duplicate scan |
| 4 | Register, Find, Verify, Add/Update photo services |
| 5 | Live camera with threading and tracking (macOS camera permission) |
| 6 | UI design: Mobbin research, Impeccable design |
| 7 | UI build and wiring |
| 8 | Backup/restore to OneDrive |
| 9 | Security review, accuracy/bias testing, macOS signing/notarization, Windows build, pilot |

## Project structure
```
mro-face/
  app/
    ui/            screens, widgets, theme
    services/      register, find, verify, review, importer, backup, auth, audit
    engine/        detector, embedder, matcher, quality
    data/          models, repositories, crypto, migrations
    camera/        capture thread, tracker
  models/          yunet.onnx, sface.onnx
  tests/
  packaging/       pyinstaller specs, entitlements, icons
  .github/workflows/
```
