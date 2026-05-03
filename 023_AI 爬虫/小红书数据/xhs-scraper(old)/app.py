"""
Xiaohongshu Data Scraper - FastAPI Main Server
Provides REST API for searching, fetching, downloading, and analyzing Xiaohongshu notes.
"""
import os
import time
import asyncio
import logging
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from scraper.client import ClientManager, check_sign_server, update_sign_server_cookie
from scraper.downloader import MediaDownloader
from scraper.packager import NotePackager
from scraper.analyzer import analyze_notes

try:
    from xhs.core import SearchSortType
except ImportError:
    SearchSortType = None

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [API] %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

# Global state
current_cookie = ""
cookie_valid = False

# Rate limiting
last_request_time = 0.0
MIN_REQUEST_INTERVAL = 2.0  # seconds


# ─── Lifespan ───────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting XHS Scraper API...")
    sign_ok = check_sign_server()
    if sign_ok:
        logger.info("Sign server is connected.")
    else:
        logger.warning("Sign server is NOT reachable at localhost:5005. Signing may fall back to built-in.")
    yield
    logger.info("Shutting down...")
    ClientManager.clear()


# ─── App Init ───────────────────────────────────────────────
app = FastAPI(title="XHS Scraper API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# ─── Rate Limit Middleware ──────────────────────────────────
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    global last_request_time
    if request.url.path.startswith("/api/"):
        now = time.time()
        elapsed = now - last_request_time
        if elapsed < MIN_REQUEST_INTERVAL:
            await asyncio.sleep(MIN_REQUEST_INTERVAL - elapsed)
        last_request_time = time.time()
    response = await call_next(request)
    return response


# ─── Request Models ─────────────────────────────────────────
class CookieRequest(BaseModel):
    cookie: str


class SearchRequest(BaseModel):
    keyword: str
    page: int = 1
    page_size: int = 20
    sort: str = "general"  # general, popularity, latest


class UserSearchRequest(BaseModel):
    keyword: str
    page: int = 1
    page_size: int = 20


class DownloadNoteRequest(BaseModel):
    xsec_token: str = ""
    with_comments: bool = True


class BatchDownloadRequest(BaseModel):
    notes: list[dict]  # [{note_id, xsec_token}]


class AnalyzeRequest(BaseModel):
    notes: list[dict]


# ─── Helpers ────────────────────────────────────────────────
def get_client():
    if not current_cookie:
        raise HTTPException(status_code=400, detail="Cookie not set. Please set cookie first.")
    return ClientManager.get_client(current_cookie)


def handle_xhs_error(e: Exception):
    """Convert xhs library exceptions to HTTP responses."""
    err_type = type(e).__name__
    err_msg = str(e)

    if "IPBlock" in err_type or "ip_block" in err_msg.lower() or "300012" in err_msg:
        return JSONResponse(status_code=429, content={
            "error": "IP_BLOCKED",
            "message": "IP已被限制，请等待几分钟后再试。建议检查网络或更换IP。",
        })
    elif "NeedVerify" in err_type or "verify" in err_msg.lower():
        return JSONResponse(status_code=403, content={
            "error": "NEED_VERIFY",
            "message": "需要人机验证，请在浏览器中完成验证后重新获取Cookie。",
        })
    elif "Sign" in err_type or "sign" in err_msg.lower() or "300015" in err_msg or "浏览器异常" in err_msg:
        return JSONResponse(status_code=401, content={
            "error": "SIGN_ERROR",
            "message": "签名验证失败。可能原因：1) Cookie已过期，请重新获取；2) 签名服务未启动，请确保sign_server.py正在运行。",
        })
    elif "DataFetch" in err_type:
        # Extract useful info from DataFetchError response
        detail = ""
        if hasattr(e, 'response') and e.response is not None:
            try:
                resp_json = e.response.json()
                detail = str(resp_json)
                # Parse specific error codes for better messages
                code = resp_json.get("code", "")
                msg = resp_json.get("msg", "")
                if code == 300011 or "账号存在异常" in msg:
                    return JSONResponse(status_code=403, content={
                        "error": "ACCOUNT_ABNORMAL",
                        "message": f"当前账号存在异常（code: {code}），请切换到其他小红书账号后重新获取Cookie。",
                    })
                elif code == -1:
                    return JSONResponse(status_code=401, content={
                        "error": "SIGN_ERROR",
                        "message": "签名验证失败（code: -1）。请尝试：1) 重新获取Cookie；2) 重启sign_server.py签名服务；3) 等待几分钟后重试。",
                    })
            except Exception:
                detail = str(e.response.text[:200]) if hasattr(e.response, 'text') else ""
        return JSONResponse(status_code=500, content={
            "error": "DATA_FETCH_ERROR",
            "message": f"数据获取失败: {err_msg}" + (f" 详情: {detail}" if detail else ""),
        })
    else:
        logger.error(f"XHS error: {err_type}: {err_msg}")
        return JSONResponse(status_code=500, content={
            "error": err_type,
            "message": err_msg,
        })


# ─── Cookie Management ─────────────────────────────────────
@app.post("/api/cookie")
async def set_cookie(req: CookieRequest):
    global current_cookie, cookie_valid
    try:
        current_cookie = req.cookie
        update_sign_server_cookie(req.cookie)

        client = get_client()
        # Verify cookie by fetching self info
        try:
            self_info = client.get_self_info()
            cookie_valid = True
            nickname = self_info.get("nickname", "Unknown") if self_info else "Unknown"
            return {"status": "ok", "message": f"Cookie verified. Logged in as: {nickname}"}
        except Exception as e:
            # Some xhs versions may not have get_self_info, try alternative
            cookie_valid = True
            return {"status": "ok", "message": "Cookie set successfully."}

    except Exception as e:
        cookie_valid = False
        return handle_xhs_error(e)


@app.get("/api/cookie/status")
async def cookie_status():
    sign_ok = check_sign_server()
    return {
        "cookie_set": bool(current_cookie),
        "cookie_valid": cookie_valid,
        "sign_server": sign_ok,
    }


# ─── Search APIs ────────────────────────────────────────────
@app.post("/api/search")
async def search_notes(req: SearchRequest):
    """Search notes by keyword."""
    try:
        client = get_client()

        # Map sort values to SearchSortType enum
        if SearchSortType:
            sort_enum_map = {
                "general": SearchSortType.GENERAL,
                "popularity": SearchSortType.MOST_POPULAR,
                "latest": SearchSortType.LATEST,
            }
            sort_param = sort_enum_map.get(req.sort, SearchSortType.GENERAL)
        else:
            # Fallback: use string value directly if enum not available
            sort_param = {
                "general": "general",
                "popularity": "popularity_descending",
                "latest": "time_descending",
            }.get(req.sort, "general")

        result = client.get_note_by_keyword(
            keyword=req.keyword,
            page=req.page,
            page_size=req.page_size,
            sort=sort_param,
        )

        # Normalize response
        items = []
        if isinstance(result, dict):
            raw_items = result.get("items", [])
            has_more = result.get("has_more", False)
        elif isinstance(result, list):
            raw_items = result
            has_more = len(raw_items) >= req.page_size
        else:
            raw_items = []
            has_more = False

        for item in raw_items:
            note_card = item.get("note_card", item)
            items.append({
                "note_id": note_card.get("note_id", ""),
                "xsec_token": note_card.get("xsec_token", ""),
                "title": note_card.get("title", ""),
                "desc": note_card.get("desc", ""),
                "type": note_card.get("type", "normal"),
                "time": note_card.get("time", 0),
                "last_update_time": note_card.get("last_update_time", 0),
                "user": {
                    "user_id": note_card.get("user", {}).get("user_id", ""),
                    "nickname": note_card.get("user", {}).get("nickname", ""),
                    "avatar": note_card.get("user", {}).get("image", ""),
                },
                "interact_info": note_card.get("interact_info", {}),
                "cover": {
                    "url": note_card.get("cover", {}).get("url_default", "")
                    or note_card.get("cover", {}).get("url", ""),
                },
                "tag_list": note_card.get("tag_list", []),
            })

        return {"has_more": has_more, "items": items, "total": len(items)}

    except HTTPException:
        raise
    except Exception as e:
        return handle_xhs_error(e)


@app.post("/api/search/user")
async def search_users(req: UserSearchRequest):
    """Search users by keyword."""
    try:
        client = get_client()

        result = client.get_user_by_keyword(
            keyword=req.keyword,
            page=req.page,
            page_size=req.page_size,
        )

        users = []
        if isinstance(result, dict):
            raw_users = result.get("users", [])
        elif isinstance(result, list):
            raw_users = result
        else:
            raw_users = []

        for u in raw_users:
            users.append({
                "user_id": u.get("user_id", ""),
                "nickname": u.get("nickname", ""),
                "avatar": u.get("image", ""),
                "desc": u.get("desc", ""),
                "gender": u.get("gender", 0),
                "ip_location": u.get("ip_location", ""),
            })

        return {"users": users}

    except Exception as e:
        return handle_xhs_error(e)


@app.get("/api/user/{user_id}/info")
async def get_user_info(user_id: str):
    """Get user profile info by user_id."""
    try:
        client = get_client()
        info = client.get_user_info(user_id=user_id)
        return {
            "user_id": user_id,
            "nickname": info.get("nickname", ""),
            "avatar": info.get("image", ""),
            "desc": info.get("desc", ""),
            "red_id": info.get("red_id", ""),
            "gender": info.get("gender", 0),
            "ip_location": info.get("ip_location", ""),
            "follows": info.get("follows", "0"),
            "fans": info.get("fans", "0"),
            "interaction": info.get("interaction", "0"),
        }
    except Exception as e:
        return handle_xhs_error(e)


@app.get("/api/user/{user_id}/notes")
async def get_user_notes(user_id: str, cursor: str = "", num: int = 30):
    """Get notes from a user's profile by user_id."""
    try:
        client = get_client()
        result = client.get_user_notes(user_id=user_id, cursor=cursor)

        notes = []
        if isinstance(result, dict):
            raw_notes = result.get("notes", [])
            has_more = result.get("has_more", False)
            next_cursor = result.get("cursor", "")
        elif isinstance(result, list):
            raw_notes = result
            has_more = len(raw_notes) >= num
            next_cursor = ""
        else:
            raw_notes = []
            has_more = False
            next_cursor = ""

        for n in raw_notes:
            note_data = n.get("note_card", n)
            notes.append({
                "note_id": note_data.get("note_id", ""),
                "xsec_token": note_data.get("xsec_token", ""),
                "title": note_data.get("display_title", "") or note_data.get("title", ""),
                "desc": note_data.get("desc", ""),
                "type": note_data.get("type", "normal"),
                "time": note_data.get("time", 0),
                "user": {
                    "user_id": note_data.get("user", {}).get("user_id", user_id),
                    "nickname": note_data.get("user", {}).get("nickname", ""),
                    "avatar": note_data.get("user", {}).get("image", ""),
                },
                "interact_info": note_data.get("interact_info", {}),
                "cover": {
                    "url": note_data.get("cover", {}).get("url_default", "")
                    or note_data.get("cover", {}).get("url", ""),
                },
            })

        return {"has_more": has_more, "cursor": next_cursor, "notes": notes}

    except Exception as e:
        return handle_xhs_error(e)


# ─── Note Detail & Comments ─────────────────────────────────
@app.get("/api/note/{note_id}")
async def get_note_detail(note_id: str, xsec_token: str = ""):
    """Get full note detail including media URLs."""
    try:
        client = get_client()

        note = client.get_note_by_id(note_id=note_id)

        # Extract media URLs immediately (they expire in ~30 seconds)
        img_urls = []
        video_url = ""

        try:
            from xhs.help import get_imgs_url_from_note, get_video_url_from_note
            img_urls = get_imgs_url_from_note(note)
            video_url = get_video_url_from_note(note)
        except Exception as e:
            logger.warning(f"Media URL extraction failed: {e}")
            # Fallback: try to extract from note data directly
            image_list = note.get("image_list", [])
            for img in image_list:
                info_list = img.get("info_list", [])
                if info_list:
                    img_urls.append(info_list[-1].get("url", ""))

            video_info = note.get("video", {})
            if video_info:
                consumer = video_info.get("consumer", {})
                video_key = consumer.get("origin_video_key", "")
                if video_key:
                    video_url = f"https://sns-video-bd.xhscdn.com/{video_key}"

        return {
            **note,
            "extracted_img_urls": img_urls,
            "extracted_video_url": video_url,
        }

    except Exception as e:
        return handle_xhs_error(e)


@app.get("/api/note/{note_id}/comments")
async def get_comments(note_id: str, cursor: str = "", xsec_token: str = ""):
    """Get comments for a note."""
    try:
        client = get_client()
        result = client.get_note_comments(
            note_id=note_id,
            cursor=cursor,
            xsec_token=xsec_token,
        )

        comments = []
        if isinstance(result, dict):
            raw_comments = result.get("comments", [])
            has_more = result.get("has_more", False)
            next_cursor = result.get("cursor", "")
        elif isinstance(result, list):
            raw_comments = result
            has_more = False
            next_cursor = ""
        else:
            raw_comments = []
            has_more = False
            next_cursor = ""

        for c in raw_comments:
            comment = {
                "id": c.get("id", ""),
                "content": c.get("content", ""),
                "create_time": c.get("create_time", 0),
                "ip_location": c.get("ip_location", ""),
                "like_count": c.get("like_count", "0"),
                "sub_comment_count": c.get("sub_comment_count", "0"),
                "user": {
                    "user_id": c.get("user_info", {}).get("user_id", ""),
                    "nickname": c.get("user_info", {}).get("nickname", ""),
                    "avatar": c.get("user_info", {}).get("image", ""),
                },
                "sub_comments": [],
            }

            # Include sub_comments if present
            for sc in c.get("sub_comments", []):
                comment["sub_comments"].append({
                    "id": sc.get("id", ""),
                    "content": sc.get("content", ""),
                    "create_time": sc.get("create_time", 0),
                    "ip_location": sc.get("ip_location", ""),
                    "like_count": sc.get("like_count", "0"),
                    "user": {
                        "user_id": sc.get("user_info", {}).get("user_id", ""),
                        "nickname": sc.get("user_info", {}).get("nickname", ""),
                        "avatar": sc.get("user_info", {}).get("image", ""),
                    },
                    "target_comment": sc.get("target_comment", {}),
                })

            comments.append(comment)

        return {"has_more": has_more, "cursor": next_cursor, "comments": comments}

    except Exception as e:
        return handle_xhs_error(e)


@app.get("/api/note/{note_id}/sub_comments")
async def get_sub_comments(note_id: str, root_comment_id: str, cursor: str = ""):
    """Get sub-comments (replies) for a root comment."""
    try:
        client = get_client()
        result = client.get_note_sub_comments(
            note_id=note_id,
            root_comment_id=root_comment_id,
            cursor=cursor,
        )

        comments = []
        if isinstance(result, dict):
            raw_comments = result.get("comments", [])
            has_more = result.get("has_more", False)
            next_cursor = result.get("cursor", "")
        else:
            raw_comments = result if isinstance(result, list) else []
            has_more = False
            next_cursor = ""

        for c in raw_comments:
            comments.append({
                "id": c.get("id", ""),
                "content": c.get("content", ""),
                "create_time": c.get("create_time", 0),
                "ip_location": c.get("ip_location", ""),
                "like_count": c.get("like_count", "0"),
                "user": {
                    "user_id": c.get("user_info", {}).get("user_id", ""),
                    "nickname": c.get("user_info", {}).get("nickname", ""),
                    "avatar": c.get("user_info", {}).get("image", ""),
                },
            })

        return {"has_more": has_more, "cursor": next_cursor, "comments": comments}

    except Exception as e:
        return handle_xhs_error(e)


# ─── Download APIs ──────────────────────────────────────────
@app.post("/api/download/note/{note_id}")
async def download_note(note_id: str, req: DownloadNoteRequest):
    """Download a single note as ZIP (metadata + content + media + comments)."""
    try:
        client = get_client()
        downloader = MediaDownloader()
        packager = NotePackager(downloader)

        # 1. Get note detail
        note = client.get_note_by_id(note_id=note_id)

        # 2. Extract media URLs
        img_urls = []
        video_url = ""
        try:
            from xhs.help import get_imgs_url_from_note, get_video_url_from_note
            img_urls = get_imgs_url_from_note(note)
            video_url = get_video_url_from_note(note)
        except Exception:
            image_list = note.get("image_list", [])
            for img in image_list:
                info_list = img.get("info_list", [])
                if info_list:
                    img_urls.append(info_list[-1].get("url", ""))

        note["extracted_img_urls"] = img_urls
        note["extracted_video_url"] = video_url

        # 3. Get comments if requested
        comments = []
        if req.with_comments:
            try:
                comments_result = client.get_note_comments(
                    note_id=note_id,
                    xsec_token=req.xsec_token,
                )
                if isinstance(comments_result, dict):
                    comments = comments_result.get("comments", [])
                elif isinstance(comments_result, list):
                    comments = comments_result
            except Exception as e:
                logger.warning(f"Failed to get comments: {e}")

        # 4. Package as ZIP
        zip_bytes = packager.package_note(note, comments)

        title = note.get("title", note_id)
        safe_title = "".join(c for c in title if c not in r'<>:"/\|?*')[:50]

        return StreamingResponse(
            iter([zip_bytes]),
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="{safe_title}.zip"'},
        )

    except HTTPException:
        raise
    except Exception as e:
        return handle_xhs_error(e)


@app.post("/api/download/batch")
async def download_batch(req: BatchDownloadRequest):
    """Download multiple notes as a single ZIP."""
    try:
        client = get_client()
        downloader = MediaDownloader()
        packager = NotePackager(downloader)

        import zipfile
        import io

        buf = io.BytesIO()

        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as outer_zf:
            for i, note_ref in enumerate(req.notes):
                note_id = note_ref.get("note_id", "")
                xsec_token = note_ref.get("xsec_token", "")

                if not note_id:
                    continue

                try:
                    # Get note detail
                    note = client.get_note_by_id(note_id=note_id)

                    # Extract media URLs
                    img_urls = []
                    video_url = ""
                    try:
                        from xhs.help import get_imgs_url_from_note, get_video_url_from_note
                        img_urls = get_imgs_url_from_note(note)
                        video_url = get_video_url_from_note(note)
                    except Exception:
                        pass

                    note["extracted_img_urls"] = img_urls
                    note["extracted_video_url"] = video_url

                    # Get comments
                    comments = []
                    try:
                        comments_result = client.get_note_comments(
                            note_id=note_id,
                            xsec_token=xsec_token,
                        )
                        if isinstance(comments_result, dict):
                            comments = comments_result.get("comments", [])
                        elif isinstance(comments_result, list):
                            comments = comments_result
                    except Exception:
                        pass

                    # Package individual note
                    note_zip = packager.package_note(note, comments)

                    title = note.get("title", note_id)
                    safe_title = "".join(c for c in title if c not in r'<>:"/\|?*')[:50]

                    # Write as nested zip
                    outer_zf.writestr(f"{safe_title}.zip", note_zip)
                    logger.info(f"Packaged note {i + 1}/{len(req.notes)}: {safe_title}")

                except Exception as e:
                    logger.error(f"Failed to package note {note_id}: {e}")
                    outer_zf.writestr(f"_error_note_{note_id}.txt", f"Error: {str(e)}")

                # Rate limit between notes
                if i < len(req.notes) - 1:
                    await asyncio.sleep(2)

        buf.seek(0)

        return StreamingResponse(
            iter([buf.getvalue()]),
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="xhs_batch_{int(time.time())}.zip"'
            },
        )

    except Exception as e:
        return handle_xhs_error(e)


# ─── Analysis API ───────────────────────────────────────────
@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest):
    """Analyze note data: statistics, word frequency, time trends, sentiment."""
    try:
        result = analyze_notes(req.notes)
        return result
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


# ─── Serve Frontend ─────────────────────────────────────────
@app.get("/")
async def serve_index():
    """Serve the main HTML page."""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(content={"message": "Static files not found. Please ensure static/index.html exists."})


# ─── Run ────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
