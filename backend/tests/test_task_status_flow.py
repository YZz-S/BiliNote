import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.enmus.note_enums import DownloadQuality
from app.enmus.task_status_enums import TaskStatus
from app.routers import note as note_router


class TaskStatusFlowTests(unittest.TestCase):
    def test_run_note_task_marks_failed_when_note_is_empty(self):
        generator = MagicMock()
        generator.generate.return_value = SimpleNamespace(markdown="")
        updater = MagicMock()

        with patch.object(note_router, "NoteGenerator", side_effect=[generator, updater]):
            with patch.object(note_router, "save_note_to_file") as save_note_to_file:
                note_router.run_note_task(
                    task_id="task-empty",
                    video_url="https://example.com/video",
                    platform="bilibili",
                    quality=DownloadQuality.medium,
                    model_name="test-model",
                    provider_id="provider-1",
                )

        save_note_to_file.assert_not_called()
        updater._update_status.assert_called_once_with(
            "task-empty",
            TaskStatus.FAILED,
            message="任务结果为空，未生成有效笔记内容",
        )

    def test_get_task_status_recovers_missing_result_file_from_cache(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            task_id = "task-recover"

            (temp_path / f"{task_id}.status.json").write_text(
                json.dumps({"status": TaskStatus.SUCCESS.value}, ensure_ascii=False),
                encoding="utf-8",
            )
            (temp_path / f"{task_id}_markdown.md").write_text(
                "# Recovered",
                encoding="utf-8",
            )
            (temp_path / f"{task_id}_transcript.json").write_text(
                json.dumps(
                    {
                        "language": "zh",
                        "full_text": "hello",
                        "segments": [],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            (temp_path / f"{task_id}_audio.json").write_text(
                json.dumps(
                    {
                        "title": "demo",
                        "duration": 12,
                        "file_path": "demo.mp3",
                        "platform": "bilibili",
                        "raw_info": {},
                        "video_id": "BV1xx",
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            with patch.object(note_router, "NOTE_OUTPUT_DIR", temp_dir):
                response = note_router.get_task_status(task_id)

            payload = json.loads(response.body)
            self.assertEqual(payload["code"], 0)
            self.assertEqual(payload["data"]["status"], TaskStatus.SUCCESS.value)
            self.assertEqual(payload["data"]["result"]["markdown"], "# Recovered")
            self.assertTrue((temp_path / f"{task_id}.json").exists())

    def test_get_task_status_marks_failed_when_result_and_cache_are_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            task_id = "task-missing"

            status_path = temp_path / f"{task_id}.status.json"
            status_path.write_text(
                json.dumps({"status": TaskStatus.SUCCESS.value}, ensure_ascii=False),
                encoding="utf-8",
            )

            updater = MagicMock()
            with patch.object(note_router, "NOTE_OUTPUT_DIR", temp_dir):
                with patch.object(note_router, "NoteGenerator", return_value=updater):
                    response = note_router.get_task_status(task_id)

            payload = json.loads(response.body)
            self.assertEqual(payload["code"], 500)
            self.assertIn("结果文件缺失", payload["msg"])

            updated_status = json.loads(status_path.read_text(encoding="utf-8"))
            self.assertEqual(updated_status["status"], TaskStatus.FAILED.value)
            self.assertIn("结果文件缺失", updated_status["message"])
            updater._update_status.assert_called_once()


if __name__ == "__main__":
    unittest.main()
