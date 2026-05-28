# 시간 라이브러리


def 현재(인자):
    from datetime import datetime

    if 인자:
        raise Exception("시간:현재 함수는 인자를 받지 않습니다.")

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def 대기(인자):
    import time

    if len(인자) != 1:
        raise Exception("시간:대기 함수는 초 1개를 받아야 합니다.")

    초 = 인자[0]
    if not isinstance(초, (int, float)) or isinstance(초, bool):
        raise Exception("시간:대기 함수의 인자는 숫자여야 합니다.")
    if 초 < 0:
        raise Exception("시간:대기 함수의 초는 0 이상이어야 합니다.")

    time.sleep(초)
    return None


def 시간값(인자):
    from datetime import datetime

    if 인자:
        raise Exception("시간:시간 함수는 인자를 받지 않습니다.")

    return datetime.now().hour


def 분(인자):
    from datetime import datetime

    if 인자:
        raise Exception("시간:분 함수는 인자를 받지 않습니다.")

    return datetime.now().minute


def 초(인자):
    from datetime import datetime

    if 인자:
        raise Exception("시간:초 함수는 인자를 받지 않습니다.")

    return datetime.now().second


def 타임스탬프(인자):
    import time

    if 인자:
        raise Exception("시간:타임스탬프 함수는 인자를 받지 않습니다.")

    return int(time.time())


기능들 = {
    "현재": 현재,
    "대기": 대기,
    "시간": 시간값,
    "분": 분,
    "초": 초,
    "타임스탬프": 타임스탬프,
}


def 시간(args):
    기능 = args.get("기능")
    인자 = args.get("인자", [])

    if 기능 not in 기능들:
        raise Exception(f"지원하지 않는 시간 기능입니다. ({기능})")

    return 기능들[기능](인자)


STDLIB = {
    "시간": 시간,
}
