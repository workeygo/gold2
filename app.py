import streamlit as st
from PIL import Image
import io
import zipfile
import os

# --- 页面配置 ---
st.set_page_config(page_title="表情包自动切割器", page_icon="✂️")

st.title("✂️ 表情包批量切割工具")
st.markdown("上传一张包含多个表情的大图，自动切分并打包下载。")

# --- 侧边栏 / 设置 ---
with st.expander("⚙️ 切割设置 (如果不准请点这里调整)", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        # 默认设置为你提供的图片格式：4列
        cols = st.number_input("横向有多少个表情 (列)", min_value=1, value=4, step=1)
    with col2:
        # 默认设置为你提供的图片格式：5行
        rows = st.number_input("纵向有多少个表情 (行)", min_value=1, value=5, step=1)
    
    margin = st.slider("边缘修剪 (去除黑边/白边)", 0, 20, 0, help="如果切出来的图有边缘线条，可以调大这个数值向内收缩")

# --- 主逻辑 ---
uploaded_file = st.file_uploader("点击上传图片", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    # 1. 读取图片
    image = Image.open(uploaded_file)
    st.image(image, caption="原始图片", use_column_width=True)

    # 获取图片尺寸
    img_w, img_h = image.size
    
    # 计算每个格子的宽和高
    tile_w = img_w / cols
    tile_h = img_h / rows

    st.divider()
    st.subheader("🔍 切割预览")
    
    # 用于存储切割后的图片对象
    cropped_images = []
    
    # 2. 开始切割
    # 创建一个进度条
    progress_bar = st.progress(0)
    total_tiles = rows * cols
    count = 0

    # 简单的网格预览容器
    preview_cols = st.columns(4) # 预览时一行显示4个

    for r in range(rows):
        for c in range(cols):
            # 计算切割坐标 (Left, Upper, Right, Lower)
            left = c * tile_w + margin
            upper = r * tile_h + margin
            right = (c + 1) * tile_w - margin
            lower = (r + 1) * tile_h - margin
            
            # 执行切割
            box = (left, upper, right, lower)
            tile = image.crop(box)
            
            # 保存到列表
            filename = f"sticker_{count+1}.png"
            cropped_images.append((filename, tile))
            
            # 显示部分预览 (为了性能，不显示全部，只显示前8个)
            if count < 8:
                with preview_cols[count % 4]:
                    st.image(tile, use_column_width=True)
            
            count += 1
            progress_bar.progress(count / total_tiles)

    if count > 8:
        st.caption(f"... 以及其他 {count - 8} 张表情")

    st.success(f"成功切割出 {count} 张表情包！")

    # 3. 打包下载
    # 创建内存中的 ZIP 文件
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        for name, img in cropped_images:
            # 将图片转为字节流
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            # 写入 ZIP
            zf.writestr(name, img_byte_arr.getvalue())
    
    # 下载按钮
    st.download_button(
        label="📦 一键打包下载所有表情 (ZIP)",
        data=zip_buffer.getvalue(),
        file_name="stickers_pack.zip",
        mime="application/zip",
        use_container_width=True
    )

