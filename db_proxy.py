# -*- coding: utf-8 -*-
"""
鸿蒙前端临时测试 - 数据库代理
警告：此代码仅用于临时测试，绝对禁止用于生产环境！
测试完毕后请立即销毁所有相关资源。
"""

import os
import json
import logging
import pymysql
from flask import Flask, jsonify, request
from flask_cors import CORS

# ==================== 配置区域 ====================
# 设置日志，方便在Railway控制台查看
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域，仅用于测试！

# ==================== 数据库连接函数 ====================
def get_db_connection():
    """
    创建并返回数据库连接
    从环境变量读取配置（Railway控制台设置的Variables）
    """
    try:
        # 从环境变量读取数据库配置
        db_config = {
            'host': os.environ.get('DB_HOST', ''),
            'port': int(os.environ.get('DB_PORT', 3306)),
            'user': os.environ.get('DB_USER', ''),
            'password': os.environ.get('DB_PASSWORD', ''),
            'database': os.environ.get('DB_NAME', ''),
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor,
            'connect_timeout': 10
        }
        
        logger.info(f"尝试连接数据库: host={db_config['host']}, "
                   f"database={db_config['database']}, user={db_config['user']}")
        
        # 验证必要配置是否存在
        if not all([db_config['host'], db_config['user'], db_config['database']]):
            logger.error("数据库环境变量配置不完整！")
            raise ValueError("数据库环境变量配置不完整")
        
        # 建立连接
        connection = pymysql.connect(**db_config)
        logger.info("数据库连接成功")
        return connection
        
    except pymysql.Error as e:
        logger.error(f"数据库连接失败 (pymysql错误): {e}")
        raise
    except Exception as e:
        logger.error(f"数据库连接失败 (其他错误): {e}")
        raise

# ==================== API路由定义 ====================
@app.route('/')
def index():
    """根路径，返回服务状态"""
    return jsonify({
        'code': 200,
        'message': '数据库代理服务运行中',
        'warning': '此服务仅用于临时测试，请勿用于生产环境！',
        'endpoints': {
            '测试连接': 'GET /test',
            '健康检查': 'GET /health'
        }
    })

@app.route('/health')
def health_check():
    """健康检查端点"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 as status")
            result = cursor.fetchone()
        conn.close()
        
        return jsonify({
            'code': 200,
            'message': '服务健康，数据库连接正常',
            'data': result
        })
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'服务异常: {str(e)}'
        }), 500

@app.route('/test', methods=['GET'])
def test_query():
    """
    测试接口：查询users表第一条数据
    访问方式：GET https://你的域名.railway.app/test
    """
    conn = None
    try:
        logger.info("收到 /test 请求")
        
        # 连接数据库
        conn = get_db_connection()
        
        # 执行查询（根据你的表结构）
        with conn.cursor() as cursor:
            # 查询users表的第一条记录
            sql = "SELECT user_id, username, role, real_name FROM users LIMIT 1"
            cursor.execute(sql)
            result = cursor.fetchone()
            
            logger.info(f"查询结果: {result}")
        
        # 返回结果
        if result:
            return jsonify({
                'code': 200,
                'message': '查询成功',
                'data': result,
                'note': '此接口仅返回第一条用户数据用于测试'
            })
        else:
            return jsonify({
                'code': 404,
                'message': '用户表中没有数据',
                'data': None
            })
            
    except pymysql.Error as e:
        logger.error(f"数据库查询错误: {e}")
        return jsonify({
            'code': 500,
            'message': f'数据库错误: {str(e)}',
            'suggestion': '请检查数据库连接配置和表结构'
        }), 500
    except Exception as e:
        logger.error(f"服务器内部错误: {e}")
        return jsonify({
            'code': 500,
            'message': f'服务器内部错误: {str(e)}'
        }), 500
    finally:
        if conn:
            conn.close()
            logger.debug("数据库连接已关闭")

# ==================== 应用启动 ====================
if __name__ == '__main__':
    """
    应用入口点
    Railway会通过Procfile中的命令启动此应用
    """
    try:
        # 获取Railway分配的端口（环境变量PORT）
        port = int(os.environ.get('PORT', 5000))
        
        logger.info("=" * 50)
        logger.info("开始启动数据库代理服务")
        logger.info(f"运行端口: {port}")
        logger.info(f"数据库主机: {os.environ.get('DB_HOST', '未设置')}")
        logger.info(f"数据库名称: {os.environ.get('DB_NAME', '未设置')}")
        logger.info("=" * 50)
        
        # 启动Flask应用
        # debug=False 在生产环境必须为False
        app.run(
            host='0.0.0.0',  # 监听所有网络接口
            port=port,
            debug=False,      # Railway上必须为False
            threaded=True     # 启用多线程处理请求
        )
        
    except Exception as e:
        logger.critical(f"应用启动失败: {e}")
        raise
