import os, json, re

try:
    raw = os.environ.get("INPUT_JSON") or "{}"
    inp = json.loads(raw)

    investor_name = (inp.get("investor_name") or os.environ.get("INPUT_INVESTOR_NAME", "")).strip()
    headline = (inp.get("headline") or os.environ.get("INPUT_HEADLINE", "")).strip()
    focus_area = (inp.get("focus_area") or os.environ.get("INPUT_FOCUS_AREA", "")).strip()

    if not investor_name:
        raise ValueError("'investor_name' is required.")
    if not headline:
        raise ValueError("'headline' is required.")

    first_name = investor_name.split()[0]

    # Combine headline and focus_area for keyword analysis
    combined = f"{headline} {focus_area}".lower()

    # --- Build a natural, specific first sentence ---
    # Rules:
    # - Never say "food and beverage" or "F&B"
    # - Never mention beverages
    # - Never say "would love to be on your radar"
    # - End with "Would love to connect."
    # - Say "premium jarred bean brand" only, never brand name
    # - Personalise to their actual profile

    # Detect what they do from their headline/focus
    # Priority: use the most specific signal available

    detail = None

    # Operator/founder who also invests
    if any(x in combined for x in ["founder", "operator", "built", "building"]) and any(x in combined for x in ["invest", "angel", "backing", "backed"]):
        if "cpg" in combined:
            detail = "your experience building and investing in CPG brands"
        elif "consumer" in combined:
            detail = "your experience building and backing consumer brands"
        else:
            detail = "your experience building and investing in consumer food brands"

    # Grocery / retail angle
    elif any(x in combined for x in ["grocery", "retail", "shelf", "supermarket"]):
        detail = "your experience in grocery and consumer food"

    # Wellness / nutrition angle
    elif any(x in combined for x in ["wellness", "nutrition", "health food", "better-for-you", "better for you"]):
        detail = "your focus on wellness and consumer food brands"

    # DTC angle
    elif any(x in combined for x in ["d2c", "direct-to-consumer", "direct to consumer", "dtc"]):
        detail = "your focus on early-stage DTC consumer brands"

    # CPG angle
    elif "cpg" in combined:
        detail = "your focus on early-stage CPG brands"

    # Food + angel/seed investing
    elif any(x in combined for x in ["food", "fmcg"]) and any(x in combined for x in ["angel", "seed", "pre-seed", "invest", "backing", "venture"]):
        detail = "your experience investing in food and consumer brands"

    # Angel / seed investor (generic but stage-aware)
    elif any(x in combined for x in ["angel", "pre-seed", "pre seed"]):
        detail = "your experience backing early-stage consumer brands"
    elif "seed" in combined and any(x in combined for x in ["invest", "fund", "venture", "backing"]):
        detail = "your focus on seed-stage consumer brands"

    # Consumer brand investor
    elif "consumer" in combined and any(x in combined for x in ["invest", "fund", "venture", "backing", "brand"]):
        detail = "your focus on early-stage consumer brands"

    # Fallback
    else:
        detail = "your experience in early-stage consumer investing"

    # Assemble the message using the required formula
    body = (
        f"I'm a Registered Nutritionist raising pre-seed for a premium jarred bean brand "
        f"launching in LA, backed by my 190k+ owned audience across TikTok/IG/YT. Would love to connect."
    )
    note = f"Hi {first_name}, I saw {detail}. {body}"

    # Safety trim if over 300 chars
    if len(note) > 300:
        # Try a shorter detail
        note = (
            f"Hi {first_name}, I saw your focus on early-stage consumer brands. {body}"
        )
    if len(note) > 300:
        note = note[:297] + "..."

    print(json.dumps({
        "connection_note": note,
        "character_count": len(note),
        "investor_name": investor_name,
    }))

except Exception as e:
    print(json.dumps({"error": str(e)}))
