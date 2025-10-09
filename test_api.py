import requests
import os
from PIL import Image
import io

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_home():
    """Test home endpoint to see all available endpoints"""
    print("Testing home endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"API Version: {data.get('version')}")
    print(f"Status: {data.get('status')}")
    print(f"\nAvailable Endpoints:")
    print(f"Basic: {len(data['endpoints']['basic'])} endpoints")
    print(f"Advanced: {len(data['endpoints']['advanced'])} endpoints")
    print(f"\nAvailable Templates: {', '.join(data['templates'])}")
    print(f"Available Styles: {', '.join(data['styles'])}\n")

def test_hd_image(image_path):
    """Test HD image upscaling"""
    if not os.path.exists(image_path):
        print(f"Test image not found: {image_path}")
        return
    
    print(f"Testing HD image upscaling with {image_path}...")
    
    with open(image_path, 'rb') as f:
        files = {'image': f}
        data = {'scale': '2'}
        response = requests.post(f"{BASE_URL}/api/ai/hd-image", files=files, data=data)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        output_path = "test_output_hd.png"
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"Success! Output saved to {output_path}\n")
    else:
        print(f"Error: {response.text}\n")

def test_cartoonify(image_path, style='cartoon'):
    """Test cartoonify endpoint"""
    if not os.path.exists(image_path):
        print(f"Test image not found: {image_path}")
        return
    
    print(f"Testing cartoonify with style '{style}' on {image_path}...")
    
    with open(image_path, 'rb') as f:
        files = {'image': f}
        data = {'style': style}
        response = requests.post(f"{BASE_URL}/api/ai/cartoonify", files=files, data=data)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        output_path = f"test_output_cartoon_{style}.png"
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"Success! Output saved to {output_path}\n")
    else:
        print(f"Error: {response.text}\n")

def test_face_swap(source_path, target_path):
    """Test face swap endpoint"""
    if not os.path.exists(source_path) or not os.path.exists(target_path):
        print(f"Test images not found")
        return
    
    print(f"Testing face swap...")
    
    with open(source_path, 'rb') as source, open(target_path, 'rb') as target:
        files = {
            'source_image': source,
            'target_image': target
        }
        response = requests.post(f"{BASE_URL}/api/ai/swap-face", files=files)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        output_path = "test_output_face_swap.png"
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"Success! Output saved to {output_path}\n")
    else:
        print(f"Error: {response.text}\n")

def test_template_style(image_path, template='ghostface'):
    """Test template style endpoint"""
    if not os.path.exists(image_path):
        print(f"Test image not found: {image_path}")
        return
    
    print(f"Testing template style '{template}' on {image_path}...")
    
    with open(image_path, 'rb') as f:
        files = {'image': f}
        data = {'template': template}
        response = requests.post(f"{BASE_URL}/api/advanced/template-styles", files=files, data=data)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        output_path = f"test_output_template_{template}.png"
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"Success! Output saved to {output_path}\n")
    else:
        print(f"Error: {response.text}\n")

if __name__ == "__main__":
    print("=" * 50)
    print("AI Photo Editing API - Test Suite")
    print("=" * 50 + "\n")
    
    test_health()
    test_home()
    
    print("=" * 50)
    print("Note: To test image processing endpoints, you need:")
    print("1. A valid Hugging Face API token in .env")
    print("2. Test images in the project directory")
    print("\nExample usage:")
    print("  test_hd_image('test.jpg')")
    print("  test_cartoonify('test.jpg', 'anime')")
    print("  test_face_swap('face.jpg', 'body.jpg')")
    print("  test_template_style('test.jpg', 'ghostface')")
    print("=" * 50)
