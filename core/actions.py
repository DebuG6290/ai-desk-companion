class ActionTypes:
    IGNORE = "IGNORE"
    EXPRESS = "EXPRESS"
    ASK = "ASK"
    SPEAK = "SPEAK"
    DISPLAY = "DISPLAY"


class ActionIntents:
    GREET_OWNER = "GREET_OWNER"
    NOTICE_UNKNOWN_PERSON = "NOTICE_UNKNOWN_PERSON"
    ASK_UNKNOWN_PERSON_TO_INTRODUCE = (
        "ASK_UNKNOWN_PERSON_TO_INTRODUCE"
    )


class ActionPriorities:
    LOW = 10
    NORMAL = 50
    HIGH = 80
    CRITICAL = 100
