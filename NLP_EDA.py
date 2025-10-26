import os
import re
import pandas as pd
from collections import Counter, defaultdict

# ===== 설정 =====
# 분석할 엑셀 파일 경로 (app.py와 같은 폴더에 있다고 가정)
XLSX_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "youtube_videos_result.xlsx")


SHEETS = [
    "결혼기념일선물",
    "여자친구생일선물",
    "여자친구선물",
    "와이프생일선물",
    "프로포즈선물",
    "어머니생신선물",
]

# 불용어(간단 버전): 한국어/영어 혼합 (원하면 추가)
STOP_KO = {
    "그리고","그런","하지만","그러나","또는","또","또한","에서","으로","으로써","에게","에게는","까지","보다",
    "부터","에서부터","에서까지","보다도","보다가","하는","한다","했다","합니다","합니다요","합니다만",
    "이것","그것","저것","이건","그건","저건","이건요","저는","우리는","여러분","당신","너","너희",
    "오늘","이번","관련","소개","영상","유튜브","채널","링크","정보","제품","추천","사용","방법","리뷰",
    "정말","진짜","아주","매우","많이","조금","다소","등","및","등등","등이","같은","등의","때문","때문에",
    "대한","하는법","주의","참고","해주세요","합니다","합니다요","드립니다","드립니다요","감사","감사합니다",
}
STOP_EN = {
    "the","and","or","a","an","is","are","to","for","of","in","on","with","at","by","from","this","that","these","those",
    "it","its","as","be","was","were","will","can","you","your","we","our","they","their","i","me","my","mine",
    "video","channel","link","info","information","product","review","please","thanks","thank","official",
}
STOPWORDS = STOP_KO | STOP_EN

def clean_and_tokenize(text: str, keep_hash_prefix: bool = False):
    """
    텍스트에서 단어/해시태그를 추출해 토큰 리스트로 반환.
    - keep_hash_prefix=False: '#선물' -> '선물' 로 정규화(일반 단어와 합산)
    - keep_hash_prefix=True : '#선물' 을 '#선물' 그대로 카운트(일반 '선물'과는 별개)
    """
    if not isinstance(text, str):
        return []

    s = text.lower()

    # 1) URL 제거
    s = re.sub(r'https?://\S+|www\.\S+', ' ', s)

    # 2) 해시태그 먼저 추출 (한글/영문/숫자/언더스코어)
    hashtag_pattern = r'#([a-z0-9_\uac00-\ud7a3]+)'
    raw_tags = re.findall(hashtag_pattern, s)

    # 3) 해시태그 제거한 텍스트로 본문 토큰화 준비
    s_wo_tags = re.sub(r'#[a-z0-9_\uac00-\ud7a3]+', ' ', s)

    # 4) 멘션(@id)만 제거
    s_wo_tags = re.sub(r'@[a-z0-9_\uac00-\ud7a3]+', ' ', s_wo_tags)

    # 5) 한글/영문/숫자/언더스코어만 유지
    s_wo_tags = re.sub(r'[^a-z0-9_\uac00-\ud7a3]+', ' ', s_wo_tags)

    # 6) 본문 토큰
    body_tokens = [t for t in s_wo_tags.split() if len(t) >= 2 and t not in STOPWORDS]

    # 7) 해시태그 토큰 정규화 / 보존
    if keep_hash_prefix:
        tag_tokens = [f"#{t}" for t in raw_tags if len(t) >= 2 and t not in STOPWORDS]
    else:
        tag_tokens = [t for t in raw_tags if len(t) >= 2 and t not in STOPWORDS]

    # 8) 본문 토큰 + 해시태그 토큰 합치고 중복 제거 X (빈도 계산은 Counter가 함)
    return body_tokens + tag_tokens


def build_word_counts_per_sheet(xlsx_path: str, sheets: list[str], description_col: str = "Description"):
    per_sheet_counters: dict[str, Counter] = {}
    total_counter = Counter()

    # 각 시트별로 Description 열에서 토큰 카운트
    for sheet in sheets:
        try:
            df = pd.read_excel(xlsx_path, sheet_name=sheet)
        except Exception as e:
            raise RuntimeError(f"시트 '{sheet}' 읽기 실패: {e}")

        if description_col not in df.columns:
            # 열 이름이 다른 경우 대비: 대소문자 무시 탐색
            candidates = [c for c in df.columns if c.strip().lower() == description_col.lower()]
            if candidates:
                description_col = candidates[0]
            else:
                # 시트에 Description 없으면 빈 카운터로 처리
                per_sheet_counters[sheet] = Counter()
                continue

        cnt = Counter()
        for desc in df[description_col].dropna():
            tokens = clean_and_tokenize(str(desc))
            cnt.update(tokens)
            total_counter.update(tokens)

        per_sheet_counters[sheet] = cnt

    return per_sheet_counters, total_counter

def make_summary_dataframe(per_sheet_counters: dict[str, Counter], total_counter: Counter):
    # 모든 단어 집합
    all_words = set(total_counter.keys())
    for c in per_sheet_counters.values():
        all_words |= set(c.keys())

    # 표 생성 (total 기준 내림차순)
    rows = []
    for w in all_words:
        row = {"word": w, "total": total_counter.get(w, 0)}
        for sheet, cnt in per_sheet_counters.items():
            row[sheet] = cnt.get(w, 0)
        rows.append(row)

    df = pd.DataFrame(rows)
    if not df.empty:
        df.sort_values(by="total", ascending=False, inplace=True)
        df["rank"] = range(1, len(df) + 1)
        # 컬럼 순서: rank, word, total, 각 시트
        cols = ["rank", "word", "total"] + list(per_sheet_counters.keys())
        df = df[cols]
    return df

def write_summary_sheet(xlsx_path: str, summary_df: pd.DataFrame, sheet_name: str = "Export Summary"):
    mode = "a" if os.path.exists(xlsx_path) else "w"
    with pd.ExcelWriter(xlsx_path, engine="openpyxl", mode=mode, if_sheet_exists="replace") as writer:
        summary_df.to_excel(writer, sheet_name=sheet_name, index=False)

def main():
    if not os.path.exists(XLSX_PATH):
        raise FileNotFoundError(f"엑셀 파일이 없습니다: {XLSX_PATH}")

    per_sheet_counters, total_counter = build_word_counts_per_sheet(XLSX_PATH, SHEETS, description_col="Description")
    summary_df = make_summary_dataframe(per_sheet_counters, total_counter)

    write_summary_sheet(XLSX_PATH, summary_df, sheet_name="Export Summary")
    print(f"✅ 완료: '{XLSX_PATH}' 파일에 'Export Summary' 시트 생성/갱신")

if __name__ == "__main__":
    main()
