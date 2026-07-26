#!/usr/bin/env python3
"""Unit tests for the deterministic Voicebox narration client."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
import wave
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIRECTORY))

import voicebox_narrate as subject


class VoiceboxNarrateTests(unittest.TestCase):
    def test_resolve_profile_uses_the_only_available_profile(self) -> None:
        profile = {"id": "voice-1", "name": "Narrator"}
        self.assertEqual(subject.resolve_profile([profile], None), profile)

    def test_resolve_profile_requires_selection_when_multiple_exist(self) -> None:
        profiles = [
            {"id": "voice-1", "name": "One"},
            {"id": "voice-2", "name": "Two"},
        ]
        with self.assertRaises(subject.VoiceboxError):
            subject.resolve_profile(profiles, None)

    def test_generation_payload_includes_explicit_engine_and_model(self) -> None:
        payload = subject.build_generation_payload(
            profile_id="voice-1",
            text="测试配音",
            language="zh",
            engine="qwen",
            model_size="1.7B",
            seed=7,
            instruct="自然、清楚",
            normalize=True,
            max_chunk_chars=800,
            crossfade_ms=50,
        )
        self.assertEqual(payload["engine"], "qwen")
        self.assertEqual(payload["model_size"], "1.7B")
        self.assertEqual(payload["language"], "zh")
        self.assertEqual(payload["seed"], 7)

    def test_parse_sse_completed_event(self) -> None:
        line = b'data: {"id":"generation-1","status":"completed","duration":1.2}\n'
        event = subject.parse_sse_data(line)
        self.assertEqual(event["status"], "completed")
        self.assertEqual(event["duration"], 1.2)

    def test_capabilities_are_read_from_live_schema_shape(self) -> None:
        spec = {
            "info": {"version": "0.5.0"},
            "components": {
                "schemas": {
                    "GenerationRequest": {
                        "properties": {
                            "engine": {"anyOf": [{"pattern": "^(qwen|tada)$"}, {"type": "null"}]},
                            "model_size": {"anyOf": [{"pattern": "^(1\\.7B|0\\.6B)$"}, {"type": "null"}]},
                            "language": {"pattern": "^(zh|en)$", "default": "en"},
                            "normalize": {"default": True},
                        }
                    }
                }
            },
        }
        capabilities = subject.extract_capabilities(spec)
        self.assertEqual(capabilities["engines"], ["qwen", "tada"])
        self.assertEqual(capabilities["modelSizes"], ["1.7B", "0.6B"])
        self.assertEqual(capabilities["languages"], ["zh", "en"])

    def test_wav_validation_uses_real_frames(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "voice.wav"
            with wave.open(str(path), "wb") as audio:
                audio.setnchannels(1)
                audio.setsampwidth(2)
                audio.setframerate(24000)
                audio.writeframes(b"\0\0" * 2400)
            details = subject.inspect_wav(path)
        self.assertEqual(details["sampleRate"], 24000)
        self.assertEqual(details["channels"], 1)
        self.assertAlmostEqual(details["durationSeconds"], 0.1)

    def test_daily_preset_is_qwen_0_6b_at_1_2x(self) -> None:
        args = SimpleNamespace(
            preset=None,
            language=None,
            engine=None,
            model_size=None,
            speed=None,
            seed=None,
            instruct=None,
            normalize=None,
            max_chunk_chars=None,
            crossfade_ms=None,
        )
        settings = subject.resolve_generation_settings(
            args, {}, {"language": "zh", "default_engine": "legacy"}
        )
        self.assertEqual(settings["preset"], "daily")
        self.assertEqual(settings["engine"], "qwen")
        self.assertEqual(settings["model_size"], "0.6B")
        self.assertEqual(settings["speed"], 1.2)

    def test_precision_preset_is_qwen_1_7b_at_1_2x(self) -> None:
        args = SimpleNamespace(
            preset="precision",
            language=None,
            engine=None,
            model_size=None,
            speed=None,
            seed=None,
            instruct=None,
            normalize=None,
            max_chunk_chars=None,
            crossfade_ms=None,
        )
        settings = subject.resolve_generation_settings(args, {}, {"language": "zh"})
        self.assertEqual(settings["model_size"], "1.7B")
        self.assertEqual(settings["speed"], 1.2)

    @unittest.skipUnless(subject.shutil.which("ffmpeg"), "FFmpeg is not installed")
    def test_tempo_adjustment_preserves_wav_and_shortens_duration(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source.wav"
            output = root / "output.wav"
            with wave.open(str(source), "wb") as audio:
                audio.setnchannels(1)
                audio.setsampwidth(2)
                audio.setframerate(24000)
                audio.writeframes(b"\0\0" * 24000)
            subject.apply_tempo(source, output, speed=1.2, force=False)
            details = subject.inspect_wav(output)
        self.assertEqual(details["sampleRate"], 24000)
        self.assertEqual(details["channels"], 1)
        self.assertGreater(details["durationSeconds"], 0.75)
        self.assertLess(details["durationSeconds"], 0.9)

    def test_section_id_rejects_path_traversal(self) -> None:
        with self.assertRaises(subject.VoiceboxError):
            subject.safe_section_id("../secret")

    def test_batch_rejects_any_existing_section_before_generation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            input_path = root / "sections.json"
            input_path.write_text(
                json.dumps(
                    {
                        "language": "zh",
                        "sections": [
                            {"id": "first", "text": "第一段。"},
                            {"id": "second", "text": "第二段。"},
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            output_dir = root / "output"
            output_dir.mkdir()
            (output_dir / "002-second.wav").write_bytes(b"existing")
            args = SimpleNamespace(
                authorized_voice=True,
                no_auto_start=True,
                start_timeout=1,
                input=input_path,
                output_dir=output_dir,
                profile=None,
                preset=None,
                language=None,
                engine=None,
                model_size=None,
                speed=None,
                seed=None,
                instruct=None,
                normalize=None,
                max_chunk_chars=None,
                crossfade_ms=None,
                timeout=1,
                force=False,
            )
            with (
                mock.patch.object(subject, "ensure_server", return_value={"status": "healthy"}),
                mock.patch.object(
                    subject,
                    "list_profiles",
                    return_value=[{"id": "voice-1", "name": "Narrator", "language": "zh"}],
                ),
                mock.patch.object(subject, "get_server_version", return_value="test"),
                mock.patch.object(
                    subject,
                    "generate_one",
                    side_effect=[
                        {
                            "generationId": "generated-first",
                            "text": "第一段。",
                            "textSha256": "text-hash",
                            "audio": {"durationSeconds": 1.0, "sha256": "audio-hash"},
                            "engine": "qwen",
                            "modelSize": "1.7B",
                            "instruct": None,
                        },
                        subject.VoiceboxError("Output already exists"),
                    ],
                ) as generate,
            ):
                with self.assertRaises(subject.VoiceboxError):
                    subject.command_batch(args, "http://127.0.0.1:17493")
            self.assertEqual(generate.call_count, 0)
            self.assertFalse((output_dir / "narration-manifest.json").exists())

    def test_batch_fixture_shape_is_json_serializable(self) -> None:
        package = {
            "language": "zh",
            "engine": "qwen",
            "model_size": "1.7B",
            "sections": [{"id": "hook", "text": "第一段。"}],
        }
        self.assertIn("sections", json.loads(json.dumps(package, ensure_ascii=False)))


if __name__ == "__main__":
    unittest.main()
