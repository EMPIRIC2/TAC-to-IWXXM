"""Unit-test fixtures for facade/part monkeypatch compatibility."""

from __future__ import annotations

from contextlib import ExitStack

import pytest


@pytest.fixture(autouse=True)
def _broadcast_split_service_patches(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep ``patch.object`` on thin facades in sync with split part modules."""
    import unittest.mock as um

    from src.services import conversion_profiles_service as cps
    from src.services import conversion_profiles_service_part_1 as cps_p1
    from src.services import conversion_profiles_service_part_2 as cps_p2
    from src.services import conversion_profiles_service_part_2_mixin_1 as cps_m1
    from src.services import conversion_profiles_service_part_2_mixin_1_mixin_1 as cps_m2
    from src.services import conversion_profiles_service_part_2_mixin_1_mixin_1_mixin_1 as cps_m3

    targets = {
        cps: [cps_p1, cps_p2, cps_m1, cps_m2, cps_m3],
    }
    real_object = um.patch.object

    def _object(target, attribute, *args, **kwargs):
        parts = targets.get(target)
        if parts is None:
            return real_object(target, attribute, *args, **kwargs)
        primary = real_object(target, attribute, *args, **kwargs)

        class _Combined:
            def __enter__(self):
                self._stack = ExitStack()
                self._stack.__enter__()
                mock = self._stack.enter_context(primary)
                for mod in parts:
                    if hasattr(mod, attribute):
                        self._stack.enter_context(real_object(mod, attribute, mock))
                return mock

            def __exit__(self, *exc):
                return self._stack.__exit__(*exc)

        return _Combined()

    monkeypatch.setattr(um.patch, "object", _object)
    return
