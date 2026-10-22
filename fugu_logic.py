"""Pure Python logic for the FuGu prototype.

Recommendation labels such as interests and skills are curated metadata for this
prototype; they are not official university classifications or aptitude scores.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

DATA_DIR = Path(__file__).parent / "data"


def load_json(filename: str) -> list[dict[str, Any]]:
    """Load a list of records from the project's data directory."""
    path = DATA_DIR / filename
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError(f"Expected a list in {path.name}")
    return data


def normalize(text: Any) -> str:
    """Normalize text for case-insensitive, accent-insensitive-ish search."""
    return " ".join(str(text or "").casefold().split())


def filter_programs(
    programs: Iterable[dict[str, Any]],
    query: str = "",
    categories: Iterable[str] | None = None,
    province: str = "Semua wilayah",
    university: str = "Semua kampus",
) -> list[dict[str, Any]]:
    """Search and filter programs. Empty filters mean no restriction."""
    q = normalize(query)
    category_set = set(categories or [])
    result: list[dict[str, Any]] = []
    for program in programs:
        searchable = " ".join(
            [
                str(program.get("program_name", "")),
                str(program.get("university", "")),
                str(program.get("city", "")),
                str(program.get("province", "")),
                str(program.get("summary", "")),
                " ".join(program.get("interests", [])),
                " ".join(program.get("skills", [])),
            ]
        )
        if q and q not in normalize(searchable):
            continue
        if category_set and program.get("category") not in category_set:
            continue
        if province != "Semua wilayah" and program.get("province") != province:
            continue
        if university != "Semua kampus" and program.get("university") != university:
            continue
        result.append(program)
    return result


def score_programs(
    programs: Iterable[dict[str, Any]],
    interests: Iterable[str],
    skills: Iterable[str] | None = None,
    preferred_province: str = "Semua wilayah",
) -> list[dict[str, Any]]:
    """Rank programs transparently by selected interests, skills and region.

    Weights: interests 70, skills/preferences 20 (if provided), region 10
    (if a province is selected). If optional criteria are not provided, the
    remaining active weights are normalized to 100. This is a preference match,
    not a validated psychometric score or prediction of academic success.
    """
    interest_set = set(interests or [])
    skill_set = set(skills or [])
    if not interest_set:
        return []

    results: list[dict[str, Any]] = []
    for program in programs:
        program_interests = set(program.get("interests", []))
        program_skills = set(program.get("skills", []))
        interest_hits = sorted(interest_set & program_interests)
        skill_hits = sorted(skill_set & program_skills)

        interest_score = 100.0 * len(interest_hits) / len(interest_set)
        active_components: list[tuple[str, float, float]] = [
            ("Minat", interest_score, 70.0)
        ]
        if skill_set:
            skill_score = 100.0 * len(skill_hits) / len(skill_set)
            active_components.append(("Preferensi/keterampilan", skill_score, 20.0))
        else:
            skill_score = None
        if preferred_province != "Semua wilayah":
            region_score = 100.0 if program.get("province") == preferred_province else 0.0
            active_components.append(("Wilayah", region_score, 10.0))
        else:
            region_score = None

        active_weight = sum(weight for _, _, weight in active_components)
        score = sum(component_score * weight for _, component_score, weight in active_components) / active_weight

        reasons: list[str] = []
        if interest_hits:
            reasons.append("Minat yang cocok: " + ", ".join(interest_hits))
        if skill_hits:
            reasons.append("Preferensi yang cocok: " + ", ".join(skill_hits))
        if preferred_province != "Semua wilayah":
            if region_score == 100:
                reasons.append(f"Berada di wilayah pilihan: {preferred_province}")
            else:
                reasons.append(f"Berada di {program.get('province', 'wilayah belum diketahui')}, bukan wilayah pilihan")
        if not interest_hits and not skill_hits:
            reasons.append("Tidak ada tag minat/preferensi yang cocok; hasil ini ditampilkan untuk perbandingan, bukan sebagai rekomendasi kuat.")
        results.append(
            {
                **program,
                "score": round(score, 1),
                "interest_score": round(interest_score, 1),
                "skill_score": None if skill_score is None else round(skill_score, 1),
                "region_score": None if region_score is None else round(region_score, 1),
                "interest_hits": interest_hits,
                "skill_hits": skill_hits,
                "reasons": reasons,
                "score_components": {
                    "Minat": round(interest_score, 1),
                    **({"Preferensi/keterampilan": round(skill_score, 1)} if skill_score is not None else {}),
                    **({"Wilayah": round(region_score, 1)} if region_score is not None else {}),
                },
            }
        )
    return sorted(results, key=lambda item: (-item["score"], item["program_name"], item["university"]))


def validate_records(programs: Iterable[dict[str, Any]]) -> list[str]:
    """Return data quality warnings useful for tests and a methods page."""
    warnings: list[str] = []
    seen_ids: set[str] = set()
    for index, program in enumerate(programs, start=1):
        pid = str(program.get("program_id", ""))
        if not pid:
            warnings.append(f"Record {index}: program_id is missing")
        elif pid in seen_ids:
            warnings.append(f"Duplicate program_id: {pid}")
        seen_ids.add(pid)
        for required in ("program_name", "university", "province", "program_url", "university_url"):
            if not program.get(required):
                warnings.append(f"{pid or index}: {required} is missing")
        for url_field in ("program_url", "university_url"):
            value = str(program.get(url_field, ""))
            if value and not value.startswith("https://"):
                warnings.append(f"{pid}: {url_field} should use HTTPS")
    return warnings
