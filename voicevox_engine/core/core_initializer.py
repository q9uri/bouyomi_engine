"""VOICEVOX CORE インスタンスの生成"""

import json
import os
import warnings
from pathlib import Path

from ..utility.core_version_utility import MOCK_CORE_VERSION, get_latest_version
from ..utility.path_utility import engine_root, get_save_dir
from .core_adapter import CoreAdapter



def _get_half_logical_cores() -> int:
    logical_cores = os.cpu_count()
    if logical_cores is None:
        return 0
    return logical_cores // 2


class CoreNotFound(Exception):
    """コアが見つからないエラー"""

    pass


class CoreManager:
    """コアの集まりを一括管理するマネージャー"""

    def __init__(self) -> None:
        self._cores: dict[str, CoreAdapter] = {}

    def versions(self) -> list[str]:
        """登録されたコアのバージョン一覧を取得する。"""
        return list(self._cores.keys())

    def latest_version(self) -> str:
        """登録された最新版コアのバージョンを取得する。"""
        return get_latest_version(self.versions())

    def register_core(self, core: CoreAdapter, version: str) -> None:
        """コアを登録する。"""
        self._cores[version] = core

    def get_core(self, version: str) -> CoreAdapter:
        """指定バージョンのコアを取得する。"""
        if version in self._cores:
            return self._cores[version]
        raise CoreNotFound(f"バージョン {version} のコアが見つかりません")

    def has_core(self, version: str) -> bool:
        """指定バージョンのコアが登録されているか否かを返す。"""
        return version in self._cores

    def items(self) -> list[tuple[str, CoreAdapter]]:
        """登録されたコアとそのバージョンのリストを取得する。"""
        return list(self._cores.items())


def initialize_cores(
    use_gpu: bool,
    voicelib_dirs: list[Path] | None = None,
    voicevox_dir: Path | None = None,
    runtime_dirs: list[Path] | None = None,
    cpu_num_threads: int | None = None,
    enable_mock: bool = True,
    load_all_models: bool = False,
) -> CoreManager:
    """
    音声ライブラリを読み込んでコアを生成する。

    Parameters
    ----------
    use_gpu: bool
        音声ライブラリに GPU を使わせるか否か
    voicelib_dirs:
        音声ライブラリ自体があるディレクトリのリスト
    voicevox_dir:
        コンパイル済みのvoicevox、またはvoicevox_engineがあるディレクトリ
    runtime_dirs:
        コアで使用するライブラリのあるディレクトリのリスト
        None のとき、voicevox_dir、カレントディレクトリになる
    cpu_num_threads:
        音声ライブラリが、推論に用いるCPUスレッド数を設定する
        Noneのとき、論理コア数の半分が指定される
    enable_mock:
        コア読み込みに失敗したとき、代わりにmockを使用するかどうか
    load_all_models:
        起動時に全てのモデルを読み込むかどうか
    """
    if cpu_num_threads == 0 or cpu_num_threads is None:
        msg = "cpu_num_threads is set to 0. Setting it to half of the logical cores."
        warnings.warn(msg, stacklevel=1)
        cpu_num_threads = _get_half_logical_cores()

    root_dir = engine_root()

    # 引数による指定を反映し、無ければ `root_dir` とする
    runtime_dirs = runtime_dirs or []
    runtime_dirs += [voicevox_dir] if voicevox_dir else []
    runtime_dirs = runtime_dirs or [root_dir]
    runtime_dirs = [p.expanduser() for p in runtime_dirs]

    # 引数による指定を反映し、無ければ `root_dir` とする
    voicelib_dirs = voicelib_dirs or []
    voicelib_dirs += [voicevox_dir] if voicevox_dir else []
    voicelib_dirs = voicelib_dirs or [root_dir]
    voicelib_dirs = [p.expanduser() for p in voicelib_dirs]

    core_manager = CoreManager()
    # モック追加
    from ..dev.core.mock import MockCoreWrapper

    if not core_manager.has_core(MOCK_CORE_VERSION):
        core = MockCoreWrapper()
        core_manager.register_core(CoreAdapter(core), MOCK_CORE_VERSION)

    return core_manager
