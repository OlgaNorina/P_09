from pydantic import BaseModel, Field, model_validator, ConfigDict
from datetime import datetime
from enum import Enum
from typing import Optional


class ContactType(str, Enum):
    RADIO = "radio"
    VISUAL = "visual"
    PHYSICAL = "physical"
    TELEPATHIC = "telepathic"


class AlienContactModel(BaseModel):
    model_config: str = ConfigDict(populate_by_name=True)

    contact_id: str = Field(min_length=5, max_length=15, alias="ID")
    timestamp: datetime = datetime.now()
    location: str = Field(min_length=3, max_length=100, alias="Location")
    contact_type: ContactType = Field(alias="Type")
    signal_strength: float = Field(ge=0.0, le=10.0, alias="Signal")
    duration_minutes: int = Field(ge=1, le=1440, alias="Duration")
    witness_count: int = Field(ge=1, le=100, alias="Witnesses")
    message_received: Optional[str] = Field(default=None, max_length=500, alias="Message")
    is_verified: bool = Field(default=False)


    @model_validator(mode="after")
    def check_signal(self) -> "AlienContactModel":
        if not self.contact_id.startswith("AC"):
            raise ValueError("Alien Contac must start with 'AC'")

        if self.contact_type == ContactType.PHYSICAL:
            if not self.is_verified:
                raise ValueError("Physical contact reports must be verified")

        if self.contact_type == ContactType.TELEPATHIC:
            if self.witness_count < 3:
                raise ValueError("Telepathic contact requires at least 3 witnesses")

        if self.signal_strength > 7:
            if not self.message_received:
                raise ValueError("Strong signals (> 7.0) should include received messages")

        return self


def main() -> None:
    print("Alien Contact Log Validation")
    print("========================================")
    print("Valid contact report:")
    
    contact001 = {
        "ID": "AC_2024_001",
        "Type": "radio",
        "Location": "Area 51, Nevada",
        "Signal": 8.5,
        "Duration": 45,
        "Witnesses": 5,
        "Message": "Greetings from Zeta Reticuli",
            }

    ac_2024_001: AlienContactModel = AlienContactModel(**contact001)
    print("ID:", ac_2024_001.contact_id)
    print("Type:", ac_2024_001.contact_type.value)
    print("Location:", ac_2024_001.location)
    print(f"Signal: {ac_2024_001.signal_strength}/10")
    print("Duration:", ac_2024_001.duration_minutes, "minutes")
    print("Witnesses:", ac_2024_001.witness_count)
    print(f"Message: '{ac_2024_001.message_received}'")

    print("\n========================================")
    print("Expected validation error:")

    contact002 = {
        "ID": "AC_2024_002",
        "Type": "telepathic",
        "Location": "Area 51, Nevada",
        "Signal": 8.5,
        "Duration": 45,
        "Witnesses": 2,
        "Message": "Greetings from Zeta Reticuli",
            }

    try:
        ac_2024_002: AlienContactModel = AlienContactModel(**contact002)
    except ValueError as err:
        print(err.errors()[0]['msg'].replace("Value error, ", ""))


    print("\n========================================")
    print("Expected validation error:")

    contact003 = {
        "ID": "AC_2024_002",
        "Type": "telepathic",
        "Location": "Area 51, Nevada",
        "Signal": 8.5,
        "Duration": 45,
        "Witnesses": 3,
        }

    try:
        ac_2024_002: AlienContactModel = AlienContactModel(**contact003)
    except ValueError as err:
        print(err.errors()[0]['msg'].replace("Value error, ", ""))


if __name__ == "__main__":
    main()
