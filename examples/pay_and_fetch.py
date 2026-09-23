#!/usr/bin/env python3
"""Walk through the whole x402 purchase: ask, pay, retry, print the data.

Run it:  python3 pay_and_fetch.py
It will print the payment requirements (the 402 body) and stop before you spend anything:
sending the USDC transfer is your wallet's job. Once you have the transaction hash, pass it:

    python3 pay_and_fetch.py 0xYOUR_TRANSFER_HASH
"""
import base64
import json
import sys
import urllib.error
import urllib.request

BASE = "https://x402-agent.majighufron.workers.dev"
TARGET = f"{BASE}/api/token-report?chain=base&token=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"  # USDC on Base
UA = {"User-Agent": "x402-agent-data-example/1.0"}


def fetch(path, proof=None):
    headers = dict(UA)
    if proof:
        headers["PAYMENT-SIGNATURE"] = proof
    req = urllib.request.Request(path, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode()), dict(r.headers)
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            return e.code, json.loads(body), dict(e.headers)
        except json.JSONDecodeError:
            return e.code, {"raw": body[:400]}, dict(e.headers)


def main():
    tx = sys.argv[1] if len(sys.argv) > 1 else None

    if not tx:
        status, body, headers = fetch(TARGET)
        print(f"HTTP {status}")
        if status != 402:
            print(json.dumps(body, indent=2)[:800])
            return
        offer = body["accepts"][0]
        print("\nPayment required:")
        print(f"  send      {int(offer['maxAmountRequired']) / 10 ** 6} USDC")
        print(f"  to        {offer['payTo']}")
        print(f"  network   {offer['networkLabel']} ({offer['network']})")
        print(f"  asset     {offer['asset']}")
        print("\nThen rerun:")
        print("  python3 pay_and_fetch.py 0xYOUR_TRANSFER_HASH")
        print("\nTip: the free catalogue is at " + BASE + "/api and a truncated sample at " + BASE + "/api/sample")
        return

    proof = base64.b64encode(json.dumps({"txHash": tx}).encode()).decode()
    status, body, headers = fetch(TARGET, proof)
    print(f"HTTP {status}")
    if status == 200:
        print("paidWith:", json.dumps(body.get("paidWith")))
        print("metadata:", json.dumps(body.get("metadata")))
        print("activity:", json.dumps(body.get("activity")))
        print("receipt header X-PAYMENT-RESPONSE:", headers.get("X-PAYMENT-RESPONSE", "")[:80], "…")
    else:
        print(json.dumps(body, indent=2)[:800])


if __name__ == "__main__":
    main()
