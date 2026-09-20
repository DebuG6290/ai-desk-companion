from core.conversation import ConversationManager


def test_conversation_starts_with_system_prompt():
    conversation = ConversationManager()

    messages = conversation.get_messages()

    assert messages[0]["role"] == "system"
    assert "Deskbot" in messages[0]["content"]


def test_conversation_stores_messages():
    conversation = ConversationManager()

    conversation.add_user_message(
        "I have an exam tomorrow."
    )

    conversation.add_assistant_message(
        "Which subject?"
    )

    conversation.add_user_message(
        "Finance."
    )

    messages = conversation.get_messages()

    assert len(messages) == 4

    assert messages[1]["content"] == (
        "I have an exam tomorrow."
    )

    assert messages[2]["content"] == (
        "Which subject?"
    )

    assert messages[3]["content"] == "Finance."


def test_conversation_trims_old_messages():
    conversation = ConversationManager(
        max_messages=4
    )

    conversation.add_user_message("one")
    conversation.add_assistant_message("two")
    conversation.add_user_message("three")
    conversation.add_assistant_message("four")
    conversation.add_user_message("five")

    messages = conversation.get_messages()

    assert len(messages) == 5
    assert messages[0]["role"] == "system"

    contents = [
        message["content"]
        for message in messages[1:]
    ]

    assert contents == [
        "two",
        "three",
        "four",
        "five",
    ]


def test_conversation_clear():
    conversation = ConversationManager()

    conversation.add_user_message(
        "Hello Deskbot"
    )

    conversation.clear()

    messages = conversation.get_messages()

    assert len(messages) == 1
    assert messages[0]["role"] == "system"
