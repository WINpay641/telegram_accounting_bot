# api_routes.py
from flask import jsonify, request
from transaction_manager import transactions
from config import Config

def register_api_routes(app):
    """注册Flask API路由"""
    @app.route('/get_transactions/<chat_id>')
    def get_transactions_api(chat_id):
        try:
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 50))
            date = request.args.get('date')
            transactions_list = transactions.get(chat_id, [])
            
            if date:
                transactions_list = [t for t in transactions_list if date in t]
            
            total = len(transactions_list)
            start = (page - 1) * per_page
            end = start + per_page
            paginated_transactions = transactions_list[start:end]
            print(f"[{Config.get_timestamp()}] API 请求: /get_transactions/{chat_id}, page={page}, per_page={per_page}, date={date or '无'}, 返回 {len(paginated_transactions)} 条记录")
            return jsonify({
                'transactions': paginated_transactions,
                'total': total,
                'page': page,
                'per_page': per_page
            })
        except Exception as e:
            print(f"[{Config.get_timestamp()}] API 错误: {e}")
            return jsonify({'error': str(e)}), 500
