"""TTSEngine のモック"""

import copy
from typing import Final

import numpy as np
from numpy.typing import NDArray

from ...metas.metas import StyleId
from ...model import AudioQuery
from ...tts_pipeline.audio_postprocessing import raw_wave_to_output_wave
from ...tts_pipeline.tts_engine import (
    TTSEngine,
    to_flatten_moras,
)
from ..core.mock import MockCoreWrapper
from ...utility.path_utility import engine_root
import subprocess
import soundfile as sf
_engine_dir = engine_root()
TEMP_WAVE_PATH = _engine_dir / "temp.wav"

class MockTTSEngine(TTSEngine):
    """製品版コア無しに音声合成が可能なモック版TTSEngine"""

    def __init__(self) -> None:
        super().__init__(MockCoreWrapper())

    def synthesize_wave(
        self,
        query: AudioQuery,
        style_id: StyleId,
        enable_interrogative_upspeak: bool,
    ) -> NDArray[np.float32]:
        """音声合成用のクエリに含まれる読み仮名に基づいてOpenJTalkで音声波形を生成する。モーラごとの調整は反映されない。"""
        # モーフィング時などに同一参照のqueryで複数回呼ばれる可能性があるので、元の引数のqueryに破壊的変更を行わない
        query = copy.deepcopy(query)

        # recall text in katakana
        flatten_moras = to_flatten_moras(query.accent_phrases)
        kana_text = "".join([mora.text for mora in flatten_moras])

        raw_wave, sr_raw_wave = self.forward(kana_text, style_id)
        wave = raw_wave_to_output_wave(query, raw_wave, sr_raw_wave)
        return wave

    def forward(self, text: str, style_id:int) -> tuple[NDArray[np.float32], int]:
        """文字列から pyopenjtalk を用いて音声を合成する。"""
        cli_path = _engine_dir / "bouyomi-cli/run"

        if style_id == 0:
            speaker = "dvd"
        elif style_id == 1:
            speaker = "f1"
        elif style_id == 2:
            speaker = "f2"
        elif style_id == 3:
            speaker = "imd1"
        elif style_id == 4:
            speaker = "jgr"
        elif style_id == 5:
            speaker = "m1"
        elif style_id == 6:
            speaker = "m2"
        elif style_id == 7:
            speaker = "r1"

        subprocess.run(f"{str(cli_path)} {TEMP_WAVE_PATH} {text} {speaker}")
        raw_wave, samplerate = sf.read(TEMP_WAVE_PATH)
        return raw_wave.astype(np.float32), samplerate
