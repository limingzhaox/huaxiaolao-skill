"""Validate references and timing, not scientific truth, art quality or animation."""
import argparse
import json
from pathlib import Path, PureWindowsPath
import sys

TAGS = {"HOLD", "POSE_SWAP", "FACE_SWAP", "DRAW_STEP", "REVEAL", "MOTION", "SYMBOL", "DIAGRAM"}


def check(plan, root, phase="plan"):
    errors, warnings = [], []
    def need(condition, message):
        if not condition:
            errors.append(message)
    def index(items, label):
        result = {}
        need(isinstance(items, list), f"{label}: expected list")
        for item in items if isinstance(items, list) else []:
            if not isinstance(item, dict) or not item.get("id"):
                errors.append(f"{label}: each entry needs an id")
                continue
            need(item["id"] not in result, f"{label}: duplicate id {item['id']}")
            result[item["id"]] = item
        return result
    def refs(ids, known, label):
        need(isinstance(ids, list), f"{label}: expected list")
        for key in ids if isinstance(ids, list) else []:
            need(key in known, f"{label}: unknown reference {key}")
    def integer(value):
        return type(value) is int
    need(isinstance(plan, dict), "plan: expected object")
    if not isinstance(plan, dict):
        return errors, warnings, {}
    need(plan.get("schema_version") == 1, "schema_version must be 1")
    project = plan.get("project", {})
    for field in ("title", "audience", "promise", "comprehension_question"):
        need(bool(project.get(field)), f"project: missing {field}")
    need(type(project.get("video_execution")) is bool, "project: video_execution must be explicit boolean")
    if project.get("video_execution"):
        warnings.append("video_execution=true: this skill provides no renderer; confirm current user scope independently")
    fmt = plan.get("format", {})
    w, h, fps = (fmt.get(k) for k in ("width", "height", "fps"))
    need(all(integer(v) and v > 0 for v in (w, h, fps)), "format: positive integer width/height/fps required")
    stage = fmt.get("stage", {})
    box = [stage.get(k) for k in ("x", "y", "width", "height")]
    if all(integer(v) for v in box) and integer(w) and integer(h):
        x, y, sw, sh = box
        need(x >= 0 and y >= 0 and sw > 0 and sh > 0 and x + sw <= w and y + sh <= h, "stage: rectangle outside canvas or empty")
        if fmt.get("layout") == "portrait-horizontal":
            need(h > w and sw > sh, "layout: portrait canvas and horizontal stage required")
    else:
        errors.append("stage: integer x/y/width/height required")
    claims = index(plan.get("claims"), "claims")
    voices = index(plan.get("voice_lines"), "voice_lines")
    assets = index(plan.get("assets"), "assets")
    scenes = index(plan.get("scenes"), "scenes")
    need(bool(scenes), "scenes: cannot be empty")
    for cid, claim in claims.items():
        kind, status = claim.get("kind"), claim.get("verification")
        need(kind in {"fact", "hypothesis", "metaphor"}, f"{cid}: invalid kind")
        need(status in {"verified", "pending", "fictional"}, f"{cid}: invalid verification")
        need(bool(claim.get("statement")) and bool(claim.get("limits")), f"{cid}: statement and limits required")
        if kind == "fact":
            sources = claim.get("sources", [])
            source_ok = isinstance(sources, list) and bool(sources) and all(
                isinstance(s, dict) and s.get("locator") and s.get("supports") and (
                    (s.get("kind") == "derivation" and s.get("method")) or
                    str(s.get("url", "")).startswith(("https://", "http://"))) for s in sources)
            if phase in {"handoff", "assets"} or status == "verified":
                need(status == "verified" and source_ok, f"{cid}: factual handoff needs verified evidence with locator/supports")
            elif status == "pending":
                warnings.append(f"{cid}: pending fact; research before factual artwork")
            else:
                errors.append(f"{cid}: a fact cannot be fictional")
    for vid, voice in voices.items():
        need(bool(voice.get("text")), f"{vid}: missing text")
        refs(voice.get("claim_ids"), claims, vid + ".claim_ids")
    root = Path(root).resolve()
    for aid, asset in assets.items():
        path = asset.get("path", "")
        need(isinstance(path, str) and bool(path), f"{aid}: path required")
        safe = False
        if isinstance(path, str) and path:
            target = (root / path).resolve()
            safe = not Path(path).is_absolute() and not PureWindowsPath(path).is_absolute() and root in target.parents
            need(safe, f"{aid}: asset path must stay relative inside plan directory")
        need(asset.get("status") in {"planned", "generated", "user_approved"}, f"{aid}: invalid status")
        need(bool(asset.get("drawing_id")), f"{aid}: drawing_id required")
        if phase == "assets":
            need(asset.get("status") != "planned", f"{aid}: asset still planned")
            need(safe and target.is_file(), f"{aid}: generated file missing")
        elif asset.get("status") == "planned":
            warnings.append(f"{aid}: planned, not a generated drawing")
    states, state_times = {}, {}
    offset = 0
    for sid, scene in scenes.items():
        duration = scene.get("duration_frames")
        need(integer(duration) and duration > 0, f"{sid}: positive duration_frames required")
        need(bool(scene.get("knowledge_task")), f"{sid}: knowledge_task required")
        refs(scene.get("claim_ids"), claims, sid + ".claim_ids")
        cursor = 0
        scene_states = scene.get("states", [])
        need(isinstance(scene_states, list) and bool(scene_states), f"{sid}: states cannot be empty")
        for state in scene_states if isinstance(scene_states, list) else []:
            if not isinstance(state, dict):
                errors.append(f"{sid}: state must be object")
                continue
            key = state.get("id")
            need(bool(key) and key not in states, f"{sid}: missing/duplicate state id {key}")
            states[key] = state
            start, end = state.get("start_frame"), state.get("end_frame")
            if integer(start) and integer(end):
                need(start == cursor, f"{key}: gap/overlap at frame {cursor}, got {start}")
                need(0 <= start < end and integer(duration) and end <= duration, f"{key}: invalid half-open interval")
                state_times[key] = offset + start
                cursor = end
            else:
                errors.append(f"{key}: integer frame interval required")
            need(state.get("tag") in TAGS, f"{key}: invalid tag")
            need(bool(state.get("change")) and bool(state.get("hold")), f"{key}: change and hold purpose required")
            need(bool(state.get("asset_ids")), f"{key}: asset_ids cannot be empty")
            refs(state.get("asset_ids"), assets, str(key) + ".asset_ids")
            refs(state.get("voice_line_ids"), voices, str(key) + ".voice_line_ids")
        need(cursor == duration, f"{sid}: states must cover full duration {duration}, ended at {cursor}")
        if integer(duration):
            offset += duration
    for key, state in states.items():
        triggers = state.get("trigger_state_ids")
        refs(triggers, states, str(key) + ".trigger_state_ids")
        for trigger in triggers if isinstance(triggers, list) else []:
            if trigger in state_times and key in state_times:
                need(state_times[trigger] < state_times[key], f"{key}: trigger {trigger} must precede response")
    need(isinstance(plan.get("review"), dict), "review: record separate factual/style/user status")
    review = plan.get("review", {})
    need(type(review.get("user_approved")) is bool, "review: user_approved must be explicit boolean")
    stats = {"output_frames_planned": offset, "independent_drawings_registered": len({a.get("drawing_id") for a in assets.values() if a.get("drawing_id")}), "primary_states": len(states)}
    return errors, warnings, stats


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--phase", choices=("plan", "handoff", "assets"), default="plan")
    args = parser.parse_args()
    try:
        data = json.loads(args.plan.read_text(encoding="utf-8-sig"))
        errors, warnings, stats = check(data, args.plan.parent, args.phase)
    except (OSError, ValueError, TypeError, AttributeError, KeyError) as exc:
        errors, warnings, stats = [f"Invalid plan: {exc}"], [], {}
    print(json.dumps({"pass": not errors, "phase": args.phase, "errors": errors, "warnings": warnings, "counts": stats, "limits": "Structure only; not fact, art, motion or user-approval verification."}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
