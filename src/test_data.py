from data_classes import *
from utils import adapt_activity_data_to_member

address = Address("street", 1, 0000, "city")
parent = Person("Voornaam ouder ", "Achternaam ouder", "xx.xx.xx-xxx.xx", address)
member = Member(
    "Voornaam lid",
    "Achternaam lid",
    "xx.xx.xx-xxx.xx",
    address,
    date(2011, 7, 7),
    2011,
    False,
)

activities = Activities()
activities.add_activity(
    adapt_activity_data_to_member(
        Activity(date(2024, 2, 23), date(2024, 2, 25), 50.0), member, 14
    )
)
activities.add_activity(
    adapt_activity_data_to_member(
        Activity(date(2024, 4, 26), date(2024, 4, 28), 40.0), member, 14
    )
)
activities.add_activity(
    adapt_activity_data_to_member(
        Activity(date(2024, 7, 3), date(2024, 7, 15), 156.0), member, 14
    )
)
