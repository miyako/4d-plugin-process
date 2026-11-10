# 4d-plugin-process
Get and set process variables, read command line arguments

![version](https://img.shields.io/badge/version-18%2B-EB8E5F)
![platform](https://img.shields.io/static/v1?label=platform&message=mac-intel%20|%20mac-arm%20|%20win-64&color=blue)
[![license](https://img.shields.io/github/license/miyako/4d-plugin-process)](LICENSE)
![downloads](https://img.shields.io/github/downloads/miyako/4d-plugin-process/total)

## Source versions and manual releases

**Bump version** and **Build** are independent, manual Actions workflows. Select
the intended branch in Actions; neither workflow imposes a default-branch-only
restriction. Both check out the immutable dispatch `github.sha`.

Run **Bump version** with `patch`, `minor`, or `major` to commit only source
metadata on that selected branch. The working tree must be clean and the remote
branch must still equal the selected SHA. An executable, mandatory pre-push hook
also checks Git's advertised old SHA, the exact target branch, a literal `HEAD`
source, exactly one update, and the bump commit's single direct parent. A late
remote advance, rewind, deletion, or same-result competing push fails closed.
The push is non-forced and disables follow-tags. No tag, build, or dispatch is
created by a bump. If it fails, inspect the remote and select its current commit
again; do not force-push the stale bump.

Run **Build** separately on the intended source commit. It has no inputs:
validated strict source `X.Y.Z` determines the new `vX.Y.Z` tag, `Process-X.Y.Z.zip`,
and `Process-X.Y.Z.dmg`. It retains Windows x64 (MSBuild v143/Windows SDK 10.0),
the universal macOS `Default` build, the merged cross-platform bundle, Developer
ID signing and verification, both notarizations, and DMG stapling. Windows output
is removed and read only at the actual `.vcxproj` OutDir
`Process.4dbase/plugins/Process.bundle/contents/windows64/Process.4DX`, never an
arbitrary prebuilt match. Both notary responses must explicitly say `Accepted`.
The existing signing/notary secret names are unchanged.

Builds across branches share one non-cancelling publication concurrency group.
Before building, and again after all native/signing/notary/staple gates, the
helper checks remote tags and every authenticated release-list page, including
drafts. Existing versions and HTTP/auth/network/malformed-page failures stop
publication. Publication creates a lightweight tag at exactly the selected SHA
using a create-only refs POST, verifies the remote tag, creates a separate public,
non-prerelease release with the original release-note behavior, then uploads
assets only to the newly returned release ID. It never reuses, updates, deletes,
clobbers, rolls back, or retries production state.

**Manual recovery:** any successful earlier writes are deliberately retained if
tag verification, release creation, or asset upload fails. Read the error,
inspect the tag's SHA and release/assets (including drafts) in GitHub, and retain
the logs. Resolve the partial state manually under repository policy; do not
blindly rerun Build, because any retained tag/release blocks it. To publish a new
version instead, make a new source bump and select that commit. There is no
automated deletion, replacement, or rollback.

### Version authority and migration evidence

The former workflows were category B: Bump created a tag; Build ran on tag pushes
or an explicitly supplied tag. The default branch was independently confirmed as
`master` by GitHub's repository API and `git ls-remote --symref origin HEAD`.

The original `042688a058fb6741979a6989e35ff1545be0b627` bump header was
marketing-first with a current-version fallback. The later explicit header in
`fef22c5` superseded that contract: it requires **MARKETING_VERSION /
CURRENT_PROJECT_VERSION AND CFBundleShortVersionString / CFBundleVersion** to
share the version. Its marketing-first implementation did not fulfill that
header. This explicit coordinated authority, not the mere absence of a phrase
about independent versions, justifies coordination here. A marketing-only header
or marketing-first/fallback contract alone would require preserving independent
build bytes, even when their values happen to equal the marketing version.

Rename-follow history for `Process.xcodeproj/project.pbxproj` reaches
`process/Process.xcodeproj/project.pbxproj` through `042688a`; the source
`English.lproj/InfoPlist.strings` likewise comes from `process/English.lproj`.
At migration baseline `401be48911b0db32113077e6b9e1182fed305e8f`, all six
project/target configurations had marketing `2.0.5` but stale current `2.0.3`.
The source `Info.plist` had short version `2.0.5` and **no CFBundleVersion**.
The actual localized resource copied by `PBXResourcesBuildPhase` still displayed
`1.0`. This migration only repairs those six current fields and the two localized
display values to the existing `2.0.5`; it does not increment a version or add an
optional plist key. Localization retains its UTF-8 BOM, CR-only endings, product
name, and 2014 copyright verbatim.

Only the three source metadata paths are version authority. The prebuilt
`Process.4dbase/Plugins/Process.bundle`, root ZIP/DMG, `build/`, 4D database/project
and schema files, manifests/constants, `English.lproj/locversion.plist` counters,
API/dependencies, native sources, resources, frameworks, and toolsets are not
version-bump targets. Supported Xcode references, optional-key absence, file
modes, BOMs, every original line ending, and nonversion bytes are preserved;
drift, duplicate keys (including quoted duplicates), invalid references, and
unsupported serialization fail before writes.

The committed reference implementations used for this migration are:

| Repository | Pinned commit | Applicable precedent |
|---|---|---|
| `miyako/4d-plugin-proxy` | `4dc9995e5523f86f4d6d4d111f89ad3f81d8fb87` | Create-only lifecycle, helpers/tests, advertised-SHA push guard |
| `miyako/4d-plugin-system-beep` | `a4b3e57d3935185c354f99f6751aded2b2038d5a` | Explicit coordinated authority across six configurations |
| `miyako/4d-plugin-window-button` | `3f14facb9aaaaff0e22eeb8e07531163680c3a8a` | Corrected marketing-only authority; independent build bytes must not be normalized |
| `miyako/4d-plugin-common-string-algorithm` | `2606a68201866ec9fcbb38b51462d79215f504ef` | Marketing-first/fallback distinction, separate Build, fresh exact Windows output |

Local regression checks (no native builds, signing, notarization, 4D execution,
Actions dispatch, or production tag/release writes):

```sh
actionlint
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s .github/tests -v
```

The suite covers live-derived and fixed source fixtures, exact byte/mode
preservation and exclusions, temporary-copy bumps, real bare-Git races,
fail-closed paginated API responses, retained publication state, and workflow
wiring/native-command stubs. Native runner and credential-dependent execution
must still be exercised by an explicitly authorized manual Build.

## Native ownership regression checks

Run `python3 .github/tests/test_ownership.py -v` on macOS for an unsigned,
offline ASan/UBSan host test of the actual dispatcher, all shared wrappers and
the complete bundled SDK. It redirects process, environment and UI boundaries
to synthetic fixtures; it does not build, sign, package or release the plugin.
The [ownership audit](.github/tests/ownership-audit.md) records the immutable
baseline/SDK inventory, contracts, baseline-versus-fixed results, and explicit
OOM, metadata and real Windows/4D limits.

## Syntax

```4d
PROCESS GET ARGUMENTS(arguments)
```

Parameter|Type|Description
------------|------------|----
arguments|ARRAY TEXT|

```4d
PROCESS SET VARIABLE(name;name)
PROCESS GET VARIABLE(name;value)
```

Parameter|Type|Description
------------|------------|----
name|TEXT|
value|TEXT|

```4d
PROCESS GET LIST(name;path;pid)
```

Parameter|Type|Description
------------|------------|----
name|ARRAY TEXT|
path|ARRAY TEXT|
pid|ARRAY LONGINT|

```4d
pid:=PROCESS Get id 
```

Parameter|Type|Description
------------|------------|----
pid|LONGINT|
