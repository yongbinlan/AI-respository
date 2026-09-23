"""Local behavioral tests using synthetic files, not portrait-quality tests."""
import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from pfp_job import FACE_FIELDS, STYLES, create_template, image_info, prepare, resolve_style


class JobTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="pfp-job-test-")
        self.root = Path(self.temp.name).resolve()
        self.photo = self.root / "照片 with spaces.png"
        Image.new("RGB", (180, 240), "gray").save(self.photo)
        self.brief = {
            "photo_path": str(self.photo), "style_path": None,
            "source_view": "full_body", "deliverable": "full_body",
            "identity_anchors": ["测试特征一", "测试特征二", "测试特征三"],
            "face_profile": {key: "合成测试描述：" + key for key in FACE_FIELDS},
            "visible_outfit": "测试上装", "outfit_mode": "preserve", "outfit_design": "",
            "background": "dark", "allow_lower_body_design": True,
            "inferred_design": [], "user_constraints": [],
        }

    def tearDown(self):
        self.temp.cleanup()

    def run_job(self, brief=None, out="run"):
        path = self.root / "brief.json"
        path.write_text(json.dumps(brief or self.brief, ensure_ascii=False), encoding="utf-8")
        return prepare(path, self.root / out)

    def test_full_body_uses_actual_photo_without_generation_claim(self):
        job = self.run_job()
        self.assertEqual(job["tasks"][0]["input_images"][0]["path"], str(self.photo))
        self.assertFalse(job["generation_performed"])
        self.assertEqual(job["checks"]["visual_identity"], "not_checked")
        self.assertTrue(Path(job["tasks"][0]["prompt_file"]).is_file())

    def test_half_body_requires_design_disclosure(self):
        self.brief["source_view"] = "half_body"
        with self.assertRaisesRegex(ValueError, "inferred_design"):
            self.run_job()
        self.assertFalse((self.root / "run").exists())
        self.brief["inferred_design"] = ["设计蓝色裤装与白色鞋子"]
        job = self.run_job()
        prompt = Path(job["tasks"][0]["prompt_file"]).read_text(encoding="utf-8")
        self.assertIn("not observed anatomy", prompt)

    def test_half_body_cannot_override_no_completion(self):
        self.brief.update(source_view="half_body", allow_lower_body_design=False)
        with self.assertRaisesRegex(ValueError, "choose avatar"):
            self.run_job()

    def test_avatar_needs_no_lower_body_invention(self):
        self.brief.update(source_view="half_body", deliverable="avatar", allow_lower_body_design=False)
        self.assertEqual(self.run_job()["tasks"][0]["target"], "avatar")

    def test_both_defers_avatar_until_master(self):
        self.brief["deliverable"] = "both"
        tasks = self.run_job()["tasks"]
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[1]["status"], "awaiting_master")
        self.assertTrue(tasks[1]["append_master_reference_before_call"])
        self.assertEqual(tasks[1]["depends_on"], "face_and_style_checked_full_body_master")

    def test_distinct_style_role(self):
        style = self.root / "style.png"
        Image.new("RGB", (128, 128), "blue").save(style)
        self.brief["style_path"] = str(style)
        refs = self.run_job()["tasks"][0]["input_images"]
        self.assertEqual(refs[1]["role"], "style_only")

    def test_reject_same_subject_style(self):
        self.brief["style_path"] = str(self.photo)
        with self.assertRaisesRegex(ValueError, "same file"):
            self.run_job()

    def test_missing_photo_does_not_become_style_conversion(self):
        self.brief.update(photo_path=None, style_path=str(self.photo))
        with self.assertRaisesRegex(ValueError, "subject photo_path"):
            self.run_job()

    def test_no_overwrite(self):
        self.run_job()
        before = (self.root / "run" / "job.json").read_bytes()
        with self.assertRaises(FileExistsError):
            self.run_job()
        self.assertEqual(before, (self.root / "run" / "job.json").read_bytes())

    def test_no_string_boolean(self):
        self.brief["allow_lower_body_design"] = "false"
        with self.assertRaisesRegex(ValueError, "boolean"):
            self.run_job()

    def test_redesign_requires_design(self):
        self.brief["outfit_mode"] = "redesign"
        with self.assertRaisesRegex(ValueError, "outfit_design"):
            self.run_job()

    def test_metadata_uses_actual_format(self):
        disguised = self.root / "actually-png.jpg"
        Image.new("RGBA", (128, 128), (0, 0, 0, 128)).save(disguised, format="PNG")
        info = image_info(disguised)
        self.assertEqual(info["format"], "PNG")
        self.assertTrue(info["has_transparent_pixels"])
        self.assertFalse(info["all_transparent"])
        self.assertEqual(info["visual_quality"], "not_checked")

    def test_fully_transparent_subject_blocked(self):
        Image.new("RGBA", (128, 128), (0, 0, 0, 0)).save(self.photo)
        with self.assertRaisesRegex(ValueError, "entirely transparent"):
            self.run_job()

    def test_corrupt_image_rejected(self):
        self.photo.write_bytes(b"not an image")
        with self.assertRaises(OSError):
            self.run_job()

    def test_relative_image_path_rejected(self):
        self.brief["photo_path"] = "unknown.png"
        with self.assertRaisesRegex(ValueError, "absolute"):
            self.run_job()

    def test_omitted_style_defaults_to_pop_mart(self):
        job = self.run_job()
        self.assertEqual(job["brief"]["style_id"], "pop_mart")
        prompt = Path(job["tasks"][0]["prompt_file"]).read_text(encoding="utf-8")
        self.assertIn("Preserve internal facial proportions first", prompt)
        self.assertIn("PVC", prompt)

    def test_all_nine_styles_support_all_three_deliverables(self):
        expected = {"pop_mart", "pixel_art", "flat_2d", "anime", "street_comic", "funko_pop", "cyberpunk", "minimal_line", "claymation"}
        self.assertEqual(set(STYLES), expected)
        for style in expected:
            for target in ("avatar", "full_body", "both"):
                with self.subTest(style=style, target=target):
                    brief = dict(self.brief, style_id=style, deliverable=target, background="auto")
                    job = self.run_job(brief, f"{style}-{target}")
                    self.assertEqual(len(job["tasks"]), 2 if target == "both" else 1)
                    self.assertFalse(job["generation_performed"])
                    for task in job["tasks"]:
                        self.assertEqual(task["style_id"], style)
                        self.assertEqual(task["input_images"][0]["path"], str(self.photo))
                        self.assertTrue(task["style_quality_check"])
                        prompt = Path(task["prompt_file"]).read_text(encoding="utf-8")
                        self.assertIn("测试特征一", prompt)
                        self.assertIn("测试上装", prompt)
                        for value in brief["face_profile"].values():
                            self.assertIn(value, prompt)
                        self.assertIn("It outranks style references", prompt)
                        self.assertEqual(task["review_order"], ["face_proportions", "case_style", "technical"])
                        self.assertTrue(all(value == "not_checked" for value in task["review_state"].values()))
                    if target == "both":
                        self.assertEqual(job["tasks"][1]["status"], "awaiting_master")

    def test_aliases_and_unknown_style_do_not_silently_fallback(self):
        for name, expected in [("Pop Mart", "pop_mart"), ("泡泡玛特", "pop_mart"), ("像素风", "pixel_art"), ("日系动漫", "anime"), ("Funko Pop", "funko_pop"), ("黏土", "claymation")]:
            self.assertEqual(resolve_style(name), expected)
        brief = dict(self.brief, style_id="nonexistent")
        with self.assertRaisesRegex(ValueError, "Unknown style_id"):
            self.run_job(brief)
        self.assertFalse((self.root / "run").exists())

    def test_2d_styles_do_not_inherit_toy_render_requirements(self):
        for style in ("pixel_art", "flat_2d", "anime", "street_comic", "minimal_line"):
            job = self.run_job(dict(self.brief, style_id=style, background="auto"), style)
            prompt = Path(job["tasks"][0]["prompt_file"]).read_text(encoding="utf-8")
            positive = "\n".join(line for line in prompt.splitlines() if not line.startswith(("Avoid:", "Style-specific avoid:")))
            self.assertNotIn("approximately two heads tall", positive)
            self.assertNotIn("premium matte soft vinyl", positive)
            self.assertNotIn("soft key light", positive)
            self.assertNotIn("distinctive rounded designer toy", positive)

    def test_funko_and_clay_materials_are_distinct(self):
        funko = self.run_job(dict(self.brief, style_id="funko_pop"), "funko")
        clay = self.run_job(dict(self.brief, style_id="claymation"), "clay")
        fp = Path(funko["tasks"][0]["prompt_file"]).read_text(encoding="utf-8")
        cp = Path(clay["tasks"][0]["prompt_file"]).read_text(encoding="utf-8")
        self.assertIn("likeness-first adaptation", fp)
        self.assertNotIn("solid black dot eyes", fp)
        self.assertNotIn("very large expressive eyes", fp)
        self.assertIn("clay fingerprints", cp)
        self.assertNotIn("PVC and soft vinyl", cp)

    def test_background_default_and_explicit_override(self):
        for style, expected in [("pop_mart", "dark"), ("pixel_art", "light"), ("cyberpunk", "dark")]:
            brief = dict(self.brief, style_id=style)
            brief.pop("background")
            self.assertEqual(self.run_job(brief, style)["brief"]["background"], expected)
        self.assertEqual(self.run_job(dict(self.brief, style_id="flat_2d", background="transparent"), "alpha")["brief"]["background"], "transparent")

    def test_inspect_accepts_actual_24px_output_but_subject_input_does_not(self):
        tiny = self.root / "pixel-art.png"
        Image.new("RGB", (24, 24), "blue").save(tiny)
        info = image_info(tiny)
        self.assertEqual((info["width"], info["height"]), (24, 24))
        with self.assertRaisesRegex(ValueError, "minimum side 64px"):
            self.run_job(dict(self.brief, photo_path=str(tiny)))

    def test_half_body_completion_remains_required_for_all_styles(self):
        for style in STYLES:
            with self.subTest(style=style):
                brief = dict(self.brief, style_id=style, source_view="half_body", allow_lower_body_design=False)
                with self.assertRaisesRegex(ValueError, "choose avatar"):
                    self.run_job(brief, style)
                brief.update(allow_lower_body_design=True, inferred_design=["设计的下装和鞋"])
                job = self.run_job(brief, style)
                prompt = Path(job["tasks"][0]["prompt_file"]).read_text(encoding="utf-8")
                self.assertIn("not observed anatomy", prompt)

    def test_missing_face_observations_fail_before_output(self):
        self.brief.pop("face_profile")
        with self.assertRaisesRegex(ValueError, "face_profile is required"):
            self.run_job()
        self.assertFalse((self.root / "run").exists())

    def test_each_face_group_needs_nonempty_observations(self):
        for key in FACE_FIELDS:
            for invalid in (None, "", "  ", 1, []):
                with self.subTest(field=key, value=invalid):
                    brief = copy.deepcopy(self.brief)
                    brief["face_profile"][key] = invalid
                    with self.assertRaisesRegex(ValueError, "face_profile missing"):
                        self.run_job(brief)
                    self.assertFalse((self.root / "run").exists())

    def test_style_reference_cannot_supply_face_or_unrequested_accessories(self):
        style = self.root / "style.png"
        Image.new("RGB", (128, 128), "blue").save(style)
        job = self.run_job(dict(self.brief, style_path=str(style)))
        prompt = Path(job["tasks"][0]["prompt_file"]).read_text(encoding="utf-8")
        self.assertIn("Do not copy its face, eye size, face outline, fringe, hat or accessories", prompt)
        self.assertEqual(job["brief"]["identity_priority"], "face_proportions_first")
        self.assertEqual(job["schema_version"], 5)

    def grid_brief(self):
        brief = copy.deepcopy(self.brief)
        brief.pop("deliverable")
        brief.pop("outfit_mode")
        brief["outfit_variants"] = [{"name": f"look-{i}", "design": f"outfit silhouette {i}"} for i in range(9)]
        return brief

    def test_default_is_one_nine_grid_with_nine_outfits(self):
        job = self.run_job(self.grid_brief())
        self.assertEqual(job["brief"]["deliverable"], "nine_grid")
        self.assertEqual(job["brief"]["outfit_mode"], "series")
        self.assertEqual(len(job["tasks"]), 1)
        task = job["tasks"][0]
        self.assertEqual((task["output_image_count"], task["design_count"]), (1, 9))
        prompt = Path(task["prompt_file"]).read_text(encoding="utf-8")
        for variant in job["brief"]["outfit_variants"]:
            self.assertIn(variant["design"], prompt)
        self.assertNotIn("nine-panel grid", prompt)
        self.assertNotIn("square 1:1", prompt)
        self.assertFalse(job["generation_performed"])

    def test_invalid_grid_designs_rejected_before_output(self):
        invalid_lists = [[], [{"name": "a", "design": "b"}] * 9,
                         [{"name": str(i), "design": ""} for i in range(9)]]
        for variants in invalid_lists:
            brief = self.grid_brief()
            brief["outfit_variants"] = variants
            with self.assertRaises(ValueError):
                self.run_job(brief)
            self.assertFalse((self.root / "run").exists())

    def test_grid_supports_each_style_and_lower_body_guard(self):
        for style in STYLES:
            brief = self.grid_brief()
            brief.update(style_id=style, source_view="half_body", allow_lower_body_design=False)
            with self.assertRaisesRegex(ValueError, "choose avatar"):
                self.run_job(brief, style)
            brief.update(allow_lower_body_design=True, inferred_design=["下装鞋子均为设计"])
            job = self.run_job(brief, style)
            task = job["tasks"][0]
            self.assertEqual(task["style_id"], style)
            self.assertEqual(task["target"], "nine_grid")
            self.assertIn("not observed anatomy", Path(task["prompt_file"]).read_text(encoding="utf-8"))

    def test_grid_outfit_mode_conflicts_do_not_silently_override(self):
        brief = self.grid_brief()
        brief["outfit_mode"] = "preserve"
        with self.assertRaisesRegex(ValueError, "requires outfit_mode series"):
            self.run_job(brief)
        brief.update(deliverable="full_body", outfit_mode="series")
        with self.assertRaisesRegex(ValueError, "series requires nine_grid"):
            self.run_job(brief)

    def test_templates_prepare_all_modes_after_observations_are_filled(self):
        for target in ("nine_grid", "full_body", "avatar", "both"):
            path = self.root / f"template-{target}.json"
            create_template(path, "黏土", target)
            brief = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(brief["style_id"], "claymation")
            self.assertIsNone(brief["photo_path"])
            brief.update({k: v for k, v in self.brief.items() if k not in {"deliverable", "outfit_mode", "allow_lower_body_design"}})
            if target == "nine_grid":
                brief["outfit_variants"] = self.grid_brief()["outfit_variants"]
            job = self.run_job(brief, target)
            self.assertEqual(job["brief"]["deliverable"], target)

    def test_template_refuses_overwrite_and_unknown_style(self):
        path = self.root / "template.json"
        create_template(path)
        before = path.read_bytes()
        with self.assertRaises(FileExistsError):
            create_template(path)
        self.assertEqual(path.read_bytes(), before)
        with self.assertRaises(ValueError):
            create_template(self.root / "bad.json", "nonexistent")
        self.assertFalse((self.root / "bad.json").exists())

    def test_design_reference_roles_with_and_without_style(self):
        design = self.root / "design.png"
        style = self.root / "style.png"
        Image.new("RGB", (128, 128), "green").save(design)
        Image.new("RGB", (128, 128), "blue").save(style)
        for include_style in (False, True):
            brief = self.grid_brief()
            brief.update(design_path=str(design), style_path=str(style) if include_style else None)
            task = self.run_job(brief, str(include_style))["tasks"][0]
            refs = task["input_images"]
            self.assertEqual(refs[-1]["role"], "outfit_design_only")
            self.assertEqual(refs[-1]["index"], 3 if include_style else 2)
            self.assertEqual(refs[-1]["path"], str(design))
            prompt = Path(task["prompt_file"]).read_text(encoding="utf-8")
            self.assertIn(f"Image {refs[-1]['index']} supplies the selected outfit themes", prompt)

    def test_reference_paths_reject_invalid_or_invisible_inputs(self):
        invisible = self.root / "invisible.png"
        Image.new("RGBA", (128, 128), (0, 0, 0, 0)).save(invisible)
        for key in ("style_path", "design_path"):
            for value in (False, [], "", str(invisible)):
                brief = self.grid_brief()
                brief[key] = value
                with self.assertRaises(ValueError):
                    self.run_job(brief)
                self.assertFalse((self.root / "run").exists())

    def test_design_reference_cannot_replace_identity_or_conflict_with_preserve(self):
        brief = self.grid_brief()
        brief["design_path"] = str(self.photo)
        with self.assertRaisesRegex(ValueError, "same file"):
            self.run_job(brief)
        design = self.root / "design.png"
        Image.new("RGB", (128, 128), "green").save(design)
        with self.assertRaisesRegex(ValueError, "requires series or redesign"):
            self.run_job(dict(self.brief, design_path=str(design)))

    @unittest.skipUnless(os.name == "nt", "Windows attachment syntax")
    def test_windows_attachment_prefix_is_normalized(self):
        info = image_info("/" + self.photo.as_posix())
        self.assertEqual(info["path"], str(self.photo))

    def test_cli_json_error_and_commands_without_pillow(self):
        script = str(Path(__file__).with_name("pfp_job.py"))
        # -S excludes site-packages: menu/template should still work without Pillow.
        menu = subprocess.run([sys.executable, "-S", script, "styles"], capture_output=True, text=True, encoding="utf-8", env=dict(os.environ, PYTHONUTF8="1"))
        self.assertEqual(menu.returncode, 0, menu.stderr)
        self.assertEqual(len(json.loads(menu.stdout)["styles"]), 9)
        missing = subprocess.run([sys.executable, "-S", script, "inspect", "--image", str(self.photo)], capture_output=True, text=True, encoding="utf-8", env=dict(os.environ, PYTHONUTF8="1"))
        self.assertEqual(missing.returncode, 2)
        self.assertIn("Pillow", json.loads(missing.stderr)["error"])

    def test_cli_bad_reference_returns_json_without_partial_job(self):
        path = self.root / "bad-brief.json"
        path.write_text(json.dumps(dict(self.brief, style_path=[])), encoding="utf-8")
        result = subprocess.run([sys.executable, "-X", "utf8", "-B", str(Path(__file__).with_name("pfp_job.py")), "prepare", "--brief", str(path), "--out", str(self.root / "run")], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stderr)["status"], "blocked")
        self.assertFalse((self.root / "run").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
