"""
Data analysis module for Xiaohongshu notes.
Provides: basic statistics, word frequency, time trends, and sentiment analysis.
"""
import re
import logging
from collections import Counter
from datetime import datetime

logger = logging.getLogger(__name__)

# Chinese stop words
STOP_WORDS = set(
    "的 了 在 是 我 有 和 就 不 人 都 一 一个 上 也 很 到 说 要 去 你 会 着 "
    "没有 看 好 自己 这 他 她 它 们 那 被 从 把 让 用 对 但 又 还 而 且 "
    "吗 吧 呢 啊 哦 哈 呀 嗯 么 啦 可以 这个 什么 怎么 如何 为什么 因为 所以 "
    "如果 虽然 但是 不过 然后 或者 以及 其实 比较 非常 真的 感觉 觉得 应该 可能 已经 "
    "https com www xhslink 小红书 还会 就是 的话 一些 什么 怎么 样 那些 这些 "
    "大家 知道 需要 时候 现在 还是 已经 可以 没有 一个 自己 他们 我们 你们 "
    "分享 推荐 喜欢 收藏 关注 评论 转发 视频 图片 笔记 链接 原文 来源 作者 "
    "发布 举报 置顶 精选 回复 删除 编辑 更多 展开 收起 已赞 已收藏".split()
)


def _safe_int(value, default=0):
    """Safely convert a value to int."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def analyze_notes(notes_data: list) -> dict:
    """
    Analyze a list of note details.

    Args:
        notes_data: List of note detail dicts (as returned by /api/note/{id})

    Returns:
        Analysis result with stats, word_freq, time_distribution, sentiment, top_keywords
    """
    if not notes_data:
        return {
            "stats": {
                "total_notes": 0, "total_likes": 0, "total_favorites": 0,
                "total_comments": 0, "avg_likes": 0, "avg_favorites": 0, "avg_comments": 0,
            },
            "word_freq": [],
            "time_distribution": {"labels": [], "note_counts": [], "like_counts": []},
            "sentiment": {
                "positive_ratio": 0, "negative_ratio": 0, "neutral_ratio": 0,
                "score_distribution": {"positive": 0, "neutral": 0, "negative": 0},
            },
            "top_keywords": [],
        }

    all_text = ""
    time_data = []
    total_likes = 0
    total_favorites = 0
    total_comments = 0
    note_interact_data = []  # For top-N charts

    for note in notes_data:
        title = note.get("title", "") or ""
        desc = note.get("desc", "") or ""
        all_text += title + " " + desc + " "

        interact = note.get("interact_info", {})
        likes = _safe_int(interact.get("liked_count", "0"))
        favorites = _safe_int(interact.get("collected_count", "0"))
        comments = _safe_int(interact.get("comment_count", "0"))
        total_likes += likes
        total_favorites += favorites
        total_comments += comments

        ts = note.get("time", 0)
        if ts:
            time_data.append((ts, likes, favorites, comments))

        note_interact_data.append({
            "title": title[:30],
            "likes": likes,
            "favorites": favorites,
            "comments": comments,
        })

    n = len(notes_data)

    # ─── 1. Basic Statistics ────────────────────────────────
    stats = {
        "total_notes": n,
        "total_likes": total_likes,
        "total_favorites": total_favorites,
        "total_comments": total_comments,
        "avg_likes": round(total_likes / n, 1),
        "avg_favorites": round(total_favorites / n, 1),
        "avg_comments": round(total_comments / n, 1),
    }

    # ─── 2. Word Frequency (jieba) ──────────────────────────
    word_freq = []
    try:
        import jieba

        # Remove URLs and special characters
        clean_text = re.sub(r"https?://\S+", "", all_text)
        clean_text = re.sub(r"[^\u4e00-\u9fff\u3400-\u4dbfa-zA-Z0-9\s]", " ", clean_text)

        words = jieba.cut(clean_text)
        filtered = [
            w.strip().lower()
            for w in words
            if len(w.strip()) >= 2 and w.strip() not in STOP_WORDS and not w.strip().isdigit()
        ]
        word_freq = Counter(filtered).most_common(100)
    except ImportError:
        logger.warning("jieba not installed, skipping word frequency analysis")
        # Fallback: simple character-based frequency
        clean_text = re.sub(r"https?://\S+", "", all_text)
        clean_text = re.sub(r"[^\u4e00-\u9fff]", "", clean_text)
        # Extract 2-character combinations
        bigrams = [clean_text[i:i+2] for i in range(len(clean_text) - 1)]
        word_freq = Counter(bigrams).most_common(100)
    except Exception as e:
        logger.error(f"Word frequency analysis error: {e}")

    top_keywords = [{"word": w, "count": c} for w, c in word_freq[:20]]

    # ─── 3. Time Distribution ───────────────────────────────
    monthly = {}
    for ts, likes, favs, comms in time_data:
        try:
            dt = datetime.fromtimestamp(ts / 1000)
            month_key = f"{dt.year}-{dt.month:02d}"
            if month_key not in monthly:
                monthly[month_key] = {"notes": 0, "likes": 0, "favorites": 0, "comments": 0}
            monthly[month_key]["notes"] += 1
            monthly[month_key]["likes"] += likes
            monthly[month_key]["favorites"] += favs
            monthly[month_key]["comments"] += comms
        except Exception:
            pass

    sorted_months = sorted(monthly.keys())
    time_distribution = {
        "labels": sorted_months,
        "note_counts": [monthly[m]["notes"] for m in sorted_months],
        "like_counts": [monthly[m]["likes"] for m in sorted_months],
        "favorite_counts": [monthly[m]["favorites"] for m in sorted_months],
        "comment_counts": [monthly[m]["comments"] for m in sorted_months],
    }

    # ─── 4. Sentiment Analysis (snownlp) ────────────────────
    positive = 0
    negative = 0
    neutral = 0

    try:
        from snownlp import SnowNLP

        for note in notes_data:
            text = (note.get("title", "") or "") + " " + (note.get("desc", "") or "")
            text = text.strip()
            if not text:
                neutral += 1
                continue

            try:
                score = SnowNLP(text).sentiments  # 0~1, >0.5 tends positive
                if score > 0.6:
                    positive += 1
                elif score < 0.4:
                    negative += 1
                else:
                    neutral += 1
            except Exception:
                neutral += 1
    except ImportError:
        logger.warning("snownlp not installed, skipping sentiment analysis")
        neutral = n
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        neutral = n

    sentiment = {
        "positive_ratio": round(positive / n, 3) if n else 0,
        "negative_ratio": round(negative / n, 3) if n else 0,
        "neutral_ratio": round(neutral / n, 3) if n else 0,
        "score_distribution": {
            "positive": positive,
            "neutral": neutral,
            "negative": negative,
        },
    }

    # ─── 5. Top Notes by Interaction ────────────────────────
    top_notes = sorted(note_interact_data, key=lambda x: x["likes"], reverse=True)[:10]

    return {
        "stats": stats,
        "word_freq": [{"word": w, "count": c} for w, c in word_freq],
        "time_distribution": time_distribution,
        "sentiment": sentiment,
        "top_keywords": top_keywords,
        "top_notes": top_notes,
    }
