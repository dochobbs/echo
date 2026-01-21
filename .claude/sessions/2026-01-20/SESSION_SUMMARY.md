# Session Summary - 2026-01-20

## Project
Echo (AI Attending tutor) - `/Users/dochobbs/Downloads/Consult/MedEd/echo`

## Branch
main

## Accomplishments
- Added AGPL-3.0 license to protect the project as open source
- Configured license to allow educational use while preventing proprietary forks
- Updated copyright notice with correct attribution (Michael Hobbs <michael@hobbs.md>)
- Fixed git remote to use SSH (dochobbs) instead of HTTPS

## Commits Made
- `c6c55c9`: DOCS: Add AGPL-3.0 license

## Issues Encountered
- GNU website timeout when fetching license text (resolved by using GitHub's SPDX mirror)
- Git push failed due to HTTPS credential mismatch (resolved by switching to SSH)

## Decisions Made
- Chose AGPL-3.0 over GPL-3.0 because Echo is a web API/service - AGPL's Section 13 covers network use, closing the "SaaS loophole"
- This ensures anyone running a modified Echo as a service must share their source code

## Next Steps
- Continue Echo development
- Consider adding license headers to source files (optional but recommended by AGPL)
