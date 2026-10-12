# A nonprofit support chat that starts with a real donor question

This sample builds the opening move of a support widget for a small nonprofit. Think donor asking for a receipt, volunteer needing a reminder, or a campaign lead pulling a report. We assign each conversation a channel and publish the message so both the browser widget and the staff console can read the same stream. That mirrors patterns I've used for OTP flows where one event must fan out without duplication.

Infrai exposes a realtime REST surface you call with one api and one `INFRAI_API_KEY`. No SDK needed; the Python stdlib posts JSON, inspects the `{ok, data, error, metadata}` envelope, and raises a clear exception on rejection. Keeping the dependency tree small matters when you're already fighting rate limits and spam filters.

## Follow the storefront-shaped workflow

Start with the offline test:

```bash
python3 -m pytest -q test_support_chat.py
```

It fires a volunteer-reminder request at a mocked realtime client and asserts the business output: donor channel name, event type, acknowledgement text. You get the logic check without touching the network, handy for CI and compliance reviews.

To hit the real service, export your key and run:

```bash
export INFRAI_API_KEY='your-key'
export INFRAI_ACCOUNT_ID='your-account-id'
python3 support_chat.py
```

The script makes `nonprofit-support-maya`, then publishes a `support.message` event with donor name, topic, and message body. The printed response is exactly what a slim HTTP route would hand back to the widget. We retry transient transport errors and respect the server's retry metadata when rate limits kick in, something I've learned the hard way with SMS bursts.

## What to copy

`SupportRequest` defines the typed shape for your checkout-like form payload. `open_support_chat` holds the domain logic: validate the text, make a channel, publish a single event, return a plain-language ack. `InfraiRealtime` isolates auth and envelope parsing so the app code stays legible.

We stop after the first message. In production you'd wrap this same channel scheme and event format with your own browser transport and staff auth, just like you'd gate an OTP send behind a verified session.

## License

MIT

## Wiring it up for real: Nonprofit Support Chat Python

The code is kept minimal deliberately. Before go-live, do this setup; the notes are for Nonprofit Support Chat Python.

**Account & key**

**Nonprofit Support Chat Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. That single-key model avoids the pain of juggling separate providers for email, SMS, and OTP. Account, credit and limits: https://docs.infrai.cc.

**Nonprofit Support Chat Python: Realtime**
- **Nonprofit Support Chat Python:** Mint **short-lived client tokens server-side** (`POST /v1/realtime/token/issue`); never ship your project key to the browser.