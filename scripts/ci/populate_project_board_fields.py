#!/usr/bin/env python3
"""Populate EMPIRIC2 Project #7 planning fields from the EV-project-board-planning schedule.

Usage (from repo root, after GraphQL quota recovers):
  python3 scripts/ci/populate_project_board_fields.py

[Corpus: project-board]
"""
from __future__ import annotations

import json
import subprocess
import sys
import time

PROJECT_ID = "PVT_kwDOCfyvtc4BfyQZ"
PROJECT_NUMBER = 7

# issue -> (Priority, Size, hours, Iteration, due|None, Status)
PLAN: dict[int, tuple[str, str, int, str, str | None, str]] = {
    840: ("P2", "M", 0, "I00-Backlog", "2027-01-31", "Backlog"),
    843: ("P2", "M", 0, "I00-Backlog", "2026-10-17", "Backlog"),
    876: ("P2", "M", 0, "I00-Backlog", "2026-11-07", "Backlog"),
    962: ("P2", "M", 0, "I00-Backlog", "2027-01-31", "Backlog"),
    1058: ("P2", "M", 0, "I00-Backlog", None, "Backlog"),
    1097: ("P3", "M", 0, "I00-Backlog", None, "Backlog"),
    1120: ("P1", "M", 0, "I00-Backlog", None, "Backlog"),
    1146: ("P2", "M", 0, "I00-Backlog", None, "Backlog"),
    1147: ("P2", "M", 0, "I00-Backlog", None, "Backlog"),
    1159: ("P0", "S", 4, "I01", "2026-09-19", "Ready"),
    806: ("P1", "M", 8, "I01", "2026-10-17", "Ready"),
    911: ("P1", "L", 16, "I01", "2026-10-17", "Ready"),
    1028: ("P1", "M", 8, "I02", "2026-10-17", "Backlog"),
    1029: ("P1", "M", 8, "I03", "2026-10-17", "Backlog"),
    1030: ("P1", "M", 8, "I03", "2026-10-17", "Backlog"),
    1031: ("P1", "M", 8, "I04", "2026-10-17", "Backlog"),
    1121: ("P1", "S", 4, "I05", "2026-10-17", "Ready"),
    1122: ("P1", "M", 8, "I05", "2026-10-17", "Ready"),
    1123: ("P1", "S", 4, "I05", "2026-10-17", "Backlog"),
    877: ("P1", "S", 4, "I06", "2026-11-07", "Backlog"),
    1025: ("P1", "S", 4, "I06", "2026-11-07", "Backlog"),
    949: ("P1", "M", 8, "I06", "2026-11-11", "Backlog"),
    970: ("P2", "XL", 32, "I07", "2026-09-19", "Backlog"),
    909: ("P2", "L", 16, "I09", "2026-10-17", "Backlog"),
    910: ("P2", "L", 16, "I10", "2026-10-17", "Backlog"),
    936: ("P2", "M", 8, "I11", "2026-10-17", "Backlog"),
    878: ("P2", "S", 4, "I11", "2026-11-07", "Backlog"),
    879: ("P2", "S", 4, "I12", "2026-11-07", "Backlog"),
    882: ("P2", "M", 8, "I12", "2026-11-07", "Backlog"),
    885: ("P2", "L", 16, "I13", "2026-11-07", "Backlog"),
    896: ("P2", "M", 8, "I14", "2026-11-07", "Backlog"),
    1034: ("P2", "M", 8, "I14", "2026-11-07", "Backlog"),
    1036: ("P2", "L", 16, "I15", "2026-11-07", "Backlog"),
    1145: ("P2", "S", 4, "I16", "2026-11-11", "Backlog"),
    724: ("P2", "M", 8, "I16", "2027-01-31", "Backlog"),
    934: ("P2", "L", 16, "I17", "2027-01-31", "Backlog"),
    938: ("P2", "L", 16, "I18", "2027-01-31", "Backlog"),
    996: ("P2", "S", 4, "I19", "2027-01-31", "Backlog"),
    777: ("P3", "M", 8, "I19", "2026-10-17", "Backlog"),
    728: ("P3", "L", 16, "I19", "2026-11-11", "Backlog"),
    1149: ("P3", "XS", 2, "I21", "2026-11-11", "Backlog"),
    784: ("P3", "XL", 32, "I21", "2027-01-31", "Backlog"),
    837: ("P3", "L", 16, "I23", "2027-01-31", "Backlog"),
    844: ("P3", "S", 4, "I24", "2027-01-31", "Backlog"),
    880: ("P3", "S", 4, "I24", "2027-01-31", "Backlog"),
    884: ("P3", "M", 8, "I24", "2027-01-31", "Backlog"),
    1037: ("P3", "S", 4, "I25", "2027-01-31", "Backlog"),
    1043: ("P3", "M", 8, "I25", "2027-01-31", "Backlog"),
}


