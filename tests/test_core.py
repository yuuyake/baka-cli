import json
import os
import stat
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from baka_cli import cli, config, utils


class TestUtils(unittest.TestCase):
    def test_unpack_packer(self):
        # Simple p.a.c.k.e.r payload: 0 -> "https", 1 -> "example", 2 -> "com", 3 -> "video", 4 -> "m3u8"
        packed = "eval(function(p,a,c,k,e,d){return p}('0://1.2/3.4',5,5,'https|example|com|video|m3u8'.split('|'),0,{}))"
        self.assertEqual(
            utils.unpack_packer(packed),
            "https://example.com/video.m3u8",
        )

    def test_unpack_packer_no_match(self):
        self.assertEqual(utils.unpack_packer("plain javascript"), "")


class TestCliHelpers(unittest.TestCase):
    def test_ep_num(self):
        self.assertEqual(cli.ep_num("Episode 1"), 1)
        self.assertEqual(cli.ep_num("Episode 12"), 12)
        self.assertEqual(cli.ep_num("Episode 12.5"), 12.5)
        self.assertNotEqual(cli.ep_num("Episode 12.5"), cli.ep_num("Episode 12"))
        self.assertIsNone(cli.ep_num("Special"))

    def test_sim(self):
        self.assertGreater(cli._sim("Frieren: Beyond Journey's End (2023)", "Frieren Beyond Journeys End"), 0.9)
        self.assertLess(cli._sim("Naruto", "One Piece"), 0.5)

    def test_search_providers_all_parallel(self):
        class FakeA:
            in_all = True
            def search(self, q):
                return [("Title A", "a1")]

        class FakeB:
            in_all = True
            def search(self, q):
                raise RuntimeError("boom")

        class FakeC:
            in_all = False
            def search(self, q):
                return [("Title C", "c1")]

        args = SimpleNamespace(all=True, provider="a")
        with patch.dict(cli.PROVIDERS, {"a": FakeA, "b": FakeB, "c": FakeC}, clear=True):
            res = cli.search_providers("test", args)
        self.assertEqual(res, [("[a] Title A", ("a", "a1", "Title A"))])


class TestConfig(unittest.TestCase):
    def test_save_and_load_atomic_permissions(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            cfg_dir = base / "baka-cli"
            cfg_file = cfg_dir / "config.json"
            old_file = base / "techno-cli" / "config.json"
            with patch.object(config, "DIR", cfg_dir), \
                 patch.object(config, "FILE", cfg_file), \
                 patch.object(config, "OLD", old_file):
                self.assertEqual(config.load(), {})
                config.save({"auth": {"anilist": {"token": "secret"}}})
                self.assertTrue(cfg_file.exists())
                mode = stat.S_IMODE(os.stat(cfg_file).st_mode)
                self.assertEqual(mode, 0o600)
                self.assertEqual(json.loads(cfg_file.read_text()), {"auth": {"anilist": {"token": "secret"}}})
                self.assertEqual(config.load()["auth"]["anilist"]["token"], "secret")


if __name__ == "__main__":
    unittest.main()
