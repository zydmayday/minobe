# coding: utf-8
import requests
import os
from urllib.parse import urlparse
from datetime import datetime, timedelta

def download_image(url_template):
    # 获取当前日期，格式为 YYYYMMDD
    current_date = '20240917'
    # current_date = (datetime.now() - timedelta(1)).strftime('%Y%m%d')

    # 替换 URL 中的日期部分为当前日期
    url_template = url_template.replace('20241021', current_date)
    

    # 循环搜索图片文件名
    for i in range(8117, 8117 + 151):  # 从 001 到 150
        # 生成图片编号，格式为 001, 002, ..., 150
        img_number = f'{i:04}'  # 保持4位数，例如 0001, 0002

        # 构建完整的图片 URL
        img_url = url_template.replace('IMG_0092', f'IMG_{img_number}')

        # 解析 URL
        parsed_url = urlparse(img_url)

        # 提取路径并分割成文件夹和文件名
        path_parts = parsed_url.path.split('/')
    
        # 文件夹名为倒数第二个部分，文件名为最后一个部分
        save_folder = path_parts[-2]

        # 创建保存文件夹，如果不存在
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        # 生成保存的图片文件名
        save_filename = f'IMG_{img_number}.jpg'
        save_path = os.path.join(save_folder, save_filename)

        # 提取用户名和密码
        auth = ('ParentsMnb', 'Minobekko57')

        print(f'img url: {img_url}')

        # 发送请求获取图片
        response = requests.get(img_url, auth=auth)

        # 检查请求是否成功
        if response.status_code == 200:
            # 将图片数据写入本地文件
            with open(save_path, 'wb') as file:
                file.write(response.content)
            print(f"download {save_filename} succeessfully, saved to {save_path}")
        else:
            print(f"can not find {save_filename}, status code: {response.status_code}")

# 图片URL模板 (注意这里包含了占位符 '20241021' 和 'IMG_0092')
# 要改url里的后缀
# description = 'nenchuoimohori'
description = 'birthdayparty'
url_template = f'https://ParentsMnb:Minobekko57@www.minobe.ed.jp/photo/photo_data/20241021{description}/IMG_0092.jpg'

# 调用函数下载图片
download_image(url_template)
