"""Meta WhatsApp Cloud API Debug Sender Script

Prints full Meta API error response for diagnosis.
"""

import json
import urllib.request
import urllib.error

token = "EAAO2IrlYU4wBSN4dNl3pMOeSqBZAkXFITHmx6TRWoquXbbFFGMgLZALJIxLJ6KcHGoQVCn3RxMzWkgwNvl0e8AjZBkMmhgfroJLwk7WOAmPsgYLoUlqpCeBus12HsErmlyRs3VqxaBHTAZB8UUzcN7i0W1H8nDH0tY5d7XnXH5ntxQgBBvUBaTNjmvm1IpSicgZDZD"
phone_id = "1212954768570236"

recipients = [
    ("917338909974", "Sri Balagi"),
    ("919092683747", "Porselvi"),
]

for phone_number, name in recipients:
    try:
        url = f"https://graph.facebook.com/v25.0/{phone_id}/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "template",
            "template": {
                "name": "hello_world",
                "language": {"code": "en_US"}
            }
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        with urllib.request.urlopen(req, timeout=15) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
        print(f"SUCCESS for {phone_number}:", resp_data)
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8")
        print(f"HTTP ERROR {exc.code} for {phone_number}:", error_body)
    except Exception as exc:
        print(f"ERROR for {phone_number}: {exc}")
