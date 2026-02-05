# Changelog - 2026-02-04

## Fixes
- `cab8cfc`: Restore auth token from localStorage on API requests
  - ApiClient.fetch() was not calling ensureInitialized(), so stored JWT
    was never loaded after page refresh. Learners could not see their old cases.
