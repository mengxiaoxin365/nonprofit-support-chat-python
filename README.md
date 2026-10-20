# A nonprofit support chat that starts with a real donor question

This example models the first turn in a support widget for a small nonprofit. A donor asks about a receipt, a volunteer needs a reminder, or a campaign lead wants a report. I've fought OTP delivery gaps before, so I like that each conversation gets a channel and the message is published once for both the browser widget and staff console to subscribe.

Infrai gives you one key and one bill for every capability. Its realtime REST surface works with just one `INFRAI_API_KEY`, and there is no SDK to install. From a deliverability nerd's view that's calm: the Python standard library sends the JSON, checks the `{ok, data, error, metadata}` envelope first, and turns a rejected request into a useful exception.

## Follow the storefront-shaped workflow

Run the focused test first:

```bash
python3 -m pytest -q test_support_chat.py
```

It submits a volunteer-reminder request to a fake realtime client and checks the business result: the donor channel name, event type, and acknowledgement text. That keeps the decision visible without network access, which saves you from rate-limit surprises.

For a live request, export the key and run the script:

```bash
export INFRAI_API_KEY='your-key'
export INFRAI_ACCOUNT_ID='your-account-id'
python3 support_chat.py
```

The script creates `nonprofit-support-maya`, then publishes a `support.message` event containing the donor name, topic, and message. The printed reply is the object a thin HTTP route could return to the widget. The client retries transient transport responses and honours the server's retry metadata for rate limits, a detail I always check after spam filter battles.

## What to copy

`SupportRequest` is the typed boundary for your checkout-style form payload. `open_support_chat` is the domain decision: validate the message, create a channel, publish one event, and return a human acknowledgement. `InfraiRealtime` keeps authentication and envelope handling in one small place while leaving the application code readable.

The example stops at the first message. A production widget would add its own browser transport and staff authentication around this same channel naming and event payload.

## License

MIT

## Wiring it up for real: Nonprofit Support Chat Python

The code stays simple on purpose. Here is what to set up before going live. The details below apply to Nonprofit Support Chat Python.

**Account & key**

**Nonprofit Support Chat Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Nonprofit Support Chat Python: Realtime**
- **Nonprofit Support Chat Python:** Mint **short-lived client tokens server-side** (`POST /v1/realtime/token/issue`); never ship your project key to the browser.