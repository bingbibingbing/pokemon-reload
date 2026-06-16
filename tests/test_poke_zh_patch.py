import unittest
from pathlib import Path

from tools.poke_zh_patch import DRAW_TEXT_SHADOW_SOURCE


class ZhPatchSourceTests(unittest.TestCase):
    def test_draw_text_shadow_routes_mapped_zh_strings_to_bitmap_renderer(self) -> None:
        self.assertIn(
            'if(global.language="zh" && global.zh_text_key_map!=(-1) && ds_map_exists(global.zh_text_key_map,argument2)){',
            DRAW_TEXT_SHADOW_SOURCE,
        )
        self.assertIn(
            'ex(7028,argument2,argument0,argument1,argument3,fa_left,1);',
            DRAW_TEXT_SHADOW_SOURCE,
        )
        self.assertNotIn("draw_get_halign()", DRAW_TEXT_SHADOW_SOURCE)

    def test_draw_modal_base_keeps_centered_confirm_text_centered(self) -> None:
        source = (Path(__file__).resolve().parents[1] / "tools" / "poke_zh_patch.py").read_text(encoding="utf-8")
        self.assertIn(
            'ex(7028,global.drawModalText,view_xview+122+offX,view_yview+global.drawModalOffset+offY,ex(5971,global.cuadrodialogo),fa_center,1);',
            source,
        )
        self.assertIn(
            'ex(7028,global.optionSelection[1],view_xview+120+offX,view_yview+107+offY,Col,fa_center,1);',
            source,
        )


if __name__ == "__main__":
    unittest.main()
