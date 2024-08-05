# CHANGELOG



## v0.1.0 (2024-08-05)

### Feature

* feat: add poetry (#10)

* Add poetry

* chore(pre-commit.ci): auto fixes

* Add poetry

* Add poetry

---------

Co-authored-by: pre-commit-ci[bot] &lt;66853113+pre-commit-ci[bot]@users.noreply.github.com&gt; ([`78f6c71`](https://github.com/uilibs/uvcclient/commit/78f6c7142457aa0667d742969d843626aa28dba9))

### Unknown

* Merge pull request #9 from uilibs/precommit

Add precommit ([`f817033`](https://github.com/uilibs/uvcclient/commit/f8170338912a22202c3df31d5014c799e94d0d8d))

* Add precommit ([`f7cfc82`](https://github.com/uilibs/uvcclient/commit/f7cfc824dcb2989cfdb99aa22358085bb46ab979))

* Add precommit ([`d6496a4`](https://github.com/uilibs/uvcclient/commit/d6496a4eac6385dae3667d93656f0abeb698bef1))

* Call this 0.11.1 ([`40c534a`](https://github.com/uilibs/uvcclient/commit/40c534ad6e0537feba7ec117d57ef4f667f252ce))

* Merge pull request #8 from joostlek/gpl

Add License ([`e40b42b`](https://github.com/uilibs/uvcclient/commit/e40b42b5241879d92034d06ddbead1bbba5591d2))

* Add License ([`12054bb`](https://github.com/uilibs/uvcclient/commit/12054bbc104b22735d3083cd7ab6b2acf7479afd))

* Call this 0.10 ([`58e7a53`](https://github.com/uilibs/uvcclient/commit/58e7a53815482b7778481f81cde95f53a60bb6f6))

* Merge branch &#39;master&#39; of https://github.com/kk7ds/uvcclient ([`8473a14`](https://github.com/uilibs/uvcclient/commit/8473a1470f77e35e632279621402d3812c152ccb))

* Merge pull request #5 from carlos-sarmiento/patch-1

Added HTTPS support to nvr.py ([`6d0b9ab`](https://github.com/uilibs/uvcclient/commit/6d0b9abc4040f9f4068c082d6ba57403196da486))

* Added HTTPS support to nvr.py ([`a635d3e`](https://github.com/uilibs/uvcclient/commit/a635d3ec40dbc93b63203338557f407cd591d8e0))

* Add get_status() to camera client ([`69640bc`](https://github.com/uilibs/uvcclient/commit/69640bc59be9cb01eb688cca18b50868615353ed))

* Add camera reboot action ([`63fd45f`](https://github.com/uilibs/uvcclient/commit/63fd45fae613a3d886771bae9298b0f6656e78d8))

* Call this 0.10.1 ([`b090128`](https://github.com/uilibs/uvcclient/commit/b090128d0c75b29fef97b311c50697d4a281416c))

* Fix version parsing when the revision is not an integer

Treat 3.4.beta5 as 3.4.0 as the &#34;beta&#34; should be equivalent
to 3.4.0.

Fixes #3 ([`f1778b0`](https://github.com/uilibs/uvcclient/commit/f1778b07e6d87f9d77251bc36114182b4bb614c3))

* Open 0.11 ([`48a270a`](https://github.com/uilibs/uvcclient/commit/48a270adbd46a90a0e53d0ee5f671d5778d7fc3b))

* This is 0.10.0 ([`d87a3fa`](https://github.com/uilibs/uvcclient/commit/d87a3fa62fb387c5e47fc5a1cac09e52395ccf9d))

* Filter deleted cameras out of index()

Obviously the intent was not ever to include deleted cameras, I just
didn&#39;t realize they&#39;d expose this way. ([`11d03e6`](https://github.com/uilibs/uvcclient/commit/11d03e6a700cb26e6324eca20d3ac93f2c976af5))

* Allow getting the record mode of a camera ([`e6d41b2`](https://github.com/uilibs/uvcclient/commit/e6d41b2dcf43718d70d2063b8e4a604c20a86cd8))

* Open 0.10.0 ([`64bec7a`](https://github.com/uilibs/uvcclient/commit/64bec7ae2440ccf73800e34191b2ae0e89df3821))

* Call this 0.9.0 ([`37e8f3b`](https://github.com/uilibs/uvcclient/commit/37e8f3bbd54fd27586e2ad1e04d108b215e19066))

* Fix direct-to-camera client operations for v3.2.x

Fixes #1 ([`e722954`](https://github.com/uilibs/uvcclient/commit/e722954b40dc12c4f8bcd993c1159b6f951402e0))

* Fix NVR communication by &#39;id&#39; for version &gt;= 3.2.x

This makes us resolve names to the &#39;id&#39; instead of &#39;uuid&#39; for newer
versions of the NVR server software.

Fixes most of #1 ([`6a32dbe`](https://github.com/uilibs/uvcclient/commit/6a32dbeb8357646f0e709e6866959f441ddf0265))

* Fix calling snapshot on py2 ([`70ac477`](https://github.com/uilibs/uvcclient/commit/70ac4772d7b050dac28ddf1e72481f304ba4b5db))

* Fall back to getting the image through the NVR if direct fails ([`c14daaf`](https://github.com/uilibs/uvcclient/commit/c14daafed001e2c61e7b144c2581a291bd423d63))

* Add get_snapshot() to nvr for when we can&#39;t reach the camera ([`eff01b8`](https://github.com/uilibs/uvcclient/commit/eff01b81a8948f72f8c564bc01db1a881cc26cdf))

* Catch OSError *and* socket.error in camera client ([`238ab51`](https://github.com/uilibs/uvcclient/commit/238ab51d0df63b658da8dbd7879a62ef1b70b35d))

* Fix tests (hopefully) for mocking open ([`f4a6b2b`](https://github.com/uilibs/uvcclient/commit/f4a6b2bddb060aab92302a8748051a079af6f285))

* Open 0.9 ([`eb41a6e`](https://github.com/uilibs/uvcclient/commit/eb41a6ed2c216541979084b4f8bcc8825dfe0403))

* Call this 0.8 ([`c03e65b`](https://github.com/uilibs/uvcclient/commit/c03e65b336deb9dec0cdde27abf53fcfcb9dd1bb))

* Update README.rst ([`a844457`](https://github.com/uilibs/uvcclient/commit/a844457cbcfdefcc63a19a24024c0ca59440ecd1))

* Provide a persistent store for camera passwords and a CLI command to set them ([`c1346d9`](https://github.com/uilibs/uvcclient/commit/c1346d92f3c0565dc4a630199ef213834706f391))

* Fix test_get_snapshot() test ([`fb1ae39`](https://github.com/uilibs/uvcclient/commit/fb1ae391bee439e7daa12c3b3e48bab28071ce26))

* Open 0.7 ([`50e6829`](https://github.com/uilibs/uvcclient/commit/50e6829dee4807c0aaad53b97319aee6cef286c8))

* Call this 0.6 ([`69383a1`](https://github.com/uilibs/uvcclient/commit/69383a17602a28a08495ba170a534f0bfbddc254))

* Fix wrong exception name error ([`150dc4e`](https://github.com/uilibs/uvcclient/commit/150dc4e9d623254bea4184a9192d963db5aa9880))

* Raise proper errors in snapshot so we can tell if we need to re-login ([`b4b3f3b`](https://github.com/uilibs/uvcclient/commit/b4b3f3b6aa5026845945519e90717cac05b5cb2e))

* Python2 fixes for talking directly to the camera ([`9e20878`](https://github.com/uilibs/uvcclient/commit/9e20878b4c732a0778cea74edb05dc912686aa38))

* Wrap connections to NVR for error handling as well ([`1116cfe`](https://github.com/uilibs/uvcclient/commit/1116cfe7071c8f5aa5690d28c0f8aae075492e09))

* Add --get-snapshot to the client ([`8b96a71`](https://github.com/uilibs/uvcclient/commit/8b96a71fde70b453a39e88fac0d4552388637757))

* Add error handling when talking directly to camera ([`55d989b`](https://github.com/uilibs/uvcclient/commit/55d989bc03976ab9813abd36f110ec3cfe2d8eb7))

* Call this 0.5 ([`9803853`](https://github.com/uilibs/uvcclient/commit/980385398d1aff21bfa05dc844c8b0137277da5e))

* Properly raise request errors, and distinguish auth failures ([`c6ab616`](https://github.com/uilibs/uvcclient/commit/c6ab616f673839d311f8b772ea095a604dda5480))

* Add and fix tests for get_snapshot() ([`0561c5c`](https://github.com/uilibs/uvcclient/commit/0561c5cc28c30997528c5613b609fd6d88108eb5))

* Call this 0.4 ([`d6b3d9a`](https://github.com/uilibs/uvcclient/commit/d6b3d9a536223997a42600e243e92ab7362c347e))

* Fix cookie name on py3 and add get_snapshot() to camera interface ([`a6b52d5`](https://github.com/uilibs/uvcclient/commit/a6b52d5a9dbcdaf2d16408a39294582b327ba905))

* Call this 0.3 ([`82765c6`](https://github.com/uilibs/uvcclient/commit/82765c61195fbf6188e195153d6484a6ae4639b8))

* Fix a couple python3 fails ([`c2d2abc`](https://github.com/uilibs/uvcclient/commit/c2d2abc0ce14a89fd81909edfd48e4747ddb7c9b))

* Add list-zones and prune-zones ([`35fd0dd`](https://github.com/uilibs/uvcclient/commit/35fd0ddbaa16fc20ca2cffa8168e47f5ebf80f26))

* Call this 0.2 ([`bdb8c82`](https://github.com/uilibs/uvcclient/commit/bdb8c824735319bcafae28b5a5390fa2d4c00d4a))

* Update gitignore ([`8dc762e`](https://github.com/uilibs/uvcclient/commit/8dc762ee39cdbe6ee64994fac12d2bfea16b093a))

* Oops, forgot this kindof important thing ([`0ee9a6a`](https://github.com/uilibs/uvcclient/commit/0ee9a6a78c0ad1dfca6b3c27e1d3c049fdf72576))

* Add support for talking direct to cameras, and setting micro LED status ([`b9382a7`](https://github.com/uilibs/uvcclient/commit/b9382a703b17b0e48f4f395d3928cb53e4a26044))

* Run nose with -v ([`9e61008`](https://github.com/uilibs/uvcclient/commit/9e61008627662460b7d7d44a097fd2c4ffdf31c4))

* Rename uvcclient.py to nvr.py for clarity ([`750530d`](https://github.com/uilibs/uvcclient/commit/750530deb377f249929e496f4d9080d8861b411f))

* Add gitignore ([`f74acb3`](https://github.com/uilibs/uvcclient/commit/f74acb35d126318cd3a112e3d7af6f090db1e996))

* Rearrange main client into separate module ([`81da59e`](https://github.com/uilibs/uvcclient/commit/81da59e3498d850adc6287c00ccee49d9282cf20))

* Add some more lifecycle information to the listing ([`9e3764f`](https://github.com/uilibs/uvcclient/commit/9e3764fb582818af5ac1198784bfd0771d15ae3e))

* Add pep8 tox target ([`21c8022`](https://github.com/uilibs/uvcclient/commit/21c8022018395de24d6e2264a25bc6a60d75f233))

* Add get/set picture settings ([`d784f71`](https://github.com/uilibs/uvcclient/commit/d784f71242ce8094029e6a13aae9aad8726aa50b))

* Add build status to README ([`fe83b2a`](https://github.com/uilibs/uvcclient/commit/fe83b2afe03ba3d8ba196b2b0ee1c74dba748945))

* Add travis CI yaml ([`6071479`](https://github.com/uilibs/uvcclient/commit/60714799c8e9c030bcaf0b6b8b091edef3e75b02))

* Fix print() in main() for py3 ([`af8842e`](https://github.com/uilibs/uvcclient/commit/af8842e92e71fb37aea53cbd81f7f1d12b932245))

* Add listing example to README ([`58629f4`](https://github.com/uilibs/uvcclient/commit/58629f4b32100298d29df7580cbf90ee96520a11))

* Update README ([`a7b9196`](https://github.com/uilibs/uvcclient/commit/a7b9196b313ebf19458a008e873053d09952e4fb))

* Require name or uuid for set_recordmode ([`ef0aa7d`](https://github.com/uilibs/uvcclient/commit/ef0aa7de57185d7e959c4847ebcf6c428fa74961))

* Add online/offline state to listing ([`49c5f69`](https://github.com/uilibs/uvcclient/commit/49c5f69add78e0b8ae7539a7a126c15dbf06cc07))

* Add some tests ([`c5ffd20`](https://github.com/uilibs/uvcclient/commit/c5ffd20f1dcf8843e9fa4d37d86b8b28701579d1))

* Initial checkin ([`033cb81`](https://github.com/uilibs/uvcclient/commit/033cb8117388fcaeaca8d80c330c5d644cdc1106))
