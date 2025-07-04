import json
from typing import List, Dict, Any, Tuple, Optional, Set


class CreditCard:
    """
    Represents a single credit card, holding its name, point value,
    and category multipliers.
    """
    def __init__(self, card_data: Dict[str, Any]):
        """
        Initializes a CreditCard object from a dictionary.
        Point value is stored in cents.
        """
        self.name: str = card_data["card_name"]
        self.point_value: float = float(card_data["point_value"])
        self.multipliers: Dict[str, float] = {k: float(v) for k, v in card_data.get("multipliers", {}).items()}
        self.default_multiplier: float = float(card_data["default_multiplier"])

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the CreditCard object back to a dictionary for JSON serialization.
        """
        return {
            "card_name": self.name,
            "point_value": self.point_value,
            "multipliers": self.multipliers,
            "default_multiplier": self.default_multiplier
        }

    def __repr__(self) -> str:
        """
        Use card name as string representation
        """
        return self.name

    def calculate_value(self, category: str) -> float:
        """
        Calculates the effective cash back value (in dollars) for a given
        spending category.
        """
        multiplier = self.multipliers.get(category, self.default_multiplier)
        # Convert cents to dollars for the final value
        return (multiplier * self.point_value) / 100.0


class Wallet:
    """
    Manages a collection of credit cards, including loading, saving,
    and modifying card data.
    """
    def __init__(self, data_file: str):
        """
        Initializes the Wallet.
        """
        self.data_file = data_file
        self.cards: List[CreditCard] = self.load_cards()

    def load_cards(self) -> List[CreditCard]:
        """
        Loads card data from the JSON file. If the file doesn't exist or
        is invalid, it returns an empty list.
        """
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            return [CreditCard(card_info) for card_info in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_cards(self):
        """
        Saves the current list of cards to the JSON file.
        """
        with open(self.data_file, 'w') as f:
            json.dump([card.to_dict() for card in self.cards], f, indent=2)

    def get_card_by_name(self, name: str) -> Optional[CreditCard]:
        """Finds a card by its name."""
        for card in self.cards:
            if card.name == name:
                return card
        return None

    def add_card(self, card_data: Dict[str, Any]):
        """Adds a new card and saves the changes."""
        if self.get_card_by_name(card_data['card_name']):
            raise ValueError(f"A card named '{card_data['card_name']}' already exists.")
        new_card = CreditCard(card_data)
        self.cards.append(new_card)
        self.save_cards()

    def update_card(self, original_name: str, card_data: Dict[str, Any]):
        """Updates an existing card's details and saves the changes."""
        card_to_update = self.get_card_by_name(original_name)
        if not card_to_update:
            raise ValueError(f"No card found named '{original_name}'.")

        new_name = card_data['card_name']
        if original_name != new_name and self.get_card_by_name(new_name):
             raise ValueError(f"A card named '{new_name}' already exists.")

        card_to_update.name = new_name
        card_to_update.point_value = float(card_data['point_value'])
        card_to_update.multipliers = {k: float(v) for k, v in card_data.get("multipliers", {}).items()}
        card_to_update.default_multiplier = float(card_data['default_multiplier'])
        self.save_cards()

    def delete_card(self, name: str):
        """Deletes a card by name and saves the changes."""
        card_to_delete = self.get_card_by_name(name)
        if not card_to_delete:
            raise ValueError(f"No card found named '{name}'.")
        self.cards.remove(card_to_delete)
        self.save_cards()

    def get_all_categories(self) -> Set[str]:
        """Gets a set of all unique spending categories across all cards."""
        categories: Set[str] = set()
        for card in self.cards:
            categories.update(card.multipliers.keys())
        return categories

    def get_best_card_for_category(self, category: str) -> Optional[Tuple[CreditCard, float]]:
        """Finds the card that offers the best value for a specific category."""
        if not self.cards:
            return None
        return max(
            ((card, card.calculate_value(category)) for card in self.cards),
            key=lambda item: item[1],
            default=None
        )

    def get_best_cards_for_all_categories(self) -> Dict[str, Dict[str, Any]]:
        """Determines the best card for every unique category available."""
        all_categories = self.get_all_categories()
        all_categories.add("default")
        
        results: Dict[str, Dict[str, Any]] = {}
        for category in sorted(list(all_categories)):
            best_card_tuple = self.get_best_card_for_category(category)
            if best_card_tuple:
                best_card, max_value = best_card_tuple
                results[category] = {
                    "best_card": best_card.name,
                    "value": max_value
                }
        return results
