---
name: sheet-dedup-cleanup
display_name: "Sheet Dedup Cleanup"
description: "One-off cleanup of the D2C Food Investor Outreach spreadsheet: removes duplicate rows, fixes dates, sorts by date."
category: sales
skill_type: sandbox
catalog_type: addon
requirements: "httpx>=0.25"
resource_requirements:
  - env_var: GOOGLE_SHEETS_CREDENTIALS_JSON
    name: "Google Sheets Credentials"
    description: "Google OAuth credentials JSON (auto-provided by gateway connection)"
  - env_var: GOOGLE_SHEETS_USER_EMAIL
    name: "Google Account Email"
    description: "Email of the connected Google account"
    optional: true
tool_schema:
  name: sheet_dedup_cleanup
  description: "One-off cleanup of the D2C Food Investor Outreach spreadsheet: removes duplicate LinkedIn URL rows, fixes date formatting, sorts by date. Returns a summary of what was removed."
  parameters:
    type: object
    properties:
      run:
        type: boolean
        description: "Set to true to execute the cleanup"
    required: [run]
---
# Sheet Dedup Cleanup

One-off cleanup skill for the D2C Food Investor Outreach spreadsheet.

Reads the full sheet, deduplicates by normalised LinkedIn URL, fixes date formatting to d-MMM-yyyy, sorts chronologically, and writes back clean data.
