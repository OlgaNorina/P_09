from pydantic import BaseModel, Field, model_validator, ValidationError
from typing import Optional
from enum import Enum
from datetime import datetime


class RankType(str, Enum):
    CADET = "cadet"
    OFFICER = "officer"
    LIEUTENANT = "lieutenant"
    CAPTAIN = "captain"
    COMMANDER = "commander"


class CrewMemberModel(BaseModel):
    memeber_id: str = Field(min_length=3, max_length=10)
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
    launch_date: datetime
    duration_days: int = Field(ge=1, le=3650)
    crew: list[CrewMemberModel] = Field(min_length=1, max_length=12)
    mission_status: str = Field(default="planned")
    budget_millions: float = Field(ge=1.0, le=10000.0)

    @model_validator(mode="after")
    def mission_validation_rules(self) -> None:
        if not self.mission_id.startswith("M"):
            raise ValueError("Mission ID must start with 'M'")

        ranks: list[str] = [member.rank for member in self.crew]

        if not RankType.COMMANDER in ranks and not RankType.CAPTAIN in ranks:
            raise ValueError("Mission must have at least one Commander or Captain")

        counter: int = 0
        active_member: bool = True
        if self.duration_days > 365:
            for member in self.crew:
                if member.years_experience >= 5:
                    counter += 1
            if counter / len(self.crew) < 0.5:
                raise ValueError("Long missions (> 365 days) need 50% experienced crew (5+ years)")
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
                "memeber_id": "001",
                "name": "Sarah Connor",
                "rank": "commander",
                "age": 50,
                "specialization": "Mission Command",
                "years_experience": 20,
            },
            {
                "memeber_id": "002",
                "name": "John Smith",
                "rank": "lieutenant",
                "age": 45,
                "specialization": "Navigation",
                "years_experience": 15,
            },
            {
                "memeber_id": "003",
                "name": "Alice Johnson",
                "rank": "officer",
                "age": 20,
                "specialization": "Engineering",
                "years_experience": 2,                
            }
        ],
        "launch_date": '2024-05-20T15:30:00'
    }

    mars_crew: SpaceMissionModel = SpaceMissionModel(**content_mars)

    print("Mission:", mars_crew.mission_name)
    print("ID:", mars_crew.mission_id)
    print("Destination:", mars_crew.destination)
    print("Duration:", mars_crew.duration_days, "days")
    print(f"Budget: ${mars_crew.budget_millions}.OM")
    print("Crew size:", len(mars_crew.crew))
    print("Crew members:")
    for i in range(len(mars_crew.crew)):
        member: str = mars_crew.crew[i]
        print(f"- {member.name} ({member.rank.value}) - {member.specialization.capitalize()}")

    content_saturn1 = {
            "mission_name": "Saturn rings",
            "mission_id": "M2025_SATURN",
            "destination": "Saturn rings",
            "duration_days": 1500,
            "budget_millions": 5000,
            "crew": [
                {
                    "memeber_id": "002",
                    "name": "Alice Johnson",
                    "rank": "officer",
                    "age": 20,
                    "specialization": "Engineering",
                    "years_experience": 2,                
                },
                {
                    "memeber_id": "002",
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
        saturn_crew1: SpaceMissionModel = SpaceMissionModel(**content_saturn1)
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
                    "memeber_id": "001",
                    "name": "Sarah Connor",
                    "rank": "commander",
                    "age": 50,
                    "specialization": "Mission Command",
                    "years_experience": 20,
                },
                {
                    "memeber_id": "002",
                    "name": "John Smith",
                    "rank": "lieutenant",
                    "age": 45,
                    "specialization": "Navigation",
                    "years_experience": 2,
                },
                {
                    "memeber_id": "003",
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
        saturn_crew2: SpaceMissionModel = SpaceMissionModel(**content_saturn2)
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
                    "memeber_id": "001",
                    "name": "Sarah Connor",
                    "rank": "commander",
                    "age": 50,
                    "specialization": "Mission Command",
                    "years_experience": 20,
                },
                {
                    "memeber_id": "002",
                    "name": "John Smith",
                    "rank": "lieutenant",
                    "age": 45,
                    "specialization": "Navigation",
                    "years_experience": 25,
                },
                {
                    "memeber_id": "003",
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
        saturn_crew3: SpaceMissionModel = SpaceMissionModel(**content_saturn3)
    except ValidationError as err2:
        print(err2.errors()[0]['msg'].replace("Value error, ", ""))


if __name__ == "__main__":
    main()
