from pathlib import Path
import tempfile
import unittest

from PIL import Image

from tools.poke_zh_render import make_line_key, render_bitmap_text


class ZhBitmapRenderTests(unittest.TestCase):
    def test_make_line_key_includes_folder_filename_and_line(self) -> None:
        self.assertEqual(make_line_key("zh", "txt_dialog", 4), "zh__txt_dialog__4")
        self.assertEqual(make_line_key("zz", "ordenPokemonExtended", 12), "zz__ordenPokemonExtended__12")

    def test_render_bitmap_text_writes_non_empty_png(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "sample.png"
            size = render_bitmap_text("测试#文字", output)
            self.assertTrue(output.exists())
            self.assertGreater(size[0], 0)
            self.assertGreater(size[1], 0)

            with Image.open(output) as image:
                self.assertEqual(image.mode, "RGBA")
                self.assertEqual(image.size, size)
                self.assertEqual(image.getbbox(), (0, 0, size[0], size[1]))
                alpha_histogram = image.getchannel("A").histogram()
                alpha_values = {value for value, count in enumerate(alpha_histogram) if count}
                self.assertLessEqual(alpha_values, {0, 255})


if __name__ == "__main__":
    unittest.main()
