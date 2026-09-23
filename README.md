# x402-agent-data

Paid on-chain data for AI agents (and humans). **Pay per call in USDC on Base over HTTP 402 (x402)** —
no signup, no API key, no account. The money goes straight to the wallet advertised in the 402
response; nothing is held by the service.

- Landing / discovery: <https://x402-agent.majighufron.workers.dev>
- MCP server (remote, streamable HTTP): `https://x402-agent.majighufron.workers.dev/mcp`
- Machine-readable catalogue: `https://x402-agent.majighufron.workers.dev/api`
- Agent instructions: `https://x402-agent.majighufron.workers.dev/llms.txt`

## Services

| Service | Price | What you get |
|---|---|---|
| `token_report` · `GET /api/token-report` | $0.01 | ERC-20 metadata, supply, recent transfer activity, optional pool balance. Chains: Base, Base Sepolia, Robinhood Chain |
| `pool_risk` · `GET /api/pool-risk` | $0.02 | Pool reserves, implied price, constant-product slippage for a given notional |
| `wallet_profile` · `GET /api/wallet-profile` | $0.03 | Transfers in/out, distinct counterparties, first and last block seen |
| `contract_dd` · `GET /api/contract-dd` | $0.05 | Due-diligence signals: risky selectors present in bytecode, owner + renounced status, activity, largest-transfer share |

Free endpoints: `/` discovery · `/api` catalogue · `/llms.txt` agent text · `/api/sample` truncated
report so you can check the data shape before paying · `/mcp` MCP server (the `service_catalog`
tool is free).

## Use it from an MCP client

Add the remote server to any MCP client (Claude Desktop, Cursor, or your own agent):

```json
{
  "mcpServers": {
    "x402-agent-data": {
      "type": "streamable-http",
      "url": "https://x402-agent.majighufron.workers.dev/mcp"
    }
  }
}
```

Tools: `service_catalog` (free), `token_report`, `pool_risk`, `wallet_profile`, `contract_dd`.
Call a paid tool once without `payment_signature` and it returns the payment requirements; pay,
then call again with `payment_signature` = base64 of `{"txHash":"0x…"}`.

## Use it over plain HTTP

```sh
# 1. Ask without paying -> HTTP 402 + payment requirements
curl -s "https://x402-agent.majighufron.workers.dev/api/token-report?chain=base&token=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"

# 2. Send the quoted USDC amount to the payTo address on Base (USDC, 6 decimals)

# 3. Retry with the proof
TX=0x…   # your transfer hash
PROOF=$(printf '{"txHash":"%s"}' "$TX" | base64)
curl -s -H "PAYMENT-SIGNATURE: $PROOF" \
  "https://x402-agent.majighufron.workers.dev/api/token-report?chain=base&token=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
```

A proof is single-use and must be from the last 15 minutes. If the service itself fails (upstream
RPC throttling), it answers `503 retryable: true` and **releases your proof**, so you can call again
without paying twice.

See [`examples/pay_and_fetch.py`](examples/pay_and_fetch.py) for a runnable walkthrough.

## Why it exists

On-chain data is usually sold as a monthly subscription behind an API key. Agent software cannot
fill in signup forms, so this exposes the same data per call: the HTTP 402 response *is* the price
list, and the wallet *is* the identity.

## Honest limits

- Upstream public RPCs throttle shared egress IPs, so a call can occasionally answer `503`;
  proofs are released so retries are free.
- `contract_dd` reports **signals**, not verdicts: selector presence says what is in the bytecode,
  not how it behaves. Proxies and dead code both hide intent.
- Payment uses a plain USDC transfer plus a proof header (self-verified). It is not the EIP-3009
  facilitator flow yet.

## License

MIT