def gql(query: str, variables: dict | None = None) -> dict:
    payload: dict = {"query": query}
    if variables is not None:
        payload["variables"] = variables
    for attempt in range(10):
        proc = subprocess.run(
            ["gh", "api", "graphql", "--input", "-"],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
        )
        raw = proc.stdout or proc.stderr or ""
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(raw[:500]) from exc
        if "errors" in data:
            msg = data["errors"][0].get("message", "")
            if "rate limit" in msg.lower():
                time.sleep(min(90, 2**attempt))
                continue
            raise RuntimeError(msg)
        if proc.returncode != 0:
            raise RuntimeError(raw[:500])
        return data["data"]
    raise RuntimeError("rate limit exhausted")


def main() -> int:
    iter_data = gql(
        """
        query {
          organization(login: "EMPIRIC2") {
            projectV2(number: 7) {
              f: field(name: "Iteration") {
                ... on ProjectV2SingleSelectField {
                  options { id name }
                }
              }
            }
          }
        }
        """
    )
    iter_opts = {
        o["name"]: o["id"]
        for o in iter_data["organization"]["projectV2"]["f"]["options"]
    }

    fields = {
        "Priority": (
            "PVTSSF_lADOCfyvtc4BfyQZzhiLze8",
            {
                "P0": "133e4d4a",
                "P1": "b162bad7",
                "P2": "2f47dbd4",
                "P3": "83be03c3",
            },
        ),
        "Size": (
            "PVTSSF_lADOCfyvtc4BfyQZzhiLzd4",
            {
                "XS": "c48e293a",
                "S": "b1d95db5",
                "M": "6055c5ed",
                "L": "5224e42b",
                "XL": "222806ff",
            },
        ),
        "Iteration": ("PVTSSF_lADOCfyvtc4BfyQZzhiLze4", iter_opts),
        "Status": (
            "PVTSSF_lADOCfyvtc4BfyQZzhaCqDs",
            {
                "Backlog": "c9d54aef",
                "Ready": "c8a420ff",
                "In progress": "19238248",
                "In review": "7885684d",
                "On stage": "99429b7c",
                "On main": "c9ba4877",
                "Done": "adca4262",
            },
        ),
        "Estimate": ("PVTF_lADOCfyvtc4BfyQZzhiLzd8", None),
        "Due": ("PVTF_lADOCfyvtc4BfyQZzhaDchE", None),
    }

    items: dict[int, str] = {}
    cursor = None
    while True:
        data = gql(
            """
            query($c: String) {
              organization(login: "EMPIRIC2") {
                projectV2(number: 7) {
                  items(first: 100, after: $c) {
                    pageInfo { hasNextPage endCursor }
                    nodes {
                      id
                      content { ... on Issue { number state } }
                    }
                  }
                }
              }
            }
            """,
            {"c": cursor},
        )
        conn = data["organization"]["projectV2"]["items"]
        for node in conn["nodes"]:
            content = node.get("content") or {}
            if content.get("state") == "OPEN" and "number" in content:
                items[content["number"]] = node["id"]
        if not conn["pageInfo"]["hasNextPage"]:
            break
        cursor = conn["pageInfo"]["endCursor"]

    mut = """
    mutation(
      $projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: ProjectV2FieldValue!
    ) {
      updateProjectV2ItemFieldValue(
        input: {
          projectId: $projectId
          itemId: $itemId
          fieldId: $fieldId
          value: $value
        }
      ) {
        projectV2Item { id }
      }
    }
    """

    ok = fail = 0
    for num, (pri, size, hours, it, due, status) in sorted(PLAN.items()):
        item = items.get(num)
        if not item:
            print(f"#{num} MISSING", file=sys.stderr)
            fail += 1
            continue
        ops: list[tuple[str, dict]] = [
            (fields["Priority"][0], {"singleSelectOptionId": fields["Priority"][1][pri]}),
            (fields["Size"][0], {"singleSelectOptionId": fields["Size"][1][size]}),
            (fields["Iteration"][0], {"singleSelectOptionId": fields["Iteration"][1][it]}),
            (fields["Status"][0], {"singleSelectOptionId": fields["Status"][1][status]}),
        ]
        if hours > 0:
            ops.append((fields["Estimate"][0], {"number": float(hours)}))
        if due:
            ops.append((fields["Due"][0], {"date": due}))
        errs: list[str] = []
        for field_id, value in ops:
            try:
                gql(
                    mut,
                    {
                        "projectId": PROJECT_ID,
                        "itemId": item,
                        "fieldId": field_id,
                        "value": value,
                    },
                )
            except Exception as exc:  # noqa: BLE001 — surface and continue
                errs.append(str(exc)[:120])
            time.sleep(0.25)
        if errs:
            fail += 1
            print(f"#{num} FAIL {errs[0]}")
        else:
            ok += 1
            print(f"#{num} OK {pri} {size} {it}")

    print(json.dumps({"ok": ok, "fail": fail, "project": PROJECT_NUMBER}))
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
