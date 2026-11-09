import importlib.util
from pathlib import Path
import plistlib
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("source_version", ROOT / ".github/scripts/source_version.py")
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)
BASELINE = "401be48911b0db32113077e6b9e1182fed305e8f"


class SourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=".source-tests-", dir=ROOT)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.copy_source()
        self.current = source.read(self.root)
        parts = list(map(int, self.current.split(".")))
        parts[2] += 1
        self.drift = ".".join(map(str, parts))

    def copy_source(self):
        for name in source.SOURCE_PATHS:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, path)

    def plist(self, **values):
        path = self.root / source.PLIST
        data = plistlib.loads(path.read_bytes())
        data.update(values)
        path.write_bytes(plistlib.dumps(data))

    def snapshot(self):
        return {name: ((self.root / name).read_bytes(),
                       stat.S_IMODE((self.root / name).stat().st_mode))
                for name in source.SOURCE_PATHS if (self.root / name).exists()}

    def assert_rejected(self, error=ValueError):
        before = self.snapshot()
        with self.assertRaises(error):
            source.bump("patch", self.root)
        self.assertEqual(self.snapshot(), before)

    def test_live_and_stable_all_modes(self):
        self.assertEqual(source.SETTING_COUNT, 6)
        for stable in (False, True):
            for mode, index in (("major", 0), ("minor", 1), ("patch", 2)):
                self.copy_source()
                old = self.current
                if stable:
                    old = "3.2.1"
                    project = self.root / source.PROJECT
                    project.write_text(
                        ("MARKETING_VERSION = 3.2.1;\nCURRENT_PROJECT_VERSION = 3.2.1;\n") * 6)
                    self.plist(CFBundleShortVersionString=old, CFBundleVersion=old)
                    (self.root / source.LOCALIZED).write_text(
                        'CFBundleName = "Process";\nCFBundleShortVersionString = "3.2.1";\n'
                        'CFBundleGetInfoString = "Process version 3.2.1, Copyright 2014 miyako.";\n')
                before = self.snapshot()
                parts = list(map(int, old.split(".")))
                parts[index] += 1
                parts[index + 1:] = [0] * (2 - index)
                expected = ".".join(map(str, parts))
                self.assertEqual(source.bump(mode, self.root), expected)
                self.assertEqual(source.read(self.root), expected)
                for name, (data, permissions) in before.items():
                    self.assertEqual(self.snapshot()[name],
                                     (data.replace(old.encode(), expected.encode()), permissions))
                if not stable:
                    self.assertNotIn("CFBundleVersion",
                                     plistlib.loads((self.root / source.PLIST).read_bytes()))

    def test_actual_project_and_target_overrides(self):
        project = source.text(self.root / source.PROJECT)
        self.assertEqual(project.count("INFOPLIST_FILE = Info.plist;"), 3)
        for key in source.KEYS:
            self.assertEqual(len(re.findall(rf"(?m)^\s*{key} =", project)), 6)
            for count in (1, 3, 6):
                for bad in ("1.2", "7", "01.2.3", "v1.2.3", "1.2.3-beta", "",
                            self.drift, "$(UNKNOWN)", "$(CURRENT_PROJECT_VERSION)"):
                    self.copy_source()
                    path = self.root / source.PROJECT
                    path.write_text(project.replace(f"{key} = {self.current};",
                                                    f"{key} = {bad};", count))
                    self.assert_rejected()

    def test_missing_extra_quoted_and_malformed_settings(self):
        path = self.root / source.PROJECT
        original = source.text(path)
        for key in source.KEYS:
            for extra in (f"{key} = {self.current};", f'"{key}" = {self.current};',
                          f"{key} = {self.current}", f"{key} nonsense"):
                path.write_text(original + "\n" + extra + "\n")
                self.assert_rejected()
            path.write_text(original.replace(f"{key} = {self.current};", "", 1))
            self.assert_rejected()
            path.write_text(original.replace(f"{key} =", f'"{key}" =', 1))
            self.assert_rejected()

    def test_plist_invalid_missing_duplicate_and_serialization(self):
        for key in ("CFBundleShortVersionString", "CFBundleVersion"):
            for bad in ("", "7", "1.2", "01.2.3", "v1.2.3", "1.2.3-beta",
                        self.drift, "$(UNKNOWN)", "$(PRODUCT_NAME)", 123, []):
                self.copy_source()
                self.plist(**{key: bad})
                self.assert_rejected()
            for value in (self.current, self.drift):
                self.copy_source()
                self.plist(**{key: self.current})
                path = self.root / source.PLIST
                path.write_text(source.text(path).replace(
                    "</dict>", f"<key>{key}</key><string>{value}</string>\n</dict>"))
                self.assert_rejected()
        self.copy_source()
        path = self.root / source.PLIST
        original = path.read_bytes()
        data = plistlib.loads(original)
        del data["CFBundleShortVersionString"]
        for bad in (plistlib.dumps(data), plistlib.dumps([]), b"not a plist",
                    original.replace(b"</dict>", b""),
                    original.replace(self.current.encode(), b"&#50;" + self.current[1:].encode()),
                    plistlib.dumps(plistlib.loads(original), fmt=plistlib.FMT_BINARY)):
            path.write_bytes(bad)
            self.assert_rejected()

    def test_references_and_optional_absence_preserved(self):
        for reference in source.REFERENCES:
            for marketing in ("$(MARKETING_VERSION)", "${MARKETING_VERSION}"):
                self.copy_source()
                self.plist(CFBundleShortVersionString=reference, CFBundleVersion=reference)
                path = self.root / source.PROJECT
                path.write_text(source.SETTING.sub(
                    lambda m: f'{m[1]}"{marketing}"{m[4]}'
                    if m[2] == "CURRENT_PROJECT_VERSION" else m[0], source.text(path)))
                before = self.snapshot()
                new = source.bump("patch", self.root)
                for name, (data, permissions) in before.items():
                    self.assertEqual(self.snapshot()[name],
                                     (data.replace(self.current.encode(), new.encode()), permissions))
        for reference in source.REFERENCES:
            self.copy_source()
            path = self.root / source.PROJECT
            path.write_text(source.text(path).replace(
                f"MARKETING_VERSION = {self.current};", f'MARKETING_VERSION = "{reference}";'))
            self.assert_rejected()
        # A literal independent build/display-current mismatch cannot be normalized by bump.
        self.copy_source()
        self.plist(CFBundleShortVersionString="$(CURRENT_PROJECT_VERSION)")
        path = self.root / source.PROJECT
        path.write_text(source.text(path).replace(
            f"CURRENT_PROJECT_VERSION = {self.current};", "CURRENT_PROJECT_VERSION = 7;"))
        self.assert_rejected()

    def test_localized_validation_quoted_and_unquoted_duplicates(self):
        path = self.root / source.LOCALIZED
        original = source.text(path)
        for pattern in (source.LOCALIZED_SHORT, source.LOCALIZED_INFO):
            for bad in ("", "1.0", "01.2.3", self.drift, "$(MARKETING_VERSION)", "invalid"):
                path.write_text(pattern.sub(lambda m: f"{m[1]}{bad}{m[3]}", original))
                self.assert_rejected()
            path.write_text(pattern.sub("", original))
            self.assert_rejected()
        for key in ("CFBundleShortVersionString", "CFBundleGetInfoString"):
            for quoted in (False, True):
                name = f'"{key}"' if quoted else key
                path.write_text(original + f'\n{name} = "{self.current}";\n')
                self.assert_rejected()
        for old, new in (("Process", "Other"), ("Copyright 2014", "Copyright 2024"),
                         ("miyako", "someone")):
            path.write_text(original.replace(old, new))
            self.assert_rejected()

    def test_exact_bytes_newlines_bom_quotes_and_modes(self):
        for ending in ("\n", "\r", "\r\n", "mixed"):
            for bom in (b"", b"\xef\xbb\xbf"):
                for quoted in (False, True):
                    self.copy_source()
                    for i, name in enumerate(source.SOURCE_PATHS):
                        path = self.root / name
                        value = source.text(path)
                        if name == source.PROJECT:
                            for key in source.KEYS:
                                literal = f'"{self.current}"' if quoted else self.current
                                value = value.replace(f"{key} = {self.current};",
                                                      f"{key} \t= \t{literal} \t;")
                        value = "".join(line.replace("\n", ("\n", "\r", "\r\n")[j % 3]
                                                     if ending == "mixed" else ending)
                                        for j, line in enumerate(value.splitlines(keepends=True)))
                        path.write_bytes(bom + value.encode())
                        path.chmod((0o755, 0o640, 0o644)[i])
                    before = self.snapshot()
                    new = source.bump("minor", self.root)
                    for name, (data, permissions) in before.items():
                        self.assertEqual(self.snapshot()[name],
                                         (data.replace(self.current.encode(), new.encode()), permissions))

    def test_all_other_tracked_files_excluded(self):
        tracked = subprocess.check_output(["git", "-C", str(ROOT), "ls-files"], text=True).splitlines()
        excluded = [name for name in tracked if Path(name) not in source.SOURCE_PATHS]
        self.assertIn("English.lproj/locversion.plist", excluded)
        self.assertIn("Process.4dbase/Project/Sources/catalog.4DCatalog", excluded)
        self.assertIn("Process.4dbase/Plugins/Process.bundle/Contents/Info.plist", excluded)
        for name in excluded:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, path)
        before = {name: ((self.root / name).read_bytes(), (self.root / name).stat().st_mode)
                  for name in excluded}
        source.bump("major", self.root)
        self.assertEqual(before, {name: ((self.root / name).read_bytes(),
                                        (self.root / name).stat().st_mode) for name in excluded})

    def test_equal_nonversion_literals_are_not_rewritten(self):
        project = self.root / source.PROJECT
        project.write_text(source.text(project) + f"\n// keep {self.current}\n")
        self.plist(UnrelatedVersion=self.current, CFBundleVersion=self.current)
        localized = self.root / source.LOCALIZED
        localized.write_text(source.text(localized) + f'\nUnrelatedVersion = "{self.current}";\n')
        before = self.snapshot()
        new = source.bump("patch", self.root)
        for name, (original, permissions) in before.items():
            if name == source.PROJECT:
                pattern = rb'((?:MARKETING_VERSION|CURRENT_PROJECT_VERSION) = )' + self.current.encode()
            elif name == source.PLIST:
                pattern = (rb'(<key>CFBundle(?:ShortVersionString|Version)</key>\s*<string>)'
                           + self.current.encode())
            else:
                pattern = (rb'(CFBundleShortVersionString = "|Process version )'
                           + self.current.encode())
            expected = re.sub(pattern, lambda m: m[1] + new.encode(), original)
            self.assertEqual(self.snapshot()[name], (expected, permissions))

    def test_original_authority_repair_only_version_bytes(self):
        for name in source.SOURCE_PATHS:
            original = subprocess.check_output(["git", "show", f"{BASELINE}:{name}"], cwd=ROOT)
            version = self.current.encode()
            if name == source.PROJECT:
                expected = original.replace(b"MARKETING_VERSION = 2.0.5;",
                                            b"MARKETING_VERSION = " + version + b";")
                expected = expected.replace(b"CURRENT_PROJECT_VERSION = 2.0.3;",
                                            b"CURRENT_PROJECT_VERSION = " + version + b";")
            elif name == source.LOCALIZED:
                expected = original.replace(b'"1.0"', b'"' + version + b'"')
                expected = expected.replace(b"version 1.0,", b"version " + version + b",")
            else:
                expected = original.replace(b"<string>2.0.5</string>",
                                            b"<string>" + version + b"</string>")
            self.assertEqual((ROOT / name).read_bytes(), expected)
            mode = subprocess.check_output(["git", "ls-tree", BASELINE, "--", str(name)],
                                           cwd=ROOT, text=True).split()[0]
            self.assertEqual(stat.S_IMODE((ROOT / name).stat().st_mode), int(mode, 8) & 0o777)

    def test_explicit_header_supersedes_original_marketing_fallback(self):
        original = subprocess.check_output(
            ["git", "show", "042688a058fb6741979a6989e35ff1545be0b627:.github/workflows/bump-version.yml"],
            cwd=ROOT, text=True)
        coordinated = subprocess.check_output(
            ["git", "show", "fef22c568b07d48160f8e01a89cc560624a84ea6:.github/workflows/bump-version.yml"],
            cwd=ROOT, text=True)
        self.assertIn("falling back to CURRENT_PROJECT_VERSION", original.split("name:")[0])
        header = coordinated.split("name:")[0]
        self.assertIn("MARKETING_VERSION/CURRENT_PROJECT_VERSION AND", header)
        self.assertIn("CFBundleShortVersionString/CFBundleVersion", header)
        self.assertIn("InfoPlist.strings in Resources",
                      source.text(self.root / source.PROJECT))

    def test_missing_files_invalid_mode_cli_no_writes(self):
        for name in source.SOURCE_PATHS:
            self.copy_source()
            (self.root / name).unlink()
            self.assert_rejected(FileNotFoundError)
        self.copy_source()
        self.assert_rejected_mode()
        before = self.snapshot()
        result = subprocess.check_output(
            [sys.executable, str(ROOT / ".github/scripts/source_version.py")],
            cwd=self.root, text=True)
        self.assertEqual(result.strip(), self.current)
        self.assertEqual(self.snapshot(), before)

    def assert_rejected_mode(self):
        before = self.snapshot()
        with self.assertRaises(ValueError):
            source.bump("other", self.root)
        self.assertEqual(self.snapshot(), before)


if __name__ == "__main__":
    unittest.main()
