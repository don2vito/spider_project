import os
import re
import io
import json
import time
import zipfile
import requests
from urllib.parse import quote
from flask import Flask, jsonify, request, send_file, Response, make_response
from flask_cors import CORS
from bs4 import BeautifulSoup
from PIL import Image

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

BASE_URL = 'https://www.guoji.pro'
REPORT_LIST_URL = f'{BASE_URL}/Report'
TOTAL_PAGES = 32

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Referer': 'https://www.guoji.pro/'
}

reports_cache = []


def extract_marketing_id(url):
    match = re.search(r'marketingId=(\d+)', url)
    return match.group(1) if match else None


def fetch_page_html(page_index):
    params = {
        'category': 2,
        'sort': 0,
        'pageindex': page_index,
        'entry': -1,
        'keyword': ''
    }
    try:
        resp = requests.get(REPORT_LIST_URL, params=params, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        resp.encoding = 'utf-8'
        return resp.text
    except Exception as e:
        print(f'Failed to fetch page {page_index}: {e}')
        return None


def parse_report_list(html):
    reports = []
    soup = BeautifulSoup(html, 'html.parser')

    all_links = soup.find_all('a', href=re.compile(r'ReportDetail\?marketingId='))
    seen_ids = set()

    for link in all_links:
        href = link.get('href', '')
        marketing_id = extract_marketing_id(href)
        if not marketing_id or marketing_id in seen_ids:
            continue
        seen_ids.add(marketing_id)

        h3_tag = link.find('h3')
        if h3_tag:
            title = h3_tag.get_text(strip=True)
        else:
            title = link.get_text(strip=True)
            title = re.split(r'内容洞察|电商热度|营销复盘|行业趋势|品类趋势|用户画像|年度报告|趋势前瞻|内容趋势|营销洞察', title)[0].strip()

        full_url = href if href.startswith('http') else f'{BASE_URL}{href}'

        cover_img = ''
        parent = link.parent
        for _ in range(5):
            if parent is None:
                break
            img = parent.find('img')
            if img:
                cover_img = img.get('src', '') or img.get('data-src', '')
                if cover_img and not cover_img.startswith('http'):
                    cover_img = f'https:{cover_img}' if cover_img.startswith('//') else f'{BASE_URL}{cover_img}'
                break
            parent = parent.parent

        if title and len(title) > 5:
            reports.append({
                'marketingId': marketing_id,
                'title': title,
                'url': full_url,
                'coverImage': cover_img
            })

    return reports


def parse_report_list_v2(html):
    reports = []
    soup = BeautifulSoup(html, 'html.parser')

    pattern = re.compile(
        r'<a[^>]*href=["\']([^"\']*ReportDetail\?marketingId=(\d+))["\'][^>]*>.*?</a>',
        re.DOTALL
    )

    all_imgs = soup.find_all('img')
    img_map = {}
    for img in all_imgs:
        src = img.get('src', '') or img.get('data-src', '')
        if src and 'doubaocdn' in src:
            parent_text = img.parent.get_text(strip=True) if img.parent else ''
            img_map[src] = parent_text

    for match in pattern.finditer(html):
        href = match.group(1)
        marketing_id = match.group(2)

        link_html = match.group(0)
        link_soup = BeautifulSoup(link_html, 'html.parser')
        title = link_soup.get_text(strip=True)

        full_url = href if href.startswith('http') else f'{BASE_URL}{href}'

        cover_img = ''
        context_start = max(0, match.start() - 2000)
        context_html = html[context_start:match.start()]
        img_matches = re.findall(r'(?:src|data-src)=["\']([^"\']*doubaocdn[^"\']*)["\']', context_html)
        if img_matches:
            cover_img = img_matches[-1]

        if title and len(title) > 5:
            reports.append({
                'marketingId': marketing_id,
                'title': title,
                'url': full_url,
                'coverImage': cover_img
            })

    return reports


def fetch_all_reports():
    all_reports = []
    seen_ids = set()

    for page in range(1, TOTAL_PAGES + 1):
        print(f'Fetching page {page}/{TOTAL_PAGES}...')
        html = fetch_page_html(page)
        if not html:
            continue

        reports = parse_report_list(html)

        if not reports:
            reports = parse_report_list_v2(html)

        for report in reports:
            mid = report['marketingId']
            if mid not in seen_ids:
                seen_ids.add(mid)
                all_reports.append(report)

        print(f'  Found {len(reports)} reports on page {page}')

    return all_reports


def fetch_report_detail(marketing_id):
    url = f'{BASE_URL}/Report/ReportDetail?marketingId={marketing_id}'
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        resp.encoding = 'utf-8'
        html = resp.text

        soup = BeautifulSoup(html, 'html.parser')

        all_images = []
        img_tags = soup.find_all('img')
        
        for img in img_tags:
            src = img.get('src', '') or img.get('data-src', '')
            if not src:
                continue
            
            if 'blogPDF' in src or 'resource.guoji.pro' in src:
                if not src.startswith('http'):
                    src = f'https:{src}' if src.startswith('//') else f'{BASE_URL}{src}'
                if src not in all_images:
                    all_images.append(src)

        images = all_images

        title = ''
        title_tag = soup.find('h1') or soup.find('h2')
        if title_tag:
            title = title_tag.get_text(strip=True)

        return {
            'marketingId': marketing_id,
            'title': title,
            'images': images
        }
    except Exception as e:
        print(f'Failed to fetch detail for {marketing_id}: {e}')
        return None


def download_image(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return Image.open(io.BytesIO(resp.content))
    except Exception as e:
        print(f'Failed to download image {url}: {e}')
        return None


def images_to_pdf(image_urls):
    images = []
    for url in image_urls:
        img = download_image(url)
        if img:
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            images.append(img)

    if not images:
        return None

    pdf_buffer = io.BytesIO()
    if len(images) == 1:
        images[0].save(pdf_buffer, format='PDF')
    else:
        images[0].save(pdf_buffer, format='PDF', save_all=True, append_images=images[1:])

    pdf_buffer.seek(0)
    return pdf_buffer


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/api/reports')
def get_reports():
    global reports_cache
    if not reports_cache:
        reports_cache = fetch_all_reports()
    return jsonify({
        'success': True,
        'data': reports_cache,
        'total': len(reports_cache)
    })


@app.route('/api/refresh')
def refresh_reports():
    global reports_cache
    reports_cache = fetch_all_reports()
    return jsonify({
        'success': True,
        'data': reports_cache,
        'total': len(reports_cache)
    })


@app.route('/api/report-detail/<marketing_id>')
def get_report_detail(marketing_id):
    detail = fetch_report_detail(marketing_id)
    if detail:
        return jsonify({'success': True, 'data': detail})
    return jsonify({'success': False, 'error': 'Failed to fetch report detail'}), 500


@app.route('/api/download-pdf/<marketing_id>')
def download_pdf(marketing_id):
    detail = fetch_report_detail(marketing_id)
    if not detail or not detail['images']:
        return jsonify({'success': False, 'error': 'No images found'}), 404

    pdf_buffer = images_to_pdf(detail['images'])
    if not pdf_buffer:
        return jsonify({'success': False, 'error': 'Failed to generate PDF'}), 500

    title = detail.get('title', marketing_id)
    safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)[:100]
    filename = f'{safe_title}.pdf'
    encoded_filename = quote(filename)

    response = make_response(send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    ))
    response.headers['Content-Disposition'] = f"attachment; filename*=UTF-8''{encoded_filename}"
    return response


@app.route('/api/download-batch', methods=['POST'])
def download_batch():
    data = request.get_json()
    marketing_ids = data.get('marketingIds', [])

    if not marketing_ids:
        return jsonify({'success': False, 'error': 'No marketing IDs provided'}), 400

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for mid in marketing_ids:
            detail = fetch_report_detail(mid)
            if not detail or not detail['images']:
                continue

            pdf_buffer = images_to_pdf(detail['images'])
            if pdf_buffer:
                title = detail.get('title', mid)
                safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)[:100]
                zf.writestr(f'{safe_title}.pdf', pdf_buffer.getvalue())

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name='reports.zip'
    )


@app.route('/api/proxy-image')
def proxy_image():
    url = request.args.get('url', '')
    allowed_domains = ['doubaocdn.com', 'guoji.pro']
    if not url or not any(domain in url for domain in allowed_domains):
        return jsonify({'success': False, 'error': 'Invalid URL'}), 400

    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return Response(
            resp.content,
            mimetype=resp.headers.get('Content-Type', 'image/jpeg')
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print('Starting GuoJi Report Crawler Server...')
    print('Access http://localhost:5001 to view the application')
    app.run(host='0.0.0.0', port=5001, debug=False)
