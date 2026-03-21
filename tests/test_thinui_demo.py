from pathlib import Path
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[1]
DEMO_SCRIPT = REPO_ROOT / "scripts" / "demo-thinui-launch.sh"


def test_thinui_demo_script_exists() -> None:
    assert DEMO_SCRIPT.exists()


def test_thinui_demo_script_prints_nes_theme_payload() -> None:
    result = subprocess.run(
        ["bash", str(DEMO_SCRIPT)],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert '"themeId": "thinui-nes-sonic"' in result.stdout
