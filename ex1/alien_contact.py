import sys
import os
import csv
import json
from pydantic import (
    BaseModel, Field, ValidationError, model_validator, ConfigDict
)
from datetime import datetime
from enum import Enum
from typing import Optional


class ContactType(str, Enum):
    RADIO = "radio"
    VISUAL = "visual"
    PHYSICAL = "physical"
    TELEPATHIC = "telepathic"


class AlienContactModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    contact_id: str = Field(min_length=5, max_length=15, alias="ID")
    timestamp: datetime = Field(
        default_factory=datetime.now, alias="Timestamp"
    )
    location: str = Field(min_length=3, max_length=100, alias="Location")
    contact_type: ContactType = Field(alias="Type")
    signal_strength: float = Field(ge=0.0, le=10.0, alias="Signal")
    duration_minutes: int = Field(ge=1, le=1440, alias="Duration")
    witness_count: int = Field(ge=1, le=100, alias="Witnesses")
    message_received: Optional[str] = Field(
        default=None, max_length=500, alias="Message"
    )
    is_verified: bool = Field(default=False)

    @model_validator(mode="after")
    def check_signal(self) -> "AlienContactModel":
        if not self.contact_id.startswith("AC"):
            raise ValueError("Alien Contact must start with 'AC'")

        if self.contact_type == ContactType.PHYSICAL:
            if not self.is_verified:
                raise ValueError("Physical contact reports must be verified")

        if self.contact_type == ContactType.TELEPATHIC:
            if self.witness_count < 3:
                raise ValueError(
                    "Telepathic contact requires at least 3 witnesses"
                )

        if self.signal_strength > 7:
            if not self.message_received:
                raise ValueError(
                    "Strong signals (> 7.0) should include received messages"
                )

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

    ac_2024_001 = AlienContactModel.model_validate(contact001)
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
        ac_2024_002 = AlienContactModel.model_validate(contact002)
        print(ac_2024_002.contact_id)
    except ValidationError as err:
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
        ac_2024_003 = AlienContactModel.model_validate(contact003)
        print("ID:", ac_2024_003.contact_id)
    except ValidationError as err:
        print(err.errors()[0]['msg'].replace("Value error, ", ""))

    if len(sys.argv) < 2:
        return

    print("\n========================================")
    print("RUN data validation on generated_data/alien_contacts")

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.", file=sys.stderr)
        sys.exit(1)

    raw_records = []
    if file_path.endswith('.csv'):
        with open(file_path, 'r', encoding="utf-8") as file:
            raw_records = list(csv.DictReader(file))

    elif file_path.endswith('.py'):
        import importlib.util
        spec = importlib.util.spec_from_file_location("data_module", file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load module from '{file_path}'")
        data_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(data_module)
        raw_records = getattr(data_module, "ALIEN_CONTACTS", [])

    elif file_path.endswith('.json'):
        with open(file_path, 'r', encoding="utf-8") as file:
            raw_records = json.load(file)

    else:
        print("Unsupported file format.", file=sys.stderr)
        sys.exit(1)

    for idx, row in enumerate(raw_records, start=1):
        try:
            contact = AlienContactModel(**row)
            print(
                f"  Contact [{contact.contact_id}]: ✅ "
                f"{contact.contact_type.value} at {contact.location}"
            )
        except ValidationError as err:
            for e in err.errors():
                field_name = e['loc'][-1] if e['loc'] else 'root'
                print(
                    f"  Contact [{idx}] ❌ INVALID: [{field_name}]: "
                    f"{e['msg'].replace("Value error, ", "")}"
                )


if __name__ == "__main__":
    main()
