from flask import Flask, render_template, request, session, redirect, url_for, send_file
from data import salary_list  # 确保这个模块存在且包含 `salary_list`
import random
import string
from PIL import Image, ImageDraw, ImageFont
import io
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 设置一个密钥用于会话


def generate_captcha():
    """生成随机验证码并返回图像和字符串"""
    captcha_text = ''.join(random.choices(string.ascii_letters + string.digits, k=5))  # 生成5位验证码
    img = Image.new('RGB', (120, 40), color=(255, 255, 255))
    d = ImageDraw.Draw(img)

    # 使用默认字体
    font = ImageFont.load_default()
    d.text((10, 10), captcha_text, fill=(0, 0, 0), font=font)

    # 保存为字节流
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    return buf, captcha_text


@app.route('/captcha')
def captcha():
    """返回验证码图片"""
    buf, captcha_text = generate_captcha()
    session['captcha'] = captcha_text  # 将验证码存入会话
    return send_file(buf, mimetype='image/png')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=["POST"])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    captcha_input = request.form.get('captcha').lower()  # 不区分大小写

    # 验证验证码
    if captcha_input != session.get('captcha', '').lower():
        return "验证码错误，请重新输入！"

    for sal in salary_list:
        if sal['name'] == username and sal['password'] == password:
            session['username'] = username
            session['is_admin'] = (username == 'admin')  # 判断是否为管理员
            print("恭喜 登录成功！")
            return redirect(url_for('admin'))

    return "用户名或者密码输入错误，请重新输入！！"


@app.route('/admin')
def admin():
    if 'username' not in session:
        return redirect(url_for('index'))  # 如果未登录，重定向到登录页面

    if session['is_admin']:
        return render_template('admin.html', salary_list=salary_list)
    else:
        user_info = next((sal for sal in salary_list if sal['name'] == session['username']), None)
        return render_template('admin.html', salary_list=[user_info])


@app.route('/delete/<name>')
def delete(name):
    if session.get('is_admin'):
        for salary in salary_list:
            if salary['name'] == name:
                salary_list.remove(salary)
        return redirect(url_for('admin'))
    return "没有权限删除其他用户的信息！"


@app.route('/change/<name>')
def change(name):
    if session.get('is_admin') or name == session['username']:
        for salary in salary_list:
            if salary['name'] == name:
                return render_template('change.html', user=salary)
    return "没有权限修改该用户的信息！"


@app.route('/changed/<name>', methods=["POST"])
def changed(name):
    if session.get('is_admin') or name == session['username']:
        for salary in salary_list:
            if salary['name'] == name:
                salary['name'] = request.form.get('name')
                salary['password'] = request.form.get('password')
                salary['department'] = request.form.get('department')
                salary['position'] = request.form.get('position')
                salary['salary'] = request.form.get('salary')
        return redirect(url_for('admin'))
    return "没有权限修改该用户的信息！"


@app.route('/add')
def add():
    if session.get('is_admin'):
        return render_template('add.html')
    return "没有权限访问该页面！"


@app.route('/add2', methods=["POST"])
def add2():
    if session.get('is_admin'):
        salary = {
            'name': request.form.get('name'),
            'password': request.form.get('password'),
            'department': request.form.get('department'),
            'position': request.form.get('position'),
            'salary': request.form.get('salary')
        }
        salary_list.insert(0, salary)
        return redirect(url_for('admin'))
    return "没有权限新增用户！"


@app.route('/logout')
def logout():
    session.clear()  # 清除会话数据
    return redirect(url_for('index'))  # 重定向到登录页面

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
