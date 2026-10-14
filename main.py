import html as html_lib
import json
import random
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import streamlit as st
import streamlit.components.v1 as components


# ============================================================
# 기본 설정
# ============================================================
st.set_page_config(
    page_title="MBTI 단짝 포켓몬 찾기",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API_BASE = "https://pokeapi.co/api/v2"
SPRITE_BASE = (
    "https://raw.githubusercontent.com/PokeAPI/sprites/"
    "master/sprites/pokemon"
)

MBTI_TYPES = [
    "INTJ", "INTP", "ENTJ", "ENTP",
    "INFJ", "INFP", "ENFJ", "ENFP",
    "ISTJ", "ISFJ", "ESTJ", "ESFJ",
    "ISTP", "ISFP", "ESTP", "ESFP",
]

# MBTI 설명과 궁합은 재미를 위한 설정입니다.
MBTI_PROFILE = {
    "INTJ": {
        "title": "전략가",
        "strength": "분석적이고 계획적인",
        "support": "큰 그림을 보고 차근차근 해결하는 점",
        "match": "ENFP",
        "match_desc": "계획적인 면과 자유로운 아이디어가 서로를 보완해요.",
    },
    "INTP": {
        "title": "탐구자",
        "strength": "호기심이 많고 논리적인",
        "support": "새로운 원리를 발견하고 깊이 탐구하는 점",
        "match": "ENTJ",
        "match_desc": "깊이 있는 생각을 실제 계획과 행동으로 발전시켜요.",
    },
    "ENTJ": {
        "title": "리더",
        "strength": "목표를 향해 적극적으로 나아가는",
        "support": "결정이 필요할 때 용기 있게 움직이는 점",
        "match": "INTP",
        "match_desc": "실행력과 분석력이 만나 더 좋은 해결책을 만들어요.",
    },
    "ENTP": {
        "title": "아이디어 뱅크",
        "strength": "재치 있고 새로운 시도를 즐기는",
        "support": "익숙한 것에서도 색다른 가능성을 찾아내는 점",
        "match": "INFJ",
        "match_desc": "기발한 발상과 깊은 통찰이 멋지게 어울려요.",
    },
    "INFJ": {
        "title": "통찰가",
        "strength": "신중하고 마음을 세심하게 살피는",
        "support": "소중한 가치와 사람을 진심으로 아끼는 점",
        "match": "ENTP",
        "match_desc": "신중함과 새로운 시각이 만나 생각의 폭이 넓어져요.",
    },
    "INFP": {
        "title": "몽상가",
        "strength": "상상력이 풍부하고 진솔한",
        "support": "자신만의 감성과 중요한 마음을 지키는 점",
        "match": "ENFJ",
        "match_desc": "섬세한 감성과 따뜻한 응원이 서로에게 힘이 돼요.",
    },
    "ENFJ": {
        "title": "따뜻한 조력자",
        "strength": "다정하고 다른 사람을 잘 응원하는",
        "support": "주변의 장점을 발견하고 함께 성장하는 점",
        "match": "INFP",
        "match_desc": "따뜻한 배려와 진솔한 마음이 자연스럽게 이어져요.",
    },
    "ENFP": {
        "title": "열정적인 탐험가",
        "strength": "호기심이 많고 아이디어가 풍부한",
        "support": "새로운 경험과 만남에서 즐거움을 발견하는 점",
        "match": "INTJ",
        "match_desc": "풍부한 아이디어와 꼼꼼한 계획이 좋은 팀을 만들어요.",
    },
    "ISTJ": {
        "title": "믿음직한 실천가",
        "strength": "꾸준하고 책임감이 강한",
        "support": "맡은 일을 성실하게 마무리하는 점",
        "match": "ESFP",
        "match_desc": "든든한 안정감과 즐거운 활기가 서로의 세계를 넓혀요.",
    },
    "ISFJ": {
        "title": "다정한 수호자",
        "strength": "세심하고 주변을 잘 챙기는",
        "support": "작은 배려로 주변을 편안하게 만드는 점",
        "match": "ESTP",
        "match_desc": "다정한 신중함과 과감한 도전이 균형을 이루어요.",
    },
    "ESTJ": {
        "title": "든든한 관리자",
        "strength": "실용적이고 실행력이 좋은",
        "support": "해야 할 일을 정리하고 책임 있게 행동하는 점",
        "match": "ISFP",
        "match_desc": "확실한 실행력과 부드러운 감성이 서로를 보완해요.",
    },
    "ESFJ": {
        "title": "사교적인 친구",
        "strength": "친근하고 배려심이 깊은",
        "support": "모두가 즐겁고 편안하도록 살피는 점",
        "match": "ISTP",
        "match_desc": "따뜻한 사교성과 침착한 문제 해결력이 조화를 이뤄요.",
    },
    "ISTP": {
        "title": "차분한 해결사",
        "strength": "침착하고 실용적인",
        "support": "직접 살펴보고 자신만의 방법으로 문제를 푸는 점",
        "match": "ESFJ",
        "match_desc": "침착한 실용성과 세심한 배려가 서로에게 도움이 돼요.",
    },
    "ISFP": {
        "title": "감성적인 예술가",
        "strength": "감각적이고 부드러운",
        "support": "자신만의 취향과 아름다운 순간을 소중히 여기는 점",
        "match": "ESTJ",
        "match_desc": "자유로운 감각과 명확한 방향성이 서로를 보완해요.",
    },
    "ESTP": {
        "title": "대담한 도전자",
        "strength": "활동적이고 과감한",
        "support": "새로운 상황에 빠르게 적응하고 직접 도전하는 점",
        "match": "ISFJ",
        "match_desc": "과감한 도전과 세심한 준비가 든든한 조합을 만들어요.",
    },
    "ESFP": {
        "title": "즐거움의 중심",
        "strength": "밝고 활기찬",
        "support": "함께하는 순간에 즐거움을 더하는 점",
        "match": "ISTJ",
        "match_desc": "명랑한 활기와 차분한 안정감이 서로를 채워 줘요.",
    },
}

TYPE_KO = {
    "normal": "노말",
    "fighting": "격투",
    "flying": "비행",
    "poison": "독",
    "ground": "땅",
    "rock": "바위",
    "bug": "벌레",
    "ghost": "고스트",
    "steel": "강철",
    "fire": "불꽃",
    "water": "물",
    "grass": "풀",
    "electric": "전기",
    "psychic": "에스퍼",
    "ice": "얼음",
    "dragon": "드래곤",
    "dark": "악",
    "fairy": "페어리",
}

TYPE_VIBE = {
    "노말": "편안하고 꾸밈없는 매력",
    "격투": "씩씩하고 도전적인 에너지",
    "비행": "자유롭고 시원한 느낌",
    "독": "개성 있고 신비로운 분위기",
    "땅": "든든하고 안정적인 매력",
    "바위": "흔들리지 않는 단단함",
    "벌레": "작은 것도 놓치지 않는 끈기",
    "고스트": "상상력을 자극하는 독특함",
    "강철": "단단하고 믿음직한 느낌",
    "불꽃": "뜨거운 열정과 추진력",
    "물": "유연하게 적응하는 차분함",
    "풀": "차분한 성장과 생기",
    "전기": "톡톡 튀는 에너지와 빠른 반응",
    "에스퍼": "깊은 생각과 신비로운 통찰",
    "얼음": "차분하고 맑은 집중력",
    "드래곤": "커다란 꿈과 강한 존재감",
    "악": "틀에 얽매이지 않는 개성",
    "페어리": "다정하고 반짝이는 매력",
}

TYPE_COLORS = {
    "노말": "#e8dfca",
    "격투": "#f4b6a9",
    "비행": "#c8d8fa",
    "독": "#dec0ef",
    "땅": "#ead1a0",
    "바위": "#d8c8a7",
    "벌레": "#dce7a4",
    "고스트": "#c8c7eb",
    "강철": "#d5dce5",
    "불꽃": "#ffd0a8",
    "물": "#b9ddf9",
    "풀": "#c7e8bd",
    "전기": "#ffe88e",
    "에스퍼": "#ffc4d4",
    "얼음": "#c9edf2",
    "드래곤": "#c9c4fb",
    "악": "#d0c2bd",
    "페어리": "#f7d2e8",
}


# ============================================================
# 온라인 포켓몬 도감
# 한 번 불러온 데이터는 24시간 캐시에 보관합니다.
# ============================================================
def api_get(url: str) -> dict:
    request = Request(
        url,
        headers={
            "User-Agent": "MBTI-Pokemon-Friend-App/1.0",
            "Accept": "application/json",
        },
    )
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_pokemon_pool() -> list:
    # API에 등록된 포켓몬과 여러 폼의 후보 목록을 가져옵니다.
    data = api_get(f"{API_BASE}/pokemon?limit=20000&offset=0")
    pool = []

    for entry in data.get("results", []):
        try:
            pokemon_id = int(
                entry["url"].rstrip("/").split("/")[-1]
            )
        except (KeyError, ValueError, TypeError):
            continue

        pool.append({
            "id": pokemon_id,
            "slug": entry.get("name", "pokemon"),
        })

    pool.sort(key=lambda item: item["id"])

    if not pool:
        raise ValueError("도감 후보 목록이 비어 있습니다.")

    return pool


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_pokemon_detail(pokemon_id: int) -> dict:
    pokemon = api_get(f"{API_BASE}/pokemon/{pokemon_id}")

    species_url = pokemon.get("species", {}).get("url")

    if not species_url:
        raise ValueError("이 포켓몬의 도감 정보를 찾을 수 없습니다.")

    species = api_get(species_url)

    names = species.get("names", [])

    korean_name = next(
        (
            item.get("name")
            for item in names
            if item.get("language", {}).get("name") == "ko"
        ),
        None,
    )

    english_species_name = next(
        (
            item.get("name")
            for item in names
            if item.get("language", {}).get("name") == "en"
        ),
        species.get("name", "Unknown").replace("-", " ").title(),
    )

    species_slug = species.get("name", "")
    pokemon_slug = pokemon.get("name", "")

    if pokemon_slug == species_slug:
        english_name = english_species_name
    elif pokemon_slug.startswith(species_slug + "-"):
        suffix = (
            pokemon_slug[len(species_slug) + 1:]
            .replace("-", " ")
            .title()
        )
        english_name = f"{english_species_name} ({suffix})"
    else:
        english_name = pokemon_slug.replace("-", " ").title()

    korean_genus = next(
        (
            item.get("genus")
            for item in species.get("genera", [])
            if item.get("language", {}).get("name") == "ko"
        ),
        "포켓몬",
    )

    flavor = next(
        (
            item.get("flavor_text")
            for item in species.get("flavor_text_entries", [])
            if item.get("language", {}).get("name") == "ko"
            and item.get("flavor_text")
        ),
        None,
    )

    if not flavor:
        flavor = next(
            (
                item.get("flavor_text")
                for item in species.get("flavor_text_entries", [])
                if item.get("language", {}).get("name") == "en"
                and item.get("flavor_text")
            ),
            "도감에 등록된 특징을 확인해 보세요!",
        )

    flavor = re.sub(
        r"\s+",
        " ",
        flavor.replace("\f", " ")
        .replace("\n", " ")
        .replace("\r", " "),
    ).strip()

    type_names = [
        TYPE_KO.get(
            item.get("type", {}).get("name", ""),
            item.get("type", {}).get("name", "").title(),
        )
        for item in sorted(
            pokemon.get("types", []),
            key=lambda obj: obj.get("slot", 1),
        )
    ]

    if not type_names:
        type_names = ["미상"]

    sprites = pokemon.get("sprites", {})
    other = sprites.get("other", {}) or {}

    official = (
        other.get("official-artwork") or {}
    ).get("front_default")

    sprite = sprites.get("front_default")

    try:
        species_id = int(species.get("id", pokemon_id))
    except (TypeError, ValueError):
        species_id = pokemon_id

    fallback_sprite = (
        sprite or f"{SPRITE_BASE}/{species_id}.png"
    )

    image_url = official or fallback_sprite

    return {
        "id": pokemon_id,
        "species_id": species_id,
        "korean_name": (
            korean_name
            or species.get("name", "포켓몬")
            .replace("-", " ")
            .title()
        ),
        "english_name": english_name,
        "genus": korean_genus,
        "flavor": flavor,
        "types": type_names,
        "image_url": image_url,
        "fallback_url": fallback_sprite,
        "pokemon_slug": pokemon_slug,
    }


def choose_pokemon(pool: list, mbti: str, round_no: int) -> dict:
    """MBTI별로 다른 순서로 포켓몬을 선택합니다.

    다시 찾기를 누르면 다음 후보를 보여줍니다.
    후보는 특정 16마리로 고정하지 않고 API 도감 목록을 이용합니다.
    """
    candidates = list(pool)

    random.Random(
        f"mbti-pokemon-friend-v1-{mbti}"
    ).shuffle(candidates)

    return candidates[round_no % len(candidates)]


def make_reasons(mbti: str, pokemon: dict) -> tuple:
    profile = MBTI_PROFILE[mbti]
    main_type = pokemon["types"][0]
    vibe = TYPE_VIBE.get(main_type, "독특한 개성")
    flavor = pokemon["flavor"]

    if len(flavor) > 105:
        shortened = (
            flavor[:105].rsplit(" ", 1)[0].rstrip("., ") + "…"
        )
    else:
        shortened = flavor

    reason1 = (
        f"{profile['strength']} {mbti}의 매력과, "
        f"{main_type} 타입의 {vibe} 매력이 잘 어울려요."
    )

    reason2 = (
        f"도감 특징은 “{shortened}”예요. "
        f"{profile['support']}와 연결해 생각하면 "
        f"{pokemon['korean_name']}의 매력을 더 재미있게 발견할 수 있어요."
    )

    return reason1, reason2


# ============================================================
# 포켓몬 배경과 클릭 애니메이션
# HTML, CSS, JavaScript를 파이썬 파일 안에 포함합니다.
# ============================================================
def make_pokemon_scene(pokemon: dict) -> str:
    image_url = html_lib.escape(
        pokemon["image_url"], quote=True
    )
    fallback_url = html_lib.escape(
        pokemon["fallback_url"], quote=True
    )
    name = html_lib.escape(
        pokemon["korean_name"], quote=True
    )
    pose_seed = int(pokemon["id"]) % 5

    template = r'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  * { box-sizing: border-box; }
  html, body {
    margin: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Malgun Gothic", sans-serif;
    background: transparent;
  }
  .scene {
    position: relative;
    width: 100%;
    height: 355px;
    overflow: hidden;
    border: 1px solid rgba(231, 194, 112, .72);
    border-radius: 25px;
    background: linear-gradient(
      180deg, #ccecf7 0%, #fff4ce 66%, #e9f0bd 100%
    );
    cursor: pointer;
    user-select: none;
    isolation: isolate;
  }
  .sun {
    position: absolute;
    right: 28px;
    top: 24px;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: #ffe58c;
    box-shadow: 0 0 0 12px rgba(255,230,150,.25),
                0 0 28px rgba(255,222,105,.6);
  }
  .cloud {
    position: absolute;
    width: 90px;
    height: 27px;
    border-radius: 30px;
    background: rgba(255,255,255,.88);
    animation: cloud-drift 12s ease-in-out infinite alternate;
  }
  .cloud:before, .cloud:after {
    content: "";
    position: absolute;
    bottom: 5px;
    border-radius: 50%;
    background: inherit;
  }
  .cloud:before {
    width: 34px;
    height: 34px;
    left: 13px;
  }
  .cloud:after {
    width: 44px;
    height: 44px;
    left: 36px;
  }
  .cloud.one {
    left: 18px;
    top: 48px;
    transform: scale(.82);
  }
  .cloud.two {
    right: 92px;
    top: 86px;
    transform: scale(.6);
    animation-delay: -4s;
  }
  .hill {
    position: absolute;
    bottom: -59px;
    border-radius: 50% 50% 0 0;
  }
  .hill.back {
    width: 125%;
    height: 145px;
    left: -12%;
    background: #b8dca7;
    transform: rotate(-4deg);
  }
  .hill.front {
    width: 120%;
    height: 105px;
    left: -8%;
    bottom: -57px;
    background: #91c987;
    transform: rotate(4deg);
  }
  .flower {
    position: absolute;
    bottom: 28px;
    z-index: 2;
    font-size: 21px;
    animation: flower-sway 3s ease-in-out infinite;
  }
  .flower.f1 { left: 17px; }
  .flower.f2 {
    right: 18px;
    bottom: 42px;
    animation-delay: -.8s;
  }
  .flower.f3 {
    left: 48px;
    bottom: 10px;
    font-size: 16px;
    animation-delay: -1.5s;
  }
  .tiny-star {
    position: absolute;
    z-index: 2;
    font-size: 20px;
    animation: twinkle 2.2s ease-in-out infinite;
  }
  .tiny-star.s1 { top: 125px; left: 25px; }
  .tiny-star.s2 {
    top: 112px;
    right: 33px;
    animation-delay: -.8s;
  }
  .pokemon-figure {
    position: absolute;
    z-index: 4;
    inset: 26px 0 31px;
    display: flex;
    align-items: center;
    justify-content: center;
    transform-origin: 50% 80%;
    pointer-events: none;
  }
  .pokemon-img {
    display: block;
    width: min(76%, 270px);
    height: 245px;
    object-fit: contain;
    filter: drop-shadow(0 12px 6px rgba(88, 91, 47, .16));
    animation: idle-float 3s ease-in-out infinite;
    transform-origin: 50% 83%;
    -webkit-user-drag: none;
    pointer-events: none;
  }
  .click-hint {
    position: absolute;
    z-index: 8;
    left: 50%;
    bottom: 13px;
    transform: translateX(-50%);
    width: max-content;
    max-width: calc(100% - 20px);
    padding: 7px 13px;
    border-radius: 999px;
    background: rgba(255,255,255,.91);
    border: 1px solid #f3dba3;
    color: #805d21;
    font-size: 12px;
    font-weight: 800;
    box-shadow: 0 3px 10px rgba(98,77,35,.08);
    pointer-events: none;
  }
  .sparkle-layer {
    position: absolute;
    inset: 0;
    z-index: 7;
    overflow: hidden;
    pointer-events: none;
  }
  .sparkle {
    position: absolute;
    font-size: 22px;
    animation: sparkle-pop .8s ease-out forwards;
  }

  .scene.pose-0 .pokemon-img {
    animation: pose-hop .85s cubic-bezier(.25,.8,.3,1) 1;
  }
  .scene.pose-1 .pokemon-img {
    animation: pose-spin .9s ease-in-out 1;
  }
  .scene.pose-2 .pokemon-img {
    animation: pose-wiggle .85s ease-in-out 1;
  }
  .scene.pose-3 .pokemon-img {
    animation: pose-dash .75s ease-in-out 1;
  }
  .scene.pose-4 .pokemon-img {
    animation: pose-flip .95s ease-in-out 1;
  }

  @keyframes idle-float {
    0%,100% { transform: translateY(1px) rotate(-1deg); }
    50% { transform: translateY(-9px) rotate(1.5deg); }
  }
  @keyframes cloud-drift {
    from { margin-left: -3px; }
    to { margin-left: 18px; }
  }
  @keyframes flower-sway {
    0%,100% { transform: rotate(-8deg); }
    50% { transform: rotate(8deg); }
  }
  @keyframes twinkle {
    0%,100% { opacity: .55; transform: scale(.85) rotate(-8deg); }
    50% { opacity: 1; transform: scale(1.18) rotate(8deg); }
  }
  @keyframes pose-hop {
    0%,100% { transform: translateY(0) rotate(0) scale(1); }
    30% { transform: translateY(-42px) rotate(-9deg) scale(1.04); }
    60% { transform: translateY(0) rotate(8deg) scale(.98); }
  }
  @keyframes pose-spin {
    0% { transform: rotate(0) scale(1); }
    45% { transform: rotate(190deg) scale(.82); }
    100% { transform: rotate(360deg) scale(1); }
  }
  @keyframes pose-wiggle {
    0%,100% { transform: rotate(0); }
    20% { transform: rotate(-12deg) translateX(-8px); }
    45% { transform: rotate(12deg) translateX(8px); }
    70% { transform: rotate(-7deg); }
  }
  @keyframes pose-dash {
    0%,100% { transform: translateX(0) skewX(0); }
    25% { transform: translateX(-32px) skewX(-7deg); }
    60% { transform: translateX(26px) skewX(7deg); }
  }
  @keyframes pose-flip {
    0%,100% { transform: translateY(0) rotateY(0) scale(1); }
    35% { transform: translateY(-18px) rotateY(100deg) scale(1.05); }
    70% { transform: translateY(0) rotateY(200deg) scale(.97); }
  }
  @keyframes sparkle-pop {
    from {
      transform: translateY(9px) scale(.3) rotate(0);
      opacity: 0;
    }
    20% { opacity: 1; }
    to {
      transform: translateY(-40px) scale(1.3) rotate(25deg);
      opacity: 0;
    }
  }
  @media (max-width: 430px) {
    .scene { height: 325px; }
    .pokemon-img { height: 220px; width: 80%; }
    .sun { width: 46px; height: 46px; right: 20px; }
  }
  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      animation-duration: .01ms !important;
      animation-iteration-count: 1 !important;
    }
  }
