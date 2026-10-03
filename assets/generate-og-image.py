#!/usr/bin/env python3
"""
生成 OG 分享图片 (JPG 格式)
尺寸：1200x630 像素
"""

from PIL import Image, ImageDraw, ImageFont
import os

# 图片尺寸
WIDTH, HEIGHT = 1200, 630

# 配色方案
COLORS = {
    'bg_dark': '#0a0a0a',
    'bg_mid': '#1a1a2e',
    'green': '#00ff88',
    'cyan': '#00d4ff',
    'purple': '#7b2ff7',
    'orange': '#FF8C42',
    'gold': '#FFD700',
    'white': '#ffffff',
    'light_gray': '#e0e0e0',
    'gray': '#b0b0b0',
    'dark_gray': '#666666',
}

def create_gradient_background(width, height):
    """创建渐变背景"""
    img = Image.new('RGB', (width, height), COLORS['bg_dark'])
    draw = ImageDraw.Draw(img)
    
    # 创建从上到下的渐变
    for y in range(height):
        ratio = y / height
        if ratio < 0.5:
            r = int(10 + (26 - 10) * (ratio * 2))
            g = int(10 + (26 - 10) * (ratio * 2))
            b = int(26 + (46 - 26) * (ratio * 2))
        else:
            r = int(26 + (15 - 26) * ((ratio - 0.5) * 2))
            g = int(26 + (15 - 26) * ((ratio - 0.5) * 2))
            b = int(46 + (26 - 46) * ((ratio - 0.5) * 2))
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    return img

def add_grid_decoration(draw, width, height):
    """添加网格装饰"""
    # 垂直线
    for x in [100, 300, 500, 700, 900, 1100]:
        draw.line([(x, 0), (x, height)], fill='#333333', width=1)
    # 水平线
    for y in [100, 200, 300, 400, 500, 600]:
        draw.line([(0, y), (width, y)], fill='#333333', width=1)

def add_circle_decoration(draw, cx, cy, r, color, opacity=0.3):
    """添加装饰圆圈"""
    # 绘制多个同心圆
    for i in range(3):
        radius = r - i * 25
        if radius > 0:
            draw.ellipse(
                [cx - radius, cy - radius, cx + radius, cy + radius],
                outline=color,
                width=2
            )

def main():
    # 创建背景
    img = create_gradient_background(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(img)
    
    # 添加网格装饰（降低不透明度效果）
    add_grid_decoration(draw, WIDTH, HEIGHT)
    
    # 尝试加载字体
    try:
        font_bold = ImageFont.truetype("msyh.ttc", 72)  # 微软雅黑 Bold
        font_regular = ImageFont.truetype("msyh.ttc", 30)
        font_small = ImageFont.truetype("msyh.ttc", 26)
        font_en = ImageFont.truetype("arial.ttf", 36)
        font_en_small = ImageFont.truetype("arial.ttf", 22)
        font_url = ImageFont.truetype("arial.ttf", 18)
    except:
        # 如果字体不存在，使用默认字体
        font_bold = ImageFont.load_default()
        font_regular = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_en = ImageFont.load_default()
        font_en_small = ImageFont.load_default()
        font_url = ImageFont.load_default()
    
    # 主要内容起始位置
    start_x = 80
    start_y = 140
    
    # Logo - REMI
    draw.text((start_x, start_y), "REMI", fill=COLORS['orange'], font=font_en)
    
    # 主标题
    draw.text((start_x, start_y + 60), "AI 应用开发者", fill=COLORS['green'], font=font_bold)
    
    # 副标题
    draw.text((start_x, start_y + 140), "专注 AI 应用落地与智能自动化系统开发", fill=COLORS['gray'], font=font_regular)
    
    # 分隔线
    draw.line([(start_x, start_y + 185), (start_x + 850, start_y + 185)], fill=COLORS['cyan'], width=3)
    
    # 作品列表
    items = [
        (COLORS['green'], "Remi Radar — 智能信息雷达"),
        (COLORS['cyan'], "AI 小说创作工作流系统"),
        (COLORS['purple'], "定制工作自动化系统"),
        (COLORS['orange'], "Agentic Growth Coach"),
    ]
    
    list_start_y = start_y + 240
    for i, (color, text) in enumerate(items):
        # 彩色方块（带圆角效果）
        square_x = start_x
        square_y = list_start_y + i * 55
        # 绘制圆角矩形（手动绘制）
        draw.rectangle([square_x + 3, square_y, square_x + 11, square_y + 14], fill=color)
        draw.rectangle([square_x, square_y + 3, square_x + 14, square_y + 11], fill=color)
        # 文字
        draw.text((square_x + 32, square_y - 2), text, fill=COLORS['white'], font=font_small)
    
    # 底部英文标语
    draw.text((start_x, start_y + 440), "EXPLORE AI POSSIBILITIES", fill=COLORS['gold'], font=font_en_small)
    
    # 装饰圆圈
    add_circle_decoration(draw, 100, 550, 150, COLORS['orange'])
    add_circle_decoration(draw, 1100, 80, 180, COLORS['gold'])
    
    # 右下角装饰
    add_circle_decoration(draw, 950, 480, 80, COLORS['orange'])
    
    # 底部 URL
    draw.text((WIDTH // 2, HEIGHT - 35), "www.remifei.cn", fill=COLORS['dark_gray'], font=font_url, anchor="mm")
    
    # 保存图片
    output_path = os.path.join(os.path.dirname(__file__), 'og-image.jpg')
    img.save(output_path, 'JPEG', quality=95)
    print(f"[OK] Generated: {output_path}")
    
    # 同时保存 PNG 版本
    output_png = os.path.join(os.path.dirname(__file__), 'og-image.png')
    img.save(output_png, 'PNG')
    print(f"[OK] Generated: {output_png}")

if __name__ == '__main__':
    main()
