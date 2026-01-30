from flask import Flask, request, jsonify
import pymysql
from flask_cors import CORS  # 解决跨域问题

app = Flask(__name__)
CORS(app)  # 允许所有域访问，仅用于测试！

DB_HOST = 'emotion-rds.rdsmfb0viq07rfq.rds.bj.baidubce.com'
DB_PORT = 3306
DB_USER = 'emotion_user'
DB_PASSWORD = '@Tuyichen1014'
DB_NAME = 'emotion_db'


def get_db_connection():
    """创建数据库连接"""
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


@app.route('/test', methods=['GET'])
def test_query():
    """测试接口：查询users表第一条用户ID和用户名"""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 执行查询，根据你的 `users` 表结构
            sql = "SELECT user_id, username FROM users LIMIT 1"
            cursor.execute(sql)
            result = cursor.fetchone()

        if result:
            return jsonify({
                'code': 200,
                'message': 'success',
                'data': result
            })
        else:
            return jsonify({
                'code': 404,
                'message': '未找到用户数据',
                'data': None
            })

    except pymysql.Error as e:
        return jsonify({
            'code': 500,
            'message': f'数据库错误: {e}',
            'data': None
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'服务器内部错误: {e}',
            'data': None
        })
    finally:
        if conn:
            conn.close()


@app.route('/query', methods=['POST'])
def custom_query():
    """（危险！）自定义查询接口，仅用于极端测试，用完请立即关闭或删除此路由"""
    # 警告：此接口极度危险，允许执行任意SQL，仅应在受控环境短暂测试。
    if not request.is_json:
        return jsonify({'code': 400, 'message': '请求必须是JSON格式'})

    data = request.get_json()
    sql = data.get('sql', '').strip()

    if not sql or ';' in sql:  # 简单的防注入检查（非常薄弱）
        return jsonify({'code': 400, 'message': 'SQL语句不合法'})

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql)
            # 区分查询和更新操作
            if sql.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                return jsonify({'code': 200, 'data': result})
            else:
                conn.commit()
                return jsonify({'code': 200, 'message': '执行成功', 'rows_affected': cursor.rowcount})
    except pymysql.Error as e:
        return jsonify({'code': 500, 'message': f'数据库错误: {e}'})
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {e}'})
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    # 调试模式请勿在公网开启！此处仅为本地测试。
    app.run(host='0.0.0.0', port=5000, debug=False)