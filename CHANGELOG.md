# CHANGELOG

## v0.1.0 (2026-04-06)

### Chore

* chore: update gitignore for unified paths ([`4de4cf1`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/4de4cf1297577976fe9c5f21437a16097051f972))

* chore: add issue templates for bug reports and feature requests ([`864c5f4`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/864c5f40d843dd2532e9fd4e76c68a8b165e011d))

* chore: update headers to improve compatibility ([`2faf8b8`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/2faf8b8edbb24d18f0eb46a2aa6d40055f12535d))

* chore(deps): update project dependencies

- typer: ^0.13.0 → ^0.19.2
- aiofiles: ^24.1.0 → ^25.1.0
- ruff: ^0.7.4 → ^0.14.1
- types-aiofiles: ^24.1.0.20250326 → ^25.1.0.20251011 ([`402d758`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/402d758b8c50735928b20ffdb459b7cfcaf9ebe3))

* chore(mypy): align default quality value type with annotation

- Update default from bool to str (&#34;720&#34;) to satisfy mypy type checking.
- Add TODO to replace str with a custom Quality enum in the future. ([`7e8ad1c`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/7e8ad1cc8b8740679297b09016c3fec34d4887ec))

* chore: add new entries to .gitignore ([`3a73134`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/3a7313476f66f27029a93a946700b1ac13c9b7bb))

* chore: downloads folder was renamed ([`ef27357`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/ef2735761d8698a53e3214225d5e1c8c2d494a84))

* chore: add await to remove warning about unexecuted coroutine ([`392f70e`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/392f70e2961ba0af085fd1392998e02ba44b1bbc))

* chore: update USER_AGENT to Firefox for compatibility ([`b8d7332`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/b8d73320bdc75949eb63f8bc96dd078b7f4e457f))

* chore: update rnet.Client impersonation to Firefox139 ([`2cb1953`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/2cb1953b195f33ac032e1726bff67f51912dca97))

* chore: update all dependencies ([`b5b4b20`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/b5b4b20508c36a326daa2116182bee77e1e58e5a))

* chore(deps): replace deprecated &#39;rnet 2.2.1&#39; with &#39;rnet 2.4.2&#39; ([`6bb3b02`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/6bb3b02dff19d88ed5edc3dc69651076419bf89f))

* chore(ci): remove FFmpeg installation step from workflow ([`682dc2c`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/682dc2c22d90ba064adc3331d5ec88096b2a89d8))

* chore(ci): remove Playwright install step from workflow ([`cb1658d`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/cb1658db3c4f0acbd2a23f67501b9e5d8584d755))

* chore(ci): add formatting check step with Ruff in workflow ([`1cd28d7`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/1cd28d701d667533e0099203f4dcf4e05c1fc497))

* chore(typing): add types-aiofiles to dev deps ([`a23edfa`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/a23edfaf9798481cc059a5af9a1f17e8f9df7bf0))

* chore: add .vtt files to .gitignore ([`c4cb668`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/c4cb668063b129dc9641910c0c4c3152abef2aea))

* chore: add slug to Unit model

Add a `slug` field to the `Unit` model and populates it using the slugified title. ([`07484ec`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/07484ecd20c27682b70c0a02bd2c874f42b49fa6))

* chore: add type checking with MyPy

Add MyPy and integrates it into the CI workflow. ([`d79bc90`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/d79bc90dd6871e1614c0cb646fdb2b6d867b76fb))

* chore: removes unused modules and streamlines codebase ([`bcd2b06`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/bcd2b06d98901b9c70563f2d6c9071b794948025))

* chore: add CI workflows for testing and release ([`bc5855e`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/bc5855e39ecf9bf6ec5c621356432fe82053407f))

* chore: setup project configuration files

Initializes project with Poetry, sets up mypy for static type checking, and configures Ruff linter. ([`af9a825`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/af9a825cc234820f415775c663218d7f0e24a98a))

### Ci

* ci: update workflow to remove macOS from testing matrix ([`ab49d61`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/ab49d61987ab91fc54f5069831b9c76d1692dbf4))

### Documentation

* docs(readme): update repo shield badges ([`5774ad5`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/5774ad5c4ab166766300204700ae02a84fbbac9e))

* docs(readme): update repo banner image ([`1cd1644`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/1cd1644dd6bd819cd1b8e8de1c07a2a89ff5d77b))

* docs(readme): add contributors section ([`f4d96a9`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/f4d96a93e77d78293e4da53d9cc8b76eea2049b2))

* docs: update usage examples ([`f76ebf7`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/f76ebf79b839b69cc0f5c8f2603c832e0d9a1139))

* docs: add clear-cache command in usage guide ([`c29cda1`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/c29cda17830ea3036f5fcfc357879cb80d4cebfc))

* docs: add troubleshooting tips for m3u8 and ts download errors in README.md ([`0b6d170`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/0b6d1703ca42f5610968d3d03c95a4337c0c6c84))

* docs: removes outdated download instructions

Removes the section detailing how to download courses using a script, as this method is no longer applicable. ([`8d3e854`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/8d3e854a5db8a41f131177bb8d7865e81ad33dc3))

* docs: update README with updated installation and usage instructions. ([`0b9b500`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/0b9b500b7fa399c7ff7731e6b3ec0f6965d8523d))

* docs(readme): update discord server link ([`2c69db4`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/2c69db41e0e87458faedf9a4ac899d4370a74629))

### Feature

* feat: integrated specialized Stitch Skills and unified course download paths ([`837e7fd`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/837e7fdb22b53bb15a545bc1b91d508c304de5ff))

* feat: add logic for downloading resources and summary ([`56c02dc`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/56c02dc2e95807995fe2a96c503ed2d70a2f1c57))

* feat: add resource and summary search ([`79ca376`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/79ca376735d28be4ba935f0fdba4a718e6f8420c))

* feat: add quality option to download ([`d5cb258`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/d5cb2587163c03afd5d12fe9f74633b04d9b530e))

* feat: add quality selection ([`78d1b06`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/78d1b0694848145e6bd917523f6953622f83a295))

* feat: add download_styles function for downloading and returning remote stylesheets ([`288892b`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/288892b9548aa38e246c27fc42a9f7f1a745c1ed))

* feat: add retry decorator ([`9d698c2`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/9d698c20d2f4061ecc470e8e0a0a0834a1373bcd))

* feat: add overwrite option to download ([`c798e66`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/c798e669218311caa6670a8a2f54f0a25cbf3805))

* feat: implement caching mechanism and CLI command to clear cache ([`a3788c4`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/a3788c4c18912102ba410e9d40db95a9dce8ee31))

* feat: add caching mechanism for API responses

Introduces a `Cache` class to store and retrieve API responses using persistent storage. This improves performance by avoiding redundant API calls and enables offline access to previously fetched data.  The cache uses JSON files for storage. ([`df8ef74`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/df8ef746f5f96879f9768cb94b79d56dc12809a3))

* feat: add subtitle download support

Downloads subtitles in VTT format if available alongside the video. ([`436ffd7`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/436ffd7f20f3eac409108875e0cea45482feceb8))

* feat: add asynchronous Platzi downloader

Implements an asynchronous downloader for Platzi courses using Playwright. Includes features for login, logout, course downloading, and saving web pages as MHTML. ([`8074323`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/8074323d79d10eb32f6561f8459f46aafa19b0e8))

### Fix

* fix(http): update request headers to prevent 403 error ([`a64bb22`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/a64bb22c2f7e78b31827f1e8da2fdd950c1ace00))

* fix(rnet-client): send headers correctly in GET request ([`218b0ec`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/218b0ec3cc371cab969dac4bf94cc7a8c548aed9))

* fix(selectors): update selectors to prevent breakage on class hash changes ([`211970d`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/211970d857bb0bd6b9e9a97bc0765db0b5546da1))

* fix: update title selector for Unit data collection ([`663f1d2`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/663f1d22102f066afb656a647824f78e913352e9))

* fix: improve clean_string function to handle newlines and extra spaces ([`33e48ba`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/33e48ba5404fa277221e43013a8a41e0ed01e962))

* fix: rename &#39;overrides&#39; to &#39;overwrite&#39; in download function ([`ad48422`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/ad48422a706884e25d0313b9c10fa3f98e3689ce))

* fix: streaming URLs extraction in m3u8_dl ([`e937926`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/e937926859c2a285627e0e863a439259f3d0e2a5))

* fix: rename &#39;overrides&#39; to &#39;overwrite&#39; in _ts_dl function ([`77bc241`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/77bc241e39820b8aab354c742f4ef080deccc7dc))

* fix: ffmpeg check in decorator ([`5c507c4`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/5c507c4da760606a1bb6e15cd060ed837c2c1cb9))

* fix: update title selector for Unit data collection ([`8491c4d`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/8491c4dfb0e7db7782abc222d32e92b0d78971a1))

* fix: adds delays to avoid rate limiting ([`ba58014`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/ba58014e4c13e3301605ab1f8bb154a05f858be7))

* fix: reduce batch size for TS downloads from 10 to 5 ([`554affb`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/554affbb0dd189b89a67be1dc5a9caf725e69bab))

* fix: update selectors for course title and draft chapters in collectors.py ([`0100e2f`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/0100e2fb49304fe0ef1a2b77146897f5b36c89e2))

* fix: add handling for quiz URLs ([`6347ebb`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/6347ebb586269ebaaa2901cafd4d4212f77d5ff8))

* fix: TypeUnit inherit from str ([`55c71fe`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/55c71fee533c49b3ce04c61a0a51edceedea1d4b))

* fix: playwright browser installation step ([`f92dcbc`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/f92dcbc202ab2be73563e9385e765488a08bccff))

* fix: playwright browser installation step ([`79d1e90`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/79d1e908bc6addaf80b8f9385dde034e532ddd4a))

* fix: playwright browser installation step ([`43360fa`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/43360fad1048720dca2d1f7bbcb330a9ce0e0b85))

* fix(login): implement temporary workaround for login issue ([`5f3aecd`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/5f3aecd30f898ce867798fa811b09bef34b89331))

* fix: remove special characters in course_name ([`6a16916`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/6a16916c512da4aefaab3e6c9425b4e4f7aebaf2))

* fix: expand clean_string for more special characters ([`6384d49`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/6384d4957870d0e2df446200a8981e49836a0169))

### Refactor

* refactor: improve data models by adding default factories for lists and an optional summary field. Fix the error: &#34;ERROR: Could not collect unit data ([`73b30d5`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/73b30d596ac43494e9dd5ead5c58b1e48d4b6e86))

* refactor: simplify lecture/video detection with early return and html template modified ([`65dc8d1`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/65dc8d1b61fdc50c219496b345c7c0e2b9c5e844))

* refactor: use ternary expression for subtitle language detection ([`d62792a`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/d62792a69832403ad630214220625fdc399585e7))

* refactor: change resources from list[Resource] to single Resource ([`ff6f2cb`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/ff6f2cb3340becae593887b3e70c639474b91a5d))

* refactor: Resource model with new structure ([`dcd2bf2`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/dcd2bf2b0a8b2b60ca60d00c82a5c2ed0f7e3212))

* refactor: change subtitles_url from str to list[str] ([`2b3bb04`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/2b3bb04bdb6681acba58aca4ca14dd7e7150c098))

* refactor: better error handling, improved HTTP client with updated impersonation and redirect support ([`33fd7f6`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/33fd7f66e73fe62faa81a689dc3db84a46390f48))

* refactor: change get_subtitles_url return type from str to list ([`d228d6d`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/d228d6d648ed4f392cb5baa53fa0f8a20f4ca047))

* refactor: remove debug print statements from cache wrapper ([`7dbb769`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/7dbb769eef200c4a312557ffe9e1c640b2c4c594))

* refactor: replace aiohttp with rnet ([`b3e7380`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/b3e7380acdcf213384dffcd0e932b97a2f248805))

* refactor: replace tempfile with platformdirs for persistent session management ([`4e6e1b8`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/4e6e1b892755d0352072f68f450128a4fcb77348))

### Style

* style(ruff): format codebase with ruff

Apply Ruff formatting after merging some unformatted PRs. No functional
changes. ([`ced5586`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/ced5586a77cecbd8ffe910e9b5c0bb9831f37526))

* style: add course details table ([`4b81154`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/4b81154f1cb10ebe7b9333ba35ab91fc26b9d9de))

* style: update progress bar format for improved clarity ([`3011e90`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/3011e9085705573536f2f7d4af65f5d4b3cf8d33))

* style: update docstrings for get_course_slug, clean_string, and slugify functions ([`400dfc2`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/400dfc2700e8a524d4d38c9d3ecb91734556b73c))

* style: format collectors for better readability ([`dcde95a`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/dcde95aa3c170ceb94561378c51aa20e5e7e00ce))

### Test

* test(utils): update test cases for clean_string and slugify functions

Include special characters and newlines ([`2c50a4d`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/2c50a4d674c8413eadf9a8189720003538aef703))

### Unknown

* Personalización completa y refactorización Senior Full Stack para PLATZI-DOWNLOADER-HARDTOUR ([`23355b9`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/23355b9c2c8c9312a44d6794c6fd96bfb1242d8e))

* Merge pull request #48 from ivansaul/chore/add-github-issue-templates

chore: add issue templates for bug reports and feature requests ([`624d30f`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/624d30ff1e70e1482ce8c9bc64fc8c3cf21013ec))

* Merge pull request #44 from ivansaul/docs/update-shield-badges

docs(readme): update repo shield badges ([`758ce39`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/758ce397f500875ef47d9431f2f0c975e072d71c))

* Merge pull request #42 from alpha-drm/master ([`ad5729c`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/ad5729c327fe7045ed0358ba1cf941685e347c0e))

* Merge pull request #41 from ivansaul/docs/update-banner

docs(readme): update repo banner image ([`1439411`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/143941114d000daf55d2743b1f95c2c7befca6eb))

* Merge pull request #40 from ivansaul/docs/add-contributors

docs(readme): add contributors section ([`e87d878`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/e87d878d2f316bbaf8332ff4ab964575b3094861))

* Merge pull request #39 from alpha-drm/master

fix(rnet-client): send headers correctly in GET request ([`8f2da59`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/8f2da59530379c5a279a6fe8b75abafbf296a734))

* Merge pull request #37 from ivansaul/chore/deps-update

chore(deps): update project dependencies ([`99357fc`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/99357fc8697a59404c8cd1191b95f64e5f2c316d))

* Merge pull request #36 from ivansaul/chore/ruff-and-mypy

chore: apply Ruff formatting and align mypy type annotations ([`d34d607`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/d34d607f3f3275f6ba05ea9e4c8f0264a28b3d68))

* Merge pull request #34 from alpha-drm/master ([`ccbdcaa`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/ccbdcaa4207a4d9d6eb69f4ea1bd6e46a5b26fe2))

* Merge pull request #31 from FlacoAfk/master

refactor: improve data models by adding default factories for lists and an optional summary field. ([`6d3f966`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/6d3f966e6f8ecb2387f138eb2d3c41f1bf69242b))

* Merge pull request #30 from alpha-drm/master

feat: add resource downloads, subtitles, and video quality selection ([`066b73f`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/066b73f0eb4d2bcb46fae21cbf2f8caed3bd4518))

* Merge pull request #25 from ivansaul/develop

Improve clean_string for Newlines and Extra Spaces ([`c430bbb`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/c430bbb0dd35c741a757251266bba500840c66b0))

* Merge pull request #23 from ivansaul/develop

Add retry decorator and fix issues ([`5b5ae24`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/5b5ae24e497a19013004028aec41994791e36c16))

* Merge pull request #22 from ivansaul/develop

Add Cache Mechanism and Clear Command ([`5916652`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/59166521bd8b778f7cc4f7e343c5f9db85786b4f))

* Merge pull request #21 from ivansaul/develop

Replace aiohttp with rnet and fix Unit title selector ([`1450f92`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/1450f92e282e0cd7449adca601e4282771263170))

* Merge pull request #20 from ivansaul/develop

fix(ci, docs): improve collectors, downloads, and CI ([`5138848`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/51388483f210ad07900bef942afcff8708f5513c))

* Merge pull request #18 from ivansaul/refactor

fix: add handling for quiz URLs ([`186fe6b`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/186fe6b5e860b155c1f508bae56a494fd1f1181b))

* Merge pull request #17 from ivansaul/refactor

feat: add caching mechanism for API responses ([`ec810cd`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/ec810cd9ef50888e1da9deb198a5471eea6e9433))

* Merge pull request #12 from ivansaul/refactor

feat: add subtitle download support ([`7288751`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/728875124fe8a45d0d5fe939bdc24fea18143f3a))

* Merge pull request #11 from ivansaul/refactor

docs: removes outdated download instructions ([`f728ab8`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/f728ab8117d36e11a0e922c880b202a180aefd4a))

* Merge pull request #10 from ivansaul/refactor

docs: update README with updated installation and usage instructions. ([`b74c429`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/b74c42966f9d88479833045c50194290f47e57ef))

* Merge pull request #9 from ivansaul/refactor

feat: add asynchronous Platzi downloader ([`7605d64`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/7605d64bb5151e2a4c9c5708465c4df1fd85e568))

* initial commit ([`bffc0d2`](https://github.com/hardtour02/PLATZI-DOWNLOADER-HARDTOUR/commit/bffc0d2708d5b409fabf507db7ab34c3c0fb314a))