</style>
</head>
<body>
<div
  class="scene"
  id="scene"
  role="button"
  tabindex="0"
  aria-label="포켓몬을 클릭해서 포즈 애니메이션 실행"
>
  <div class="sun"></div>
  <div class="cloud one"></div>
  <div class="cloud two"></div>
  <div class="tiny-star s1">✦</div>
  <div class="tiny-star s2">✧</div>
  <div class="hill back"></div>
  <div class="hill front"></div>
  <div class="flower f1">🌼</div>
  <div class="flower f2">🌷</div>
  <div class="flower f3">🌱</div>

  <div class="pokemon-figure">
    <img
      id="pokemonImage"
      class="pokemon-img"
      src="__IMAGE_URL__"
      alt="__POKEMON_NAME__"
      draggable="false"
      onerror="this.onerror=null;this.src='__FALLBACK_URL__';"
    >
  </div>

  <div class="sparkle-layer" id="sparkleLayer"></div>
  <div class="click-hint">
    👆 포켓몬을 눌러 고유 포즈를 확인해 보세요!
  </div>
</div>

<script>
  const scene = document.getElementById('scene');
  const sparkleLayer = document.getElementById('sparkleLayer');
  const poseClasses = [
    'pose-0', 'pose-1', 'pose-2', 'pose-3', 'pose-4'
  ];
  const sparkleSymbols = [
    '✨', '⭐', '💛', '✦', '🌟', '⚡'
  ];
  const poseSeed = Number('__POSE_SEED__');
  let clickCount = 0;

  function doPose() {
    scene.classList.remove(...poseClasses);
    void scene.offsetWidth;

    const pose = (poseSeed + clickCount) % poseClasses.length;
    scene.classList.add(poseClasses[pose]);
    clickCount += 1;

    for (let i = 0; i < 9; i += 1) {
      const spark = document.createElement('span');
      spark.className = 'sparkle';
      spark.textContent =
        sparkleSymbols[
          Math.floor(Math.random() * sparkleSymbols.length)
        ];

      spark.style.left = (15 + Math.random() * 70) + '%';
      spark.style.top = (20 + Math.random() * 52) + '%';
      spark.style.animationDelay = (Math.random() * .15) + 's';
      sparkleLayer.appendChild(spark);

      window.setTimeout(() => spark.remove(), 1000);
    }
  }

  scene.addEventListener('click', doPose);

  scene.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      doPose();
    }
  });
