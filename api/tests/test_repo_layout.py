from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

PRD_DIRECTORIES = [
    "apps/web",
    "api/app/agents",
    "api/app/orchestration",
    "api/app/services",
    "api/app/repositories",
    "api/app/models",
    "api/app/schemas",
    "api/app/api",
    "api/app/core",
    "api/tests",
    "packages/shared",
]

PRD_FILES = [
    "docker-compose.yml",
    "pnpm-workspace.yaml",
    "package.json",
    ".env.example",
    "README.md",
]


def test_prd_layout_exists() -> None:
    missing = [p for p in PRD_DIRECTORIES if not (ROOT_DIR / p).is_dir()]
    missing += [p for p in PRD_FILES if not (ROOT_DIR / p).is_file()]

    assert missing == []
