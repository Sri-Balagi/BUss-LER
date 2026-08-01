"""Fetch Display Phone Number from Meta Graph API"""

import json
import urllib.request

token = "EAAO2IrlYU4wBSN4dNl3pMOeSqBZAkXFITHmx6TRWoquXbbFFGMgLZALJIxLJ6KcHGoQVCn3RxMzWkgwNvl0e8AjZBkMmhgfroJLwk7WOAmPsgYLoUlqpCeBus12HsErmlyRs3VqxaBHTAZB8UUzcN7i0W1H8nDH0tY5d7XnXH5ntxQgBBvUBaTNjmvm1IpSicgZDZD"
phone_id = "1212954768570236"

try:
    url = f"https://graph.facebook.com/v25.0/{phone_id}?fields=display_phone_number,verified_name,quality_rating,code_verification_status"
    headers = {"Authorization": f"Bearer {token}"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    print("META_PHONE_DETAILS:", json.dumps(data))
except Exception as exc:
    print("ERROR:", exc)
