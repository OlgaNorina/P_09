from pydantic import BaseModel, Field, ValidationError
from datetime import datetime
from typing import Optional


class SpaceStationModel(BaseModel):
    station_id: str = Field(min_length=3, max_length=10)
    name: str = Field(min_length=1, max_length=50)
    crew_size: int = Field(ge=0, le=20)
    power_level: float = Field(ge=0.0, le=100.0)
    oxygen_level: float = Field(ge=0.0, le=100.0)
    last_maintenance: Optional[datetime] = None
    is_operational: bool = Field(default=True)
    notes: Optional[str] = Field(None, max_length=200)

def main() -> None:
    print("Space Station Data Validation")
    print("========================================")

    content001 = {
             "station_id": "ISS001",
             "name": "International Space Station",
             "crew_size": 6,
             "power_level": 85.5,
             "oxygen_level": 92.3,
             "is_operational": True,
        }

    iss001: SpaceStationModel = SpaceStationModel(**content001)
    print("Valid station created:")
    print("ID:", iss001.station_id)
    print("Name:", iss001.name)
    print("Crew:", iss001.crew_size, "people")
    print("Power:", iss001.power_level, "%")
    print("Oxygen:", iss001.oxygen_level, "%")
    print("Status:", "Operational" if True else "Inactive")

    print("\n========================================")
    print("Expected validation error:")
    print("Input should be less than or equal to 20")

    content002 = {
             "station_id": "ISS002",
             "name": "International Space Station",
             "crew_size": 25,
             "power_level": 85.5,
             "oxygen_level": 92.3,
             "is_operational": True,
        }
    try:
        iss002: SpaceStationModel = SpaceStationModel(**content002)
    except ValidationError:
        pass


if __name__ == "__main__":
    main()
