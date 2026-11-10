"""md 문서의 줄바꿈이 GitHub에서도 보이도록 문단 안의 줄 끝에 공백 두 개를 붙인다.

사용법: python3 tools/fix_linebreaks.py [--check]
- 인자 없이 실행하면 파일을 고친다. --check는 고칠 곳이 있으면 목록만 보이고 종료 코드 1을 돌려준다.
- 여러 번 실행해도 결과가 같다. 작명/, 참고자료/, 과거작업/, .obsidian/은 건드리지 않는다.
- 표, 제목, 목록 항목 사이, 코드 블록 안은 건드리지 않는다.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"작명", "참고자료", "과거작업", ".obsidian", ".git", ".trash", "tools"}
LIST = re.compile(r"^\s*([-*+]|\d+[.)])\s")
SPECIAL = re.compile(r"^\s*(#|\||>|```|---)")


def fix(text):
    lines = text.split("\n")
    out = []
    fence = False
    for i, line in enumerate(lines):
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        if line.lstrip().startswith("```"):
            fence = not fence
        need = (
            not fence
            and line.strip()
            and nxt.strip()
            and not line.endswith("  ")
            and not SPECIAL.match(line)
            and not SPECIAL.match(nxt)
            and not LIST.match(nxt)
            and not nxt.lstrip().startswith("```")
        )
        out.append(line.rstrip() + "  " if need else line)
    return "\n".join(out)


def main():
    check = "--check" in sys.argv
    changed = []
    for p in sorted(ROOT.rglob("*.md")):
        if SKIP & set(p.relative_to(ROOT).parts):
            continue
        old = p.read_text(encoding="utf-8")
        new = fix(old)
        if new != old:
            changed.append(p.relative_to(ROOT))
            if not check:
                p.write_text(new, encoding="utf-8")
    for c in changed:
        print(c)
    print(f"{len(changed)}개 파일", "(고칠 곳)" if check else "수정")
    sys.exit(1 if check and changed else 0)


main()
