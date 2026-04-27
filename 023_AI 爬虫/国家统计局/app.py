"""
国家统计局月度数据代理服务器
提供 API 接口供前端 HTML 应用调用，处理与国家统计局 API V2.0 的交互。
"""

import logging
from flask import Flask, jsonify, request
from flask_cors import CORS

from stats_client import StatsClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 允许前端跨域访问

client = StatsClient()


@app.route("/api/tree")
def api_tree():
    """获取完整月度指标树"""
    try:
        code = request.args.get("code", "1")
        tree = client.get_full_tree(code=code)
        return jsonify({"success": True, "data": tree})
    except Exception as e:
        logger.error(f"获取指标树失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/indicators")
def api_indicators():
    """获取指定 cid 的指标列表"""
    cid = request.args.get("cid")
    dt = request.args.get("dt")
    name = request.args.get("name")
    if not cid:
        return jsonify({"success": False, "error": "cid 参数必填"}), 400
    try:
        indicators = client.get_indicators(cid, dt=dt, name=name)
        return jsonify({"success": True, "data": indicators})
    except Exception as e:
        logger.error(f"获取指标列表失败 (cid={cid}): {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/data", methods=["POST"])
def api_data():
    """
    批量获取多个 cid 的数据
    请求体: { "cids": ["uuid1", "uuid2", ...], "months": 36 }
    """
    body = request.get_json(force=True)
    if not body:
        return jsonify({"success": False, "error": "请求体不能为空"}), 400

    cids = body.get("cids", [])
    months = body.get("months", 36)

    if not cids:
        return jsonify({"success": False, "error": "cids 参数必填"}), 400

    dt_range = client.calc_monthly_range(months)
    dt_param = client.calc_monthly_range_dt(months)
    logger.info(f"开始批量获取数据: {len(cids)} 个指标集, 时间范围: {dt_range}")

    results = []
    for i, cid in enumerate(cids):
        try:
            logger.info(f"[{i + 1}/{len(cids)}] 正在获取 cid={cid} 的数据...")

            # 先获取该 cid 的指标列表
            indicators = client.get_indicators(cid, dt=dt_param)
            if not indicators:
                logger.warning(f"cid={cid} 无指标，跳过")
                results.append({"cid": cid, "indicators": [], "data": [], "success": True, "message": "无指标"})
                continue

            indicator_ids = [ind["_id"] for ind in indicators]

            # 获取数据
            data = client.get_data(cid, indicator_ids, [dt_range])
            results.append({
                "cid": cid,
                "indicators": indicators,
                "data": data,
                "success": True
            })
            logger.info(f"[{i + 1}/{len(cids)}] cid={cid} 获取成功，{len(indicators)} 个指标")

        except Exception as e:
            logger.error(f"[{i + 1}/{len(cids)}] cid={cid} 获取失败: {e}")
            results.append({"cid": cid, "error": str(e), "success": False})

    success_count = sum(1 for r in results if r["success"])
    logger.info(f"批量获取完成: {success_count}/{len(cids)} 成功")

    return jsonify({"success": True, "data": results})


@app.route("/api/health")
def api_health():
    """健康检查"""
    return jsonify({"status": "ok", "timestamp": __import__('time').time()})


if __name__ == "__main__":
    logger.info("国家统计局月度数据代理服务器启动中...")
    logger.info("服务地址: http://localhost:5000")
    logger.info("API 端点: /api/tree, /api/indicators, /api/data, /api/health")
    app.run(host="0.0.0.0", port=5000, debug=True)
