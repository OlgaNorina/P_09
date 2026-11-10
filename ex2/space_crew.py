import sys
import os
import csv
import json
from pydantic import BaseModel, Field, model_validator, ValidationError
from enum import Enum
from datetime import datetime
from typing_extensions import Self


class RankType(str, Enum):
    CADET = "cadet"
    OFFICER = "officer"
    LIEUTENANT = "lieutenant"
    CAPTAIN = "captain"
    COMMANDER = "commander"


class CrewMemberModel(BaseModel):
    member_id: str = Field(min_length=3, max_length=10)
    name: str = Field(min_length=2, max_length=50)
    rank: RankType
    age: int = Field(ge=18, le=80)
    specialization: str = Field(min_length=3, max_length=30)
    years_experience: int = Field(ge=0, le=50)
    is_active: bool = Field(default=True)


class SpaceMissionModel(BaseModel):
    mission_id: str = Field(min_length=5, max_length=15)
    mission_name: str = Field(min_length=3, max_length=100)
    destination: str = Field(min_length=3, max_length=50)
    launch_date: datetime = Field(...)
    duration_days: int = Field(ge=1, le=3650)
    crew: list[CrewMemberModel] = Field(min_length=1, max_length=12)
    mission_status: str = Field(default="planned")
    budget_millions: float = Field(ge=1.0, le=10000.0)

    @model_validator(mode="after")
    
    def mission_validation_rules(self) -> Self:
        if not self.mission_id.startswith("M"):
            raise ValueError("Mission ID must start with 'M'")

        ranks: list[str] = [member.rank for member in self.crew]

        if RankType.COMMANDER not in ranks and RankType.CAPTAIN not in ranks:
            raise ValueError(
                "Mission must have at least one Commander or Captain"
            )

        counter: int = 0
        if self.duration_days > 365:
            for member in self.crew:
                if member.years_experience >= 5:
                    counter += 1
            if counter / len(self.crew) < 0.5:
                raise ValueError(
                    "Long missions (> 365 days) need 50% experienced crew "
                    "(5+ years)"
                )
            if any(not member.is_active for member in self.crew):
                raise ValueError("All crew members must be active")

        return self


