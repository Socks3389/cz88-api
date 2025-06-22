import requests
import schedule
import time
import os
import zipfile
from datetime import datetime
import shutil
import logging

# 配置日志
logging.basicConfig(
    filename='ip_db_update.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def download_and_update_db():
    download_url = "https://www.cz88.net/api/communityIpAuthorization/communityIpDbFile?fn=czdb&key=9aff9249-4876-3b14-a70b-04313b7d0d16"
    db_path = "/root/proxy_pool/czdb/cz88_public_v4.czdb"  # 替换为实际数据库路径
    temp_dir = "temp_download"
    
    try:
        # 创建临时目录
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            
        # 下载文件
        logging.info("开始下载数据库文件...")
        response = requests.get(download_url)
        if response.status_code != 200:
            raise Exception(f"下载失败，状态码: {response.status_code}")
            
        # 保存zip文件
        zip_path = os.path.join(temp_dir, "czdb.zip")  # 下载的压缩包名称
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        logging.info("下载完成")
            
        # 解压文件
        logging.info("开始解压文件...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        logging.info("解压完成")
            
        # 查找并替换数据库文件
        for file in os.listdir(temp_dir):
            if file.endswith('.czdb'):
                # 备份原数据库
                if os.path.exists(db_path):
                    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    shutil.copy2(db_path, backup_path)
                    logging.info(f"已创建备份: {backup_path}")
                    
                # 替换数据库文件
                new_db_path = os.path.join(temp_dir, file)
                shutil.copy2(new_db_path, db_path)
                logging.info("数据库更新成功")
                break
                
    except Exception as e:
        logging.error(f"更新失败: {str(e)}")
    finally:
        # 清理临时文件
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            logging.info("临时文件已清理")

if __name__ == "__main__":
    # 设置每周三晚上11点运行
    schedule.every().wednesday.at("23:00").do(download_and_update_db)
    logging.info("更新计划已启动")
    
    # 持续运行
    while True:
        schedule.run_pending()
        time.sleep(60)