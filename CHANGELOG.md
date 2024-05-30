# Changelog

## [0.8.2](https://github.com/chssn/eaip-parser/compare/v0.8.1...v0.8.2) (2024-05-30)


### Bug Fixes

* geo bounds too narrow ([48f92ba](https://github.com/chssn/eaip-parser/commit/48f92bacdaf2d55baab130add2d4fa5adecaff85))
* index out of bounds ([0d621d2](https://github.com/chssn/eaip-parser/commit/0d621d2ac2b25cd13babd4b490dabe55d4ceead6))
* value error on legitimate action ([78154bb](https://github.com/chssn/eaip-parser/commit/78154bb59b620099c02de426bbfa67712130b657))
* warning about non-25kHz frequencies ([2e117e7](https://github.com/chssn/eaip-parser/commit/2e117e7beb8f905219492f18d6b192554a6f2add))

# CHANGELOG




## v0.8.1 (2023-08-05)

### Documentation

* docs: updated logging messages ([`94f7c0a`](https://github.com/chssn/eaip-parser/commit/94f7c0aaf537e70ccc55a81082624683aa6c2085))

* docs: clarified use of search string ([`996d30b`](https://github.com/chssn/eaip-parser/commit/996d30bd336690746401a80994577aaec298b3d6))

### Fix

* fix: not handling rougue tripple digit rwy ([`96fc797`](https://github.com/chssn/eaip-parser/commit/96fc7976ed0a4b7060a8c2205b374f18db63b980))

* fix: not handling out of bounds rwy numbers ([`fdf2f6b`](https://github.com/chssn/eaip-parser/commit/fdf2f6bd6c872fa6934a51e569b51bb6f74d920f))

* fix: returning &#39;True&#39; result in error ([`1d7b2ce`](https://github.com/chssn/eaip-parser/commit/1d7b2cefdec2f10271a0219fe31ab8f6601f0cd5))

* fix: function modified to return a dict ([`20035fe`](https://github.com/chssn/eaip-parser/commit/20035fe6d681600a507f7a46c4ed51aa6d946109))

### Performance

* perf: un-neccessary elif ([`2b64fcf`](https://github.com/chssn/eaip-parser/commit/2b64fcffbe2f21d98f7e471fc01e07de61e0e961))

### Test

* test: updated with new functions ([`475c97f`](https://github.com/chssn/eaip-parser/commit/475c97f8f000254ab1a6fafb0afcef8d143ff149))

* test: updated to test the returned dict ([`7d74f4e`](https://github.com/chssn/eaip-parser/commit/7d74f4e18f3ce9652c6b5a18cf5b75e29fa869a0))

## v0.8.0 (2023-08-04)

### Feature

* feat: added &#39;Airports&#39; builder ([`058156f`](https://github.com/chssn/eaip-parser/commit/058156f7ece8bc6a0ac0700a03703c0134065937))

### Fix

* fix: updated regex class ([`ef94ade`](https://github.com/chssn/eaip-parser/commit/ef94adec4196528ea9b740a35e5b3209e8161c25))

* fix: basic check that returned coords are in UK ([`b071ca1`](https://github.com/chssn/eaip-parser/commit/b071ca17b5f77e3e53afd4aac8e9e7b2a936aba2))

* fix: &#39;str&#39; object does not support item deletion ([`e84bb57`](https://github.com/chssn/eaip-parser/commit/e84bb57b2721e4bd4a6a9296047e059c0720e78b))

* fix: TypeError: &#39;NoneType&#39; object is not iterable ([`9f4ffc9`](https://github.com/chssn/eaip-parser/commit/9f4ffc90a235199c7f58f548f19a15d620141eab))

### Style

* style: unecessary parens ([`018ecc3`](https://github.com/chssn/eaip-parser/commit/018ecc3e714d01594738f69ba6dd26db2ce2f0b5))

* style: trailing whitespace ([`5b35338`](https://github.com/chssn/eaip-parser/commit/5b353386ed48f4e2584f586ac2c56f5642f6d39c))

### Unknown

* Merge branch &#39;main&#39; of https://github.com/chssn/eaip-parser ([`afe99dd`](https://github.com/chssn/eaip-parser/commit/afe99dd494d01d04139345ab9f139c0265f47442))

## v0.7.0 (2023-08-03)

### Ci

* ci: more attempts to get __init__ to update ([`0352955`](https://github.com/chssn/eaip-parser/commit/0352955122a23d1a967a71a55897efb6b1c41c96))

### Feature

* feat: scrape AD 2 data to df ([`e09173d`](https://github.com/chssn/eaip-parser/commit/e09173d76c67526f61cf08d8ec845ddb79fe1ad6))

* feat: added full scrape of AD 2 ([`ce853b5`](https://github.com/chssn/eaip-parser/commit/ce853b5e0b8bdcad7ff52b164900c7f640f36c72))

### Fix

* fix: better handling of http errors ([`54b5758`](https://github.com/chssn/eaip-parser/commit/54b5758e1807cfbf93352a1c8d96363e310f229d))

### Refactor

* refactor: pytest failing ([`1185384`](https://github.com/chssn/eaip-parser/commit/1185384b860b12a3fd63a203cb1c677b0f787ae2))

* refactor: moved file name function ([`eb744b6`](https://github.com/chssn/eaip-parser/commit/eb744b65305a5559791166c2ba57a7fc5d141173))

### Test

* test: updated tests to reflect new function home ([`17daaf6`](https://github.com/chssn/eaip-parser/commit/17daaf6bdc44f4661219f0a99fb8c6e57a08bdb7))

* test: updated to reflect change in run function ([`28e1a69`](https://github.com/chssn/eaip-parser/commit/28e1a69ec59e55440ca590e5b121ae1167529afc))

## v0.6.0 (2023-08-02)

### Ci

* ci: manual version bump ([`b500513`](https://github.com/chssn/eaip-parser/commit/b5005134b30f9d409aa7e4a71f4d5870dc81782c))

### Documentation

* docs: added extra debug messages ([`363f6de`](https://github.com/chssn/eaip-parser/commit/363f6defd917c1df1fd84db5f3296cb351e03206))

* docs: corrected typo ([`a9ec9f5`](https://github.com/chssn/eaip-parser/commit/a9ec9f59fe96fe02a41776f7b4e275380e367763))

### Feature

* feat: added enr 4 validation ([`6ed5a6e`](https://github.com/chssn/eaip-parser/commit/6ed5a6e74a8281f3566fee06a21b20c1c4011770))

* feat: added enr 5 data ([`f1f2c0b`](https://github.com/chssn/eaip-parser/commit/f1f2c0b91e73d5f0a989531c7e76fbcaab6c99eb))

### Fix

* fix: bonus space being added to a load of lines ([`d601f24`](https://github.com/chssn/eaip-parser/commit/d601f24c961ae9d84c90f0ccba6feb5328888820))

* fix: no rate limiter for coordinate conversion ([`50a8124`](https://github.com/chssn/eaip-parser/commit/50a8124dc3477ff4218de46da0a68604bc7eb9d2))

### Refactor

* refactor: changed validate.py to compare.py ([`f9e9c15`](https://github.com/chssn/eaip-parser/commit/f9e9c157ca2407bd565a3c26a6742436809c0c75))

### Test

* test: updated test_run with new functions ([`c450fe4`](https://github.com/chssn/eaip-parser/commit/c450fe40653e3d6fdf92b8dbf1d62e5cd6bca58c))

### Unknown

* Merge branch &#39;main&#39; of https://github.com/chssn/eaip-parser ([`39ffa9c`](https://github.com/chssn/eaip-parser/commit/39ffa9c065de02097bb2b1c04071cd02cdf174a8))

## v0.5.1 (2023-08-02)

### Fix

* fix: version number not being updated ([`6e98a3a`](https://github.com/chssn/eaip-parser/commit/6e98a3aa09f341e204d04999a22d1d13d23680d2))

### Unknown

* Merge branch &#39;main&#39; of https://github.com/chssn/eaip-parser ([`7ddf393`](https://github.com/chssn/eaip-parser/commit/7ddf3932af764dec481e3607e75530d7f062c315))

## v0.5.0 (2023-08-02)

### Documentation

* docs: clearer debugging ([`aa782c7`](https://github.com/chssn/eaip-parser/commit/aa782c774dea09b0d74fca3b2c48b429842c4695))

* docs: corrected typos ([`1f57442`](https://github.com/chssn/eaip-parser/commit/1f57442344c259a325fb604a502e20f8630e946e))

### Feature

* feat: option to start fresh again ([`d8cf49a`](https://github.com/chssn/eaip-parser/commit/d8cf49a16052bebcc3972526956e815a57de6d6b))

* feat: validate will now start to move data around ([`7630112`](https://github.com/chssn/eaip-parser/commit/7630112595d6dd68b33b1eb3124ce623ef37ee6c))

### Fix

* fix: copying files with a length of 0 bytes ([`589d26d`](https://github.com/chssn/eaip-parser/commit/589d26d9b405223861aca760144f83d1959e3ec1))

* fix: failing on first http error ([`2097d67`](https://github.com/chssn/eaip-parser/commit/2097d678b1b5d487b14b115aa27cac59466b36dc))

* fix: not deleting non-empty directories ([`835c9a0`](https://github.com/chssn/eaip-parser/commit/835c9a0b14ce15dde1967b42b72fe827acdfa144))

* fix: not splitting routes correctly ([`7f160ad`](https://github.com/chssn/eaip-parser/commit/7f160ad4f1e2a5b5ad16a63c1113be90e902d9dd))

* fix: entering a None line after a non-contiuation ([`4d75be3`](https://github.com/chssn/eaip-parser/commit/4d75be347cb89c82c7fbef81c8d535158ee9a173))

* fix: not handling an empty list correctly ([`7b764b5`](https://github.com/chssn/eaip-parser/commit/7b764b579c05a595257f8984f988e442bd44e29e))

* fix: added validation to url_suffix ([`35fa287`](https://github.com/chssn/eaip-parser/commit/35fa287af1459e8ee05eb80dbb3895235237dc64))

### Test

* test: updated tests with new function changes ([`d68c548`](https://github.com/chssn/eaip-parser/commit/d68c5488fd4eb2e4e3a40a6e77eee477e44e5080))

* test: updates to webscrape tests ([`0da7b42`](https://github.com/chssn/eaip-parser/commit/0da7b423655f9380637d9e2ecf96a38c1870e80d))

* test: updated url_suffix test ([`e6ca0bf`](https://github.com/chssn/eaip-parser/commit/e6ca0bfb15be00a8803e8fa6b952727721e3fe93))

## v0.4.1 (2023-08-01)

### Build

* build: updated requirements ([`5dd2bb2`](https://github.com/chssn/eaip-parser/commit/5dd2bb2e8ddb0f9bed564e560931aad87297ed57))

### Chore

* chore: re-order commands ([`cae71cb`](https://github.com/chssn/eaip-parser/commit/cae71cbeca17dc7f14e9a081062f05bddbe4c1d9))

* chore: Update main.yml ([`0fb8f2b`](https://github.com/chssn/eaip-parser/commit/0fb8f2bb3dae87cca9fb4e0ab3a274543f1f2535))

* chore: added semantic release workflow ([`9fb0d5f`](https://github.com/chssn/eaip-parser/commit/9fb0d5f35a05048911650730260790692fcb44cd))

### Ci

* ci: added pylint and pytest ([`e543ac8`](https://github.com/chssn/eaip-parser/commit/e543ac81d71257423b9938029abb4f4b235b7481))

* ci: updates to workflow ([`fc0a787`](https://github.com/chssn/eaip-parser/commit/fc0a787717c755a791ff34d4ee8d8d09956abdc4))

* ci: semantic release config update ([`18e70b3`](https://github.com/chssn/eaip-parser/commit/18e70b3e67de4859112c38d20fd06e86b858d57b))

### Fix

* fix: deleted errored call ([`a7657d6`](https://github.com/chssn/eaip-parser/commit/a7657d630c56c05391b605ae1418fb3111c5f5c6))

### Refactor

* refactor: extensive lint ([`66d836b`](https://github.com/chssn/eaip-parser/commit/66d836b25959b24e081b9477dce4cd2926c594a7))

### Test

* test: rewrote enr4 test ([`9ca09cc`](https://github.com/chssn/eaip-parser/commit/9ca09ccd05578dcb304189833e640bd55c74189b))

* test: remove test files ([`f6537e9`](https://github.com/chssn/eaip-parser/commit/f6537e9d62b35c45bceb90b62ef5610ef94a752c))

* test: include the working directory this time ([`dafddc4`](https://github.com/chssn/eaip-parser/commit/dafddc4adef3fe51fa25998eeb0b6facdcde128a))

* test: update to be platform agnostic ([`5fcf8ba`](https://github.com/chssn/eaip-parser/commit/5fcf8ba0edff43f7206debe644e5e687ee60903f))

* test: updated test followin lint ([`0c46803`](https://github.com/chssn/eaip-parser/commit/0c4680323585a5c2cbc44f28a0a07c39c4eab1d2))

## v0.4.0 (2023-07-31)

### Documentation

* docs: corrected wording ([`d57535e`](https://github.com/chssn/eaip-parser/commit/d57535e88154ee756b97b339b1b88a1f0ef4912e))

* docs: updated commenting ([`333c338`](https://github.com/chssn/eaip-parser/commit/333c338540a9b895c248f0136d1caa300ebb48a7))

### Feature

* feat: processing enr4.4 ([`1410e25`](https://github.com/chssn/eaip-parser/commit/1410e25ea269ffe8ce35e2aec685fdf2344ab3c3))

### Fix

* fix: not identifying non-continuous sections ([`9d88e33`](https://github.com/chssn/eaip-parser/commit/9d88e3343c8ef2596fe3d8d40bbdd0cba4bfb24e))

* fix: added better error checking ([`7ffb23c`](https://github.com/chssn/eaip-parser/commit/7ffb23c9eac175f009ca8f93ba78df6459d79120))

* fix: file not found ([`102be50`](https://github.com/chssn/eaip-parser/commit/102be508ddce377098949f49f821649cee000d24))

* fix: file path not formatted correctly ([`851dfd5`](https://github.com/chssn/eaip-parser/commit/851dfd5eb425874ff481c7695fa1e81674b04237))

* fix: only returning dme points ([`e2d076a`](https://github.com/chssn/eaip-parser/commit/e2d076aa7c12b6d57037a3d47a85484f5ef1f222))

* fix: moved common regex strings ([`a8855f8`](https://github.com/chssn/eaip-parser/commit/a8855f82e82902ab3a10cd089f0e3bbe9d209fbd))

* fix: frequency not formatting correctly ([`f4c6735`](https://github.com/chssn/eaip-parser/commit/f4c67355415bd6f0cbd650c0be0a144b36479c85))

* fix: var ref before assigned ([`03e19a7`](https://github.com/chssn/eaip-parser/commit/03e19a7de44e5b3274c302dcb3e58515eff69dbb))

* fix: adding non-continuous stmnt to first line ([`a677830`](https://github.com/chssn/eaip-parser/commit/a6778303866cf359b62f342b80a434686386efa6))

* fix: not working correctly with non-cont airways ([`d7fbf55`](https://github.com/chssn/eaip-parser/commit/d7fbf55bc2af65332816e50713f03c7fab861397))

* fix: reduced module verbosity ([`4030050`](https://github.com/chssn/eaip-parser/commit/40300504d57494fa27e82ba07a865767e0b32ab9))

### Performance

* perf: removed redundant function ([`31739dd`](https://github.com/chssn/eaip-parser/commit/31739ddc465f4198bbe23a1950b07eb1cb22d5ea))

### Refactor

* refactor: re-ordered functions ([`ebf5323`](https://github.com/chssn/eaip-parser/commit/ebf53234e8308399fa778a9f8aa695e06057e053))

### Test

* test: updated test data ([`f0cb645`](https://github.com/chssn/eaip-parser/commit/f0cb64559ab77a9c6049ea4fbe1bd54ac351d9e4))

* test: updated test data ([`f358b41`](https://github.com/chssn/eaip-parser/commit/f358b41c36c318d1b2934f6b7e7494fe0c68a86e))

* test: added more test data ([`4bd3175`](https://github.com/chssn/eaip-parser/commit/4bd31755b4ad8306bd3bd0ab2b3b1a292e25d416))

* test: added additional test data ([`06273c5`](https://github.com/chssn/eaip-parser/commit/06273c5c33835f34c804c2fe3aad6e35003e090e))

### Unknown

* Merge pull request #3 from chssn/webscrape-to-panads

Webscrape to panads ([`4ec8fed`](https://github.com/chssn/eaip-parser/commit/4ec8fed1422330682fb1ed25c395bcedb9355108))

* Merge pull request #2 from chssn/main

update webscrape-to-pandas ([`5446337`](https://github.com/chssn/eaip-parser/commit/544633760cadcf8e995990dca1901203d188d655))

## v0.3.0 (2023-07-30)

### Chore

* chore: various build bits ([`ace66cd`](https://github.com/chssn/eaip-parser/commit/ace66cd1d0d090ee1e190ef25bdd94c3fbb1e3b5))

### Feature

* feat: added ENR4.1 checks ([`312d81a`](https://github.com/chssn/eaip-parser/commit/312d81a51d22ec88de8ad839daef57acae2db8d1))

* feat: added TACAN to VOR/ILS frequency conversion ([`b7d1151`](https://github.com/chssn/eaip-parser/commit/b7d1151d7d434928ccec529bf6b606c9a80afc13))

* feat: added upper airway validation ([`3703596`](https://github.com/chssn/eaip-parser/commit/37035969d61e518d14796c6689e71085f1ed9233))

* feat: initial data validation for airways ([`5e7bc7b`](https://github.com/chssn/eaip-parser/commit/5e7bc7b2261d3849d4bc570b179271e0c19ff653))

* feat: added git functions ([`80f6610`](https://github.com/chssn/eaip-parser/commit/80f66105e32cb66076ac7176f0ec189daa6dddc5))

* feat: process enr3.2 and enr3.3 ([`26c35c3`](https://github.com/chssn/eaip-parser/commit/26c35c3e85bfc11e9fd2fa5544cf4709f07ccb77))

* feat: process enr3.2 and enr3.3 ([`866397d`](https://github.com/chssn/eaip-parser/commit/866397dc3e245924767880a296ea5536a2cbd468))

* feat: parse enr2.1 and enr2.2 ([`98e0f75`](https://github.com/chssn/eaip-parser/commit/98e0f75ec821f76ba0b504f48f34b03c2a0c34f1))

### Fix

* fix: typo ([`52713ae`](https://github.com/chssn/eaip-parser/commit/52713aec2475b50210dffa07324757ed19c243c8))

* fix: ENR 4 processing not happening ([`f28d2b8`](https://github.com/chssn/eaip-parser/commit/f28d2b881424fb1bbc1f4bfd57ddcb11e22796c7))

* fix: vor dme validator not running from main ([`b2052e1`](https://github.com/chssn/eaip-parser/commit/b2052e19f41afda5234a290f379ddfcb5451bbc6))

* fix: incorrect class parathensis ([`7585295`](https://github.com/chssn/eaip-parser/commit/7585295187ec6112ac28d6b70836b764698b2eca))

* fix: validator not running at module level ([`6bb1445`](https://github.com/chssn/eaip-parser/commit/6bb1445bc483dbd986db1152a894e466d0825c35))

* fix: redefined upper airway split fl ([`a7491ed`](https://github.com/chssn/eaip-parser/commit/a7491ed2c0afabd913f22b68d625e9a5616134ef))

* fix: not getting all points correctly ([`b7d6d36`](https://github.com/chssn/eaip-parser/commit/b7d6d36ab78a9a2eb652ceaa3c1a6c3ad1354205))

* fix: corrected airway formatting ([`6b23104`](https://github.com/chssn/eaip-parser/commit/6b231045b15c27ed3e2099748975572200ebd689))

* fix: corrected error and logging handling ([`00393fc`](https://github.com/chssn/eaip-parser/commit/00393fc2ec934da7653ccfd8371e71287328f2cf))

* fix: general updates to prep for enr3.2 ([`ce33a0c`](https://github.com/chssn/eaip-parser/commit/ce33a0c2da8455a26e43bb2f00479b0663baf8c7))

* fix: not parsing CTR correctly ([`e31c884`](https://github.com/chssn/eaip-parser/commit/e31c884c05dfc1cd34fd850f96ba78925799b0ae))

### Performance

* perf: removed redundant code ([`520fc68`](https://github.com/chssn/eaip-parser/commit/520fc68650f6e1414dd5a7bff7d69ebb34456cf0))

* perf: removed redundant error check ([`bed28aa`](https://github.com/chssn/eaip-parser/commit/bed28aa5d9fbbe0d6e66596fc2f94b3517c3d3cf))

* perf: removed unused functions ([`d61a48e`](https://github.com/chssn/eaip-parser/commit/d61a48e8eba22b4dda1ab2c27355ecc9cb9f5d19))

### Style

* style: cleaned up comments and applied encoding ([`8ff9b94`](https://github.com/chssn/eaip-parser/commit/8ff9b944e05c5908a162b35095a573f6331365c2))

* style: referenced index to satisfy pep8 ([`9541db2`](https://github.com/chssn/eaip-parser/commit/9541db28bf586d67389d5b05c4d49f9f29d38b29))

* style: minor pep8 change ([`83c6d6e`](https://github.com/chssn/eaip-parser/commit/83c6d6e91f7578e0a14f0ff60e996f14cdec040f))

* style: minor pep8 changes ([`cdc433a`](https://github.com/chssn/eaip-parser/commit/cdc433a2921215db8acf428e183eb74d0ad710a8))

* style: line too long ([`bdb8301`](https://github.com/chssn/eaip-parser/commit/bdb8301ebfe10e9b65fad37c80636556d5242dde))

### Test

* test: removed problematic test ([`bda950d`](https://github.com/chssn/eaip-parser/commit/bda950d3e82824b495f3b98bd38c719cdd443e20))

* test: added ENR4.1 test data ([`76b6397`](https://github.com/chssn/eaip-parser/commit/76b63976e078698e359c668fc6f288b7ee53c8ec))

* test: added basic tacan tests ([`bccf4bf`](https://github.com/chssn/eaip-parser/commit/bccf4bff6f2a2871b19b4c2d8f5b6fd0f71cf236))

* test: new webscrape tests ([`56e8fb1`](https://github.com/chssn/eaip-parser/commit/56e8fb1514cad4464975c520a657ff52fa63a8cb))

* test: updated functions test to 99% coverage ([`6060f7a`](https://github.com/chssn/eaip-parser/commit/6060f7af041924bdfc27709622bfb02755a14b36))

* test: corrected enr 3 testing ([`5625170`](https://github.com/chssn/eaip-parser/commit/56251704ecb3731bcbe4ca17d225654bcf05c23a))

* test: added test data for webscrape ([`d8dffad`](https://github.com/chssn/eaip-parser/commit/d8dffad28771c500165d6ebf1d1b5614d4ef4807))

* test: don&#39;t look in these directories for tests ([`a2dce95`](https://github.com/chssn/eaip-parser/commit/a2dce958ab02f6cbcd7219e8bc10cf6fbfd5b653))

* test: added tests for builder module ([`9858aff`](https://github.com/chssn/eaip-parser/commit/9858affb97e3a63806c54d921420b85068398a8c))

* test: new pytest and assoc data ([`e63df7d`](https://github.com/chssn/eaip-parser/commit/e63df7df014e1faf13c89b0f9e736877219d1070))

* test: cleanup unused data ([`dafd1a9`](https://github.com/chssn/eaip-parser/commit/dafd1a9aa4661592bcd39b8a452ed191477cdb55))

### Unknown

* Merge pull request #1 from chssn/webscrape-to-panads

Webscrape to panads ([`20daa91`](https://github.com/chssn/eaip-parser/commit/20daa9102ab063cef9c5e255b07fae02622be992))

* pref: removed duplicate statement ([`59f03e8`](https://github.com/chssn/eaip-parser/commit/59f03e829c3eec0d20ffa58577e654911ff0ffcf))

## v0.2.0 (2023-07-27)

### Chore

* chore: added Debug folder to gitignore ([`15f3f80`](https://github.com/chssn/eaip-parser/commit/15f3f80dd530aa7de5d84246b71ee8486ef4faca))

### Feature

* feat: started rebuild of webscrape ([`62a64da`](https://github.com/chssn/eaip-parser/commit/62a64da980e943598106c78f269434dec256b04f))

* feat: function to check if freq is 25KHz compliant ([`4be7e83`](https://github.com/chssn/eaip-parser/commit/4be7e838c0ec77c65c5f1cbfe61604473d880d2d))

## v0.1.2 (2023-07-26)

### Chore

* chore: added comments ([`46bd2ad`](https://github.com/chssn/eaip-parser/commit/46bd2adf67446860db5134eb58d57dc6cf261262))

### Fix

* fix: removed some print statements ([`f4d2f97`](https://github.com/chssn/eaip-parser/commit/f4d2f97dc225e5013bde584355da599e3e8a6e04))

* fix: passing full match instead of part thereof ([`1e14456`](https://github.com/chssn/eaip-parser/commit/1e1445618a0e8069f36b24cf5bef0b8a6402aea9))

* fix: dms2dd function not accepting DDMMSS input ([`a09916a`](https://github.com/chssn/eaip-parser/commit/a09916a16f9633a4b626ed6dae8eef8c62caf67b))

### Test

* test: updated for change in dms2dd function ([`ad73ac7`](https://github.com/chssn/eaip-parser/commit/ad73ac7dc3ba5ec920823e1b87c4b2ae6aad819a))

## v0.1.1 (2023-07-25)

### Fix

* fix: incorrect escaping of regex ([`65255e7`](https://github.com/chssn/eaip-parser/commit/65255e7a2202901d8a744ab2f27cb552d459e21f))

### Performance

* perf: removed unused library ([`7a47436`](https://github.com/chssn/eaip-parser/commit/7a474369ad25c16ff0e4204b0cbcae5727917017))

### Style

* style: pep8 conformity changes ([`0754e13`](https://github.com/chssn/eaip-parser/commit/0754e1326f8238b728e679f1a2f7ef8147b89722))

## v0.1.0 (2023-07-25)

### Chore

* chore: added versioning ([`6065e79`](https://github.com/chssn/eaip-parser/commit/6065e79df081b7d470ff1f101337ec65e726ffb1))

* chore: module rename ([`6d7e79d`](https://github.com/chssn/eaip-parser/commit/6d7e79d429aa7916a511eb1bb7886ad06580e002))

* chore: updated comments ([`0129699`](https://github.com/chssn/eaip-parser/commit/0129699811d6527d6ae6e1429f20071fb11f43ec))

### Feature

* feat: parses all point lat lon data ([`a30f0da`](https://github.com/chssn/eaip-parser/commit/a30f0dab6104f7bc19a97b27818bec3e140d9558))

### Fix

* fix: move and cleanup functions ([`4374e24`](https://github.com/chssn/eaip-parser/commit/4374e24650b531bac8ccffd2f64a905f243440b7))

* fix: incorrect debug message ([`118dd35`](https://github.com/chssn/eaip-parser/commit/118dd35f561bece6273abea848ee8129325b47fe))

* fix: not finding runways ([`512985a`](https://github.com/chssn/eaip-parser/commit/512985a36bacddacc7073ba3fd2f2d188ea36a59))

* fix: update regex for aerodrome search ([`aeb7285`](https://github.com/chssn/eaip-parser/commit/aeb728524d00a6a0ec7299767cff7b09cb5a945e))

* fix: allow date entry in Webscrape class ([`f2584b2`](https://github.com/chssn/eaip-parser/commit/f2584b2e7030a03181f6b011f2562050d4d48965))

* fix: set default to scrape the next airac data ([`ff2c671`](https://github.com/chssn/eaip-parser/commit/ff2c671aaa34c7ebea03ce9aeeb035bbb5160498))

* fix: unable to set custom date ([`d0de2f5`](https://github.com/chssn/eaip-parser/commit/d0de2f50e0692e9861ced7847e2cb3ab3272808b))

* fix: improved error checking ([`2c74fa0`](https://github.com/chssn/eaip-parser/commit/2c74fa032fdd7a46c58cb22c316ab120439bef1f))

* fix: var ref before defined ([`079cd8a`](https://github.com/chssn/eaip-parser/commit/079cd8a12355854c1fdb28b029fd88351a966bcd))

### Performance

* perf: cleaned up code ([`ff2e1c6`](https://github.com/chssn/eaip-parser/commit/ff2e1c69d81402e27451ec535e1aa2f5f0ca7b3a))

* perf: remove redundant try except statement ([`54a60e9`](https://github.com/chssn/eaip-parser/commit/54a60e9d3be6340cc909c3811c2a952b5c0380db))

* perf: added timeout to get request ([`8f89f36`](https://github.com/chssn/eaip-parser/commit/8f89f36c513e9d4d3d7472463b8ab5066cc0075a))

### Style

* style: removed trailing white space ([`e5b2ab1`](https://github.com/chssn/eaip-parser/commit/e5b2ab19b064f1e8349ba0e6deca87f1ef9e8953))

### Unknown

* tests: add test data ([`fc77c44`](https://github.com/chssn/eaip-parser/commit/fc77c44b5d9401afd994e452276b8526ad8aa518))

* tests: added tests for airac and functions ([`b0669ed`](https://github.com/chssn/eaip-parser/commit/b0669edd76229eb29ee315f983e1a12966f69c38))

* tests: updated pytest for airac and functions ([`faa6bc5`](https://github.com/chssn/eaip-parser/commit/faa6bc5f21394b01afccd81430f9419c1db7d2b1))

* tests: copied airac test over ([`30ebd21`](https://github.com/chssn/eaip-parser/commit/30ebd2132de5bb3d462afbbef0fc188bf3634379))

* added requirements.txt ([`5e56c60`](https://github.com/chssn/eaip-parser/commit/5e56c603cdee930f7ca2866158dc82a9c3505784))

* un f ([`82afba9`](https://github.com/chssn/eaip-parser/commit/82afba91f995c7c99b0ae7ebc79874fe074a3528))

* no df ([`2f58577`](https://github.com/chssn/eaip-parser/commit/2f58577d10fc5e87fef4bf06a5ddbe2372582f05))

* Update .gitignore ([`b715713`](https://github.com/chssn/eaip-parser/commit/b715713330ce647b5dc17c8db49983f093cb20b1))

* Initial commit ([`8d90bcc`](https://github.com/chssn/eaip-parser/commit/8d90bcc3bb699c35206afd8b22158127e3483712))
