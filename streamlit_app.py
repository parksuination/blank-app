import os
import sys
from typing import Any, Dict, List, Optional

import requests
import streamlit as st
from dotenv import load_dotenv


# Load environment variables from .env if present (for local development)
load_dotenv()

API_ENDPOINT = "https://www.googleapis.com/youtube/v3/videos"


def humanize_int(n: Optional[str]) -> str:
    try:
        i = int(n) if n is not None else 0
    except (TypeError, ValueError):
        i = 0
    # Korean style short units for readability (approximation)
    if i >= 100_000_000:
        return f"{i/100_000_000:.1f}억회"
    if i >= 10_000:
        return f"{i/10_000:.1f}만회"
    return f"{i:,}회"


def get_config(key: str, default: Optional[str] = None) -> Optional[str]:
    """Fetch configuration from Streamlit secrets first, then environment variables.

    This allows cloud deployment via `.streamlit/secrets.toml` while retaining
    local development via `.env`.
    """
    # st.secrets behaves like a dict; guard in case secrets are not set
    try:
        if key in st.secrets:
            val = st.secrets.get(key)
            if val is not None and val != "":
                return str(val)
    except Exception:
        pass
    # Fallback to environment variable
    val = os.getenv(key)
    if val is not None and val != "":
        return val
    return default


@st.cache_data(show_spinner=True)
def fetch_trending(api_key: str, region_code: str = "KR", max_results: int = 30) -> List[Dict[str, Any]]:
    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": region_code,
        "maxResults": max(1, min(max_results, 50)),  # API allows up to 50
        "key": api_key,
    }
    resp = requests.get(API_ENDPOINT, params=params, timeout=15)
    # Basic HTTP error handling
    if not resp.ok:
        try:
            problem = resp.json()
        except Exception:
            problem = {"error": {"message": resp.text}}
        raise RuntimeError(f"YouTube API HTTP {resp.status_code}: {problem}")

    data = resp.json()
    if "items" not in data:
        raise RuntimeError("Unexpected API response: missing 'items'")

    return data.get("items", [])


def main() -> None:
    st.set_page_config(page_title="YouTube Trending (KR)", layout="wide")
    st.title("유튜브 인기 동영상")
    st.caption("간단한 YouTube API로 가져온 실시간 인기 동영상 목록")

    # Controls (prefer secrets -> env)
    default_region = (get_config("REGION_CODE", "KR") or "KR").upper()[:2]
    default_max_str = get_config("MAX_RESULTS", "30") or "30"
    try:
        default_max = int(default_max_str)
    except ValueError:
        default_max = 30

    with st.sidebar:
        st.header("설정")
        region_code = st.text_input("지역 코드 (ISO 3166-1 alpha-2)", value=default_region, help="예: KR, US, JP 등")
        max_results = st.slider("가져올 개수", min_value=1, max_value=50, value=max(1, min(default_max, 50)))
        refresh = st.button("🔄 새로고침", help="캐시를 비우고 다시 불러옵니다")

    if refresh:
        # Clear all cached data for this session and rerun
        st.cache_data.clear()
        st.experimental_rerun()

    api_key = get_config("YOUTUBE_API_KEY")
    if not api_key:
        st.error(
            "API 키를 찾을 수 없습니다. 로컬 개발 시 프로젝트 루트의 .env 또는 클라우드 배포 시 .streamlit/secrets.toml에 YOUTUBE_API_KEY를 설정하세요.\n"
            "예: YOUTUBE_API_KEY=YOUR_KEY_HERE"
        )
        with st.expander("도움말: API 키 설정 방법"):
            st.markdown(
                "- 로컬: 프로젝트 루트에 `.env` 파일을 만들고 다음 내용을 넣으세요.\n\n"
                "  `YOUTUBE_API_KEY=YOUR_YOUTUBE_DATA_API_KEY`\n\n"
                "- 배포(Streamlit Cloud 등): `.streamlit/secrets.toml`에 아래와 같이 설정하세요.\n\n"
                "  ```toml\nYOUTUBE_API_KEY = \"YOUR_YOUTUBE_DATA_API_KEY\"\nREGION_CODE = \"KR\"\nMAX_RESULTS = \"30\"\n  ```"
            )
        return

    # Fetch data
    try:
        items = fetch_trending(api_key=api_key, region_code=region_code or "KR", max_results=max_results)
    except requests.Timeout:
        st.error("요청 시간이 초과되었습니다. 네트워크 상태를 확인하고 다시 시도하세요.")
        return
    except requests.RequestException as e:
        st.error(f"네트워크 오류가 발생했습니다: {e}")
        return
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        return

    if not items:
        st.info("표시할 동영상이 없습니다.")
        return

    st.subheader(f"인기 동영상 Top {len(items)} ({region_code.upper()})")

    # Display list
    for idx, v in enumerate(items, start=1):
        vid = v.get("id")
        sn = v.get("snippet", {})
        stc = v.get("statistics", {})
        title = sn.get("title", "제목 없음")
        channel = sn.get("channelTitle", "채널 정보 없음")
        thumb = (
            (sn.get("thumbnails", {}) or {}).get("medium", {}) or {}
        ).get("url") or ((sn.get("thumbnails", {}) or {}).get("high", {}) or {}).get("url")
        views = humanize_int(stc.get("viewCount"))
        video_url = f"https://www.youtube.com/watch?v={vid}" if vid else None

        row = st.container()
        with row:
            cols = st.columns([1, 4])
            with cols[0]:
                if thumb:
                    st.image(thumb, use_container_width=True)
                else:
                    st.write(":grey_background[썸네일 없음]")
            with cols[1]:
                if video_url:
                    st.markdown(f"**{idx}. [ {title} ]({video_url})**")
                else:
                    st.markdown(f"**{idx}. {title}**")
                st.write(f"채널: {channel}")
                st.write(f"조회수: {views}")
        st.divider()

    st.caption("데이터 출처: YouTube Data API v3 · 이 앱은 학습/데모 목적입니다.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Fallback error catcher to ensure Streamlit shows a friendly message
        st.error(f"예상치 못한 오류가 발생했습니다: {e}")
        raise
