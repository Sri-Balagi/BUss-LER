"""Live Meta WhatsApp Cloud API Message Sender Script for 917338909974"""

import json
import urllib.request

token = "EAAO2IrlYU4wBSN4dNl3pMOeSqBZAkXFITHmx6TRWoquXbbFFGMgLZALJIxLJ6KcHGoQVCn3RxMzWkgwNvl0e8AjZBkMmhgfroJLwk7WOAmPsgYLoUlqpCeBus12HsErmlyRs3VqxaBHTAZB8UUzcN7i0W1H8nDH0tY5d7XnXH5ntxQgBBvUBaTNjmvm1IpSicgZDZD"
phone_id = "1212954768570236"
target_number = "916380909423"

try:
    url = f"https://graph.facebook.com/v25.0/{phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": target_number,
        "type": "text",
        "text": {
            "body": "Hello Sri Balagi! This is a live message sent from BizOS Platform via Meta WhatsApp Cloud API (+91 84384 26511). Hope you are doing great! 🚀✨"
        },
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    print(f"Connecting to Meta Cloud API for WhatsApp delivery to {target_number}...")
    with urllib.request.urlopen(req, timeout=15) as resp:
        resp_data = json.loads(resp.read().decode("utf-8"))

    print(f"SUCCESS: REAL LIVE WHATSAPP MESSAGE DELIVERED TO {target_number}!")
    print("Meta API Response:", json.dumps(resp_data))
except Exception as exc:
    print(f"ERROR for {target_number}: {exc}")
