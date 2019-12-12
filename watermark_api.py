"""
4
"""

import datetime
import os
import random
from datetime import timedelta

import flask
from flask import render_template, request, make_response, jsonify
from werkzeug.utils import secure_filename

from watermark import mark_photo

# initialize our Flask application and the Keras model
app = flask.Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 2MB
# 设置允许的文件格式
ALLOWED_EXTENSIONS = {'png', 'jpg', 'JPG', 'PNG', 'bmp'}
# 设置静态文件缓存过期时间
app.send_file_max_age_default = timedelta(seconds=1)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def create_uuid():  # 生成唯一的图片的名称字符串，防止图片显示时的重名问题
    nowTime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")  # 生成当前时间
    randomNum = random.randint(0, 100)  # 生成的随机整数n，其中0<=n<=100
    if randomNum <= 10:
        randomNum = str(0) + str(randomNum)
    uniqueNum = str(nowTime) + str(randomNum)
    return uniqueNum


@app.route('/watermark/query', methods=['POST', 'GET'])  # 添加路由
def upload():
    """
    :return:
    """
    if request.method == 'POST':
        f = request.files['file']

        if not (f and allowed_file(f.filename)):
            return jsonify({"error": 1001, "msg": "请检查上传的图片类型，仅限于png、PNG、jpg、JPG、bmp"})

        mark_text = request.form.get("mark_text")
        size = request.form.get("size")
        color = request.form.get("color")
        space = request.form.get("space")
        angle = request.form.get("angle")
        opacity = request.form.get("opacity")
        # print(mark_text, space)
        basepath = os.path.dirname(__file__)  # 当前文件所在路径
        new_name = "{0}.{1}".format(create_uuid(), f.filename)
        upload_path = os.path.join(basepath, 'static/images', secure_filename(new_name))
        water_path = os.path.join(basepath, 'static/water', secure_filename(new_name))
        f.save(upload_path)
        mark_photo(upload_path, water_path, mark_text=mark_text, size=int(size), color=color, opacity=float(opacity),
                   space=int(space), angle=int(angle))
        image_data = open(water_path, "rb").read()
        os.remove(upload_path)
        os.remove(water_path)
        response = make_response(image_data)
        response.headers['Content-Type'] = 'image/png'
        return response

    return render_template('upload.html')


if __name__ == '__main__':
    # app.debug = True
    # mkdir -p static/images
    # mkdir -p static/water
    # nohup python -u watermark_api.py >nohup_watermark_api.log 2>&1 &
    app.run(host='0.0.0.0', port=8987, debug=False)
