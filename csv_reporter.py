"""
csv_reporter.py
---------------

Exports analysis results to:

1. CSV
2. JSON
3. Excel

Compatible with NLP Analyser.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def _safe_join(items, key=None):

    if not items:
        return ""

    values = []

    for item in items:

        if isinstance(item, dict):

            if key:
                values.append(
                    str(item.get(key, ""))
                )

            else:
                values.append(str(item))

        else:
            values.append(str(item))

    return " | ".join(values)


# ---------------------------------------------------------
# EXCEL EXPORT
# ---------------------------------------------------------

def generate_excel_report(
    quarterly_analyses,
    company_name,
    output_path
):

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    rows = []

    for q in quarterly_analyses:

        metrics = q.get(
            "key_metrics_mentioned",
            {}
        )

        rows.append({

            "Quarter":
                q.get("quarter", ""),

            "Tone":
                q.get("management_tone", {})
                 .get("overall", ""),

            "Tone Score":
                q.get("management_tone", {})
                 .get("score", ""),

            "Summary":
                q.get("summary", ""),

            "Revenue Growth":
                metrics.get(
                    "revenue_growth",
                    ""
                ),

            "Margin":
                metrics.get(
                    "margin",
                    ""
                ),

            "Earnings Triggers":
                _safe_join(
                    q.get(
                        "earnings_triggers",
                        []
                    ),
                    "trigger"
                ),

            "Business Changes":
                _safe_join(
                    q.get(
                        "business_changes",
                        []
                    ),
                    "description"
                ),

            "Risks":
                _safe_join(
                    q.get(
                        "risks_and_issues",
                        []
                    ),
                    "risk"
                ),

            "Commitments":
                _safe_join(
                    q.get(
                        "commitments_made",
                        []
                    ),
                    "commitment"
                ),

            "Deviations":
                " | ".join(
                    q.get(
                        "deviations",
                        []
                    )
                )

        })

    df = pd.DataFrame(rows)

    with pd.ExcelWriter(
        output_path,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Concall Analysis"
        )

    return output_path


# ---------------------------------------------------------
# CSV EXPORT
# ---------------------------------------------------------

def generate_csv_report(
    quarterly_analyses,
    company_name,
    output_path,
):

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    fieldnames = [

        "Quarter",
        "Summary",
        "Tone",
        "Tone Score",
        "Revenue Growth",
        "Margin",
        "Earnings Triggers",
        "Business Changes",
        "Risks",
        "Commitments",
        "Deviations"

    ]

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for q in quarterly_analyses:

            metrics = q.get(
                "key_metrics_mentioned",
                {}
            )

            writer.writerow({

                "Quarter":
                    q.get("quarter", ""),

                "Summary":
                    q.get("summary", ""),

                "Tone":
                    q.get("management_tone", {})
                     .get("overall", ""),

                "Tone Score":
                    q.get("management_tone", {})
                     .get("score", ""),

                "Revenue Growth":
                    metrics.get(
                        "revenue_growth",
                        ""
                    ),

                "Margin":
                    metrics.get(
                        "margin",
                        ""
                    ),

                "Earnings Triggers":
                    _safe_join(
                        q.get(
                            "earnings_triggers",
                            []
                        ),
                        "trigger"
                    ),

                "Business Changes":
                    _safe_join(
                        q.get(
                            "business_changes",
                            []
                        ),
                        "description"
                    ),

                "Risks":
                    _safe_join(
                        q.get(
                            "risks_and_issues",
                            []
                        ),
                        "risk"
                    ),

                "Commitments":
                    _safe_join(
                        q.get(
                            "commitments_made",
                            []
                        ),
                        "commitment"
                    ),

                "Deviations":
                    " | ".join(
                        q.get(
                            "deviations",
                            []
                        )
                    )

            })

    return output_path


# ---------------------------------------------------------
# JSON EXPORT
# ---------------------------------------------------------

def generate_json_report(
    quarterly_analyses,
    company_name,
    output_path,
):

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = {

        "company":
            company_name,

        "quarters":
            len(
                quarterly_analyses
            ),

        "analysis":
            quarterly_analyses,

    }

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False,
        )

    return output_path