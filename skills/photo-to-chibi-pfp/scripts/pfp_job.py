#!/usr/bin/env python3
"""Prepare local chibi jobs and inspect image metadata. No network or generation."""
import argparse
import json
import sys
import warnings
from pathlib import Path

from PIL import Image, ImageOps


STYLE_FILE = Path(__file__).resolve().parents[1] / "references" / "styles.json"
STYLES = json.loads(STYLE_FILE.read_text(encoding="utf-8"))
FACE_FIELDS = ("face_outline", "eyes", "brows", "nose", "mouth", "hairline_and_hair")


def validate_face_profile(value):
    if not isinstance(value, dict):
        raise ValueError("face_profile is required: inspect the original face before preparing a job")
    missing = [key for key in FACE_FIELDS if not isinstance(value.get(key), str) or not value[key].strip()]
    if missing:
        raise ValueError(f"face_profile missing observed proportions: {missing}; do not infer measurements")
    return {key: value[key].strip() for key in FACE_FIELDS}


def resolve_style(value):
    if value is None:
        return "pop_mart"
    if not isinstance(value, str) or not value.strip():
        raise ValueError("style_id must be a style name, or omitted for pop_mart")
    normalized = value.strip().casefold().replace("-", "_").replace(" ", "_")
    for key, spec in STYLES.items():
        names = [key, *spec["aliases"]]
        if any(normalized == x.casefold().replace("-", "_").replace(" ", "_") for x in names):
            return key
    raise ValueError(f"Unknown style_id {value!r}; choose one of {list(STYLES)}")


def image_info(value, minimum_side=1):
    path = Path(value).expanduser()
    if not path.is_absolute():
        raise ValueError("Image paths must be absolute")
    path = path.resolve(strict=True)
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        with Image.open(path) as raw:
            fmt = raw.format
            if fmt not in {"JPEG", "PNG", "WEBP"}:
                raise ValueError("Use a static JPEG, PNG or WebP image")
            if getattr(raw, "n_frames", 1) != 1:
                raise ValueError("Animated images are not supported")
            raw.load()
            im = ImageOps.exif_transpose(raw)
            width, height = im.size
            if min(width, height) < minimum_side:
                raise ValueError(f"Image is too small for input (minimum side {minimum_side}px)")
            alpha = im.getchannel("A").getextrema() if "A" in im.getbands() else None
            if alpha is None and "transparency" in im.info:
                alpha = im.convert("RGBA").getchannel("A").getextrema()
            return {
                "path": str(path), "format": fmt, "width": width, "height": height,
                "mode": im.mode, "square": width == height,
                "alpha_extrema": list(alpha) if alpha else None,
                "has_transparent_pixels": bool(alpha and alpha[0] < 255),
                "all_transparent": bool(alpha and alpha[1] == 0),
                "visual_quality": "not_checked",
            }


def text_list(value, name, minimum=0):
    if not isinstance(value, list) or len(value) < minimum:
        raise ValueError(f"{name} requires at least {minimum} observed/designed entries")
    if not all(isinstance(x, str) and x.strip() for x in value):
        raise ValueError(f"{name} must contain non-empty strings")
    return [x.strip() for x in value]