def main() -> None:
    print("Space Mission Crew Validation")
    print("=========================================")
    print("Valid mission created:")
    content_mars = {
        "mission_name": "Mars Colony Establishment",
        "mission_id": "M2024_MARS",
        "destination": "Mars",
        "duration_days": 900,
        "budget_millions": 2500,
        "crew": [
            {
                "member_id": "001",
                "name": "Sarah Connor",
                "rank": "commander",
                "age": 50,
                "specialization": "Mission Command",
                "years_experience": 20,
            },
            {
                "member_id": "002",
                "name": "John Smith",
                "rank": "lieutenant",
                "age": 45,
                "specialization": "Navigation",
                "years_experience": 15,
            },
            {
                "member_id": "003",
                "name": "Alice Johnson",
                "rank": "officer",
                "age": 20,
                "specialization": "Engineering",
                "years_experience": 2,
            }
        ],
        "launch_date": '2024-05-20T15:30:00'
    }

    mars_crew: SpaceMissionModel = SpaceMissionModel.model_validate(content_mars)

    print("Mission:", mars_crew.mission_name)
    print("ID:", mars_crew.mission_id)
    print("Destination:", mars_crew.destination)
    print("Duration:", mars_crew.duration_days, "days")
    print(f"Budget: ${mars_crew.budget_millions}.0M")
    print("Crew size:", len(mars_crew.crew))
    print("Crew members:")
    for i in range(len(mars_crew.crew)):
        member: str = mars_crew.crew[i]
        print(
            f"- {member.name} ({member.rank.value}) - "
            f"{member.specialization.capitalize()}"
        )

    content_saturn1 = {
            "mission_name": "Saturn rings",
            "mission_id": "M2025_SATURN",
            "destination": "Saturn rings",
            "duration_days": 1500,
            "budget_millions": 5000,
            "crew": [
                {
                    "member_id": "002",
                    "name": "Alice Johnson",
                    "rank": "officer",
                    "age": 20,
                    "specialization": "Engineering",
                    "years_experience": 2,
                },
                {
                    "member_id": "002",
                    "name": "John Smith",
                    "rank": "lieutenant",
                    "age": 45,
                    "specialization": "Navigation",
                    "years_experience": 15,
                },
                ],
            "launch_date": '2024-05-20T15:30:00'
        }

    print("\n=========================================")
    print("Expected validation error:")
    try:
        saturn_crew1: SpaceMissionModel = SpaceMissionModel.model_validate(content_saturn1)
        print("Mission:", saturn_crew1.mission_name)
    except ValidationError as err:
        print(err.errors()[0]['msg'].replace("Value error, ", ""))

    print("\n=========================================")
    print("Expected validation error:")

    content_saturn2 = {
            "mission_name": "Saturn rings",
            "mission_id": "M2025_SATURN",
            "destination": "Saturn rings",
            "duration_days": 1500,
            "budget_millions": 5000,
            "crew": [
                {
                    "member_id": "001",
                    "name": "Sarah Connor",
                    "rank": "commander",
                    "age": 50,
                    "specialization": "Mission Command",
                    "years_experience": 20,
                },
                {
                    "member_id": "002",
                    "name": "John Smith",
                    "rank": "lieutenant",
                    "age": 45,
                    "specialization": "Navigation",
                    "years_experience": 2,
                },
                {
                    "member_id": "003",
                    "name": "Alice Johnson",
                    "rank": "officer",
                    "age": 20,
                    "specialization": "Engineering",
                    "years_experience": 2,
                }
            ],
            "launch_date": '2024-05-20T15:30:00'
        }

    try:
        saturn_crew2: SpaceMissionModel = SpaceMissionModel.model_validate(content_saturn2)
        print("Mission:", saturn_crew2.mission_name)
    except ValidationError as err2:
        print(err2.errors()[0]['msg'].replace("Value error, ", ""))

    print("\n=========================================")
    print("Expected validation error:")
    content_saturn3 = {
            "mission_name": "Saturn rings",
            "mission_id": "M2025_SATURN",
            "destination": "Saturn rings",
            "duration_days": 1500,
            "budget_millions": 5000,
            "crew": [
                {
                    "member_id": "001",
                    "name": "Sarah Connor",
                    "rank": "commander",
                    "age": 50,
                    "specialization": "Mission Command",
                    "years_experience": 20,
                },
                {
                    "member_id": "002",
                    "name": "John Smith",
                    "rank": "lieutenant",
                    "age": 45,
                    "specialization": "Navigation",
                    "years_experience": 25,
                },
                {
                    "member_id": "003",
                    "name": "Alice Johnson",
                    "rank": "officer",
                    "age": 20,
                    "specialization": "Engineering",
                    "years_experience": 2,
                    "is_active": False,
                }
            ],
            "launch_date": '2024-05-20T15:30:00'
        }

    try:
        saturn_crew3: SpaceMissionModel = SpaceMissionModel.model_validate(content_saturn3)
        print("Mission:", saturn_crew3.mission_name)
    except ValidationError as err2:
        print(err2.errors()[0]['msg'].replace("Value error, ", ""))

    if len(sys.argv) < 2:
        return

    print("\n========================================")
    print("RUN data validation on generated_data/space_missions")

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
        data_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(data_module)
        raw_records = getattr(data_module, "SPACE_MISSIONS", [])

    elif file_path.endswith('.json'):
        with open(file_path, 'r', encoding="utf-8") as file:
            raw_records = json.load(file)

    else:
        print("Unsupported file format.", file=sys.stderr)
        sys.exit(1)

    for idx, row in enumerate(raw_records, start=1):
        try:
            station = SpaceMissionModel(**row)
            print(f"  Mission [{station.mission_id}]: ✅ {station.destination}")
        except ValidationError as err:
            for e in err.errors():
                print(f"  Mission [{idx}] ❌ INVALID: {e['msg']}")


if __name__ == "__main__":
    main()
