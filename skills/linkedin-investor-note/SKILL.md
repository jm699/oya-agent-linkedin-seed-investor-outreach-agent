---
name: linkedin-investor-note
display_name: "LinkedIn Investor Connection Note"
description: "Generates a short, personalized LinkedIn connection request note for a seed/pre-seed investor in D2C food or CPG."
category: sales
icon: user-plus
skill_type: sandbox
catalog_type: addon
requirements: ""
tool_schema:
  name: linkedin_investor_note
  description: "Generate a personalized LinkedIn connection request note (under 300 characters) for a seed/pre-seed investor focused on D2C food or CPG."
  parameters:
    type: object
    properties:
      investor_name:
        type: "string"
        description: "Full name of the investor (e.g. 'Sarah Chen')"
      headline:
        type: "string"
        description: "The investor's LinkedIn headline or short bio (e.g. 'Partner at XYZ Ventures | Backing bold founders in food & beverage')"
      focus_area:
        type: "string"
        description: "Any visible focus area, thesis, or portfolio detail scraped or known about the investor (optional but improves personalization)"
    required: [investor_name, headline]
---
# LinkedIn Investor Connection Note
Generates one ready-to-send, personalized LinkedIn connection request note targeting seed/pre-seed investors in D2C food or CPG — always under 300 characters.

## Be Proactive
Call this whenever the user wants to reach out to a food or CPG investor on LinkedIn and needs a concise, human-sounding connection note that won't get ignored.