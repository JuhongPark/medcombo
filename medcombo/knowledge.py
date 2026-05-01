"""Curated knowledge-base loading and lookup."""

from __future__ import annotations

import json
from pathlib import Path

from medcombo.models import DrugClass, Ingredient, MedicationRecord, SourceReference
from medcombo.text import clean_key


class KnowledgeBase:
    def __init__(
        self,
        data_version: str,
        medications: dict[str, MedicationRecord],
        ingredients: dict[str, Ingredient],
        drug_classes: dict[str, DrugClass],
        interactions: tuple[dict, ...],
        sources: dict[str, SourceReference],
    ) -> None:
        self.data_version = data_version
        self.medications = medications
        self.ingredients = ingredients
        self.drug_classes = drug_classes
        self.interactions = interactions
        self.sources = sources
        self.alias_index = self._build_alias_index()

    @classmethod
    def load_demo(cls, data_dir: Path | None = None) -> "KnowledgeBase":
        root = Path(__file__).resolve().parents[1]
        demo_dir = data_dir or root / "data" / "demo"

        medication_data = _read_json(demo_dir / "medications.json")
        interaction_data = _read_json(demo_dir / "interactions.json")
        source_data = _read_json(demo_dir / "sources.json")

        ingredients = {
            row["ingredient_id"]: Ingredient(
                ingredient_id=row["ingredient_id"],
                name=row["name"],
                source_ids=tuple(row["source_ids"]),
            )
            for row in medication_data["ingredients"]
        }

        drug_classes = {
            row["class_id"]: DrugClass(
                class_id=row["class_id"],
                name=row["name"],
                class_source=row["class_source"],
                source_ids=tuple(row["source_ids"]),
            )
            for row in medication_data["drug_classes"]
        }

        medications = {
            row["medication_id"]: MedicationRecord(
                medication_id=row["medication_id"],
                display_name=row["display_name"],
                normalized_name=row["normalized_name"],
                rxcui=row["rxcui"],
                aliases=tuple(row["aliases"]),
                active_ingredients=tuple(row["active_ingredients"]),
                drug_classes=tuple(row["drug_classes"]),
                source_ids=tuple(row["source_ids"]),
            )
            for row in medication_data["medications"]
        }

        sources = {
            row["source_id"]: SourceReference(
                source_id=row["source_id"],
                title=row["title"],
                publisher=row["publisher"],
                url=row["url"],
                retrieved_or_version_date=row["retrieved_or_version_date"],
                source_type=row["source_type"],
            )
            for row in source_data["sources"]
        }

        return cls(
            data_version=medication_data["data_version"],
            medications=medications,
            ingredients=ingredients,
            drug_classes=drug_classes,
            interactions=tuple(interaction_data["interactions"]),
            sources=sources,
        )

    def medication(self, medication_id: str) -> MedicationRecord:
        return self.medications[medication_id]

    def ingredient(self, ingredient_id: str) -> Ingredient:
        return self.ingredients[ingredient_id]

    def drug_class(self, class_id: str) -> DrugClass:
        return self.drug_classes[class_id]

    def source_list(self, source_ids: tuple[str, ...] | list[str]) -> tuple[SourceReference, ...]:
        return tuple(self.sources[source_id] for source_id in source_ids if source_id in self.sources)

    def _build_alias_index(self) -> dict[str, tuple[str, ...]]:
        alias_index: dict[str, set[str]] = {}
        for medication in self.medications.values():
            terms = set(medication.aliases)
            terms.add(medication.display_name)
            terms.add(medication.normalized_name)
            for term in terms:
                alias_index.setdefault(clean_key(term), set()).add(medication.medication_id)
        return {key: tuple(sorted(ids)) for key, ids in alias_index.items()}


def _read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
