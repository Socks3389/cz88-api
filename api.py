from flask import Flask, jsonify, request
from czdb.db_searcher import DbSearcher
import os
import logging
from logging.handlers import RotatingFileHandler
import atexit

# 配置日志
logging.basicConfig(
    handlers=[RotatingFileHandler('ip_query.log', maxBytes=10000000, backupCount=5)],
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

app = Flask(__name__)

# 数据库配置
DATABASE_PATH = os.getenv('CZDB_PATH', 'cz88_public_v4.czdb')
QUERY_TYPE = "BTREE"
KEY = "Tfhi+ijvEd6QVK4YUIEElA=="

db_searcher = None

def init_db():
    global db_searcher
    try:
        db_searcher = DbSearcher(DATABASE_PATH, QUERY_TYPE, KEY)
        logging.info("数据库初始化成功")
        return True
    except Exception as e:
        logging.error(f"数据库初始化错误: {e}")
        return False

@atexit.register
def cleanup():
    if db_searcher:
        db_searcher.close()
        logging.info("数据库连接已关闭")

with app.app_context():
    init_db()

@app.route('/api', methods=['GET'])
def query_ip():
    ip = request.args.get('ip')
    if not ip:
        logging.warning(f"缺少IP参数 - 客户端: {request.remote_addr}")
        return jsonify({
            'code': 400,
            'error': 'IP地址参数未提供'
        }), 400
    
    try:
        if not db_searcher:
            if not init_db():
                return jsonify({
                    'code': 500,
                    'error': '数据库未初始化'
                }), 500
        
        region = db_searcher.search(ip)
        # 替换特殊字符
        region = region.replace('\t', ' - ').replace('//', ' - ')
        logging.info(f"成功查询IP: {ip}")
        return jsonify({
            'code': 200,
            'data': {
                'region': region
            }
        })
    except Exception as e:
        logging.error(f"查询IP {ip} 时出错: {str(e)}")
        return jsonify({
            'code': 500,
            'error': f'查询出错: {str(e)}'
        }), 500

@app.errorhandler(Exception)
def handle_error(error):
    logging.error(f"系统错误: {str(error)}")
    return jsonify({
        'code': 500,
        'error': str(error)
    }), 500

# 初始化数据库
init_db()

if __name__ == '__main__':
    # 设置主机和端口
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # 启动服务
    logging.info(f"服务启动于 http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=False)