<!--next-version-placeholder-->

## v0.4.0 (2023-07-31)
### Feature
* Processing enr4.4 ([`1410e25`](https://github.com/chssn/eaip-parser/commit/1410e25ea269ffe8ce35e2aec685fdf2344ab3c3))

### Fix
* Not identifying non-continuous sections ([`9d88e33`](https://github.com/chssn/eaip-parser/commit/9d88e3343c8ef2596fe3d8d40bbdd0cba4bfb24e))
* Added better error checking ([`7ffb23c`](https://github.com/chssn/eaip-parser/commit/7ffb23c9eac175f009ca8f93ba78df6459d79120))
* File not found ([`102be50`](https://github.com/chssn/eaip-parser/commit/102be508ddce377098949f49f821649cee000d24))
* File path not formatted correctly ([`851dfd5`](https://github.com/chssn/eaip-parser/commit/851dfd5eb425874ff481c7695fa1e81674b04237))
* Only returning dme points ([`e2d076a`](https://github.com/chssn/eaip-parser/commit/e2d076aa7c12b6d57037a3d47a85484f5ef1f222))
* Moved common regex strings ([`a8855f8`](https://github.com/chssn/eaip-parser/commit/a8855f82e82902ab3a10cd089f0e3bbe9d209fbd))
* Frequency not formatting correctly ([`f4c6735`](https://github.com/chssn/eaip-parser/commit/f4c67355415bd6f0cbd650c0be0a144b36479c85))
* Var ref before assigned ([`03e19a7`](https://github.com/chssn/eaip-parser/commit/03e19a7de44e5b3274c302dcb3e58515eff69dbb))
* Adding non-continuous stmnt to first line ([`a677830`](https://github.com/chssn/eaip-parser/commit/a6778303866cf359b62f342b80a434686386efa6))
* Not working correctly with non-cont airways ([`d7fbf55`](https://github.com/chssn/eaip-parser/commit/d7fbf55bc2af65332816e50713f03c7fab861397))
* Reduced module verbosity ([`4030050`](https://github.com/chssn/eaip-parser/commit/40300504d57494fa27e82ba07a865767e0b32ab9))

### Documentation
* Corrected wording ([`d57535e`](https://github.com/chssn/eaip-parser/commit/d57535e88154ee756b97b339b1b88a1f0ef4912e))
* Updated commenting ([`333c338`](https://github.com/chssn/eaip-parser/commit/333c338540a9b895c248f0136d1caa300ebb48a7))

### Performance
* Removed redundant function ([`31739dd`](https://github.com/chssn/eaip-parser/commit/31739ddc465f4198bbe23a1950b07eb1cb22d5ea))

## v0.3.0 (2023-07-30)
### Feature
* Added ENR4.1 checks ([`312d81a`](https://github.com/chssn/eaip-parser/commit/312d81a51d22ec88de8ad839daef57acae2db8d1))
* Added TACAN to VOR/ILS frequency conversion ([`b7d1151`](https://github.com/chssn/eaip-parser/commit/b7d1151d7d434928ccec529bf6b606c9a80afc13))
* Added upper airway validation ([`3703596`](https://github.com/chssn/eaip-parser/commit/37035969d61e518d14796c6689e71085f1ed9233))
* Initial data validation for airways ([`5e7bc7b`](https://github.com/chssn/eaip-parser/commit/5e7bc7b2261d3849d4bc570b179271e0c19ff653))
* Added git functions ([`80f6610`](https://github.com/chssn/eaip-parser/commit/80f66105e32cb66076ac7176f0ec189daa6dddc5))
* Process enr3.2 and enr3.3 ([`26c35c3`](https://github.com/chssn/eaip-parser/commit/26c35c3e85bfc11e9fd2fa5544cf4709f07ccb77))
* Process enr3.2 and enr3.3 ([`866397d`](https://github.com/chssn/eaip-parser/commit/866397dc3e245924767880a296ea5536a2cbd468))
* Parse enr2.1 and enr2.2 ([`98e0f75`](https://github.com/chssn/eaip-parser/commit/98e0f75ec821f76ba0b504f48f34b03c2a0c34f1))
* Started rebuild of webscrape ([`62a64da`](https://github.com/chssn/eaip-parser/commit/62a64da980e943598106c78f269434dec256b04f))
* Function to check if freq is 25KHz compliant ([`4be7e83`](https://github.com/chssn/eaip-parser/commit/4be7e838c0ec77c65c5f1cbfe61604473d880d2d))

### Fix
* Typo ([`52713ae`](https://github.com/chssn/eaip-parser/commit/52713aec2475b50210dffa07324757ed19c243c8))
* ENR 4 processing not happening ([`f28d2b8`](https://github.com/chssn/eaip-parser/commit/f28d2b881424fb1bbc1f4bfd57ddcb11e22796c7))
* Vor dme validator not running from main ([`b2052e1`](https://github.com/chssn/eaip-parser/commit/b2052e19f41afda5234a290f379ddfcb5451bbc6))
* Incorrect class parathensis ([`7585295`](https://github.com/chssn/eaip-parser/commit/7585295187ec6112ac28d6b70836b764698b2eca))
* Validator not running at module level ([`6bb1445`](https://github.com/chssn/eaip-parser/commit/6bb1445bc483dbd986db1152a894e466d0825c35))
* Redefined upper airway split fl ([`a7491ed`](https://github.com/chssn/eaip-parser/commit/a7491ed2c0afabd913f22b68d625e9a5616134ef))
* Not getting all points correctly ([`b7d6d36`](https://github.com/chssn/eaip-parser/commit/b7d6d36ab78a9a2eb652ceaa3c1a6c3ad1354205))
* Corrected airway formatting ([`6b23104`](https://github.com/chssn/eaip-parser/commit/6b231045b15c27ed3e2099748975572200ebd689))
* Corrected error and logging handling ([`00393fc`](https://github.com/chssn/eaip-parser/commit/00393fc2ec934da7653ccfd8371e71287328f2cf))
* General updates to prep for enr3.2 ([`ce33a0c`](https://github.com/chssn/eaip-parser/commit/ce33a0c2da8455a26e43bb2f00479b0663baf8c7))
* Not parsing CTR correctly ([`e31c884`](https://github.com/chssn/eaip-parser/commit/e31c884c05dfc1cd34fd850f96ba78925799b0ae))

### Performance
* Removed redundant code ([`520fc68`](https://github.com/chssn/eaip-parser/commit/520fc68650f6e1414dd5a7bff7d69ebb34456cf0))
* Removed redundant error check ([`bed28aa`](https://github.com/chssn/eaip-parser/commit/bed28aa5d9fbbe0d6e66596fc2f94b3517c3d3cf))
* Removed unused functions ([`d61a48e`](https://github.com/chssn/eaip-parser/commit/d61a48e8eba22b4dda1ab2c27355ecc9cb9f5d19))

## v0.2.0 (2023-07-27)


## v0.1.2 (2023-07-26)
### Fix
* Removed some print statements ([`f4d2f97`](https://github.com/chssn/eaip-parser/commit/f4d2f97dc225e5013bde584355da599e3e8a6e04))
* Passing full match instead of part thereof ([`1e14456`](https://github.com/chssn/eaip-parser/commit/1e1445618a0e8069f36b24cf5bef0b8a6402aea9))
* Dms2dd function not accepting DDMMSS input ([`a09916a`](https://github.com/chssn/eaip-parser/commit/a09916a16f9633a4b626ed6dae8eef8c62caf67b))

## v0.1.1 (2023-07-25)
### Fix
* Incorrect escaping of regex ([`65255e7`](https://github.com/chssn/eaip-parser/commit/65255e7a2202901d8a744ab2f27cb552d459e21f))

### Performance
* Removed unused library ([`7a47436`](https://github.com/chssn/eaip-parser/commit/7a474369ad25c16ff0e4204b0cbcae5727917017))

## v0.1.0 (2023-07-25)
### Feature
* Parses all point lat lon data ([`a30f0da`](https://github.com/chssn/eaip-parser/commit/a30f0dab6104f7bc19a97b27818bec3e140d9558))

### Fix
* Move and cleanup functions ([`4374e24`](https://github.com/chssn/eaip-parser/commit/4374e24650b531bac8ccffd2f64a905f243440b7))
* Incorrect debug message ([`118dd35`](https://github.com/chssn/eaip-parser/commit/118dd35f561bece6273abea848ee8129325b47fe))
* Not finding runways ([`512985a`](https://github.com/chssn/eaip-parser/commit/512985a36bacddacc7073ba3fd2f2d188ea36a59))
* Update regex for aerodrome search ([`aeb7285`](https://github.com/chssn/eaip-parser/commit/aeb728524d00a6a0ec7299767cff7b09cb5a945e))
* Allow date entry in Webscrape class ([`f2584b2`](https://github.com/chssn/eaip-parser/commit/f2584b2e7030a03181f6b011f2562050d4d48965))
* Set default to scrape the next airac data ([`ff2c671`](https://github.com/chssn/eaip-parser/commit/ff2c671aaa34c7ebea03ce9aeeb035bbb5160498))
* Unable to set custom date ([`d0de2f5`](https://github.com/chssn/eaip-parser/commit/d0de2f50e0692e9861ced7847e2cb3ab3272808b))
* Improved error checking ([`2c74fa0`](https://github.com/chssn/eaip-parser/commit/2c74fa032fdd7a46c58cb22c316ab120439bef1f))
* Var ref before defined ([`079cd8a`](https://github.com/chssn/eaip-parser/commit/079cd8a12355854c1fdb28b029fd88351a966bcd))

### Performance
* Cleaned up code ([`ff2e1c6`](https://github.com/chssn/eaip-parser/commit/ff2e1c69d81402e27451ec535e1aa2f5f0ca7b3a))
* Remove redundant try except statement ([`54a60e9`](https://github.com/chssn/eaip-parser/commit/54a60e9d3be6340cc909c3811c2a952b5c0380db))
* Added timeout to get request ([`8f89f36`](https://github.com/chssn/eaip-parser/commit/8f89f36c513e9d4d3d7472463b8ab5066cc0075a))
