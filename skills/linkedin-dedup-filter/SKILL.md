---
name: linkedin-dedup-filter
display_name: "LinkedIn Dedup Filter"
description: "Deduplicates LinkedIn profile URLs against an already-contacted list and returns up to 25 net-new profiles."
category: sales
icon: filter
skill_type: sandbox
catalog_type: addon
tool_schema:
  name: linkedin_dedup_filter
  description: "Takes a list of LinkedIn profile URLs from a search and a list of already-contacted URLs from a Google Sheet, then returns a deduplicated list of net-new profiles not previously contacted, capped at 25 entries."
  parameters:
    type: object
    properties:
      search_urls:
        type: array
        items:
          type: string
        description: "List of LinkedIn profile URLs returned from the LinkedIn search."
      contacted_urls:
        type: array
        items:
          type: string
        description: "List of LinkedIn profile URLs already contacted, sourced from the Google Sheet."
      cap:
        type: integer
        description: "Maximum number of net-new profiles to return (default 25, max 25)."
        default: 25
    required: [search_urls, contacted_urls]
---
# LinkedIn Dedup Filter
Deduplicates LinkedIn profile URLs against an already-contacted list and returns up to 25 net-new profiles.

## Be Proactive
Call this skill immediately after retrieving LinkedIn search results and the contacted-URLs list from the Google Sheet, before doing any outreach, to ensure you never re-contact the same person.