# 랜덤 라이브러리


def 무작위(인자):
    import random

    if len(인자) != 2:
        raise Exception("랜덤:무작위 함수는 시작값과 끝값 2개를 받아야 합니다.")

    시작, 끝 = 인자
    if not isinstance(시작, int) or not isinstance(끝, int):
        raise Exception("랜덤:무작위 함수의 인자는 정수여야 합니다.")

    return random.randint(시작, 끝)


def 선택(인자):
    import random

    if len(인자) != 1:
        raise Exception("랜덤:선택 함수는 목록 1개를 받아야 합니다.")

    대상 = 인자[0]
    if not isinstance(대상, list):
        raise Exception("랜덤:선택 함수는 목록에만 사용할 수 있습니다.")
    if not 대상:
        raise Exception("빈 목록에서는 랜덤:선택을 사용할 수 없습니다.")

    return random.choice(대상)


def 섞기(인자):
    import random

    if len(인자) != 1:
        raise Exception("랜덤:섞기 함수는 목록 1개를 받아야 합니다.")

    대상 = 인자[0]
    if not isinstance(대상, list):
        raise Exception("랜덤:섞기 함수는 목록에만 사용할 수 있습니다.")

    결과 = list(대상)
    random.shuffle(결과)
    return 결과


def 실수(인자):
    import random

    if 인자:
        raise Exception("랜덤:실수 함수는 인자를 받지 않습니다.")

    return random.random()


기능들 = {
    "무작위": 무작위,
    "선택": 선택,
    "섞기": 섞기,
    "실수": 실수,
}


def 랜덤(args):
    기능 = args.get("기능")
    인자 = args.get("인자", [])

    if 기능 not in 기능들:
        raise Exception(f"지원하지 않는 랜덤 기능입니다. ({기능})")

    return 기능들[기능](인자)


STDLIB = {
    "랜덤": 랜덤,
}
