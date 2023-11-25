from flask import Flask, jsonify, request

from crawler import crawl

app = Flask(__name__)

@app.route('/add_address', methods=['GET'])
def chatbot():
    if request.method == 'GET':
        try:
            # 크롤링 및 데이터 저장
            result = crawl()
            return result
        except:
            return "fail", 500
        
    return "message not found", 400

@app.route('/health', methods=['GET'])
def health():
    return jsonify(result="ApiMessages.OK")

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=1235) #서비스시 host값 ip로 변경, port도 변경, route경로도 확인할것