</script>
</body>
</html>'''

    return (
        template.replace("__IMAGE_URL__", image_url)
        .replace("__FALLBACK_URL__", fallback_url)
        .replace("__POKEMON_NAME__", name)
        .replace("__POSE_SEED__", str(pose_seed))
    )


# ============================================================
# 메인 페이지 디자인
# ============================================================
st.markdown(
    """
    <style>
      :root { color-scheme: light; }

      .stApp {
        background:
          radial-gradient(
            circle at 8% 8%,
            rgba(255, 220, 130, .28),
            transparent 24%
          ),
          radial-gradient(
            circle at 92% 23%,
            rgba(255, 235, 178, .36),
            transparent 25%
          ),
          linear-gradient(
            180deg,
            #fff9e9 0%,
            #fffdf6 58%,
            #fff5da 100%
          );
        color: #493b2b;
      }

      [data-testid="stHeader"] {
        background: rgba(255, 249, 233, .72);
      }

      .block-container {
        max-width: 1120px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
      }

      h1, h2, h3 {
        color: #493b2b !important;
        letter-spacing: -0.035em;
      }

      .hero {
        text-align: center;
        padding: 12px 0 22px;
      }

      .hero-pill {
        display: inline-block;
        padding: 7px 15px;
        border-radius: 999px;
        border: 1px solid #f1d38e;
        background: #fff0c5;
        color: #8d641f;
        font-size: 13px;
        font-weight: 800;
        letter-spacing: 1px;
      }

      .hero h1 {
        margin: 13px 0 8px;
        font-size: clamp(2.1rem, 5vw, 3.4rem);
        line-height: 1.2;
        font-weight: 900;
      }

      .hero h1 span {
        color: #d99421;
      }

      .hero p {
        margin: 0;
        color: #81725d;
        font-size: 1.05rem;
        line-height: 1.75;
      }

      .hero-decoration {
        font-size: 1.7rem;
        letter-spacing: .3rem;
        margin-top: 10px;
      }

      .section-label {
        margin: 14px 0 5px;
        text-align: center;
        font-size: 1.55rem;
        font-weight: 900;
        color: #493b2b;
      }

      .section-subtitle {
        margin: 0 0 18px;
        text-align: center;
        color: #82745e;
      }

      .stButton > button {
        min-height: 3.15rem;
        border-radius: 15px;
        border: 1px solid #eadbbd;
        background: rgba(255,255,255,.86);
        color: #5b472b;
        font-size: 1.05rem;
        font-weight: 850;
        box-shadow: 0 4px 10px rgba(120, 88, 34, .035);
        transition:
          transform .15s ease,
          box-shadow .15s ease,
          border-color .15s ease;
      }

      .stButton > button:hover {
        border-color: #e9bd50;
        color: #684915;
        background: #fff3cd;
        transform: translateY(-2px);
        box-shadow: 0 7px 15px rgba(120,88,34,.09);
      }

      .stButton > button[kind="primary"] {
        background: #ffda70;
        color: #573d13;
        border-color: #efc04e;
      }

      .result-ribbon {
        margin: 12px 0 18px;
        padding: 14px 18px;
        text-align: center;
        border-radius: 18px;
        background: linear-gradient(
          90deg,
          #fff0bd,
          #fff8df,
          #fff0bd
        );
        border: 1px solid #f0d78f;
        color: #80571c;
        font-size: 1.1rem;
        font-weight: 850;
      }

      .result-name {
        margin: 0 0 7px;
        font-size: clamp(1.8rem, 3vw, 2.5rem);
        font-weight: 900;
        line-height: 1.2;
      }

      .result-name small {
        display: block;
        margin-top: 6px;
        color: #83745e;
        font-size: 1rem;
        font-weight: 650;
        letter-spacing: 0;
      }

      .mini-heading {
        margin: 13px 0 8px;
        font-size: 1.1rem;
        font-weight: 900;
        color: #5a4427;
      }

      .type-chips {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 8px 0 15px;
      }

      .type-chip {
        display: inline-block;
        padding: 6px 13px;
        border-radius: 999px;
        color: #554532;
        font-weight: 850;
        font-size: .93rem;
        border: 1px solid rgba(113,89,51,.12);
      }

      .info-card {
        padding: 17px 19px;
        margin: 10px 0;
        border-radius: 18px;
        border: 1px solid #f0e0bf;
        background: rgba(255,255,255,.82);
        line-height: 1.8;
        color: #5d4d38;
      }

      .reason-card {
        padding: 17px 19px;
        margin: 10px 0;
        border-radius: 18px;
        border: 1px solid #f2dfb0;
        background: #fff8e7;
        line-height: 1.85;
        color: #57452d;
      }

      .compat-card {
        padding: 16px 18px;
        border-radius: 18px;
        background: #fff0c7;
        border: 1px solid #efd48f;
        margin: 15px 0;
        line-height: 1.7;
      }

      .compat-card strong {
        font-size: 1.12rem;
        color: #9a691b;
      }

      .tiny-note {
        color: #887b66;
        font-size: .86rem;
        line-height: 1.7;
      }

      div[data-testid="stAlert"] {
        border-radius: 14px;
      }

      @media (max-width: 640px) {
        .block-container {
          padding: .8rem .8rem 2rem;
        }

        .hero p {
          font-size: .95rem;
        }

        .section-label {
          font-size: 1.3rem;
        }

        .stButton > button {
          min-height: 2.85rem;
          font-size: .98rem;
        }
      }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 페이지 상단
# ============================================================
st.markdown(
    """
    <div class="hero">
      <div class="hero-pill">🌟 MY MBTI × POKÉMON 🌟</div>
      <h1>나의 <span>단짝 포켓몬</span> 찾기!</h1>
      <p>
        나의 MBTI를 고르면 포켓몬 도감 속에서 단짝을 찾아드려요.<br>
        마음에 드는 포켓몬 그림을 클릭하면 특별 포즈도 볼 수 있어요!
      </p>
      <div class="hero-decoration">🌼 ⚡ 🍯 🌿</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 세션 상태
# ============================================================
if "selected_mbti" not in st.session_state:
    st.session_state.selected_mbti = None

if "partner_round" not in st.session_state:
    st.session_state.partner_round = 0

if "celebrate" not in st.session_state:
    st.session_state.celebrate = False


# ============================================================
# 온라인 도감 불러오기
# ============================================================
try:
    with st.spinner("🌍 포켓몬 도감을 불러오는 중이에요..."):
        pokemon_pool = fetch_pokemon_pool()

except (
    HTTPError,
    URLError,
    TimeoutError,
    ValueError,
    json.JSONDecodeError,
) as error:
    st.error(
        "포켓몬 도감을 불러오지 못했어요. "
        "인터넷 연결을 확인한 뒤 페이지를 새로고침해 주세요."
    )
    st.caption(
        "이 앱은 온라인 도감과 이미지 주소를 사용하므로 "
        "실행 중 인터넷 연결이 필요합니다."
    )
    st.stop()

except Exception:
    st.error("도감에 연결할 수 없어요. 잠시 후 다시 시도해 주세요.")
    st.stop()


# ============================================================
# MBTI 선택 버튼 16개
# ============================================================
st.markdown(
    '<div class="section-label">내 MBTI는 무엇일까요?</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-subtitle">'
    '아래 16가지 유형 중 하나를 선택해 주세요 ✨'
    '</div>',
    unsafe_allow_html=True,
)

for row_start in range(0, len(MBTI_TYPES), 4):
    cols = st.columns(4, gap="small")

    for col, mbti in zip(
        cols,
        MBTI_TYPES[row_start:row_start + 4],
    ):
        with col:
            button_type = (
                "primary"
                if st.session_state.selected_mbti == mbti
                else "secondary"
            )

            if st.button(
                mbti,
                key=f"mbti_{mbti}",
                use_container_width=True,
                type=button_type,
            ):
                st.session_state.selected_mbti = mbti
                st.session_state.partner_round = 0
                st.session_state.celebrate = True

st.markdown(
    f'<p class="tiny-note" style="text-align:center;margin-top:12px;">'
    f'도감 후보 {len(pokemon_pool):,}개를 사용해요. '
    f'기본 포켓몬과 도감에 등록된 여러 폼이 포함됩니다.'
    f'</p>',
    unsafe_allow_html=True,
)


# ============================================================
# 포켓몬 결과
# ============================================================
if st.session_state.selected_mbti:
    selected_mbti = st.session_state.selected_mbti
    profile = MBTI_PROFILE[selected_mbti]

    candidate = choose_pokemon(
        pokemon_pool,
        selected_mbti,
        st.session_state.partner_round,
    )

    with st.spinner("💛 당신의 단짝 포켓몬을 만나러 가는 중..."):
        try:
            pokemon = fetch_pokemon_detail(candidate["id"])

        except Exception:
            # 선택된 후보가 실패하면 다음 후보를 시도합니다.
            fallback_candidate = choose_pokemon(
                pokemon_pool,
                selected_mbti,
                st.session_state.partner_round + 1,
            )

            try:
                pokemon = fetch_pokemon_detail(
                    fallback_candidate["id"]
                )

            except Exception:
                st.error(
                    "이 포켓몬의 상세 정보를 불러오지 못했어요. "
                    "‘다른 단짝 찾기’를 눌러 다시 시도해 주세요."
                )
                st.stop()

    # 단짝이 나타나면 축하 효과 실행
    if st.session_state.celebrate:
        st.balloons()
        st.session_state.celebrate = False

    st.markdown(
        f'<div class="result-ribbon">'
        f'🎉 축하해요! {selected_mbti} · '
        f'{profile["title"]}의 단짝 포켓몬을 찾았어요! 🎉'
        f'</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([1, 1.08], gap="large")

    with left:
        # HTML 안에 CSS와 JavaScript가 함께 들어갑니다.
        components.html(
            make_pokemon_scene(pokemon),
            height=370,
            scrolling=False,
        )

        st.caption(
            "포켓몬 그림을 마우스로 클릭하거나 키보드에서 "
            "Enter를 눌러 보세요. 점프·회전·흔들기 등 포즈가 바뀝니다!"
        )

    with right:
        escaped_ko = html_lib.escape(pokemon["korean_name"])
        escaped_en = html_lib.escape(pokemon["english_name"])

        st.markdown(
            f'<div class="result-name">'
            f'{escaped_ko}'
            f'<small>({escaped_en})</small>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # 타입 표시
        st.markdown(
            '<div class="mini-heading">🏷️ 타입</div>',
            unsafe_allow_html=True,
        )

        chips = []

        for type_name in pokemon["types"]:
            color = TYPE_COLORS.get(type_name, "#f5e8ca")

            chips.append(
                f'<span class="type-chip" style="background:{color};">'
                f'{html_lib.escape(type_name)}'
                f'</span>'
            )

        st.markdown(
            f'<div class="type-chips">{"".join(chips)}</div>',
            unsafe_allow_html=True,
        )

        # 포켓몬 특징
        st.markdown(
            '<div class="mini-heading">📖 포켓몬 특징</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="info-card">'
            f'<strong>{html_lib.escape(pokemon["genus"])}</strong><br>'
            f'{html_lib.escape(pokemon["flavor"])}'
            f'</div>',
            unsafe_allow_html=True,
        )

        # MBTI와 포켓몬이 어울리는 이유
        reason1, reason2 = make_reasons(
            selected_mbti,
            pokemon,
        )

        st.markdown(
            '<div class="mini-heading">'
            '💛 우리 둘이 잘 어울리는 이유'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="reason-card">'
            f'{html_lib.escape(reason1)}<br><br>'
            f'{html_lib.escape(reason2)}'
            f'</div>',
            unsafe_allow_html=True,
        )

        # 궁합 MBTI
        match_type = profile["match"]
        match_desc = profile["match_desc"]

        st.markdown(
            f'<div class="compat-card">'
            f'🤝 <strong>잘 맞는 다른 MBTI: {match_type}</strong><br>'
            f'{html_lib.escape(match_desc)}'
            f'</div>',
            unsafe_allow_html=True,
        )

    # 다음 포켓몬 찾기
    if st.button(
        "🎲 다른 단짝 포켓몬 만나기",
        type="primary",
        use_container_width=True,
        key="reroll_pokemon",
    ):
        st.session_state.partner_round += 1
        st.session_state.celebrate = True
        st.rerun()

else:
    # 아직 MBTI를 선택하지 않은 첫 화면
    st.markdown(
        """
        <div class="info-card" style="text-align:center;margin-top:22px;">
          <div style="font-size:2.2rem;">🥚 ✨ 🌈</div>
          <strong>어떤 포켓몬이 나올까요?</strong><br>
          MBTI 버튼을 눌러 나만의 단짝을 찾아보세요!<br>
          <span class="tiny-note">
            선택할 때마다 축하 효과가 나타나고,
            포켓몬 그림을 클릭하면 여러 포즈로 움직여요.
          </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# 하단 안내
# ============================================================
st.markdown(
    """
    <div class="tiny-note" style="text-align:center;margin-top:24px;">
      포켓몬 이름·타입·도감 설명·이미지는 PokéAPI를 통해 불러옵니다.<br>
      MBTI 매칭과 궁합 설명은 재미를 위한 설정이며
      과학적인 성격 진단은 아닙니다.
    </div>
    """,
    unsafe_allow_html=True,
)
