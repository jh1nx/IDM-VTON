"""
IDM-VTON API测试脚本
测试虚拟试穿API的功能
"""

import base64
import requests
from PIL import Image
import io
import os
import time

def image_to_base64(image_path):
    """将图片文件转换为base64字符串"""
    with open(image_path, 'rb') as img_file:
        img_data = img_file.read()
        img_base64 = base64.b64encode(img_data).decode('utf-8')
        # 获取文件扩展名判断图片格式
        ext = os.path.splitext(image_path)[1].lower()
        if ext == '.jpg' or ext == '.jpeg':
            mime_type = 'image/jpeg'
        elif ext == '.png':
            mime_type = 'image/png'
        else:
            mime_type = 'image/jpeg'  # 默认
        
        return f"data:{mime_type};base64,{img_base64}"

def base64_to_image(base64_str, output_path):
    """将base64字符串保存为图片文件"""
    if base64_str.startswith('data:image'):
        base64_str = base64_str.split(',')[1]
    
    img_data = base64.b64decode(base64_str)
    with open(output_path, 'wb') as f:
        f.write(img_data)

def test_tryon_api_with_gradio_client():
    """使用gradio_client测试API"""
    try:
        from gradio_client import Client
        
        # 连接到本地Gradio服务
        client = Client("http://127.0.0.1:7861")  # 默认Gradio端口
        
        print("📋 测试参数:")
        # 准备测试图片
        human_image_path = "/root/autodl-tmp/IDM-VTON/gradio_demo/example/human/00034_00.jpg"
        garment_image_path = "/root/autodl-tmp/IDM-VTON/gradio_demo/example/cloth/04469_00.jpg"
        
        if not os.path.exists(human_image_path):
            print(f"❌ 人物图片不存在: {human_image_path}")
            return False
            
        if not os.path.exists(garment_image_path):
            print(f"❌ 服装图片不存在: {garment_image_path}")
            return False
        
        # 转换图片为base64
        print("🔄 转换图片为base64格式...")
        human_base64 = image_to_base64(human_image_path)
        garment_base64 = image_to_base64(garment_image_path)
        
        print(f"✅ 人物图片编码完成，长度: {len(human_base64)}")
        print(f"✅ 服装图片编码完成，长度: {len(garment_base64)}")
        
        # 测试参数
        test_params = {
            "human_image_base64": human_base64,
            "garment_image_base64": garment_base64,
            "garment_description": "a white shirt",
            "auto_mask": True,
            "auto_crop": False,
            "denoise_steps": 25,
            "seed": 42
        }
        
        print("📤 发送API请求...")
        start_time = time.time()
        
        # 调用API
        result = client.predict(
            human_image_base64=test_params["human_image_base64"],
            garment_image_base64=test_params["garment_image_base64"],
            garment_description=test_params["garment_description"],
            auto_mask=test_params["auto_mask"],
            auto_crop=test_params["auto_crop"],
            denoise_steps=test_params["denoise_steps"],
            seed=test_params["seed"],
            api_name="/tryon"
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"✅ API调用成功，处理时间: {processing_time:.2f}秒")
        
        # 保存结果
        if result and len(result) >= 2:
            result_base64, mask_base64 = result
            
            # 创建输出目录
            output_dir = "test_output"
            os.makedirs(output_dir, exist_ok=True)
            
            # 保存试穿结果
            if result_base64:
                result_path = os.path.join(output_dir, "tryon_result.png")
                base64_to_image(result_base64, result_path)
                print(f"✅ 试穿结果已保存: {result_path}")
            
            # 保存遮罩图
            if mask_base64:
                mask_path = os.path.join(output_dir, "mask_result.png")
                base64_to_image(mask_base64, mask_path)
                print(f"✅ 遮罩图已保存: {mask_path}")
            
            return True
        else:
            print("❌ API返回结果格式错误")
            return False
            
    except ImportError:
        print("❌ 请安装gradio_client: pip install gradio_client")
        return False
    except Exception as e:
        print(f"❌ API测试失败: {str(e)}")
        return False

def test_tryon_api_with_requests():
    """使用requests直接测试API（备用方法）"""
    try:
        print("📋 使用requests测试API...")
        
        # API端点
        api_url = "http://127.0.0.1:7860/api/tryon"
        
        # 准备测试图片
        human_image_path = "gradio_demo/example/human/00008_00.jpg"
        garment_image_path = "gradio_demo/example/cloth/00034_00.jpg"
        
        if not os.path.exists(human_image_path):
            print(f"❌ 人物图片不存在: {human_image_path}")
            return False
            
        if not os.path.exists(garment_image_path):
            print(f"❌ 服装图片不存在: {garment_image_path}")
            return False
        
        # 转换图片为base64
        human_base64 = image_to_base64(human_image_path)
        garment_base64 = image_to_base64(garment_image_path)
        
        # 构建请求数据
        request_data = {
            "data": [
                human_base64,      # human_image_base64
                garment_base64,    # garment_image_base64
                "a white shirt",   # garment_description
                True,              # auto_mask
                False,             # auto_crop
                25,                # denoise_steps
                42                 # seed
            ]
        }
        
        print("📤 发送POST请求...")
        start_time = time.time()
        
        response = requests.post(api_url, json=request_data, timeout=300)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API调用成功，处理时间: {processing_time:.2f}秒")
            
            if 'data' in result and len(result['data']) >= 2:
                result_base64, mask_base64 = result['data']
                
                # 创建输出目录
                output_dir = "test_output"
                os.makedirs(output_dir, exist_ok=True)
                
                # 保存结果
                if result_base64:
                    result_path = os.path.join(output_dir, "tryon_result_requests.png")
                    base64_to_image(result_base64, result_path)
                    print(f"✅ 试穿结果已保存: {result_path}")
                
                if mask_base64:
                    mask_path = os.path.join(output_dir, "mask_result_requests.png")
                    base64_to_image(mask_base64, mask_path)
                    print(f"✅ 遮罩图已保存: {mask_path}")
                
                return True
            else:
                print("❌ API返回数据格式错误")
                return False
        else:
            print(f"❌ API请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ requests测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试IDM-VTON API...")
    print("=" * 50)
    
    # 检查当前目录
    if not os.path.exists("gradio_demo"):
        print("❌ 请在IDM-VTON项目根目录下运行此测试")
        return
    
    print("📍 当前目录正确")
    
    # 首先尝试使用gradio_client
    print("\n🔍 方法1: 使用gradio_client测试")
    print("-" * 30)
    success1 = test_tryon_api_with_gradio_client()
    
    if not success1:
        print("\n🔍 方法2: 使用requests测试")
        print("-" * 30)
        success2 = test_tryon_api_with_requests()
        
        if not success2:
            print("\n❌ 所有测试方法都失败了")
            print("请确保:")
            print("1. Gradio服务正在运行 (python merged_new.py)")
            print("2. 服务地址为 http://127.0.0.1:7860")
            print("3. API已正确注册")
            return
    
    print("\n🎉 API测试完成！")
    print("查看 test_output/ 目录中的结果图片")

if __name__ == "__main__":
    main()
