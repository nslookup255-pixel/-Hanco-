# 파일 라이브러리


def _경로값(인자, 함수이름):
    from pathlib import Path

    if len(인자) != 1:
        raise Exception(f"{함수이름} 함수는 경로 1개를 받아야 합니다.")

    경로 = 인자[0]
    if not isinstance(경로, str):
        raise Exception(f"{함수이름} 함수의 경로는 문자열이어야 합니다.")

    return Path(경로)


def _경로와내용(인자, 함수이름):
    from pathlib import Path

    if len(인자) != 2:
        raise Exception(f"{함수이름} 함수는 경로와 내용 2개를 받아야 합니다.")

    경로, 내용 = 인자
    if not isinstance(경로, str):
        raise Exception(f"{함수이름} 함수의 경로는 문자열이어야 합니다.")
    if not isinstance(내용, str):
        raise Exception(f"{함수이름} 함수의 내용은 문자열이어야 합니다.")

    return Path(경로), 내용


def 읽기(인자):
    경로 = _경로값(인자, "파일:읽기")
    if not 경로.exists():
        raise Exception(f"파일이 존재하지 않습니다. ({경로})")
    if not 경로.is_file():
        raise Exception(f"파일만 읽을 수 있습니다. ({경로})")

    return 경로.read_text(encoding="utf-8")


def 쓰기(인자):
    경로, 내용 = _경로와내용(인자, "파일:쓰기")
    경로.write_text(내용, encoding="utf-8")
    return None


def 추가(인자):
    경로, 내용 = _경로와내용(인자, "파일:추가")
    with 경로.open("a", encoding="utf-8") as 파일:
        파일.write(내용)
    return None


def 존재(인자):
    경로 = _경로값(인자, "파일:존재")
    return 경로.exists()


def 삭제(인자):
    경로 = _경로값(인자, "파일:삭제")
    if not 경로.exists():
        return False
    if not 경로.is_file():
        raise Exception(f"파일만 삭제할 수 있습니다. ({경로})")

    경로.unlink()
    return True


def 목록(인자):
    경로 = _경로값(인자, "파일:목록")
    if not 경로.exists():
        raise Exception(f"경로가 존재하지 않습니다. ({경로})")
    if not 경로.is_dir():
        raise Exception(f"폴더만 목록으로 볼 수 있습니다. ({경로})")

    return sorted([항목.name for 항목 in 경로.iterdir()])


def 생성(인자):
    경로 = _경로값(인자, "파일:생성")
    경로.touch()
    return None


기능들 = {
    "읽기": 읽기,
    "쓰기": 쓰기,
    "추가": 추가,
    "존재": 존재,
    "삭제": 삭제,
    "목록": 목록,
    "생성": 생성,
}


def 파일(args):
    기능 = args.get("기능")
    인자 = args.get("인자", [])

    if 기능 not in 기능들:
        raise Exception(f"지원하지 않는 파일 기능입니다. ({기능})")

    return 기능들[기능](인자)


STDLIB = {
    "파일": 파일,
}
