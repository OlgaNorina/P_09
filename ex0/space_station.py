import sys
import csv
import json
import os
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ValidationError


class SpaceStationModel(BaseModel):
    station_id: str = Field(min_length=3, max_length=10)
    name: str = Field(min_length=1, max_length=50)
    crew_size: int = Field(ge=0, le=20)
    power_level: float = Field(ge=0.0, le=100.0)
    oxygen_level: float = Field(ge=0.0, le=100.0)
    last_maintenance: Optional[datetime] = Field(default=None)
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
        print("ID:", iss002.station_id)
    except ValidationError:
        pass

    if len(sys.argv) < 2:
        return

    print("\n========================================")
    print("RUN data validation on generated_data/space_stations")

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
        raw_records = getattr(data_module, "SPACE_STATIONS", [])

    elif file_path.endswith('.json'):
        with open(file_path, 'r', encoding="utf-8") as file:
            raw_records = json.load(file)

    else:
        print("Unsupported file format.", file=sys.stderr)
        sys.exit(1)

    for idx, row in enumerate(raw_records, start=1):
        try:
            station = SpaceStationModel(**row)
            print(f"  Mission [{station.station_id}]: ✅ {station.name}")
        except ValidationError as err:
            for e in err.errors():
                field_name = e['loc'][-1] if e['loc'] else 'root'
                print(
                    f"  Mission [{idx}] ❌ INVALID: [{field_name}]: {e['msg']}"
                )


if __name__ == "__main__":
    main()
