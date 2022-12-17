#!env python3
# """Action body."""
import os
import re
from actions_toolkit import core

KNOWN_PYTHONS = ("3.7", "3.8", "3.9", "3.10", "3.11", "3.12-dev")
PLATFORM_MAP = {
    "linux": "ubuntu-22.04",
    "macos": "macos-12",
    "windows": "windows-latest",
}
IMPLICIT_PLATFORM = "linux"


# loop list staring with given item
def main() -> None:
    """Main."""
    try:
        other_envs = core.get_input("other_envs", required=False).split(",")
        platforms = core.get_input("platforms", required=False).split(",")
        min_python = core.get_input("min_python", required=True)
        stategies = {}
        for platform in PLATFORM_MAP:
            stategies[platform] = core.get_input(platform, required=False)

        core.debug(f"Testing strategy: {stategies}")

        result = []
        default_python = KNOWN_PYTHONS[KNOWN_PYTHONS.index(min_python)]
        python_flavours = len(KNOWN_PYTHONS[KNOWN_PYTHONS.index(min_python) :])
        for env in other_envs:
            result.append(
                {
                    "name": env,
                    "tox_env": env,
                    "python-version": default_python,
                    "os": PLATFORM_MAP["linux"],
                }
            )
        for platform in platforms:
            for i, python in enumerate(
                KNOWN_PYTHONS[KNOWN_PYTHONS.index(min_python) :]
            ):
                py_name = re.sub(r"[^0-9]", "", python.strip("."))
                if platform == IMPLICIT_PLATFORM:
                    suffix = ""
                else:
                    suffix = f"-{platform}"

                if stategies[platform] == "minmax" and (
                    i not in (0, python_flavours - 1)
                ):
                    continue

                result.append(
                    {
                        "name": f"py{py_name}{suffix}",
                        "python-version": python,
                        "os": PLATFORM_MAP[platform],
                        "tox_env": f"py{py_name}",
                    }
                )

        core.info(f"Generated {len(result)} matrix entries.")
        names = [k["name"] for k in result]
        core.info(f"Job names: {', '.join(names)}")

        core.set_output("matrix_include", result)

    except Exception as exc:
        core.set_failed(f"Action failed due to {exc}")


if __name__ == "__main__":

    # only used for local testing, emulating use from github actions
    if os.getenv("GITHUB_ACTIONS") is None:
        os.environ["INPUT_OTHER_ENVS"] = "lint,pkg"
        os.environ["INPUT_MIN_PYTHON"] = "3.8"
        os.environ["INPUT_PLATFORMS"] = "linux,macos"  # macos and windows
        os.environ["INPUT_LINUX"] = "full"
        os.environ["INPUT_MACOS"] = "minmax"
        os.environ["INPUT_WINDOWS"] = "minmax"

    main()
