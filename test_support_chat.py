from support_chat import SupportRequest, open_support_chat


class FakeRealtime:
    def __init__(self):
        self.created = []
        self.published = []

    def create_channel(self, channel):
        self.created.append(channel)
        return {"ok": True}

    def publish(self, channel, event, data, account_id):
        self.published.append((channel, event, data, account_id))
        return {"ok": True}


def test_support_message_creates_channel_and_acknowledges_topic():
    fake = FakeRealtime()
    result = open_support_chat(SupportRequest("Maya Chen", "volunteer reminder", "When is Saturday's shift?"), fake, "acct-1")
    assert result.channel == "nonprofit-support-maya-chen"
    assert result.acknowledgement.endswith("volunteer reminder.")
    assert fake.published[0][1] == "support.message"
