from dataclasses import dataclass, field
from typing import Dict, List

from pet import Pet


@dataclass
class Owner:
    """The person who owns one or more pets and sets scheduling preferences."""

    owner_id: int
    name: str
    contact_info: str = ""
    preferences: Dict[str, str] = field(default_factory=dict)  # e.g. {"wake_time": "07:00"}
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """TODO: append pet to self.pets."""
        pass

    def remove_pet(self, pet_id: int) -> None:
        """TODO: remove a pet by id."""
        pass

    def get_pet(self, pet_id: int) -> Pet:
        """TODO: look up and return a pet by id."""
        pass