def prepare(brief_path, output):
    brief_path = Path(brief_path).expanduser()
    output = Path(output).expanduser()
    if not brief_path.is_absolute() or not output.is_absolute():
        raise ValueError("Brief and output paths must be absolute")
    brief = json.loads(brief_path.read_text(encoding="utf-8-sig"))
    if not isinstance(brief, dict):
        raise ValueError("Brief must be an object")
    if not isinstance(brief.get("photo_path"), str) or not brief["photo_path"].strip():
        raise ValueError("A real subject photo_path is required; a style-only image is insufficient")
    style_id = resolve_style(brief.get("style_id"))
    spec = STYLES[style_id]
    background = brief.get("background", "auto")
    if background == "auto":
        background = spec["default_background"]
    deliverable = brief.get("deliverable", "nine_grid")
    brief = dict(brief, style_id=style_id, background=background, deliverable=deliverable,
                 outfit_mode=brief.get("outfit_mode", "series" if deliverable == "nine_grid" else "preserve"))
    photo = image_info(brief["photo_path"], minimum_side=64)
    if photo["all_transparent"]:
        raise ValueError("Subject image is entirely transparent")
    style = image_info(brief["style_path"]) if brief.get("style_path") else None
    if style and style["path"] == photo["path"]:
        raise ValueError("Subject and style inputs must not be the same file")
    for key, allowed in {
        "source_view": {"full_body", "half_body"},
        "deliverable": {"nine_grid", "full_body", "avatar", "both"},
        "outfit_mode": {"preserve", "redesign", "series"},
        "background": {"dark", "light", "transparent"},
    }.items():
        if brief.get(key) not in allowed:
            raise ValueError(f"{key} must be one of {sorted(allowed)}")
    anchors = text_list(brief.get("identity_anchors"), "identity_anchors", 3)
    if len(anchors) > 8:
        raise ValueError("Use 3 to 8 specific identity anchors")
    face_profile = validate_face_profile(brief.get("face_profile"))
    outfit = brief.get("visible_outfit")
    if not isinstance(outfit, str) or not outfit.strip():
        raise ValueError("visible_outfit must describe what was actually observed")
    inferred = text_list(brief.get("inferred_design", []), "inferred_design")
    constraints = text_list(brief.get("user_constraints", []), "user_constraints")
    allow_lower = brief.get("allow_lower_body_design", False)
    if not isinstance(allow_lower, bool):
        raise ValueError("allow_lower_body_design must be a JSON boolean")
    needs_lower = brief["source_view"] == "half_body" and brief["deliverable"] in {"nine_grid", "full_body", "both"}
    if needs_lower and not allow_lower:
        raise ValueError("Full-body output from half-body input needs designed lower body; request a full-body photo or choose avatar")
    if needs_lower and not inferred:
        raise ValueError("Record designed lower clothing and footwear in inferred_design")
    redesign = brief.get("outfit_design", "")
    if brief["outfit_mode"] == "redesign" and (not isinstance(redesign, str) or not redesign.strip()):
        raise ValueError("redesign requires an explicit outfit_design")
    variants = []
    if brief["deliverable"] == "nine_grid":
        if brief["outfit_mode"] != "series":
            raise ValueError("nine_grid requires outfit_mode series; record any preserved clothing in each design")
        variants = brief.get("outfit_variants")
        if not isinstance(variants, list) or len(variants) != 9:
            raise ValueError("outfit_variants requires exactly 9 designs")
        if any(not isinstance(v, dict) or any(not isinstance(v.get(k), str) or not v[k].strip()
               for k in ("name", "design")) for v in variants):
            raise ValueError("Each outfit variant needs nonempty name and design")
        variants = [{k: v[k].strip() for k in ("name", "design")} for v in variants]
        if len({v["name"].casefold() for v in variants}) != 9 or len({v["design"].casefold() for v in variants}) != 9:
            raise ValueError("Nine outfit variants must have distinct names and designs")
    elif brief["outfit_mode"] == "series":
        raise ValueError("outfit_mode series requires nine_grid")
    normalized = dict(brief, photo_path=photo["path"], style_path=style["path"] if style else None,
                      face_profile=face_profile, identity_priority="face_proportions_first",
                      outfit_variants=variants)
    output = output.resolve()
    # Validate every input before creating any output. Existing runs are never overwritten.
    output.mkdir(parents=True, exist_ok=False)
    targets = ["full_body", "avatar"] if brief["deliverable"] == "both" else [brief["deliverable"]]
    tasks = []
    for target in targets:
        dependent = target == "avatar" and brief["deliverable"] == "both"
        refs = [{"index": 1, "role": "identity_and_visible_clothing", "path": photo["path"]}]
        if style:
            refs.append({"index": 2, "role": "style_only", "path": style["path"]})
        roles = "Image 1 is the primary source for facial geometry, natural expression, hair silhouette and visible clothing. It outranks style references for every internal facial proportion."
        if style:
            roles += " Image 2 controls material, finish, compatible body stylization, lighting and presentation only. Do not copy its face, eye size, face outline, fringe, hat or accessories. Adapt its style to image 1's facial geometry."
        if dependent:
            roles += " Append the full-body master ONLY AFTER its face and style reviews pass, as the LAST image. It supplies the established character design; the original subject photo remains authoritative for facial geometry."
        framing = (
            "One character, square 1:1 full-body composition, nearly frontal, entire hair/hat, both hands and shoe soles visible with breathing room. Relaxed pose, grounded feet."
            if target == "full_body" else
            "One character, square 1:1 head-and-shoulders avatar. Face large and readable at 96px, complete hair top, eyes and cheeks within the central circular crop safe area; no tiny full-body figure."
        )
        if target == "nine_grid":
            framing = "ONE portrait 3:4 presentation sheet, exactly three columns and three rows, nine full-body versions of the SAME person in ONE selected art style. Equal cell spacing and consistent character scale, each hair top, hands and shoe soles fully visible, no overlap. Same face proportions, skin, hair and expression across all nine. Distinct outfit silhouettes and accessories, not just recolors. No labels. This is one overview image, not nine independent high-resolution files."
        backdrop = {
            "dark": "Clean deep charcoal background, clear silhouette contrast; render lighting only when compatible with the selected style.",
            "light": "Clean warm off-white background with clear silhouette contrast; no additional material or lighting beyond the selected style.",
            "transparent": "Genuinely transparent background with clean alpha, no checkerboard pattern, no solid backdrop; preserve complete subject edges.",
        }[brief["background"]]
        outfit_text = ("Preserve visible clothing and key colors within the selected style's palette/monochrome abstraction: " + outfit) if brief["outfit_mode"] == "preserve" else ("User-authorized outfit redesign: " + redesign)
        if target == "nine_grid":
            outfit_text = "Nine-outfit series requested by the user's default: clothing and coordinated accessory redesign is permitted, while the original face/hair remain fixed. Original visible outfit as design context: " + outfit + "\nRead left-to-right, top-to-bottom:\n" + "\n".join(f"{i}. {v['name']}: {v['design']}" for i, v in enumerate(variants, 1))
        lower = (
            "The photo does NOT show the lower body. Pants/skirt and shoes below are invented coordinated design, not observed anatomy or recovered clothing: " + "; ".join(inferred)
            if needs_lower and target in {"full_body", "nine_grid"} else
            "Do not invent or change visible identity features. Unobserved details are not facts."
        )
        prompt = "\n".join([
            "Use case: style-transfer. Asset: " + spec["asset"] + ".",
            "Create a stylized portrait of THIS person. Preserve internal facial proportions first, then adapt the selected style around that face. Do not substitute the reference's generic doll face.",
            "Selected style: " + style_id + " / " + spec["label"],
            "Input roles: " + roles,
            "Observed identity anchors: " + "; ".join(anchors),
            "Observed facial geometry: " + "; ".join(f"{key}: {value}" for key, value in face_profile.items()),
            "Face lock: preserve face width-to-height relationship and jaw/chin shape, eye shape and eye spacing, brow thickness/arch and brow-to-eye distance, nose bridge/width/length, mouth width/lip shape and nose-to-mouth/chin spacing. Preserve hairline, parting, short/long silhouette and natural skin tone. Do not enlarge eyes, shrink nose/mouth, round the jaw or add baby cheeks by default. You may scale the whole head relative to the body, without rearranging features inside it. Simplify surface texture into the selected medium without preserving photoreal pores or hair strands.",
            outfit_text, lower,
            "Style: " + spec["design"],
            "Rendering: " + spec["render"],
            "Identity protection: " + spec["identity_note"],
            "Composition: " + framing,
            "Background: " + backdrop,
            "User constraints: " + ("; ".join(constraints) or "None beyond the current request."),
            "Avoid: generic template face, skin whitening, changed natural hair color, removed glasses, face-obscuring accessories, copied reference character, " + ("extra figures beyond the nine designs, mixed art styles, overlapping cells, " if target == "nine_grid" else "nine-panel grid, extra people, unsolicited accessories, ") + "extra limbs, fused hands, distorted eyewear, floating feet, cropped head/shoes, text, watermark, unintended branding, uncanny photoreal skin pores.",
            "Style-specific avoid: " + spec["avoid"],
        ]) + "\n"
        prompt_name = f"prompt-{target}.txt"
        (output / prompt_name).write_text(prompt, encoding="utf-8")
        tasks.append({
            "target": target, "style_id": style_id, "style_quality_check": spec["quality_check"],
            "prompt_file": str(output / prompt_name), "input_images": refs,
            "depends_on": "face_and_style_checked_full_body_master" if dependent else None,
            "append_master_reference_before_call": dependent,
            "output_image_count": 1,
            "design_count": 9 if target == "nine_grid" else 1,
            "review_order": ["face_proportions", "case_style", "technical"],
            "review_state": {"face_proportions": "not_checked", "case_style": "not_checked", "technical": "not_checked"},
            "status": "awaiting_master" if dependent else "prepared",
        })
    job = {
        "schema_version": 4, "status": "prepared", "backend": "built_in_image_gen",
        "generation_performed": False, "brief": normalized,
        "input_metadata": {"photo": photo, "style": style}, "tasks": tasks,
        "checks": {"input_files": "pass", "visual_identity": "not_checked", "output_visual_quality": "not_checked"},
    }
    (output / "job.json").write_text(json.dumps(job, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return job


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare", help="Validate a visual brief and write prompts; does not generate images")
    prep.add_argument("--brief", required=True)
    prep.add_argument("--out", required=True)
    inspect = sub.add_parser("inspect", help="Report actual image metadata; does not assess likeness")
    inspect.add_argument("--image", required=True)
    sub.add_parser("styles", help="List the default and eight optional styles")
    args = parser.parse_args()
    try:
        if args.command == "styles":
            result = {"default": "pop_mart", "styles": {key: {"label": value["label"], "aliases": value["aliases"]} for key, value in STYLES.items()}}
        else:
            result = prepare(args.brief, args.out) if args.command == "prepare" else image_info(args.image)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, TypeError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
