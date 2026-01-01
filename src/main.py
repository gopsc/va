from flask import Flask, request, jsonify
import requests
from waitress import serve

app = Flask(__name__)

@app.route('/', methods=['POST'])
def proxy_request():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Missing JSON data'}), 400
        
        url = data.get('url')
        if not url:
            return jsonify({'error': 'Missing target URL'}), 400
        
        method = data.get('method', 'GET').upper()
        headers = data.get('headers', {})
        params = data.get('params', {})
        payload = data.get('payload')
        
        # 禁用自动解压缩，确保我们获取原始内容
        # 复制并修改headers，避免修改原始请求的headers
        request_headers = headers.copy() if headers else {}
        request_headers['Accept-Encoding'] = 'identity'  # 只接受未压缩的响应
        
        response = requests.request(
            method=method,
            url=url,
            headers=request_headers,
            params=params,
            json=payload if isinstance(payload, dict) else payload,
            timeout=30,
            stream=False,
            allow_redirects=True
        )
        
        # 获取内容和状态码
        content = response.content
        status_code = response.status_code
        
        # 过滤掉hop-by-hop头字段
        hop_by_hop_headers = {
            'connection', 'keep-alive', 'proxy-authenticate', 
            'proxy-authorization', 'te', 'trailers', 'transfer-encoding', 'upgrade'
        }
        
        # 重新构建响应头，只保留安全的头
        filtered_headers = {}
        for key, value in response.headers.items():
            key_lower = key.lower()
            if key_lower not in hop_by_hop_headers:
                # 移除压缩相关头，避免客户端解压缩错误
                if key_lower not in ['content-encoding', 'vary', 'accept-encoding']:
                    filtered_headers[key] = value
        
        # 添加正确的Content-Length
        filtered_headers['Content-Length'] = str(len(content))
        
        return content, status_code, filtered_headers
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print('the va run at 0.0.0.0:7203')
    serve(app, host='0.0.0.0', port=7203)
