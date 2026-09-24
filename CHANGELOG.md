# Changelog

## [Unreleased](https://github.com/PASTA-ELN/pasta-eln/tree/HEAD)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.2.3b2...HEAD)

**Bug fixes:**

- Extractor item type does not work on Linux. [\#642](https://github.com/PASTA-ELN/pasta-eln/issues/642)
- Links in tutorial do not work out-of-the-box. [\#639](https://github.com/PASTA-ELN/pasta-eln/issues/639)

## [v3.3.0](https://github.com/PASTA-ELN/pasta-eln/tree/v3.3.0) (2026-09-24)

**Release source commit:** `40fe64ffd238d681472a1dfe577dc4dd81eb542e`
**Previous stable release:** `v3.2.3` (`0f2c7534418bcf69146620b065e5acd17ea9c581`)

### New features

- **New user interface:** redesigned sidebar, tabs, table, and Details pane; the form, configuration, and all other dialogs have been moved to the new design. ([`68cb14fa`](https://github.com/PASTA-ELN/pasta-eln/commit/68cb14faca84632eb98b416614df4e4c65a6746c)) ([`c7eb0f8e`](https://github.com/PASTA-ELN/pasta-eln/commit/c7eb0f8e4408b51dd85bad14ffa4f31b95f12751)) ([`9704ac0f`](https://github.com/PASTA-ELN/pasta-eln/commit/9704ac0f3ba94092b9d7f87366259def5a8867a5)) ([`d9ae7cdd`](https://github.com/PASTA-ELN/pasta-eln/commit/d9ae7cdd2bde3fb62988a35139ada34898728771)) ([`1ddcda9e`](https://github.com/PASTA-ELN/pasta-eln/commit/1ddcda9e24921bcae278217477af188a03f7bc51)) ([`8cc81e17`](https://github.com/PASTA-ELN/pasta-eln/commit/8cc81e1720833c10fdc1973321463af3b69aabee)) ([`26b4ea7c`](https://github.com/PASTA-ELN/pasta-eln/commit/26b4ea7cbef2bc19aedfb39fe3e7687371ec405c)) ([`a0b08261`](https://github.com/PASTA-ELN/pasta-eln/commit/a0b08261c53ade6ba15b450b8ea9bf81e5358d53)) ([`f68e077f`](https://github.com/PASTA-ELN/pasta-eln/commit/f68e077fd1618a87b40adf3cf50c06e9acef0866)) ([`0f9ff9c6`](https://github.com/PASTA-ELN/pasta-eln/commit/0f9ff9c68fb6d7797ff0a51658ec9fcf1f99bc2e)) ([`e6029d99`](https://github.com/PASTA-ELN/pasta-eln/commit/e6029d998f5aad2b68c9c77a140439b97a511338))
- Actions for projects, Details, and the table are reorganized; the table has additional actions, and menus are tidied up (#587). ([`1e11cf6d`](https://github.com/PASTA-ELN/pasta-eln/commit/1e11cf6d53dff676d6492a3a473851b5a7a10ae7)) ([`c2971da3`](https://github.com/PASTA-ELN/pasta-eln/commit/c2971da3067724cba93a48f3d9ba050fa7d0001f)) ([`a8922eb2`](https://github.com/PASTA-ELN/pasta-eln/commit/a8922eb20af374d1acf6cb0a06941d6857ac80b5))
- **Workplan Creator:** a new dialog, available from the menu bar, for assembling workplans from the procedures of the current project. Steps can be searched, arranged by drag and drop (with connecting arrows), and exported as a named workplan with sample information into the standard operating procedures. ([`4dbdbe17`](https://github.com/PASTA-ELN/pasta-eln/commit/4dbdbe172805540bd4302c3780894582477a519e)) ([`65509307`](https://github.com/PASTA-ELN/pasta-eln/commit/65509307920d41f15cfb5044dc7ca3799678f021)) ([`48413a98`](https://github.com/PASTA-ELN/pasta-eln/commit/48413a98d22b3d1cce84ee46f6ce80c6325d523e)) ([`b5a61381`](https://github.com/PASTA-ELN/pasta-eln/commit/b5a613814f4839329bc45383235f0ad8cb945979)) ([`1e2f6a2a`](https://github.com/PASTA-ELN/pasta-eln/commit/1e2f6a2adc119b9e05121609cb09795e317cbf62)) ([`7d410532`](https://github.com/PASTA-ELN/pasta-eln/commit/7d410532b9564e8c4061d28376b501ed923f78c5)) ([`d7928720`](https://github.com/PASTA-ELN/pasta-eln/commit/d7928720831a0d9c28ded279c4e6731e5c8de3b4)) ([`271c66cc`](https://github.com/PASTA-ELN/pasta-eln/commit/271c66cc4b742c46b9b1fbcfe5a1f36e521ff9bb)) ([`4dcac323`](https://github.com/PASTA-ELN/pasta-eln/commit/4dcac323c43ebff4c0bb64721f7de5da3de764d8)) ([`6baa1664`](https://github.com/PASTA-ELN/pasta-eln/commit/6baa1664ffd0a94e113c8146d852f45e71922d73)) ([`c8290faa`](https://github.com/PASTA-ELN/pasta-eln/commit/c8290faa841415f565ff050620cb91f9c847ad77)) ([`6709aee2`](https://github.com/PASTA-ELN/pasta-eln/commit/6709aee244dfa3461a0a6755028b096ac40cd39e)) ([`f3df87e9`](https://github.com/PASTA-ELN/pasta-eln/commit/f3df87e92ed01980ebd0241e7493d02fb502524a)) ([`f643b144`](https://github.com/PASTA-ELN/pasta-eln/commit/f643b144890f9a77a482bfbc108afa067e167567)) ([`17b52639`](https://github.com/PASTA-ELN/pasta-eln/commit/17b52639fbfdd55d4a04fd0b21b15778a08d4539))
- Hidden projects can be shown or hidden from the sidebar, and each project card displays a hidden icon (#477). ([`6883903c`](https://github.com/PASTA-ELN/pasta-eln/commit/6883903c47a3374469f50abc6901bd4cce0cb760))
- An indicator shows when an item has multiple branches (#451). ([`eda51e28`](https://github.com/PASTA-ELN/pasta-eln/commit/eda51e28be256dec9ed5ea3b72d5e10f8fe3c896))
- Items can be added directly from the project view (#595). ([`324a206a`](https://github.com/PASTA-ELN/pasta-eln/commit/324a206abb2ad1ee32979ff995a8ca37a44524d5))
- Measurement files can be imported via the menu (#441). ([`cc0e98d9`](https://github.com/PASTA-ELN/pasta-eln/commit/cc0e98d9cdcfd5383ab22b0e4a848594bf83f8ef))
- Linked items can be navigated from the Details pane (#505). ([`0d6911df`](https://github.com/PASTA-ELN/pasta-eln/commit/0d6911df42de37128819bade837b82c06208c85e))
- Folders, including their subfolders, can be excluded from scanning by placing a `.pastaELN_ignore` file in them. ([`05cb8932`](https://github.com/PASTA-ELN/pasta-eln/commit/05cb89321d241864377673e5445bed4b486f4f08))
- Standardized user-facing terminology, labels, and messages, including item type names. ([`0869f28a`](https://github.com/PASTA-ELN/pasta-eln/commit/0869f28a55e0d36de25761f5000944e56a78445a)) ([`c7c3f47b`](https://github.com/PASTA-ELN/pasta-eln/commit/c7c3f47bc8272e987395d254ca746b24ca40dfe4)) ([`3cacc52a`](https://github.com/PASTA-ELN/pasta-eln/commit/3cacc52a588b37748baf3b3c6d28f28bfbab5e8c))

### Improvements

- **eLabFTW synchronization:**
  - All five synchronization modes are supported. ([`f5f9c084`](https://github.com/PASTA-ELN/pasta-eln/commit/f5f9c084b4c81d8c5ddfc932a3cc9ddb1180845e))
  - Faster communication by reusing a session and data, and by skipping entries that are already synchronized. ([`f5f9c084`](https://github.com/PASTA-ELN/pasta-eln/commit/f5f9c084b4c81d8c5ddfc932a3cc9ddb1180845e)) ([`13f4d769`](https://github.com/PASTA-ELN/pasta-eln/commit/13f4d769a77774192c3954adc7360041da44805a))
  - Synchronization is no longer prevented when files, such as large files, are missing. ([`3335cceb`](https://github.com/PASTA-ELN/pasta-eln/commit/3335cceb14c551dc7be150e437e7943be2ab2b9c))
  - Uploads have a maximum size, defaulting to 100 MB. ([`ffd486db`](https://github.com/PASTA-ELN/pasta-eln/commit/ffd486dbc215ec68d33fcbc10712964dd44e1814)) ([`02e1dc65`](https://github.com/PASTA-ELN/pasta-eln/commit/02e1dc651fa869563a9878968097ec2a70aeb991))
  - Added a progress dialog for uploads, a cleaner upload message, and the synchronization runtime. ([`6adbb900`](https://github.com/PASTA-ELN/pasta-eln/commit/6adbb9000a588878d73088a2fbfa41fb65808c38)) ([`b3ea303a`](https://github.com/PASTA-ELN/pasta-eln/commit/b3ea303a3f9721d84b8cc4faec90ec5d3d210315)) ([`d2a0f663`](https://github.com/PASTA-ELN/pasta-eln/commit/d2a0f6639d3c36e98977afd70bb622977c66bc85))
  - Improved error logging for synchronization. ([`8d6b5a0f`](https://github.com/PASTA-ELN/pasta-eln/commit/8d6b5a0f2c2938c0525371b3b7c788e1aa85a1ec))
- Extractors run in parallel with a time limit. ([`02e1dc65`](https://github.com/PASTA-ELN/pasta-eln/commit/02e1dc651fa869563a9878968097ec2a70aeb991))
- Add-on loading is centralized to prevent the wrong add-ons from being used. After changing add-ons, restart PASTA-ELN. ([`05c5008a`](https://github.com/PASTA-ELN/pasta-eln/commit/05c5008a66db15a1f9b77f821f4fc38f21945cd9)) ([`db07f128`](https://github.com/PASTA-ELN/pasta-eln/commit/db07f128f43c05d991d4edfb5e9ec0302c7b9f33))
- Add-ons in the project view are sorted by name, and errors in add-ons print a traceback. ([`b3ea303a`](https://github.com/PASTA-ELN/pasta-eln/commit/b3ea303a3f9721d84b8cc4faec90ec5d3d210315)) ([`3e7647bb`](https://github.com/PASTA-ELN/pasta-eln/commit/3e7647bb760bfe69aa6fcc89b9738edc070f6821))
- Before moving the configuration, PASTA-ELN asks whether to back it up. ([`7a626f75`](https://github.com/PASTA-ELN/pasta-eln/commit/7a626f7580befb8a7a17f6bb73badf5cb42be8d4))
- Selecting an item in the project tree shows it in the Details pane, and clicking the item again closes it (#648). ([`d883caf3`](https://github.com/PASTA-ELN/pasta-eln/commit/d883caf37eec1e91905192c64e390b60cdab1db9)) ([`ef19db39`](https://github.com/PASTA-ELN/pasta-eln/commit/ef19db3961a2352ee9c5d3e17ec701ad31cd3008))
- The three-dot menu appears only on hover. ([`14a8d455`](https://github.com/PASTA-ELN/pasta-eln/commit/14a8d4550b8eb54c63f3bbd5b7aebb08fc581fee))
- Improved project view scrolling. ([`611d3bc1`](https://github.com/PASTA-ELN/pasta-eln/commit/611d3bc14fb9fcb4b9e6ef96d28b29c7f2772ceb))
- The Details pane also shows unidentified item types; message dialogs are rendered more clearly. ([`95dfd06b`](https://github.com/PASTA-ELN/pasta-eln/commit/95dfd06b2d0bcd8c9417cfbf6f781e355edf42c1))
- Improved the gallery, the database report style, and images in forms; improved the appearance of database verification. ([`0f028c7b`](https://github.com/PASTA-ELN/pasta-eln/commit/0f028c7b8d882ebd2d6458c6e764e645ada5f859)) ([`21684ec1`](https://github.com/PASTA-ELN/pasta-eln/commit/21684ec1d92d8f081305f08fca57ac7bbc719475))
- Updated tree view colors, rounded corners less strongly, and adjusted spacing throughout the interface. ([`6d26504d`](https://github.com/PASTA-ELN/pasta-eln/commit/6d26504d9fa950b4ca0c1522539dec3e1318b73c)) ([`d8030d78`](https://github.com/PASTA-ELN/pasta-eln/commit/d8030d78981127db8206c606a60baf822bf0e78a)) ([`c278fd97`](https://github.com/PASTA-ELN/pasta-eln/commit/c278fd97bda8c162baeabda2f8335acd32eec978))
- The default example now uses the FZJ logo. ([`7a984e90`](https://github.com/PASTA-ELN/pasta-eln/commit/7a984e90502356f47ea72c0f7ee5b83807771e9c))
- Updated dependencies to eliminate known security vulnerabilities, including a PKCS#7 decryption issue. ([`44663805`](https://github.com/PASTA-ELN/pasta-eln/commit/44663805c628bdf0f3ed503a82b3dc22980f2acd)) ([`5589e855`](https://github.com/PASTA-ELN/pasta-eln/commit/5589e855f6c6b88e3e4805d1ec6baef7005db1ac))

### Bug fixes

- Fixed links not being shown correctly in Details. ([`40784f6a`](https://github.com/PASTA-ELN/pasta-eln/commit/40784f6a493d647c9d974b2657edacf80c897e7b))
- Fixed Details extractor actions, and Details and form rendering for generated names and Markdown content; Details only crops non-HTML strings. ([`e82bf4fd`](https://github.com/PASTA-ELN/pasta-eln/commit/e82bf4fdfeaa18c645ad57e8000db10045daffdd)) ([`3dc28d33`](https://github.com/PASTA-ELN/pasta-eln/commit/3dc28d33f43d5f3aa470a07cd892f551afff95e1)) ([`db07f128`](https://github.com/PASTA-ELN/pasta-eln/commit/db07f128f43c05d991d4edfb5e9ec0302c7b9f33))
- Fixed the tags table. ([`3dc28d33`](https://github.com/PASTA-ELN/pasta-eln/commit/3dc28d33f43d5f3aa470a07cd892f551afff95e1))
- Fixed item visibility (#579). ([`02b2f201`](https://github.com/PASTA-ELN/pasta-eln/commit/02b2f2017f333a08e6745aae1d250393c8179d9f))
- Fixed #643, #640, and #603. ([`db07f128`](https://github.com/PASTA-ELN/pasta-eln/commit/db07f128f43c05d991d4edfb5e9ec0302c7b9f33))
- Fixed segmentation faults and crashes. ([`8db0220a`](https://github.com/PASTA-ELN/pasta-eln/commit/8db0220ae0a6f275b914ce571693821caf98b979)) ([`db07f128`](https://github.com/PASTA-ELN/pasta-eln/commit/db07f128f43c05d991d4edfb5e9ec0302c7b9f33)) ([`6709aee2`](https://github.com/PASTA-ELN/pasta-eln/commit/6709aee244dfa3461a0a6755028b096ac40cd39e)) ([`d8030d78`](https://github.com/PASTA-ELN/pasta-eln/commit/d8030d78981127db8206c606a60baf822bf0e78a))
- Prevented a crash when connected but unable to resolve the URL while checking for a new version. ([`0882ad92`](https://github.com/PASTA-ELN/pasta-eln/commit/0882ad927171e59c0269bef85aed0b9f6a10320a))
- The item type editor is now initialized with item type labels. ([`0882ad92`](https://github.com/PASTA-ELN/pasta-eln/commit/0882ad927171e59c0269bef85aed0b9f6a10320a))
- Fixed a bug in the editor. ([`a356e062`](https://github.com/PASTA-ELN/pasta-eln/commit/a356e0622834dc5a24c4da1f9cdbbd573e38d2e4))
- Fixed metadata plots that did not display. ([`dd552ebf`](https://github.com/PASTA-ELN/pasta-eln/commit/dd552ebfd0d1e2d5e8ab34e21f603e5b34597b16))
- Removing a project also removes its hidden children. ([`dd552ebf`](https://github.com/PASTA-ELN/pasta-eln/commit/dd552ebfd0d1e2d5e8ab34e21f603e5b34597b16))
- Rerunning an extractor now changes the item type correctly. ([`75bdb03b`](https://github.com/PASTA-ELN/pasta-eln/commit/75bdb03b9ba2b73089e6e6754329951a69c061f2))
- Prevented apostrophes from corrupting stored properties. ([`093f60d6`](https://github.com/PASTA-ELN/pasta-eln/commit/093f60d6fa817bede1137fd6e186e45c70a853ab))
- PASTA-ELN restarts after changing the project group. ([`093f60d6`](https://github.com/PASTA-ELN/pasta-eln/commit/093f60d6fa817bede1137fd6e186e45c70a853ab))
- Fixed scanning after extractors were parallelized. ([`2ad9d8e6`](https://github.com/PASTA-ELN/pasta-eln/commit/2ad9d8e6fe6b07a81ef3dd8030d695e65c72f3c4))
- Made deleting items in the table safer. ([`e902d225`](https://github.com/PASTA-ELN/pasta-eln/commit/e902d225f27ed07296d5b1b454976f89a93e07fe))
- Fixed sending to and getting from eLabFTW, and re-pulling from eLabFTW. ([`97077c59`](https://github.com/PASTA-ELN/pasta-eln/commit/97077c59d53409b1a2c32bbc14238e55fd54ae32)) ([`43d424e4`](https://github.com/PASTA-ELN/pasta-eln/commit/43d424e46df498cda5bf673c28eb6cfcc3a6e84d))
- Fixed updating the add-on list, and ensured that vendor and user metadata are handled as dictionaries. ([`95dfd06b`](https://github.com/PASTA-ELN/pasta-eln/commit/95dfd06b2d0bcd8c9417cfbf6f781e355edf42c1))
- Fixed shortcuts. ([`5c273bfb`](https://github.com/PASTA-ELN/pasta-eln/commit/5c273bfbe04877048d4496737273a24bf8876318))
- Improved alignment of right-aligned content. ([`5cf64107`](https://github.com/PASTA-ELN/pasta-eln/commit/5cf64107bac9e73d1af1ceee732b51c5a7be5b09)) ([`8ad2c68f`](https://github.com/PASTA-ELN/pasta-eln/commit/8ad2c68fff30215a5334ad633aa779c7dc5b6167)) ([`86ef438e`](https://github.com/PASTA-ELN/pasta-eln/commit/86ef438ef1abba09b7093418c6a43333cb47d4da)) ([`ff092dc0`](https://github.com/PASTA-ELN/pasta-eln/commit/ff092dc0d3c9472c91797eda1508dd6b7d08dd7f)) ([`f92c3ce7`](https://github.com/PASTA-ELN/pasta-eln/commit/f92c3ce70bee563a0e2216c0d500d43c16f8438d))
- Removed an SVG warning. ([`889d3d9a`](https://github.com/PASTA-ELN/pasta-eln/commit/889d3d9a819d70919e18102f820d57662aadfb00))
- Improved shutdown so that the backend is reliably closed. ([`269e276d`](https://github.com/PASTA-ELN/pasta-eln/commit/269e276d94e4018790a5e904722470cad84e192a)) ([`c36ce951`](https://github.com/PASTA-ELN/pasta-eln/commit/c36ce9513013ed01dfd2937e22724445256ec5d1))
- Fixed centering of the main widget. ([`93bb8915`](https://github.com/PASTA-ELN/pasta-eln/commit/93bb8915a1e5a46454ce02506f35ef823ad64719))

### Documentation

- Updated the README and documentation, and added the design philosophy. ([`cb0213fc`](https://github.com/PASTA-ELN/pasta-eln/commit/cb0213fc315080fca0555e9a07fd4f0c4ae9ee2b)) ([`54885e3c`](https://github.com/PASTA-ELN/pasta-eln/commit/54885e3cfcc73783e698131a8ea8a9ca17c7042f)) ([`48993c97`](https://github.com/PASTA-ELN/pasta-eln/commit/48993c9706d764d0527a776bc86f3afb7a988c39))

## [v3.2.3b2](https://github.com/PASTA-ELN/pasta-eln/tree/v3.2.3b2) (2026-03-10)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.2.3b1...v3.2.3b2)

## [v3.2.3b1](https://github.com/PASTA-ELN/pasta-eln/tree/v3.2.3b1) (2026-02-27)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.2.2...v3.2.3b1)

**New features:**

- Linking files in hindsight. [\#624](https://github.com/PASTA-ELN/pasta-eln/issues/624)
- key-value pairs as metadata and vice versa. [\#617](https://github.com/PASTA-ELN/pasta-eln/issues/617)
- Checking for double SHASUM//file duplicates. [\#604](https://github.com/PASTA-ELN/pasta-eln/issues/604)
- Checkboxes for the gallery view. [\#523](https://github.com/PASTA-ELN/pasta-eln/issues/523)

**Improvements:**

- Links do not apply for already created items? [\#635](https://github.com/PASTA-ELN/pasta-eln/issues/635)
- Change of style for csv-extractor? [\#632](https://github.com/PASTA-ELN/pasta-eln/issues/632)
- Removing one copy of measurement causes removal of all its copies. [\#629](https://github.com/PASTA-ELN/pasta-eln/issues/629)
- Double occurrence of keys. [\#620](https://github.com/PASTA-ELN/pasta-eln/issues/620)
- Form-Editor: sort tags in alphabetical order. [\#607](https://github.com/PASTA-ELN/pasta-eln/issues/607)
- 3.2.1b2 - overlap of item type and ID. [\#580](https://github.com/PASTA-ELN/pasta-eln/issues/580)

**Bug fixes:**

- Linking of items shows the internal ID but not the name. [\#636](https://github.com/PASTA-ELN/pasta-eln/issues/636)
- Error while rerunning extractors. [\#631](https://github.com/PASTA-ELN/pasta-eln/issues/631)
- A once added key can't be changed afterwards. [\#621](https://github.com/PASTA-ELN/pasta-eln/issues/621)
- Same file name - misrecognition of duplicates? [\#606](https://github.com/PASTA-ELN/pasta-eln/issues/606)

**Maintenance:**

- Get test\_03 working again. [\#628](https://github.com/PASTA-ELN/pasta-eln/issues/628)

## [v3.2.2](https://github.com/PASTA-ELN/pasta-eln/tree/v3.2.2) (2026-01-20)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.2.2b2...v3.2.2)

**New features:**

- Extractor arguments. [\#633](https://github.com/PASTA-ELN/pasta-eln/issues/633)

## [v3.2.2b2](https://github.com/PASTA-ELN/pasta-eln/tree/v3.2.2b2) (2025-12-27)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.2.2b1...v3.2.2b2)

**New features:**

- More possibilities for Key-writing. [\#623](https://github.com/PASTA-ELN/pasta-eln/issues/623)

**Improvements:**

- Capitalization of user metadata. [\#610](https://github.com/PASTA-ELN/pasta-eln/issues/610)

**Bug fixes:**

- Gallery View not working. [\#605](https://github.com/PASTA-ELN/pasta-eln/issues/605)

## [v3.2.2b1](https://github.com/PASTA-ELN/pasta-eln/tree/v3.2.2b1) (2025-12-25)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.2.1...v3.2.2b1)

**New features:**

- Linking items automatically in the same folder. [\#626](https://github.com/PASTA-ELN/pasta-eln/issues/626)
- Add several items by applying one extractor. [\#618](https://github.com/PASTA-ELN/pasta-eln/issues/618)
- Renaming and adding a key-value pair lead to rerunning of extractors. [\#615](https://github.com/PASTA-ELN/pasta-eln/issues/615)
- Drag-and-drop of a folder - Adding only files? [\#601](https://github.com/PASTA-ELN/pasta-eln/issues/601)
- Add-On folder in a new project group. [\#594](https://github.com/PASTA-ELN/pasta-eln/issues/594)
- Creation of new projects allows assignment of projects to other projects. [\#592](https://github.com/PASTA-ELN/pasta-eln/issues/592)

**Improvements:**

- Order of extractions when importing several files. [\#613](https://github.com/PASTA-ELN/pasta-eln/issues/613)
- User metadata - ordering by name? By relevance? [\#611](https://github.com/PASTA-ELN/pasta-eln/issues/611)
- Sorting children? [\#600](https://github.com/PASTA-ELN/pasta-eln/issues/600)
- When switching to hidden items only in table view, make sure that the details of hidden items do not remain open. [\#597](https://github.com/PASTA-ELN/pasta-eln/issues/597)
- Visibility of project status in project view. [\#593](https://github.com/PASTA-ELN/pasta-eln/issues/593)
- Unexpected behavior while deleting the folder with existing content in GUI. [\#591](https://github.com/PASTA-ELN/pasta-eln/issues/591)
- 3.2.1.b2 - key-value pairs when changing item type. [\#584](https://github.com/PASTA-ELN/pasta-eln/issues/584)
- Button visibility in pink/purple color schema. [\#575](https://github.com/PASTA-ELN/pasta-eln/issues/575)
- A large number of tags obscures the preview. [\#500](https://github.com/PASTA-ELN/pasta-eln/issues/500)
- List of tags. [\#492](https://github.com/PASTA-ELN/pasta-eln/issues/492)
- Create GUIs for history. [\#348](https://github.com/PASTA-ELN/pasta-eln/issues/348)

**Bug fixes:**

- Creation of new item type jumps to a different research group. [\#590](https://github.com/PASTA-ELN/pasta-eln/issues/590)
- Re-ordering of item type key-value-pairs. [\#589](https://github.com/PASTA-ELN/pasta-eln/issues/589)
- Drag-and-drop of images is not working. [\#614](https://github.com/PASTA-ELN/pasta-eln/issues/614)
- Default data plot yields error. [\#599](https://github.com/PASTA-ELN/pasta-eln/issues/599)
- Assigning of non-assigned item to project is not working. [\#596](https://github.com/PASTA-ELN/pasta-eln/issues/596)
- 3.2.1b2 - Labeling of items does not work properly. [\#582](https://github.com/PASTA-ELN/pasta-eln/issues/582)
- 3.2.1b2 - Assigning "not assigned" as project does not work. [\#581](https://github.com/PASTA-ELN/pasta-eln/issues/581)

## [v3.2.1](https://github.com/PASTA-ELN/pasta-eln/tree/v3.2.1) (2025-10-17)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.2.1b2...v3.2.1)

**New features:**

- 3.2.1b2 - Creation of new items? [\#583](https://github.com/PASTA-ELN/pasta-eln/issues/583)

**Improvements:**

- 3.2.1.b2 - Changing an item type of a file. [\#585](https://github.com/PASTA-ELN/pasta-eln/issues/585)

## [v3.2.1b2](https://github.com/PASTA-ELN/pasta-eln/tree/v3.2.1b2) (2025-10-10)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.2.1b1...v3.2.1b2)

**Improvements:**

- Scan button remains visible when accessing common lists. [\#578](https://github.com/PASTA-ELN/pasta-eln/issues/578)
- Templates for items. [\#571](https://github.com/PASTA-ELN/pasta-eln/issues/571)
- Export/Import of projects. [\#568](https://github.com/PASTA-ELN/pasta-eln/issues/568)
- Renaming the "List" dropdown menu to "Global List". [\#564](https://github.com/PASTA-ELN/pasta-eln/issues/564)
- Duplicating projects messes up file system. [\#563](https://github.com/PASTA-ELN/pasta-eln/issues/563)
- Not assigned items. [\#562](https://github.com/PASTA-ELN/pasta-eln/issues/562)
- Squished dialogs in some random cases on Ubuntu Wayland. [\#548](https://github.com/PASTA-ELN/pasta-eln/issues/548)
- Deselecting when closing item details. [\#503](https://github.com/PASTA-ELN/pasta-eln/issues/503)
- Order of tags/rating in the project view. [\#490](https://github.com/PASTA-ELN/pasta-eln/issues/490)
- v3.0: possible column headers. [\#337](https://github.com/PASTA-ELN/pasta-eln/issues/337)

**Bug fixes:**

- Restart when changing Research group? [\#572](https://github.com/PASTA-ELN/pasta-eln/issues/572)
- Changing item type works only unreliably. [\#569](https://github.com/PASTA-ELN/pasta-eln/issues/569)
- Data set duplication for items with file. [\#545](https://github.com/PASTA-ELN/pasta-eln/issues/545)
- Adding key-value pairs does not work. [\#510](https://github.com/PASTA-ELN/pasta-eln/issues/510)
- 3.2.1b1 - Repair/Re-installation broken. [\#567](https://github.com/PASTA-ELN/pasta-eln/issues/567)
- Windows: rename on the same name does not work. Go through code and search for all, wrap in if-clause. [\#565](https://github.com/PASTA-ELN/pasta-eln/issues/565)

**Maintenance:**

- create more applied test with links. [\#17](https://github.com/PASTA-ELN/pasta-eln/issues/17)

## [v3.2.1b1](https://github.com/PASTA-ELN/pasta-eln/tree/v3.2.1b1) (2025-09-11)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.2.0...v3.2.1b1)

**Improvements:**

- Standard Operation Procedures - Folder. [\#556](https://github.com/PASTA-ELN/pasta-eln/issues/556)
- "Instrument" vs. "Instruments". [\#543](https://github.com/PASTA-ELN/pasta-eln/issues/543)
- 3.2.0b3 - "unfolding" of Project view. [\#540](https://github.com/PASTA-ELN/pasta-eln/issues/540)
- sidebar buttons vanish when selecting item type list. [\#539](https://github.com/PASTA-ELN/pasta-eln/issues/539)
- unidentified items show full folder path. [\#525](https://github.com/PASTA-ELN/pasta-eln/issues/525)
- Column for the metaVendor file extension is empty. [\#524](https://github.com/PASTA-ELN/pasta-eln/issues/524)
- Details window contents do not scale with the window size. [\#516](https://github.com/PASTA-ELN/pasta-eln/issues/516)
- Sidebar: change to list of Todo, Todo priority. [\#307](https://github.com/PASTA-ELN/pasta-eln/issues/307)
- Order files / subitems by name in project view.  [\#260](https://github.com/PASTA-ELN/pasta-eln/issues/260)

**Bug fixes:**

- Non-extractor add-ons do not work in 3.2.0. [\#560](https://github.com/PASTA-ELN/pasta-eln/issues/560)
- Re-installation // Repair broken. [\#561](https://github.com/PASTA-ELN/pasta-eln/issues/561)
- 3.2.06b - Creating a new project broken. [\#557](https://github.com/PASTA-ELN/pasta-eln/issues/557)
- Linking via the lists in the data schema editor does not work. [\#509](https://github.com/PASTA-ELN/pasta-eln/issues/509)

## [v3.2.0](https://github.com/PASTA-ELN/pasta-eln/tree/v3.2.0) (2025-09-08)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.2.0b7...v3.2.0)

## [v3.2.0b7](https://github.com/PASTA-ELN/pasta-eln/tree/v3.2.0b7) (2025-08-26)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.2.0b6...v3.2.0b7)

**New features:**

- 3.2.0b6 - Creating a new project group. [\#558](https://github.com/PASTA-ELN/pasta-eln/issues/558)

**Improvements:**

- 3.1.11 - Definitions Editor. [\#554](https://github.com/PASTA-ELN/pasta-eln/issues/554)
- 3.2.0b6 - Definitions editor? [\#553](https://github.com/PASTA-ELN/pasta-eln/issues/553)
- 3.2.0b6 - The "Unidentified" list keeps dropdown lists from earlier lists. [\#552](https://github.com/PASTA-ELN/pasta-eln/issues/552)
- Deleting filter lines breaks filter lines. [\#550](https://github.com/PASTA-ELN/pasta-eln/issues/550)
- Shadow of the PASTA-ELN GUI. [\#379](https://github.com/PASTA-ELN/pasta-eln/issues/379)

**Bug fixes:**

- Filter lines break sometimes\(?\) [\#549](https://github.com/PASTA-ELN/pasta-eln/issues/549)
- 3.2.0b6 - Bugs in the item type editor. [\#551](https://github.com/PASTA-ELN/pasta-eln/issues/551)

**Documentation:**

- Installation Instructions - non-hardcoded Pasta path. [\#559](https://github.com/PASTA-ELN/pasta-eln/issues/559)
- Instructions to update for people without terminal. [\#555](https://github.com/PASTA-ELN/pasta-eln/issues/555)

## [v3.2.0b6](https://github.com/PASTA-ELN/pasta-eln/tree/v3.2.0b6) (2025-08-22)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.2.0b5...v3.2.0b6)

**New features:**

- Link to devices in the measurement item as default. [\#537](https://github.com/PASTA-ELN/pasta-eln/issues/537)
- New item types are not accessible? [\#491](https://github.com/PASTA-ELN/pasta-eln/issues/491)
- Configuration GUI: allow user to check if hidden items are by default hidden \(new\) or shown \(current\) [\#486](https://github.com/PASTA-ELN/pasta-eln/issues/486)

**Improvements:**

- Hardcoded subtypes for items? [\#544](https://github.com/PASTA-ELN/pasta-eln/issues/544)
- 3.2.0b3 - update of view after drag&drop. [\#538](https://github.com/PASTA-ELN/pasta-eln/issues/538)
- Renaming folders shifts the numbering? [\#534](https://github.com/PASTA-ELN/pasta-eln/issues/534)
- Example project ships with database problem. [\#533](https://github.com/PASTA-ELN/pasta-eln/issues/533)
- The down-arrow in the column editor moves up. [\#531](https://github.com/PASTA-ELN/pasta-eln/issues/531)
- Suggestion: Move "Invert hidden status of selected" to the "Selection" menu. [\#522](https://github.com/PASTA-ELN/pasta-eln/issues/522)
- Group editing of tags overwrites existing rating. [\#521](https://github.com/PASTA-ELN/pasta-eln/issues/521)
- tif extractor source unknown? [\#518](https://github.com/PASTA-ELN/pasta-eln/issues/518)
- Renaming a folder on the HDD breaks Pasta. [\#507](https://github.com/PASTA-ELN/pasta-eln/issues/507)
- batch file download. [\#498](https://github.com/PASTA-ELN/pasta-eln/issues/498)
- Storage of tags in item creation. [\#494](https://github.com/PASTA-ELN/pasta-eln/issues/494)
- Overlap Checkbox - Name of item. [\#483](https://github.com/PASTA-ELN/pasta-eln/issues/483)
- Shift in details view when clicking a linked item. [\#479](https://github.com/PASTA-ELN/pasta-eln/issues/479)
- Marking several items in a project. [\#383](https://github.com/PASTA-ELN/pasta-eln/issues/383)
- Backend; restart function \_\_init\_\_\(restart=False\) [\#341](https://github.com/PASTA-ELN/pasta-eln/issues/341)
- Progress bar. [\#147](https://github.com/PASTA-ELN/pasta-eln/issues/147)

**Bug fixes:**

- 3.2.0b5 - Add // add + next not working. [\#546](https://github.com/PASTA-ELN/pasta-eln/issues/546)
- Group edit or sequential edit: afterwards an \_ids is present in the database. [\#515](https://github.com/PASTA-ELN/pasta-eln/issues/515)
- Duplicating data sets does not work. [\#512](https://github.com/PASTA-ELN/pasta-eln/issues/512)
- Filtering by Tag in column editor does not work. [\#502](https://github.com/PASTA-ELN/pasta-eln/issues/502)
- New item types added are assigned "random" names. [\#501](https://github.com/PASTA-ELN/pasta-eln/issues/501)
- Sidebar: click on workflows closes that project in the sidebar. [\#488](https://github.com/PASTA-ELN/pasta-eln/issues/488)
- 3.2.0b3 - Project visibility leads to errors. [\#542](https://github.com/PASTA-ELN/pasta-eln/issues/542)
- Clicking a folder checkbox does not select the folder, but goes to project view. [\#541](https://github.com/PASTA-ELN/pasta-eln/issues/541)
- Link in setup window does not work. [\#532](https://github.com/PASTA-ELN/pasta-eln/issues/532)
- Cancelling a project group deletion does not stop the deletion. [\#530](https://github.com/PASTA-ELN/pasta-eln/issues/530)
- New tabs for the data schema editor do not work. [\#519](https://github.com/PASTA-ELN/pasta-eln/issues/519)

**Documentation:**

- Filter documentation for \*\*\*-Rating. [\#535](https://github.com/PASTA-ELN/pasta-eln/issues/535)

**Maintenance:**

- Check for updates - only for released versions. [\#520](https://github.com/PASTA-ELN/pasta-eln/issues/520)
- Requirements for installation of Pasta. [\#499](https://github.com/PASTA-ELN/pasta-eln/issues/499)

## [v3.2.0b5](https://github.com/PASTA-ELN/pasta-eln/tree/v3.2.0b5) (2025-08-13)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.2.0b4...v3.2.0b5)

## [v3.2.0b4](https://github.com/PASTA-ELN/pasta-eln/tree/v3.2.0b4) (2025-08-11)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.2.0b3...v3.2.0b4)

## [v3.2.0b3](https://github.com/PASTA-ELN/pasta-eln/tree/v3.2.0b3) (2025-08-09)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.2.0b2...v3.2.0b3)

## [v3.2.0b2](https://github.com/PASTA-ELN/pasta-eln/tree/v3.2.0b2) (2025-08-08)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.2.0b1...v3.2.0b2)

**Improvements:**

- Deselecting of rating not possible. [\#517](https://github.com/PASTA-ELN/pasta-eln/issues/517)
- Label moves when Selecting entry in table. [\#514](https://github.com/PASTA-ELN/pasta-eln/issues/514)
- Group edit. [\#504](https://github.com/PASTA-ELN/pasta-eln/issues/504)
- Automated update of packages. [\#463](https://github.com/PASTA-ELN/pasta-eln/issues/463)
- Remove \#TODO in code. [\#398](https://github.com/PASTA-ELN/pasta-eln/issues/398)
- Use pyside6 binding in matplotlib. [\#340](https://github.com/PASTA-ELN/pasta-eln/issues/340)

## [v3.2.0b1](https://github.com/PASTA-ELN/pasta-eln/tree/v3.2.0b1) (2025-07-03)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.1.11...v3.2.0b1)

**New features:**

- Adding a list via "Add key-value" button. [\#511](https://github.com/PASTA-ELN/pasta-eln/issues/511)
- Recognizing folders on "project level" as new projects. [\#508](https://github.com/PASTA-ELN/pasta-eln/issues/508)

**Improvements:**

- Formatting in comment box. [\#489](https://github.com/PASTA-ELN/pasta-eln/issues/489)
- Repair/install stuck at 75%. [\#481](https://github.com/PASTA-ELN/pasta-eln/issues/481)

**Bug fixes:**

- Windows: default desktop icon does not work. [\#497](https://github.com/PASTA-ELN/pasta-eln/issues/497)

## [v3.1.11](https://github.com/PASTA-ELN/pasta-eln/tree/v3.1.11) (2025-06-15)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.1.10...v3.1.11)

## [v3.1.10](https://github.com/PASTA-ELN/pasta-eln/tree/v3.1.10) (2025-06-12)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.1.10b2...v3.1.10)

## [v3.1.10b2](https://github.com/PASTA-ELN/pasta-eln/tree/v3.1.10b2) (2025-06-12)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.1.10b1...v3.1.10b2)

**New features:**

- Editing history/changelog per item. [\#495](https://github.com/PASTA-ELN/pasta-eln/issues/495)

**Improvements:**

- Example project item categories? [\#493](https://github.com/PASTA-ELN/pasta-eln/issues/493)
- Why show auto button in form when no add-on present? [\#487](https://github.com/PASTA-ELN/pasta-eln/issues/487)

**Bug fixes:**

- Details: long comment does not render fully. [\#485](https://github.com/PASTA-ELN/pasta-eln/issues/485)
- Error message after deleting the example project. [\#474](https://github.com/PASTA-ELN/pasta-eln/issues/474)

## [v3.1.10b1](https://github.com/PASTA-ELN/pasta-eln/tree/v3.1.10b1) (2025-06-10)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.1.9...v3.1.10b1)

**New features:**

- Filter list of items by key-value pair. [\#478](https://github.com/PASTA-ELN/pasta-eln/issues/478)
- Compile data from different items. [\#473](https://github.com/PASTA-ELN/pasta-eln/issues/473)
- Update notification/auto-update in pasta? [\#472](https://github.com/PASTA-ELN/pasta-eln/issues/472)
- Selecting a folder when creating new items. [\#423](https://github.com/PASTA-ELN/pasta-eln/issues/423)
- Add "Change columns" option to the Unidentified table view. [\#170](https://github.com/PASTA-ELN/pasta-eln/issues/170)

**Improvements:**

- Typo in API-key info box. [\#482](https://github.com/PASTA-ELN/pasta-eln/issues/482)
- Imported projects are folders? [\#470](https://github.com/PASTA-ELN/pasta-eln/issues/470)
- Update of extractors in the current project group. [\#466](https://github.com/PASTA-ELN/pasta-eln/issues/466)
- Alternative to cairo package? [\#465](https://github.com/PASTA-ELN/pasta-eln/issues/465)
- List of folders. [\#458](https://github.com/PASTA-ELN/pasta-eln/issues/458)
- Warning message about folders when repeatedly deleting the same file. [\#447](https://github.com/PASTA-ELN/pasta-eln/issues/447)
- Windows 10: initial window looks strange. [\#420](https://github.com/PASTA-ELN/pasta-eln/issues/420)
- Project head: has scrollbar and width that do not make sense. [\#374](https://github.com/PASTA-ELN/pasta-eln/issues/374)
- Ability to change from table row item to project and backward. [\#332](https://github.com/PASTA-ELN/pasta-eln/issues/332)
- Ability to lock property definitions. [\#331](https://github.com/PASTA-ELN/pasta-eln/issues/331)
- Sidebar change functionality \(depends on working project tree\) [\#13](https://github.com/PASTA-ELN/pasta-eln/issues/13)

**Bug fixes:**

- AttributeError in workflow. [\#484](https://github.com/PASTA-ELN/pasta-eln/issues/484)
- Instrument details open automatically but it can't be closed. [\#382](https://github.com/PASTA-ELN/pasta-eln/issues/382)
- Display bug in eln-Details. [\#350](https://github.com/PASTA-ELN/pasta-eln/issues/350)

**Documentation:**

- Attachments part of the document type or the individual entry. [\#372](https://github.com/PASTA-ELN/pasta-eln/issues/372)

## [v3.1.9](https://github.com/PASTA-ELN/pasta-eln/tree/v3.1.9) (2025-05-27)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.1.8...v3.1.9)

**New features:**

- Navigating via list. [\#480](https://github.com/PASTA-ELN/pasta-eln/issues/480)
- Using items as "folders". [\#475](https://github.com/PASTA-ELN/pasta-eln/issues/475)
- Allow to move items to "no project". [\#192](https://github.com/PASTA-ELN/pasta-eln/issues/192)

**Improvements:**

- Different menu layout for Mac? [\#476](https://github.com/PASTA-ELN/pasta-eln/issues/476)
- Missing bat-file. [\#471](https://github.com/PASTA-ELN/pasta-eln/issues/471)
- How to filter by \*\*\*\*-rating? [\#468](https://github.com/PASTA-ELN/pasta-eln/issues/468)
- Moving the filter dropdown menu to the left. [\#442](https://github.com/PASTA-ELN/pasta-eln/issues/442)
- Filtering for \*-rating not possible. [\#435](https://github.com/PASTA-ELN/pasta-eln/issues/435)
- Warning\(?\) when entering "\*" in the view filter. [\#433](https://github.com/PASTA-ELN/pasta-eln/issues/433)
- Using an excel file / csv to mass import items. [\#431](https://github.com/PASTA-ELN/pasta-eln/issues/431)
- "Gallery view" for all images in a project. [\#429](https://github.com/PASTA-ELN/pasta-eln/issues/429)
- Table: create two filters; remove the first. [\#363](https://github.com/PASTA-ELN/pasta-eln/issues/363)
- pyInstaller. [\#349](https://github.com/PASTA-ELN/pasta-eln/issues/349)
- Changing "Type" column title. [\#154](https://github.com/PASTA-ELN/pasta-eln/issues/154)
- Warning for the ipynb extractor. [\#112](https://github.com/PASTA-ELN/pasta-eln/issues/112)
- Improve tables. [\#19](https://github.com/PASTA-ELN/pasta-eln/issues/19)

**Bug fixes:**

- error on python -m pasta\_eln.gui execution in terminal. [\#467](https://github.com/PASTA-ELN/pasta-eln/issues/467)

## [v3.1.8](https://github.com/PASTA-ELN/pasta-eln/tree/v3.1.8) (2025-05-19)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.1.7...v3.1.8)

**New features:**

- No automated restart when a new project group add-on folder is created. [\#459](https://github.com/PASTA-ELN/pasta-eln/issues/459)

**Improvements:**

- Making the folder paths copy-able in the configurations. [\#462](https://github.com/PASTA-ELN/pasta-eln/issues/462)
- "size 0" for imported tif file? [\#460](https://github.com/PASTA-ELN/pasta-eln/issues/460)
- Projects not visible in sidebar. [\#457](https://github.com/PASTA-ELN/pasta-eln/issues/457)
- Progress bar for drag+drop progress. [\#456](https://github.com/PASTA-ELN/pasta-eln/issues/456)
- Toggling detail visibility for identical files. [\#455](https://github.com/PASTA-ELN/pasta-eln/issues/455)
- "Show all item details"-option missing. [\#454](https://github.com/PASTA-ELN/pasta-eln/issues/454)
- Sorting files by name in the project view. [\#453](https://github.com/PASTA-ELN/pasta-eln/issues/453)
- list of instruments in the data schema editor is called "instrument". [\#450](https://github.com/PASTA-ELN/pasta-eln/issues/450)
- Automated scan when drag/drop-ing files. [\#440](https://github.com/PASTA-ELN/pasta-eln/issues/440)
- Drag/Drop of folders? [\#438](https://github.com/PASTA-ELN/pasta-eln/issues/438)
- When moving addOn directory in project group editor, there should be three options. [\#419](https://github.com/PASTA-ELN/pasta-eln/issues/419)
- Deleting the only folder in a project. [\#396](https://github.com/PASTA-ELN/pasta-eln/issues/396)
- Make "aiohttp" dependency optional. [\#188](https://github.com/PASTA-ELN/pasta-eln/issues/188)

**Bug fixes:**

- Dot in properties table is lost. [\#452](https://github.com/PASTA-ELN/pasta-eln/issues/452)
- There is sometimes a bug during the github actions. [\#444](https://github.com/PASTA-ELN/pasta-eln/issues/444)

**Documentation:**

- Instruction for RSS feed on website. [\#461](https://github.com/PASTA-ELN/pasta-eln/issues/461)

**Maintenance:**

- Making the messages from the test extraction copy-able. [\#464](https://github.com/PASTA-ELN/pasta-eln/issues/464)
- Install requirements in scanNewExtractors. [\#156](https://github.com/PASTA-ELN/pasta-eln/issues/156)

## [v3.1.7](https://github.com/PASTA-ELN/pasta-eln/tree/v3.1.7) (2025-05-12)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.1.6...v3.1.7)

**Improvements:**

- Procedures are not accessible anymore in the lists. [\#448](https://github.com/PASTA-ELN/pasta-eln/issues/448)
- Changing the order of projects in the list on the left. [\#392](https://github.com/PASTA-ELN/pasta-eln/issues/392)

## [v3.1.6](https://github.com/PASTA-ELN/pasta-eln/tree/v3.1.6) (2025-05-09)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.1.5...v3.1.6)

**Bug fixes:**

- Update project destroys path of this and its children. [\#446](https://github.com/PASTA-ELN/pasta-eln/issues/446)

## [v3.1.5](https://github.com/PASTA-ELN/pasta-eln/tree/v3.1.5) (2025-05-05)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.1.4...v3.1.5)

## [v3.1.4](https://github.com/PASTA-ELN/pasta-eln/tree/v3.1.4) (2025-05-05)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.1.3...v3.1.4)

## [v3.1.3](https://github.com/PASTA-ELN/pasta-eln/tree/v3.1.3) (2025-05-05)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.1.2...v3.1.3)

**Improvements:**

- Description in data schema editos appear for all item types. [\#445](https://github.com/PASTA-ELN/pasta-eln/issues/445)

## [v3.1.2](https://github.com/PASTA-ELN/pasta-eln/tree/v3.1.2) (2025-04-21)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.1.1...v3.1.2)

**New features:**

- Checking folder names when creating a new project. [\#428](https://github.com/PASTA-ELN/pasta-eln/issues/428)

**Improvements:**

- capitalization of tags. [\#437](https://github.com/PASTA-ELN/pasta-eln/issues/437)
- "Ratings" vs. "tags". [\#432](https://github.com/PASTA-ELN/pasta-eln/issues/432)
- User names in elabFTW. [\#425](https://github.com/PASTA-ELN/pasta-eln/issues/425)
- Details provided in the API-key info box. [\#424](https://github.com/PASTA-ELN/pasta-eln/issues/424)
- Reordering when switching visibility. [\#422](https://github.com/PASTA-ELN/pasta-eln/issues/422)
- Theme: blue-light the icons are in black in the sidebar. [\#357](https://github.com/PASTA-ELN/pasta-eln/issues/357)
- v3.0: fix color issues when using \_amber theme. [\#338](https://github.com/PASTA-ELN/pasta-eln/issues/338)

**Bug fixes:**

- Duplication of items: Double clicking and Wrong list view. [\#416](https://github.com/PASTA-ELN/pasta-eln/issues/416)

## [v3.1.1](https://github.com/PASTA-ELN/pasta-eln/tree/v3.1.1) (2025-04-15)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.0.17...v3.1.1)

**Improvements:**

- Tags not searchable when using \*\*\*-ratings. [\#434](https://github.com/PASTA-ELN/pasta-eln/issues/434)
- Case sensitivity for folder names. [\#427](https://github.com/PASTA-ELN/pasta-eln/issues/427)
- Mandatoriness in the data schema editor. [\#418](https://github.com/PASTA-ELN/pasta-eln/issues/418)
- svg's do not appear in pasta as in VScode. [\#391](https://github.com/PASTA-ELN/pasta-eln/issues/391)
- The qr code line shows \[''\] after sample dimensions are added. [\#387](https://github.com/PASTA-ELN/pasta-eln/issues/387)
- Dataverse upload window. [\#316](https://github.com/PASTA-ELN/pasta-eln/issues/316)

**Bug fixes:**

- Data-verse: Repeatedly changing "metadata block" in metadata editor throws segmentation fault. [\#330](https://github.com/PASTA-ELN/pasta-eln/issues/330)
- ELN file generation for Dataverse upload. [\#321](https://github.com/PASTA-ELN/pasta-eln/issues/321)
- Dataverse: Saving the Metadata form reverts changes in Configure. [\#320](https://github.com/PASTA-ELN/pasta-eln/issues/320)

## [v3.0.17](https://github.com/PASTA-ELN/pasta-eln/tree/v3.0.17) (2025-03-29)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.0.16...v3.0.17)

**Improvements:**

- Warning message for folder creation during installation. [\#413](https://github.com/PASTA-ELN/pasta-eln/issues/413)
- Project group editor \(during programming lesson\) [\#409](https://github.com/PASTA-ELN/pasta-eln/issues/409)

**Bug fixes:**

- Data scheme editor -\> same name in different tabs yield error. [\#417](https://github.com/PASTA-ELN/pasta-eln/issues/417)
- Deletion of project group + subsequent saving error. [\#414](https://github.com/PASTA-ELN/pasta-eln/issues/414)

## [v3.0.16](https://github.com/PASTA-ELN/pasta-eln/tree/v3.0.16) (2025-03-25)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.0.15...v3.0.16)

**New features:**

- Restart of pasta after creating a new project group. [\#412](https://github.com/PASTA-ELN/pasta-eln/issues/412)
- Adding instruments to the links in a measurement. [\#393](https://github.com/PASTA-ELN/pasta-eln/issues/393)

**Improvements:**

- Renaming x0 and x1 into project/folder in the schema editor. [\#411](https://github.com/PASTA-ELN/pasta-eln/issues/411)
- items in schema editor vanish. [\#410](https://github.com/PASTA-ELN/pasta-eln/issues/410)
- Larger \(and/or more obvious\) notification windows. [\#406](https://github.com/PASTA-ELN/pasta-eln/issues/406)
- Export as html. [\#402](https://github.com/PASTA-ELN/pasta-eln/issues/402)
- Schema editor - List. [\#401](https://github.com/PASTA-ELN/pasta-eln/issues/401)
- List of tags shows \_all\_ items in that project. [\#394](https://github.com/PASTA-ELN/pasta-eln/issues/394)
- Selection of extractors for a multiply used file format. [\#388](https://github.com/PASTA-ELN/pasta-eln/issues/388)

**Bug fixes:**

- Add-On updater not working. [\#405](https://github.com/PASTA-ELN/pasta-eln/issues/405)
- Error in item editor. [\#399](https://github.com/PASTA-ELN/pasta-eln/issues/399)

## [v3.0.15](https://github.com/PASTA-ELN/pasta-eln/tree/v3.0.15) (2025-03-21)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.0.14...v3.0.15)

**Improvements:**

- Breaking pasta completely using the schema editor. [\#408](https://github.com/PASTA-ELN/pasta-eln/issues/408)
- Use Alt-Up Alt-Down to move up and down in form editor. [\#407](https://github.com/PASTA-ELN/pasta-eln/issues/407)
- elnidentifier key-value pair. [\#403](https://github.com/PASTA-ELN/pasta-eln/issues/403)
- Schema editor - mandatoriness. [\#400](https://github.com/PASTA-ELN/pasta-eln/issues/400)

**Bug fixes:**

- Form: autosave is not working anymore. [\#364](https://github.com/PASTA-ELN/pasta-eln/issues/364)

**Maintenance:**

- Test selected item extraction. [\#397](https://github.com/PASTA-ELN/pasta-eln/issues/397)
- "Test extraction from a file". [\#395](https://github.com/PASTA-ELN/pasta-eln/issues/395)

## [v3.0.14](https://github.com/PASTA-ELN/pasta-eln/tree/v3.0.14) (2025-03-15)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.0.13...v3.0.14)

**New features:**

- Adding metadata to the list instead of showing only the one from the current item. [\#390](https://github.com/PASTA-ELN/pasta-eln/issues/390)

**Improvements:**

- Showing the sample dimensions in the details column in the sample list. [\#386](https://github.com/PASTA-ELN/pasta-eln/issues/386)
- Sidebar buttons vanish on resizing window. [\#378](https://github.com/PASTA-ELN/pasta-eln/issues/378)
- Import and edit the eLabFTW project. [\#141](https://github.com/PASTA-ELN/pasta-eln/issues/141)

**Bug fixes:**

- Importing eln file multiple times. [\#229](https://github.com/PASTA-ELN/pasta-eln/issues/229)
- Editing comments in imported eln projects. [\#228](https://github.com/PASTA-ELN/pasta-eln/issues/228)
- Creation of project groups not working. [\#404](https://github.com/PASTA-ELN/pasta-eln/issues/404)
- Wrong version number in window title. [\#380](https://github.com/PASTA-ELN/pasta-eln/issues/380)
- Double clicking on empty cells in metadata table throws console errors. [\#305](https://github.com/PASTA-ELN/pasta-eln/issues/305)

## [v3.0.13](https://github.com/PASTA-ELN/pasta-eln/tree/v3.0.13) (2025-03-11)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.0.12...v3.0.13)

## [v3.0.12](https://github.com/PASTA-ELN/pasta-eln/tree/v3.0.12) (2025-03-11)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.0.11...v3.0.12)

## [v3.0.11](https://github.com/PASTA-ELN/pasta-eln/tree/v3.0.11) (2025-02-24)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.0.10...v3.0.11)

## [v3.0.10](https://github.com/PASTA-ELN/pasta-eln/tree/v3.0.10) (2025-02-20)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.0.9...v3.0.10)

## [v3.0.9](https://github.com/PASTA-ELN/pasta-eln/tree/v3.0.9) (2025-02-10)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.0.8...v3.0.9)

## [v3.0.8](https://github.com/PASTA-ELN/pasta-eln/tree/v3.0.8) (2025-02-07)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.0.7...v3.0.8)

## [v3.0.7](https://github.com/PASTA-ELN/pasta-eln/tree/v3.0.7) (2025-02-07)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.0.5...v3.0.7)

## [v3.0.5](https://github.com/PASTA-ELN/pasta-eln/tree/v3.0.5) (2025-01-30)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.0.4...v3.0.5)

**Improvements:**

- Selecting the columns shown in the sample list. [\#385](https://github.com/PASTA-ELN/pasta-eln/issues/385)
- Offering more sample geometries. [\#384](https://github.com/PASTA-ELN/pasta-eln/issues/384)

**Bug fixes:**

- Data hierarchy editor allows to remove default metadata group. [\#235](https://github.com/PASTA-ELN/pasta-eln/issues/235)

## [v3.0.4](https://github.com/PASTA-ELN/pasta-eln/tree/v3.0.4) (2025-01-08)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.0.3b2...v3.0.4)

## [v3.0.3b2](https://github.com/PASTA-ELN/pasta-eln/tree/v3.0.3b2) (2025-01-01)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.0.3b1...v3.0.3b2)

## [v3.0.3b1](https://github.com/PASTA-ELN/pasta-eln/tree/v3.0.3b1) (2024-12-29)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.0.2...v3.0.3b1)

## [v3.0.2](https://github.com/PASTA-ELN/pasta-eln/tree/v3.0.2) (2024-12-19)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.0.0...v3.0.2)

## [v3.0.0](https://github.com/PASTA-ELN/pasta-eln/tree/v3.0.0) (2024-12-19)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.0.1...v3.0.0)

## [v3.0.1](https://github.com/PASTA-ELN/pasta-eln/tree/v3.0.1) (2024-12-19)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.0.0b7...v3.0.1)

## [v3.0.0b7](https://github.com/PASTA-ELN/pasta-eln/tree/v3.0.0b7) (2024-12-16)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.0.0b6...v3.0.0b7)

## [v3.0.0b6](https://github.com/PASTA-ELN/pasta-eln/tree/v3.0.0b6) (2024-12-16)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.0.0b5...v3.0.0b6)

## [v3.0.0b5](https://github.com/PASTA-ELN/pasta-eln/tree/v3.0.0b5) (2024-12-16)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.0.0b4...v3.0.0b5)

## [v3.0.0b4](https://github.com/PASTA-ELN/pasta-eln/tree/v3.0.0b4) (2024-12-16)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.0.0b3...v3.0.0b4)

**Improvements:**

- Change the database: only one location of definitions. [\#377](https://github.com/PASTA-ELN/pasta-eln/pull/377) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Small changes. [\#376](https://github.com/PASTA-ELN/pasta-eln/pull/376) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

## [v3.0.0b3](https://github.com/PASTA-ELN/pasta-eln/tree/v3.0.0b3) (2024-12-09)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.0.0b2...v3.0.0b3)

**Improvements:**

- Adapt datahierarchy tool to use sqlite backend. [\#367](https://github.com/PASTA-ELN/pasta-eln/issues/367)
- Small changes. [\#375](https://github.com/PASTA-ELN/pasta-eln/pull/375) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

## [v3.0.0b2](https://github.com/PASTA-ELN/pasta-eln/tree/v3.0.0b2) (2024-12-02)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v3.0.0b1...v3.0.0b2)

## [v3.0.0b1](https://github.com/PASTA-ELN/pasta-eln/tree/v3.0.0b1) (2024-12-02)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.6.0...v3.0.0b1)

**New features:**

- Little side project: GUI for server actions. [\#16](https://github.com/PASTA-ELN/pasta-eln/issues/16)
- feat\(dataverse\): adapt data-verse module for new sqlite database.  [\#368](https://github.com/PASTA-ELN/pasta-eln/pull/368) ([jmurugan-fzj](https://github.com/jmurugan-fzj))
- feat\(data\_hierarchy\): implement changes for data type row.  [\#351](https://github.com/PASTA-ELN/pasta-eln/pull/351) ([jmurugan-fzj](https://github.com/jmurugan-fzj))

**Improvements:**

- Form: ctrl-s -\> save. [\#356](https://github.com/PASTA-ELN/pasta-eln/issues/356)
- Show that the details are hidden in project view. [\#355](https://github.com/PASTA-ELN/pasta-eln/issues/355)
- Adapt dataverse module to use sqlite backend. [\#353](https://github.com/PASTA-ELN/pasta-eln/issues/353)
- tags are incorrect in form: everywhere? [\#342](https://github.com/PASTA-ELN/pasta-eln/issues/342)
- Improve GUI of form. [\#339](https://github.com/PASTA-ELN/pasta-eln/issues/339)
- Report of project or folder. [\#333](https://github.com/PASTA-ELN/pasta-eln/issues/333)
- PASTA SQLite. [\#328](https://github.com/PASTA-ELN/pasta-eln/issues/328)
- Complete uninstallation. [\#267](https://github.com/PASTA-ELN/pasta-eln/issues/267)
- Speed up code. [\#261](https://github.com/PASTA-ELN/pasta-eln/issues/261)
- Possible update for pyside6. [\#247](https://github.com/PASTA-ELN/pasta-eln/issues/247)
- “More-change columns”.  [\#237](https://github.com/PASTA-ELN/pasta-eln/issues/237)
- Import of SampleDB.eln leads to segmentation fault. [\#231](https://github.com/PASTA-ELN/pasta-eln/issues/231)
- Project view: how to display 2000000 entries. [\#216](https://github.com/PASTA-ELN/pasta-eln/issues/216)
- SQLite based database. [\#159](https://github.com/PASTA-ELN/pasta-eln/issues/159)
- Creating items in the project view. [\#151](https://github.com/PASTA-ELN/pasta-eln/issues/151)
- Displaying IRIs and units. [\#148](https://github.com/PASTA-ELN/pasta-eln/issues/148)
- Rendering in projects. [\#105](https://github.com/PASTA-ELN/pasta-eln/issues/105)
- create function for searchChildNumber. [\#21](https://github.com/PASTA-ELN/pasta-eln/issues/21)
- Little side project: configAuthors.py. [\#15](https://github.com/PASTA-ELN/pasta-eln/issues/15)
- Two concept questions that we might discuss in future. [\#14](https://github.com/PASTA-ELN/pasta-eln/issues/14)
- Improve / change project tree. [\#12](https://github.com/PASTA-ELN/pasta-eln/issues/12)
- Ability to push data to dataverse. [\#10](https://github.com/PASTA-ELN/pasta-eln/issues/10)
- docs\(dataverse\): correct menu path for dataverse UI.  [\#371](https://github.com/PASTA-ELN/pasta-eln/pull/371) ([jmurugan-fzj](https://github.com/jmurugan-fzj))
- fix tuple branch in details. [\#362](https://github.com/PASTA-ELN/pasta-eln/pull/362) ([enmar-alkhafagi](https://github.com/enmar-alkhafagi))
- fix 322. [\#325](https://github.com/PASTA-ELN/pasta-eln/pull/325) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- 319. [\#324](https://github.com/PASTA-ELN/pasta-eln/pull/324) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

**Bug fixes:**

- Data-verse parallel uploads throws segmentation fault and crashes PASTA App. [\#365](https://github.com/PASTA-ELN/pasta-eln/issues/365)
- Scanning fails. [\#358](https://github.com/PASTA-ELN/pasta-eln/issues/358)
- Delete item from project view: incorrect. [\#354](https://github.com/PASTA-ELN/pasta-eln/issues/354)
- Scanning \(3.0\) [\#335](https://github.com/PASTA-ELN/pasta-eln/issues/335)
- Changing project details \(3.0\) [\#334](https://github.com/PASTA-ELN/pasta-eln/issues/334)
- Moving files inside and outside the GUI. [\#322](https://github.com/PASTA-ELN/pasta-eln/issues/322)
- Right click in project view. [\#319](https://github.com/PASTA-ELN/pasta-eln/issues/319)
- Verify database before and after Dataverse upload. [\#312](https://github.com/PASTA-ELN/pasta-eln/issues/312)
- CouchDB configuration in pasta\_eln 2.3.6. [\#309](https://github.com/PASTA-ELN/pasta-eln/issues/309)
- Qt plugin issue after new installation. [\#308](https://github.com/PASTA-ELN/pasta-eln/issues/308)
- Double-clicking on the "list" metadata field in Data Hierarchy. [\#306](https://github.com/PASTA-ELN/pasta-eln/issues/306)
- Errors during corrosion data import. [\#302](https://github.com/PASTA-ELN/pasta-eln/issues/302)
- Importing eln file 2. [\#296](https://github.com/PASTA-ELN/pasta-eln/issues/296)
- Importing eln file. [\#295](https://github.com/PASTA-ELN/pasta-eln/issues/295)
- Install on Ubuntu 24.04. [\#278](https://github.com/PASTA-ELN/pasta-eln/issues/278)
- Changing file names. [\#269](https://github.com/PASTA-ELN/pasta-eln/issues/269)
- Details GUI issue. [\#253](https://github.com/PASTA-ELN/pasta-eln/issues/253)
- fix\(dataverse\): implement fix for data-verse upload crash.  [\#366](https://github.com/PASTA-ELN/pasta-eln/pull/366) ([jmurugan-fzj](https://github.com/jmurugan-fzj))
- fix\(pasta\_app\_crash\): revert the PySide6 fixed version requirement. [\#359](https://github.com/PASTA-ELN/pasta-eln/pull/359) ([jmurugan-fzj](https://github.com/jmurugan-fzj))
- fix\(dataverse\): implement fix for the auto-selected items in metadata UI. [\#327](https://github.com/PASTA-ELN/pasta-eln/pull/327) ([jmurugan-fzj](https://github.com/jmurugan-fzj))
- fix\(dataverse\): implement fix for edit-error with empty list values. [\#326](https://github.com/PASTA-ELN/pasta-eln/pull/326) ([jmurugan-fzj](https://github.com/jmurugan-fzj))
- fix\(dataverse\): implement fix for config revert during metadata edits. [\#323](https://github.com/PASTA-ELN/pasta-eln/pull/323) ([jmurugan-fzj](https://github.com/jmurugan-fzj))
- test extractors does not work although the rerun extractor does. [\#360](https://github.com/PASTA-ELN/pasta-eln/issues/360)
- PASTA APP crashes with segmentation fault. [\#352](https://github.com/PASTA-ELN/pasta-eln/issues/352)
- Extractors not working. [\#311](https://github.com/PASTA-ELN/pasta-eln/issues/311)
- Links to samples which have a \_ in the docID, do not work as links. [\#230](https://github.com/PASTA-ELN/pasta-eln/issues/230)
- 253. [\#346](https://github.com/PASTA-ELN/pasta-eln/pull/346) ([enmar-alkhafagi](https://github.com/enmar-alkhafagi))
- in ContextMenu. [\#344](https://github.com/PASTA-ELN/pasta-eln/pull/344) ([enmar-alkhafagi](https://github.com/enmar-alkhafagi))

**Documentation:**

- Document data-verse module. [\#369](https://github.com/PASTA-ELN/pasta-eln/issues/369)
- docs\(dataverse\): extend docs to include the documentation of dataverse.  [\#370](https://github.com/PASTA-ELN/pasta-eln/pull/370) ([jmurugan-fzj](https://github.com/jmurugan-fzj))

**Maintenance:**

- Datahierarchy editor version 2.0. [\#329](https://github.com/PASTA-ELN/pasta-eln/issues/329)
- Python 3.12/ 3.11 requirement is too strict, relax in setup. Cfg. [\#310](https://github.com/PASTA-ELN/pasta-eln/issues/310)
- test how the main form looks with groups of questions and attachments. [\#226](https://github.com/PASTA-ELN/pasta-eln/issues/226)
- Test elabFTW import, after next consortium meeting. [\#209](https://github.com/PASTA-ELN/pasta-eln/issues/209)
- refactor\(data\_hierarchy\): adapt datahierarchy tool to use sqlite backend.   [\#373](https://github.com/PASTA-ELN/pasta-eln/pull/373) ([jmurugan-fzj](https://github.com/jmurugan-fzj))
- Version 3.0: Sqlite. [\#347](https://github.com/PASTA-ELN/pasta-eln/pull/347) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

## [v2.6.0](https://github.com/PASTA-ELN/pasta-eln/tree/v2.6.0) (2024-07-12)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.6.0b3...v2.6.0)

## [v2.6.0b3](https://github.com/PASTA-ELN/pasta-eln/tree/v2.6.0b3) (2024-07-11)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.6.0b2...v2.6.0b3)

**Bug fixes:**

- fix\(data-hierarchy\): implement fix for edit-error with single list values. [\#317](https://github.com/PASTA-ELN/pasta-eln/pull/317) ([jmurugan-fzj](https://github.com/jmurugan-fzj))

## [v2.6.0b2](https://github.com/PASTA-ELN/pasta-eln/tree/v2.6.0b2) (2024-07-10)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.6.0b1...v2.6.0b2)

**Bug fixes:**

- Data-verse fails to support upload in multiple user configured project groups. [\#301](https://github.com/PASTA-ELN/pasta-eln/issues/301)
- Error during eln file export when the organization list is empty. [\#294](https://github.com/PASTA-ELN/pasta-eln/issues/294)
- Opening "Dataverse Configuration" throws errors. [\#292](https://github.com/PASTA-ELN/pasta-eln/issues/292)
- Cryptography module not found.  [\#290](https://github.com/PASTA-ELN/pasta-eln/issues/290)
- fix\(data-hierarchy\): implement fix for edit-error with empty list values. [\#313](https://github.com/PASTA-ELN/pasta-eln/pull/313) ([jmurugan-fzj](https://github.com/jmurugan-fzj))
- fix\(dataverse\): integrated changes for handling multiple project groups. [\#304](https://github.com/PASTA-ELN/pasta-eln/pull/304) ([jmurugan-fzj](https://github.com/jmurugan-fzj))

## [v2.6.0b1](https://github.com/PASTA-ELN/pasta-eln/tree/v2.6.0b1) (2024-06-24)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.5.3...v2.6.0b1)

**New features:**

- feat\(dataverse\): implement data upload history module. [\#303](https://github.com/PASTA-ELN/pasta-eln/pull/303) ([jmurugan-fzj](https://github.com/jmurugan-fzj))
- Add cryptography to requirements. [\#291](https://github.com/PASTA-ELN/pasta-eln/pull/291) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

**Improvements:**

- Auto-filling the "Project" field. [\#153](https://github.com/PASTA-ELN/pasta-eln/issues/153)
- Auto-filling the "link" fields. [\#152](https://github.com/PASTA-ELN/pasta-eln/issues/152)
- Repair issue that occurs if author's organization... [\#298](https://github.com/PASTA-ELN/pasta-eln/pull/298) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Changes in form do not change the filename on the disk. [\#297](https://github.com/PASTA-ELN/pasta-eln/pull/297) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Sb python3.12. [\#284](https://github.com/PASTA-ELN/pasta-eln/pull/284) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

**Bug fixes:**

- Add new projects throws errors. [\#274](https://github.com/PASTA-ELN/pasta-eln/issues/274)
- Removing information from metadata fields. [\#268](https://github.com/PASTA-ELN/pasta-eln/issues/268)
- Temporarily block import to not cause errors. [\#300](https://github.com/PASTA-ELN/pasta-eln/pull/300) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

**Maintenance:**

- refactor\(dataverse\): move initialize\_database to backend.py.  [\#299](https://github.com/PASTA-ELN/pasta-eln/pull/299) ([jmurugan-fzj](https://github.com/jmurugan-fzj))

## [v2.5.3](https://github.com/PASTA-ELN/pasta-eln/tree/v2.5.3) (2024-05-15)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.5.3b1...v2.5.3)

## [v2.5.3b1](https://github.com/PASTA-ELN/pasta-eln/tree/v2.5.3b1) (2024-05-15)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.5.2...v2.5.3b1)

**New features:**

- perf\(dataverse\): implement changes to improve multiple uploads. [\#280](https://github.com/PASTA-ELN/pasta-eln/pull/280) ([jmurugan-fzj](https://github.com/jmurugan-fzj))
- feat\(dataverse\): implement data upload feature. [\#273](https://github.com/PASTA-ELN/pasta-eln/pull/273) ([jmurugan-fzj](https://github.com/jmurugan-fzj))

**Improvements:**

- Measurements in Unidentified table. [\#264](https://github.com/PASTA-ELN/pasta-eln/issues/264)
- feat\(dataverse\): extend metadata editor to show a save summary. [\#287](https://github.com/PASTA-ELN/pasta-eln/pull/287) ([jmurugan-fzj](https://github.com/jmurugan-fzj))
- sign eln file. [\#286](https://github.com/PASTA-ELN/pasta-eln/pull/286) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- feat\(dataverse\): integrate actual ELN generation functionality. [\#282](https://github.com/PASTA-ELN/pasta-eln/pull/282) ([jmurugan-fzj](https://github.com/jmurugan-fzj))
- Sb eln export multiple projects. [\#279](https://github.com/PASTA-ELN/pasta-eln/pull/279) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Sb 268 remove entries during editing. [\#276](https://github.com/PASTA-ELN/pasta-eln/pull/276) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- 153. [\#275](https://github.com/PASTA-ELN/pasta-eln/pull/275) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Skip things that have been done before and skip folders. [\#272](https://github.com/PASTA-ELN/pasta-eln/pull/272) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Speed up database:getHierarchy: factor \>30. [\#271](https://github.com/PASTA-ELN/pasta-eln/pull/271) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

**Bug fixes:**

- Scan Project with new folder and directories, does not create folder but unidentified item. [\#270](https://github.com/PASTA-ELN/pasta-eln/issues/270)
- Issues during the corrosion data import. [\#232](https://github.com/PASTA-ELN/pasta-eln/issues/232)
- fix\(dataverse\): fix for check\_if\_dataverse\_exists method failures. [\#288](https://github.com/PASTA-ELN/pasta-eln/pull/288) ([jmurugan-fzj](https://github.com/jmurugan-fzj))
- fix\(dataverse\): implement fix for the cancellation logic issue. [\#281](https://github.com/PASTA-ELN/pasta-eln/pull/281) ([jmurugan-fzj](https://github.com/jmurugan-fzj))
- Safeguard against fast form filling that does not create an autosave. [\#277](https://github.com/PASTA-ELN/pasta-eln/pull/277) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

**Maintenance:**

- clean the pytest such that my releaseScript runs successfully. [\#289](https://github.com/PASTA-ELN/pasta-eln/pull/289) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Export: you have to specify what you want to export. [\#285](https://github.com/PASTA-ELN/pasta-eln/pull/285) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- refactor\(dataverse\): restructure login configuration. [\#283](https://github.com/PASTA-ELN/pasta-eln/pull/283) ([jmurugan-fzj](https://github.com/jmurugan-fzj))

## [v2.5.2](https://github.com/PASTA-ELN/pasta-eln/tree/v2.5.2) (2024-04-17)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.5.2b2...v2.5.2)

## [v2.5.2b2](https://github.com/PASTA-ELN/pasta-eln/tree/v2.5.2b2) (2024-04-16)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.5.2b1...v2.5.2b2)

**New features:**

- Closing the "You will loose all new data..." warning pop-up. [\#224](https://github.com/PASTA-ELN/pasta-eln/issues/224)

**Improvements:**

- Sb 236 autosave fix. [\#266](https://github.com/PASTA-ELN/pasta-eln/pull/266) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Sb 232 fix also second run. [\#265](https://github.com/PASTA-ELN/pasta-eln/pull/265) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

**Bug fixes:**

- Changing item type to "Unidentified". [\#255](https://github.com/PASTA-ELN/pasta-eln/issues/255)
- Using “enter” to add a tag opens the extended comment field. [\#254](https://github.com/PASTA-ELN/pasta-eln/issues/254)
- Bugs and features that SB found. [\#263](https://github.com/PASTA-ELN/pasta-eln/pull/263) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

## [v2.5.2b1](https://github.com/PASTA-ELN/pasta-eln/tree/v2.5.2b1) (2024-04-12)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.5.1...v2.5.2b1)

**Improvements:**

- Drag drop. [\#262](https://github.com/PASTA-ELN/pasta-eln/pull/262) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- \#255. [\#259](https://github.com/PASTA-ELN/pasta-eln/pull/259) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- fix the issue \#254. [\#258](https://github.com/PASTA-ELN/pasta-eln/pull/258) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Sb 236 make autosave more logical. [\#257](https://github.com/PASTA-ELN/pasta-eln/pull/257) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

## [v2.5.1](https://github.com/PASTA-ELN/pasta-eln/tree/v2.5.1) (2024-04-05)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.5.1b1...v2.5.1)

**Improvements:**

- Slow code if change of project details. [\#144](https://github.com/PASTA-ELN/pasta-eln/issues/144)
- Sb 232 corrosion import2. [\#252](https://github.com/PASTA-ELN/pasta-eln/pull/252) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

**Bug fixes:**

- Right click on the empty project view. [\#227](https://github.com/PASTA-ELN/pasta-eln/issues/227)
- "Rerun extractors" removes shasum.  [\#220](https://github.com/PASTA-ELN/pasta-eln/issues/220)
- Metadata not saved in forms. [\#208](https://github.com/PASTA-ELN/pasta-eln/issues/208)

## [v2.5.1b1](https://github.com/PASTA-ELN/pasta-eln/tree/v2.5.1b1) (2024-04-05)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.5.0...v2.5.1b1)

**Improvements:**

- Check capilization in GUI: no "All Measurements". [\#185](https://github.com/PASTA-ELN/pasta-eln/issues/185)
- Fix \#241: WIndows installation. [\#250](https://github.com/PASTA-ELN/pasta-eln/pull/250) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Fix \#193. [\#249](https://github.com/PASTA-ELN/pasta-eln/pull/249) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- \#191. [\#248](https://github.com/PASTA-ELN/pasta-eln/pull/248) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Ignore configuration .pastaELN.json when restoring. [\#245](https://github.com/PASTA-ELN/pasta-eln/pull/245) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- User prompt improvements. [\#242](https://github.com/PASTA-ELN/pasta-eln/pull/242) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- speed up edit of project. [\#240](https://github.com/PASTA-ELN/pasta-eln/pull/240) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Fix \#185 \#227 \#220 in one PR since ... [\#239](https://github.com/PASTA-ELN/pasta-eln/pull/239) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

**Bug fixes:**

- CouchDB not installed on Windows. [\#241](https://github.com/PASTA-ELN/pasta-eln/issues/241)
- Removing the organization from "Author" configuration. [\#222](https://github.com/PASTA-ELN/pasta-eln/issues/222)
- ProjectView -\> Edit Project -\> Change name: new name not represented in left side bar. [\#193](https://github.com/PASTA-ELN/pasta-eln/issues/193)
- Project view -\> edit: after form closes, the corresponding item is expanded / collapsed. [\#191](https://github.com/PASTA-ELN/pasta-eln/issues/191)
- Display of comments in views. [\#98](https://github.com/PASTA-ELN/pasta-eln/issues/98)
- \#208. [\#246](https://github.com/PASTA-ELN/pasta-eln/pull/246) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- debug issue \#236. [\#243](https://github.com/PASTA-ELN/pasta-eln/pull/243) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

**Documentation:**

- Rescale all text documents in details, when the splitter changes size. [\#244](https://github.com/PASTA-ELN/pasta-eln/pull/244) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

## [v2.5.0](https://github.com/PASTA-ELN/pasta-eln/tree/v2.5.0) (2024-03-25)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.5.0b8...v2.5.0)

## [v2.5.0b8](https://github.com/PASTA-ELN/pasta-eln/tree/v2.5.0b8) (2024-03-25)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.5.0b7...v2.5.0b8)

**New features:**

- feat\(dataverse\): implement upload config dialog. [\#234](https://github.com/PASTA-ELN/pasta-eln/pull/234) ([jmurugan-fzj](https://github.com/jmurugan-fzj))

**Improvements:**

- Sb 222 remove twice. [\#238](https://github.com/PASTA-ELN/pasta-eln/pull/238) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

## [v2.5.0b7](https://github.com/PASTA-ELN/pasta-eln/tree/v2.5.0b7) (2024-03-21)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.5.0b6...v2.5.0b7)

**New features:**

- feat\(dataverse-integration\): implement metadata editor. [\#211](https://github.com/PASTA-ELN/pasta-eln/pull/211) ([jmurugan-fzj](https://github.com/jmurugan-fzj))

**Improvements:**

- Fix subissue 2 of \#222. [\#233](https://github.com/PASTA-ELN/pasta-eln/pull/233) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

## [v2.5.0b6](https://github.com/PASTA-ELN/pasta-eln/tree/v2.5.0b6) (2024-03-19)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.5.0b5...v2.5.0b6)

**New features:**

- feat\(terminology-service\): implement standalone version. [\#219](https://github.com/PASTA-ELN/pasta-eln/pull/219) ([jmurugan-fzj](https://github.com/jmurugan-fzj))

**Improvements:**

- Deleting a data type. [\#207](https://github.com/PASTA-ELN/pasta-eln/issues/207)
- Rerunning extractors of items with no files. [\#206](https://github.com/PASTA-ELN/pasta-eln/issues/206)
- Unidentified is not dataHierarchy: makes code simpler if it is. [\#194](https://github.com/PASTA-ELN/pasta-eln/issues/194)
- Installation of CouchDB via pastaELN Wizard not possible. [\#182](https://github.com/PASTA-ELN/pasta-eln/issues/182)
- Typos. [\#172](https://github.com/PASTA-ELN/pasta-eln/issues/172)
- "Projects" button in left sidebar. [\#150](https://github.com/PASTA-ELN/pasta-eln/issues/150)
- Importing items of other Data Types. [\#143](https://github.com/PASTA-ELN/pasta-eln/issues/143)
- Order of data hierarchy has to be followed in form. [\#135](https://github.com/PASTA-ELN/pasta-eln/issues/135)
- Export/import of items with the same name. [\#126](https://github.com/PASTA-ELN/pasta-eln/issues/126)
- Permanent project view. [\#95](https://github.com/PASTA-ELN/pasta-eln/issues/95)
- Improve main form. [\#11](https://github.com/PASTA-ELN/pasta-eln/issues/11)
- fix \#95, fully? [\#225](https://github.com/PASTA-ELN/pasta-eln/pull/225) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- fix \#221 and \#222, since related. [\#223](https://github.com/PASTA-ELN/pasta-eln/pull/223) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

**Bug fixes:**

- Saving the "Author" Configuration. [\#221](https://github.com/PASTA-ELN/pasta-eln/issues/221)
- Imported eln files incorrectly displayed. [\#204](https://github.com/PASTA-ELN/pasta-eln/issues/204)
- "Hide/show all item details" works only for x1. [\#203](https://github.com/PASTA-ELN/pasta-eln/issues/203)
- "Hide project details" results in error. [\#202](https://github.com/PASTA-ELN/pasta-eln/issues/202)
- Adding "Curated" column to the Project table view. [\#171](https://github.com/PASTA-ELN/pasta-eln/issues/171)
- "Mark item as hidden" after "Hide item details". [\#166](https://github.com/PASTA-ELN/pasta-eln/issues/166)
- Adding a new type leads to PASTA app crash. [\#176](https://github.com/PASTA-ELN/pasta-eln/issues/176)

## [v2.5.0b5](https://github.com/PASTA-ELN/pasta-eln/tree/v2.5.0b5) (2024-03-14)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.5.0b4...v2.5.0b5)

**Improvements:**

- Sb improve install. [\#218](https://github.com/PASTA-ELN/pasta-eln/pull/218) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Sb speed up start. [\#214](https://github.com/PASTA-ELN/pasta-eln/pull/214) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- \#203. [\#213](https://github.com/PASTA-ELN/pasta-eln/pull/213) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- \#202. [\#212](https://github.com/PASTA-ELN/pasta-eln/pull/212) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

**Bug fixes:**

- debug install.workflow.github. [\#217](https://github.com/PASTA-ELN/pasta-eln/pull/217) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

## [v2.5.0b4](https://github.com/PASTA-ELN/pasta-eln/tree/v2.5.0b4) (2024-03-12)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.4.28...v2.5.0b4)

**Improvements:**

- Update pypi.yml. [\#215](https://github.com/PASTA-ELN/pasta-eln/pull/215) ([srmnitc](https://github.com/srmnitc))
- Sb 126 items same name. [\#200](https://github.com/PASTA-ELN/pasta-eln/pull/200) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Sb 141 external import elab ftw. [\#199](https://github.com/PASTA-ELN/pasta-eln/pull/199) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- 143: unknown items should be in the undefined group. [\#198](https://github.com/PASTA-ELN/pasta-eln/pull/198) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

**Bug fixes:**

- CouchDB connectivity issues in pasta\_eln-2.4.27. [\#201](https://github.com/PASTA-ELN/pasta-eln/issues/201)
- Prevent extractor if the table line iteem does not have a file. [\#210](https://github.com/PASTA-ELN/pasta-eln/pull/210) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

## [v2.4.28](https://github.com/PASTA-ELN/pasta-eln/tree/v2.4.28) (2024-03-04)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.5.0b3...v2.4.28)

## [v2.5.0b3](https://github.com/PASTA-ELN/pasta-eln/tree/v2.5.0b3) (2024-02-27)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.5.0b2...v2.5.0b3)

## [v2.5.0b2](https://github.com/PASTA-ELN/pasta-eln/tree/v2.5.0b2) (2024-02-27)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.5.0b1...v2.5.0b2)

## [v2.5.0b1](https://github.com/PASTA-ELN/pasta-eln/tree/v2.5.0b1) (2024-02-27)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.4.27...v2.5.0b1)

**New features:**

- Allow user to disable / enable autosave in the configuration. [\#184](https://github.com/PASTA-ELN/pasta-eln/issues/184)
- New version of .eln and reading sampleDB and kadi4mat files. [\#197](https://github.com/PASTA-ELN/pasta-eln/pull/197) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- feat\(dataverse-integration\): implement dataverse configuration dialog. [\#196](https://github.com/PASTA-ELN/pasta-eln/pull/196) ([jmurugan-fzj](https://github.com/jmurugan-fzj))
- implemented feature wish \#150. [\#195](https://github.com/PASTA-ELN/pasta-eln/pull/195) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- feat\(dataverse-integration\): add base classes and templates. [\#190](https://github.com/PASTA-ELN/pasta-eln/pull/190) ([jmurugan-fzj](https://github.com/jmurugan-fzj))
- Implement improvements to the edit form. [\#186](https://github.com/PASTA-ELN/pasta-eln/pull/186) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- add organizations to author. [\#180](https://github.com/PASTA-ELN/pasta-eln/pull/180) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- feat\(dataverse-integration\): implement dataverse client library. [\#165](https://github.com/PASTA-ELN/pasta-eln/pull/165) ([jmurugan-fzj](https://github.com/jmurugan-fzj))

**Improvements:**

- Displaying issues after "Rerun extractors". [\#167](https://github.com/PASTA-ELN/pasta-eln/issues/167)
- Renaming of the Ontology editor/Questionnaires. [\#106](https://github.com/PASTA-ELN/pasta-eln/issues/106)
- Fix \#168.  [\#183](https://github.com/PASTA-ELN/pasta-eln/pull/183) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Sb couchdb3.3.3. [\#181](https://github.com/PASTA-ELN/pasta-eln/pull/181) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Display issues after rerun extractors. [\#178](https://github.com/PASTA-ELN/pasta-eln/pull/178) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Sb less user interaction. [\#177](https://github.com/PASTA-ELN/pasta-eln/pull/177) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- feat\(data\_hierarchy\): renaming and restructuring data hierarchy tool. [\#130](https://github.com/PASTA-ELN/pasta-eln/pull/130) ([jmurugan-fzj](https://github.com/jmurugan-fzj))

**Bug fixes:**

- "All items" table view opens after editing. [\#168](https://github.com/PASTA-ELN/pasta-eln/issues/168)
- Deleting projects with same names. [\#162](https://github.com/PASTA-ELN/pasta-eln/issues/162)
- Repair smaller bugs that I found.  [\#189](https://github.com/PASTA-ELN/pasta-eln/pull/189) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- code does not crash if shortcut and/or icon does not exist in a. [\#179](https://github.com/PASTA-ELN/pasta-eln/pull/179) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

**Documentation:**

- Issue 182: update documentation. [\#187](https://github.com/PASTA-ELN/pasta-eln/pull/187) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Improve editor of documents. [\#174](https://github.com/PASTA-ELN/pasta-eln/pull/174) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

**Maintenance:**

- ci\(pasta\): update issue templates. [\#175](https://github.com/PASTA-ELN/pasta-eln/pull/175) ([jmurugan-fzj](https://github.com/jmurugan-fzj))
- refactor\(data-hierarchy\): modify textual information in UI. [\#173](https://github.com/PASTA-ELN/pasta-eln/pull/173) ([jmurugan-fzj](https://github.com/jmurugan-fzj))
- docs\(data\_hierarchy\): adapting help page to the latest version. [\#131](https://github.com/PASTA-ELN/pasta-eln/pull/131) ([jmurugan-fzj](https://github.com/jmurugan-fzj))

## [v2.4.27](https://github.com/PASTA-ELN/pasta-eln/tree/v2.4.27) (2023-12-18)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.4.26...v2.4.27)

**New features:**

- implement HT idea. [\#169](https://github.com/PASTA-ELN/pasta-eln/pull/169) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

## [v2.4.26](https://github.com/PASTA-ELN/pasta-eln/tree/v2.4.26) (2023-12-14)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.4.25...v2.4.26)

**Improvements:**

- Confirmation popup when deleting multiple items. [\#149](https://github.com/PASTA-ELN/pasta-eln/issues/149)
- Comment display in the project view header. [\#111](https://github.com/PASTA-ELN/pasta-eln/issues/111)

**Bug fixes:**

- Using "Hide project details" raises an error. [\#161](https://github.com/PASTA-ELN/pasta-eln/issues/161)
- Data loss when changing Data Type. [\#146](https://github.com/PASTA-ELN/pasta-eln/issues/146)
- Project header moved after changing Data Type. [\#142](https://github.com/PASTA-ELN/pasta-eln/issues/142)
- Changing data types and rerunning extractors. [\#136](https://github.com/PASTA-ELN/pasta-eln/issues/136)
- Does not start in windows, reason unclear. [\#86](https://github.com/PASTA-ELN/pasta-eln/issues/86)
- Debug \#162: Deleting projects with same names. [\#164](https://github.com/PASTA-ELN/pasta-eln/pull/164) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

## [v2.4.25](https://github.com/PASTA-ELN/pasta-eln/tree/v2.4.25) (2023-12-12)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.4.24...v2.4.25)

**Improvements:**

- Progress bar to import and export. [\#18](https://github.com/PASTA-ELN/pasta-eln/issues/18)
- Repaired issue \#111. [\#160](https://github.com/PASTA-ELN/pasta-eln/pull/160) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Try to repair \#142. [\#158](https://github.com/PASTA-ELN/pasta-eln/pull/158) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- \#repair issue 146. [\#157](https://github.com/PASTA-ELN/pasta-eln/pull/157) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Repair issue \#149. [\#155](https://github.com/PASTA-ELN/pasta-eln/pull/155) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

**Bug fixes:**

- Import and edit the eLabFTW project. [\#133](https://github.com/PASTA-ELN/pasta-eln/issues/133)

**Maintenance:**

- Deleting an item in a specific table opens a general table. [\#134](https://github.com/PASTA-ELN/pasta-eln/issues/134)

## [v2.4.24](https://github.com/PASTA-ELN/pasta-eln/tree/v2.4.24) (2023-11-17)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.4.23...v2.4.24)

**Improvements:**

- Appearance options not used from saved state. [\#125](https://github.com/PASTA-ELN/pasta-eln/issues/125)
- Removing all columns from tables. [\#116](https://github.com/PASTA-ELN/pasta-eln/issues/116)
- Importing incorrect. [\#115](https://github.com/PASTA-ELN/pasta-eln/issues/115)
- Checkboxes in project table view. [\#113](https://github.com/PASTA-ELN/pasta-eln/issues/113)
- Long text in the project view header. [\#110](https://github.com/PASTA-ELN/pasta-eln/issues/110)
- repair issue \#134. [\#140](https://github.com/PASTA-ELN/pasta-eln/pull/140) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Sb redo name has to be in table. [\#137](https://github.com/PASTA-ELN/pasta-eln/pull/137) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

**Bug fixes:**

- Unidentified table cannot be opened. [\#114](https://github.com/PASTA-ELN/pasta-eln/issues/114)
- debug unknown keys with strange values. [\#138](https://github.com/PASTA-ELN/pasta-eln/pull/138) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

**Documentation:**

- if \_attachment in doc prior to saving a new document, …. [\#139](https://github.com/PASTA-ELN/pasta-eln/pull/139) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

## [v2.4.23](https://github.com/PASTA-ELN/pasta-eln/tree/v2.4.23) (2023-11-09)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.4.22...v2.4.23)

## [v2.4.22](https://github.com/PASTA-ELN/pasta-eln/tree/v2.4.22) (2023-11-09)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.4.21...v2.4.22)

## [v2.4.21](https://github.com/PASTA-ELN/pasta-eln/tree/v2.4.21) (2023-11-09)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.4.20...v2.4.21)

**Improvements:**

- Jpeg extractor issue. [\#118](https://github.com/PASTA-ELN/pasta-eln/issues/118)
- Deleting structure levels 2 and 1. [\#117](https://github.com/PASTA-ELN/pasta-eln/issues/117)
- Edit of sample that has no project. [\#85](https://github.com/PASTA-ELN/pasta-eln/issues/85)
- repaired \#125: Appearance options not used from saved state. [\#127](https://github.com/PASTA-ELN/pasta-eln/pull/127) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Sb extractor bad metadata. [\#122](https://github.com/PASTA-ELN/pasta-eln/pull/122) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- repaired \#116. [\#121](https://github.com/PASTA-ELN/pasta-eln/pull/121) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Repaired \#110 and \#111 since they belong to the same file. [\#119](https://github.com/PASTA-ELN/pasta-eln/pull/119) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

**Bug fixes:**

- Bug if branch not in doc. [\#107](https://github.com/PASTA-ELN/pasta-eln/issues/107)
- Editing unassigned items. [\#82](https://github.com/PASTA-ELN/pasta-eln/issues/82)
- Importing .eln with unidentified-\>measurement files. [\#79](https://github.com/PASTA-ELN/pasta-eln/issues/79)
- Creating new project after eLabFTW eln import. [\#78](https://github.com/PASTA-ELN/pasta-eln/issues/78)
- undo a recently created bug. [\#132](https://github.com/PASTA-ELN/pasta-eln/pull/132) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Remove bug that occurs if you remove a project with content. [\#124](https://github.com/PASTA-ELN/pasta-eln/pull/124) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Sb project view x3 does not exist. [\#123](https://github.com/PASTA-ELN/pasta-eln/pull/123) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Sb table bugs. [\#120](https://github.com/PASTA-ELN/pasta-eln/pull/120) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

## [v2.4.20](https://github.com/PASTA-ELN/pasta-eln/tree/v2.4.20) (2023-10-27)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.4.19...v2.4.20)

**Improvements:**

- Repair rendering in projects \#105. [\#109](https://github.com/PASTA-ELN/pasta-eln/pull/109) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

## [v2.4.19](https://github.com/PASTA-ELN/pasta-eln/tree/v2.4.19) (2023-10-27)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.4.18...v2.4.19)

**Improvements:**

- Ontologie issues for Steffen. [\#92](https://github.com/PASTA-ELN/pasta-eln/issues/92)
- Heading styles in project view. [\#84](https://github.com/PASTA-ELN/pasta-eln/issues/84)
- Improving user experience with "Visibility" options. [\#62](https://github.com/PASTA-ELN/pasta-eln/issues/62)
- comment in project view. [\#36](https://github.com/PASTA-ELN/pasta-eln/issues/36)

**Bug fixes:**

- Autosaving after adding the comment. [\#87](https://github.com/PASTA-ELN/pasta-eln/issues/87)
- Changing column names in table. [\#76](https://github.com/PASTA-ELN/pasta-eln/issues/76)
- Hide in item editor. [\#63](https://github.com/PASTA-ELN/pasta-eln/issues/63)
- Button should highlight premature end of install. [\#32](https://github.com/PASTA-ELN/pasta-eln/issues/32)
- repair bug \#107. [\#108](https://github.com/PASTA-ELN/pasta-eln/pull/108) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

## [v2.4.18](https://github.com/PASTA-ELN/pasta-eln/tree/v2.4.18) (2023-10-25)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.4.17...v2.4.18)

## [v2.4.17](https://github.com/PASTA-ELN/pasta-eln/tree/v2.4.17) (2023-10-25)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.4.16...v2.4.17)

**New features:**

- Implemented visibility issues mentioned in \#62. [\#103](https://github.com/PASTA-ELN/pasta-eln/pull/103) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- add codespell: configuration, workflow + get it to fix found typos. [\#96](https://github.com/PASTA-ELN/pasta-eln/pull/96) ([yarikoptic](https://github.com/yarikoptic))
- fixed: Creating new project after eLabFTW eln import \#78. [\#91](https://github.com/PASTA-ELN/pasta-eln/pull/91) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- fixed: Autosaving after adding the comment. [\#89](https://github.com/PASTA-ELN/pasta-eln/pull/89) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

**Improvements:**

- Cancel export eln. [\#65](https://github.com/PASTA-ELN/pasta-eln/issues/65)
- Markdown editor - heading styles. [\#64](https://github.com/PASTA-ELN/pasta-eln/issues/64)
- - Unified comments in all views \#98 \#84. [\#104](https://github.com/PASTA-ELN/pasta-eln/pull/104) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Sb start windows. [\#97](https://github.com/PASTA-ELN/pasta-eln/pull/97) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Honor labels from ontology in project view and change the default labels …. [\#93](https://github.com/PASTA-ELN/pasta-eln/pull/93) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Fixed: Changing column names in table \#76. [\#90](https://github.com/PASTA-ELN/pasta-eln/pull/90) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Fixed: [\#88](https://github.com/PASTA-ELN/pasta-eln/pull/88) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

**Bug fixes:**

- Deleting "Comment" in Ontology editor. [\#99](https://github.com/PASTA-ELN/pasta-eln/issues/99)
- Using "Re-order" in Questionnaires. [\#66](https://github.com/PASTA-ELN/pasta-eln/issues/66)
- fix\(ontology\): runtime errors been thrown for flags returning NoneType. [\#102](https://github.com/PASTA-ELN/pasta-eln/pull/102) ([jmurugan-fzj](https://github.com/jmurugan-fzj))
- fix\(ontology\): consecutive save click throws console errors.  [\#101](https://github.com/PASTA-ELN/pasta-eln/pull/101) ([jmurugan-fzj](https://github.com/jmurugan-fzj))
- repaired issue \#63. [\#73](https://github.com/PASTA-ELN/pasta-eln/pull/73) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

**Maintenance:**

- test\(ontology\): added automated tests for ontology component. [\#100](https://github.com/PASTA-ELN/pasta-eln/pull/100) ([jmurugan-fzj](https://github.com/jmurugan-fzj))

## [v2.4.16](https://github.com/PASTA-ELN/pasta-eln/tree/v2.4.16) (2023-10-13)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.4.14...v2.4.16)

**New features:**

- Merging the new changes, so I can use this Branch again. [\#9](https://github.com/PASTA-ELN/pasta-eln/pull/9) ([RaphaelRoeske](https://github.com/RaphaelRoeske))

**Improvements:**

- Table view: Change columns. [\#59](https://github.com/PASTA-ELN/pasta-eln/issues/59)
- Auto-populating IRI field of ontology editor.  [\#58](https://github.com/PASTA-ELN/pasta-eln/issues/58)
- Deletion of an item in table view. [\#57](https://github.com/PASTA-ELN/pasta-eln/issues/57)
- Import of own .eln files. [\#38](https://github.com/PASTA-ELN/pasta-eln/issues/38)
- Importing the eLabFTW .eln files. [\#37](https://github.com/PASTA-ELN/pasta-eln/issues/37)
- project view header: show comment nicely. [\#20](https://github.com/PASTA-ELN/pasta-eln/issues/20)
- feat\(ontology\): auto-populating IRI fields of ontology editor tool. [\#75](https://github.com/PASTA-ELN/pasta-eln/pull/75) ([jmurugan-fzj](https://github.com/jmurugan-fzj))

**Bug fixes:**

- Deleting Structure 0 data types in Questionnaires. [\#68](https://github.com/PASTA-ELN/pasta-eln/issues/68)
- Empty properties in Questionnaires. [\#67](https://github.com/PASTA-ELN/pasta-eln/issues/67)
- fix\(ontology\): deletion of structural level types & normal types. [\#83](https://github.com/PASTA-ELN/pasta-eln/pull/83) ([jmurugan-fzj](https://github.com/jmurugan-fzj))
- fix\(ontology\): introduced check for properties with empty names. [\#80](https://github.com/PASTA-ELN/pasta-eln/pull/80) ([jmurugan-fzj](https://github.com/jmurugan-fzj))
- fix\(ontology\): enabled auto stretch for the property table. [\#77](https://github.com/PASTA-ELN/pasta-eln/pull/77) ([jmurugan-fzj](https://github.com/jmurugan-fzj))
- repaired \#36 \#20. [\#74](https://github.com/PASTA-ELN/pasta-eln/pull/74) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- repaired \#59. [\#72](https://github.com/PASTA-ELN/pasta-eln/pull/72) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- repaired issue \#64. [\#71](https://github.com/PASTA-ELN/pasta-eln/pull/71) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- \#65. [\#70](https://github.com/PASTA-ELN/pasta-eln/pull/70) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Sb improve logging save view error. [\#81](https://github.com/PASTA-ELN/pasta-eln/pull/81) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

## [v2.4.14](https://github.com/PASTA-ELN/pasta-eln/tree/v2.4.14) (2023-10-03)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.4.13...v2.4.14)

**New features:**

- Minor changes to release new version, none of the edited files are part of package. [\#69](https://github.com/PASTA-ELN/pasta-eln/pull/69) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

**Improvements:**

- Project visibility issues. [\#35](https://github.com/PASTA-ELN/pasta-eln/issues/35)
- Importing sleepy brain data for the workshop. [\#31](https://github.com/PASTA-ELN/pasta-eln/issues/31)

**Bug fixes:**

- Issues when minimizing/maximizing individual items in projects. [\#56](https://github.com/PASTA-ELN/pasta-eln/issues/56)
- Ontology data modification via ontology-editor throw exceptions. [\#55](https://github.com/PASTA-ELN/pasta-eln/issues/55)
- Bug: delete file if there is no file. [\#61](https://github.com/PASTA-ELN/pasta-eln/pull/61) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Repair bugs in import of data from .eln file. [\#60](https://github.com/PASTA-ELN/pasta-eln/pull/60) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

**Maintenance:**

- Using recipes leads to strange response. [\#34](https://github.com/PASTA-ELN/pasta-eln/issues/34)

## [v2.4.13](https://github.com/PASTA-ELN/pasta-eln/tree/v2.4.13) (2023-09-26)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.4.12...v2.4.13)

**New features:**

- Add help button functionality to ontology editor tool. [\#47](https://github.com/PASTA-ELN/pasta-eln/issues/47)
- docs\(ontology\): add help button functionality to ontology editor tool.  [\#52](https://github.com/PASTA-ELN/pasta-eln/pull/52) ([jmurugan-fzj](https://github.com/jmurugan-fzj))

**Improvements:**

- Ontology editor GUI changes. [\#30](https://github.com/PASTA-ELN/pasta-eln/issues/30)

**Bug fixes:**

- Auto-scale the whole UI elements when resizing the ontology editor window. [\#48](https://github.com/PASTA-ELN/pasta-eln/issues/48)
- Save fails in ontology editor. [\#42](https://github.com/PASTA-ELN/pasta-eln/issues/42)
- fix\(ontology\): added missing initDocTypeViews invoke to save function. [\#54](https://github.com/PASTA-ELN/pasta-eln/pull/54) ([jmurugan-fzj](https://github.com/jmurugan-fzj))
- safeguard if data-label not present in default set of icons. [\#53](https://github.com/PASTA-ELN/pasta-eln/pull/53) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- fix\(ontology\): auto resizing the whole ontology editor window. [\#51](https://github.com/PASTA-ELN/pasta-eln/pull/51) ([jmurugan-fzj](https://github.com/jmurugan-fzj))
- fix\(ontology\): save fails in ontology editor. [\#50](https://github.com/PASTA-ELN/pasta-eln/pull/50) ([jmurugan-fzj](https://github.com/jmurugan-fzj))
- Issue 34 debug. [\#45](https://github.com/PASTA-ELN/pasta-eln/pull/45) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Addressed bugs reported in https://github.com/PASTA-ELN/pasta-eln/pul…. [\#44](https://github.com/PASTA-ELN/pasta-eln/pull/44) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

## [v2.4.12](https://github.com/PASTA-ELN/pasta-eln/tree/v2.4.12) (2023-09-18)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.4.11...v2.4.12)

**Improvements:**

- quickFix to solve HTs installation issue. [\#49](https://github.com/PASTA-ELN/pasta-eln/pull/49) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

## [v2.4.11](https://github.com/PASTA-ELN/pasta-eln/tree/v2.4.11) (2023-09-18)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.4.10...v2.4.11)

**New features:**

- Reformat gui.py to allow for easier reading. [\#29](https://github.com/PASTA-ELN/pasta-eln/pull/29) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

**Improvements:**

- Text visibility. [\#33](https://github.com/PASTA-ELN/pasta-eln/issues/33)
- feat\(ontology\): editor GUI changes and other modifications. [\#46](https://github.com/PASTA-ELN/pasta-eln/pull/46) ([jmurugan-fzj](https://github.com/jmurugan-fzj))
- change button text-color; tab in textEdit for form. [\#43](https://github.com/PASTA-ELN/pasta-eln/pull/43) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Content of form is autosaved in home folder. If computer is closed wi…. [\#22](https://github.com/PASTA-ELN/pasta-eln/pull/22) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

**Bug fixes:**

- Changing the pasta application for the new version of ontology data. [\#28](https://github.com/PASTA-ELN/pasta-eln/issues/28)
- Bug if meta not in extractor. [\#40](https://github.com/PASTA-ELN/pasta-eln/pull/40) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Implement new version 3 of the ontology into the backend. [\#39](https://github.com/PASTA-ELN/pasta-eln/pull/39) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))
- Fix installation bug. [\#26](https://github.com/PASTA-ELN/pasta-eln/pull/26) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

**Maintenance:**

- ci\(ontology\): added pytest and coverage calculation as a workflow. [\#27](https://github.com/PASTA-ELN/pasta-eln/pull/27) ([jmurugan-fzj](https://github.com/jmurugan-fzj))
- ci\(ontology\): update the myPy workflow yml file. [\#25](https://github.com/PASTA-ELN/pasta-eln/pull/25) ([jmurugan-fzj](https://github.com/jmurugan-fzj))
- feat\(ontology\): added tests for the ontology editor. [\#23](https://github.com/PASTA-ELN/pasta-eln/pull/23) ([jmurugan-fzj](https://github.com/jmurugan-fzj))
- feat\(ontology\): first draft version of ontology editor. [\#8](https://github.com/PASTA-ELN/pasta-eln/pull/8) ([jmurugan-fzj](https://github.com/jmurugan-fzj))

## [v2.4.10](https://github.com/PASTA-ELN/pasta-eln/tree/v2.4.10) (2023-08-31)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.4.9...v2.4.10)

## [v2.4.9](https://github.com/PASTA-ELN/pasta-eln/tree/v2.4.9) (2023-08-31)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.4.8...v2.4.9)

## [v2.4.8](https://github.com/PASTA-ELN/pasta-eln/tree/v2.4.8) (2023-08-31)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.4.7...v2.4.8)

**Improvements:**

- Develop buttons and actions that rely on lambda function. [\#6](https://github.com/PASTA-ELN/pasta-eln/pull/6) ([SteffenBrinckmann](https://github.com/SteffenBrinckmann))

**Documentation:**

- \(feat\): Cleaning documentations. [\#7](https://github.com/PASTA-ELN/pasta-eln/pull/7) ([jmurugan-fzj](https://github.com/jmurugan-fzj))

## [v2.4.7](https://github.com/PASTA-ELN/pasta-eln/tree/v2.4.7) (2023-07-31)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.4.6...v2.4.7)

## [v2.4.6](https://github.com/PASTA-ELN/pasta-eln/tree/v2.4.6) (2023-07-30)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.4.5...v2.4.6)

## [v2.4.5](https://github.com/PASTA-ELN/pasta-eln/tree/v2.4.5) (2023-07-16)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.4.4...v2.4.5)

## [v2.4.4](https://github.com/PASTA-ELN/pasta-eln/tree/v2.4.4) (2023-07-09)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.4.3...v2.4.4)

## [v2.4.3](https://github.com/PASTA-ELN/pasta-eln/tree/v2.4.3) (2023-07-04)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.4.2...v2.4.3)

## [v2.4.2](https://github.com/PASTA-ELN/pasta-eln/tree/v2.4.2) (2023-06-28)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.4.1...v2.4.2)

## [v2.4.1](https://github.com/PASTA-ELN/pasta-eln/tree/v2.4.1) (2023-06-27)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.4.0...v2.4.1)

## [v2.4.0](https://github.com/PASTA-ELN/pasta-eln/tree/v2.4.0) (2023-06-26)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.36...v2.4.0)

## [v2.3.36](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.36) (2023-06-24)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.34...v2.3.36)

## [v2.3.34](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.34) (2023-06-21)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.33...v2.3.34)

## [v2.3.33](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.33) (2023-06-19)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.32...v2.3.33)

## [v2.3.32](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.32) (2023-06-17)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.31...v2.3.32)

## [v2.3.31](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.31) (2023-06-15)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.30...v2.3.31)

## [v2.3.30](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.30) (2023-06-07)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.29...v2.3.30)

## [v2.3.29](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.29) (2023-06-06)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.28...v2.3.29)

## [v2.3.28](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.28) (2023-06-05)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.27...v2.3.28)

## [v2.3.27](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.27) (2023-06-05)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.26...v2.3.27)

## [v2.3.26](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.26) (2023-05-25)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.25...v2.3.26)

## [v2.3.25](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.25) (2023-05-24)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.24...v2.3.25)

## [v2.3.24](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.24) (2023-05-20)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.23...v2.3.24)

## [v2.3.23](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.23) (2023-05-16)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.22...v2.3.23)

## [v2.3.22](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.22) (2023-05-16)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.21...v2.3.22)

## [v2.3.21](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.21) (2023-05-15)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.20...v2.3.21)

## [v2.3.20](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.20) (2023-05-14)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.19...v2.3.20)

## [v2.3.19](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.19) (2023-05-14)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.18...v2.3.19)

## [v2.3.18](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.18) (2023-05-12)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.17...v2.3.18)

## [v2.3.17](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.17) (2023-04-27)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.16...v2.3.17)

## [v2.3.16](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.16) (2023-04-26)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.15...v2.3.16)

## [v2.3.15](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.15) (2023-04-14)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.14...v2.3.15)

## [v2.3.14](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.14) (2023-04-12)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.13...v2.3.14)

## [v2.3.13](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.13) (2023-04-12)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.12...v2.3.13)

## [v2.3.12](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.12) (2023-04-09)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.11...v2.3.12)

## [v2.3.11](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.11) (2023-04-05)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.10...v2.3.11)

## [v2.3.10](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.10) (2023-04-05)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.9...v2.3.10)

## [v2.3.9](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.9) (2023-04-05)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.8...v2.3.9)

## [v2.3.8](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.8) (2023-04-05)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.7...v2.3.8)

## [v2.3.7](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.7) (2023-04-04)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.6...v2.3.7)

## [v2.3.6](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.6) (2023-04-03)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.5...v2.3.6)

## [v2.3.5](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.5) (2023-03-31)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.4...v2.3.5)

## [v2.3.4](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.4) (2023-03-31)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.3...v2.3.4)

## [v2.3.3](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.3) (2023-03-30)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.2...v2.3.3)

## [v2.3.2](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.2) (2023-03-30)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.1...v2.3.2)

## [v2.3.1](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.1) (2023-03-29)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.3.0...v2.3.1)

## [v2.3.0](https://github.com/PASTA-ELN/pasta-eln/tree/v2.3.0) (2023-03-29)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.2.22...v2.3.0)

## [v2.2.22](https://github.com/PASTA-ELN/pasta-eln/tree/v2.2.22) (2023-03-23)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.2.21...v2.2.22)

**Improvements:**

- merge. [\#5](https://github.com/PASTA-ELN/pasta-eln/pull/5) ([RaphaelRoeske](https://github.com/RaphaelRoeske))
- pull. [\#4](https://github.com/PASTA-ELN/pasta-eln/pull/4) ([RaphaelRoeske](https://github.com/RaphaelRoeske))
- Update Branch.  [\#2](https://github.com/PASTA-ELN/pasta-eln/pull/2) ([RaphaelRoeske](https://github.com/RaphaelRoeske))
- Update Changes to Raphael Branch. [\#1](https://github.com/PASTA-ELN/pasta-eln/pull/1) ([RaphaelRoeske](https://github.com/RaphaelRoeske))

## [v2.2.21](https://github.com/PASTA-ELN/pasta-eln/tree/v2.2.21) (2023-02-16)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.2.20...v2.2.21)

## [v2.2.20](https://github.com/PASTA-ELN/pasta-eln/tree/v2.2.20) (2023-02-16)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.2.19...v2.2.20)

## [v2.2.19](https://github.com/PASTA-ELN/pasta-eln/tree/v2.2.19) (2023-02-16)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.2.18...v2.2.19)

## [v2.2.18](https://github.com/PASTA-ELN/pasta-eln/tree/v2.2.18) (2023-02-16)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.2.17...v2.2.18)

## [v2.2.17](https://github.com/PASTA-ELN/pasta-eln/tree/v2.2.17) (2023-02-16)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.2.16...v2.2.17)

## [v2.2.16](https://github.com/PASTA-ELN/pasta-eln/tree/v2.2.16) (2023-02-16)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.2.15...v2.2.16)

## [v2.2.15](https://github.com/PASTA-ELN/pasta-eln/tree/v2.2.15) (2023-02-07)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.2.14...v2.2.15)

## [v2.2.14](https://github.com/PASTA-ELN/pasta-eln/tree/v2.2.14) (2023-02-07)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.2.13...v2.2.14)

## [v2.2.13](https://github.com/PASTA-ELN/pasta-eln/tree/v2.2.13) (2023-02-07)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.2.12...v2.2.13)

## [v2.2.12](https://github.com/PASTA-ELN/pasta-eln/tree/v2.2.12) (2023-02-07)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.2.11...v2.2.12)

## [v2.2.11](https://github.com/PASTA-ELN/pasta-eln/tree/v2.2.11) (2023-02-07)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.2.10...v2.2.11)

## [v2.2.10](https://github.com/PASTA-ELN/pasta-eln/tree/v2.2.10) (2023-02-07)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.2.9...v2.2.10)

## [v2.2.9](https://github.com/PASTA-ELN/pasta-eln/tree/v2.2.9) (2023-02-07)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.2.8...v2.2.9)

## [v2.2.8](https://github.com/PASTA-ELN/pasta-eln/tree/v2.2.8) (2023-02-07)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.2.7...v2.2.8)

## [v2.2.7](https://github.com/PASTA-ELN/pasta-eln/tree/v2.2.7) (2023-01-31)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.2.6...v2.2.7)

## [v2.2.6](https://github.com/PASTA-ELN/pasta-eln/tree/v2.2.6) (2023-01-24)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.2.5...v2.2.6)

## [v2.2.5](https://github.com/PASTA-ELN/pasta-eln/tree/v2.2.5) (2023-01-24)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.2.4...v2.2.5)

## [v2.2.4](https://github.com/PASTA-ELN/pasta-eln/tree/v2.2.4) (2023-01-24)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.2.3...v2.2.4)

## [v2.2.3](https://github.com/PASTA-ELN/pasta-eln/tree/v2.2.3) (2023-01-24)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.2.2...v2.2.3)

## [v2.2.2](https://github.com/PASTA-ELN/pasta-eln/tree/v2.2.2) (2023-01-24)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.2.1...v2.2.2)

## [v2.2.1](https://github.com/PASTA-ELN/pasta-eln/tree/v2.2.1) (2023-01-17)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.2.0...v2.2.1)

## [v2.2.0](https://github.com/PASTA-ELN/pasta-eln/tree/v2.2.0) (2023-01-11)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.1.12...v2.2.0)

## [v2.1.12](https://github.com/PASTA-ELN/pasta-eln/tree/v2.1.12) (2023-01-09)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.1.11...v2.1.12)

## [v2.1.11](https://github.com/PASTA-ELN/pasta-eln/tree/v2.1.11) (2023-01-09)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.1.10...v2.1.11)

## [v2.1.10](https://github.com/PASTA-ELN/pasta-eln/tree/v2.1.10) (2023-01-08)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.1.9...v2.1.10)

## [v2.1.9](https://github.com/PASTA-ELN/pasta-eln/tree/v2.1.9) (2023-01-06)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.1.8...v2.1.9)

## [v2.1.8](https://github.com/PASTA-ELN/pasta-eln/tree/v2.1.8) (2023-01-05)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.1.7...v2.1.8)

## [v2.1.7](https://github.com/PASTA-ELN/pasta-eln/tree/v2.1.7) (2023-01-04)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.1.6...v2.1.7)

## [v2.1.6](https://github.com/PASTA-ELN/pasta-eln/tree/v2.1.6) (2023-01-04)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.1.5...v2.1.6)

## [v2.1.5](https://github.com/PASTA-ELN/pasta-eln/tree/v2.1.5) (2023-01-04)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.1.4...v2.1.5)

## [v2.1.4](https://github.com/PASTA-ELN/pasta-eln/tree/v2.1.4) (2023-01-03)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.1.3...v2.1.4)

## [v2.1.3](https://github.com/PASTA-ELN/pasta-eln/tree/v2.1.3) (2023-01-02)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.1.2...v2.1.3)

## [v2.1.2](https://github.com/PASTA-ELN/pasta-eln/tree/v2.1.2) (2022-12-29)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.1.1...v2.1.2)

## [v2.1.1](https://github.com/PASTA-ELN/pasta-eln/tree/v2.1.1) (2022-12-28)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.1.0...v2.1.1)

## [v2.1.0](https://github.com/PASTA-ELN/pasta-eln/tree/v2.1.0) (2022-12-27)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.0.29...v2.1.0)

## [v2.0.29](https://github.com/PASTA-ELN/pasta-eln/tree/v2.0.29) (2022-11-29)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.0.28...v2.0.29)

## [v2.0.28](https://github.com/PASTA-ELN/pasta-eln/tree/v2.0.28) (2022-11-29)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.0.27...v2.0.28)

## [v2.0.27](https://github.com/PASTA-ELN/pasta-eln/tree/v2.0.27) (2022-11-29)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.0.26...v2.0.27)

## [v2.0.26](https://github.com/PASTA-ELN/pasta-eln/tree/v2.0.26) (2022-11-29)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.0.25...v2.0.26)

## [v2.0.25](https://github.com/PASTA-ELN/pasta-eln/tree/v2.0.25) (2022-11-29)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.0.24...v2.0.25)

## [v2.0.24](https://github.com/PASTA-ELN/pasta-eln/tree/v2.0.24) (2022-11-29)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.0.23...v2.0.24)

## [v2.0.23](https://github.com/PASTA-ELN/pasta-eln/tree/v2.0.23) (2022-11-29)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.0.22...v2.0.23)

## [v2.0.22](https://github.com/PASTA-ELN/pasta-eln/tree/v2.0.22) (2022-11-29)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.0.21...v2.0.22)

## [v2.0.21](https://github.com/PASTA-ELN/pasta-eln/tree/v2.0.21) (2022-11-29)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.0.20...v2.0.21)

## [v2.0.20](https://github.com/PASTA-ELN/pasta-eln/tree/v2.0.20) (2022-11-29)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.0.19...v2.0.20)

## [v2.0.19](https://github.com/PASTA-ELN/pasta-eln/tree/v2.0.19) (2022-11-29)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.0.18...v2.0.19)

## [v2.0.18](https://github.com/PASTA-ELN/pasta-eln/tree/v2.0.18) (2022-11-29)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.0.17...v2.0.18)

## [v2.0.17](https://github.com/PASTA-ELN/pasta-eln/tree/v2.0.17) (2022-11-29)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.0.16...v2.0.17)

## [v2.0.16](https://github.com/PASTA-ELN/pasta-eln/tree/v2.0.16) (2022-11-29)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.0.15...v2.0.16)

## [v2.0.15](https://github.com/PASTA-ELN/pasta-eln/tree/v2.0.15) (2022-11-29)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.0.14...v2.0.15)

## [v2.0.14](https://github.com/PASTA-ELN/pasta-eln/tree/v2.0.14) (2022-11-29)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.0.13...v2.0.14)

## [v2.0.13](https://github.com/PASTA-ELN/pasta-eln/tree/v2.0.13) (2022-11-29)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.0.12...v2.0.13)

## [v2.0.12](https://github.com/PASTA-ELN/pasta-eln/tree/v2.0.12) (2022-11-29)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.0.11...v2.0.12)

## [v2.0.11](https://github.com/PASTA-ELN/pasta-eln/tree/v2.0.11) (2022-11-29)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.0.10...v2.0.11)

## [v2.0.10](https://github.com/PASTA-ELN/pasta-eln/tree/v2.0.10) (2022-11-29)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.0.9...v2.0.10)

## [v2.0.9](https://github.com/PASTA-ELN/pasta-eln/tree/v2.0.9) (2022-11-29)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.0.8...v2.0.9)

## [v2.0.8](https://github.com/PASTA-ELN/pasta-eln/tree/v2.0.8) (2022-11-29)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.0.7...v2.0.8)

## [v2.0.7](https://github.com/PASTA-ELN/pasta-eln/tree/v2.0.7) (2022-11-29)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.0.6...v2.0.7)

## [v2.0.6](https://github.com/PASTA-ELN/pasta-eln/tree/v2.0.6) (2022-11-29)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.0.5...v2.0.6)

## [v2.0.5](https://github.com/PASTA-ELN/pasta-eln/tree/v2.0.5) (2022-11-29)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.0.3...v2.0.5)

## [v2.0.3](https://github.com/PASTA-ELN/pasta-eln/tree/v2.0.3) (2022-11-29)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.0.4...v2.0.3)

## [v2.0.4](https://github.com/PASTA-ELN/pasta-eln/tree/v2.0.4) (2022-11-29)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.0.2...v2.0.4)

## [v2.0.2](https://github.com/PASTA-ELN/pasta-eln/tree/v2.0.2) (2022-11-28)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/v2.0.1...v2.0.2)

## [v2.0.1](https://github.com/PASTA-ELN/pasta-eln/tree/v2.0.1) (2022-11-28)
[Full Changelog](https://github.com/PASTA-ELN/pasta-eln/compare/16b677de6e458ca47c90c50e5e79356847c9c32e...v2.0.1)
\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
