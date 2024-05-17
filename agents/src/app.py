from llama_cpp import Llama
from llama_cpp.llama_tokenizer import LlamaHFTokenizer
from data_agent.src import agent as data_agent
from swap_agent.src import agent as swap_agent
from flask_cors import CORS
from flask import Flask, request, jsonify
from config import Config
import json



def load_llm():
    llm = Llama(
        model_path=Config.MODEL_PATH,
        chat_format="functionary-v2",
        tokenizer=LlamaHFTokenizer.from_pretrained("meetkai/functionary-small-v2.4-GGUF"),
        n_gpu_layers=0,
        n_batch=4000,
        n_ctx=4000
    )
    return llm


llm=load_llm()

app = Flask(__name__)
CORS(app)

@app.route('/swap_agent/', methods=['POST'])
def generate_response_swapagent():
    global llm
    try:
        data = request.get_json()
        if 'prompt' in data:
            prompt = data['prompt']
            wallet_address = data['wallet_address']
            chain_id = data['chain_id']
            response, role = swap_agent.generate_response(prompt, chain_id, wallet_address,llm)
            return jsonify({"role": role, "content": response})
        else:
            return jsonify({"error": "Missing required parameters"}), 400

    except Exception as e:
        return jsonify({"Error": str(e)}), 500 

@app.route('/swap_agent/tx_status', methods=['POST'])
def generate_tx_status():
    try:
        data = request.get_json()
        if 'status' in data:
            prompt = data['status']
            tx_hash = data.get('tx_hash', '')
            tx_type = data.get('tx_type', '')
            response = swap_agent.get_status(prompt, tx_hash, tx_type)
            return jsonify({"role": "assistant", "content": response})
        else:
            return jsonify({"error": "Missing required parameters"}), 400

    except Exception as e:
        return jsonify({"Error": str(e)}), 500 

@app.route('/swap_agent/messages', methods=['GET'])
def get_messages():
    try:
        messages= swap_agent.get_messages()
        return jsonify({"messages": messages})
    except Exception as e:
        return jsonify({"Error": str(e)}), 500 
    

@app.route('/swap_agent/clear_messages', methods=['GET'])
def clear_messages():
    try:
        swap_agent.clear_messages()
        return jsonify({"response": "successfully cleared message history"})
    except Exception as e:
        return jsonify({"Error": str(e)}), 500 
    
    
@app.route('/swap_agent/allowance', methods=['POST'])
def check_allowance_api():
    try:
        data = request.get_json()
        if 'tokenAddress' in data:
            token = data['tokenAddress']
            wallet_address = data['walletAddress']
            chain_id = data["chain_id"]
            res = swap_agent.check_allowance(token, wallet_address, chain_id)
            return jsonify({"response": res})
        else:
            return jsonify({"error": "Missing required parameters"}), 400

    except Exception as e:
        return jsonify({"Error": str(e)}), 500 
    
@app.route('/swap_agent/approve', methods=['POST'])
def approve_api():
    try:
        data = request.get_json()
        if 'tokenAddress' in data:
            token = data['tokenAddress']
            chain_id = data['chain_id']
            amount = data['amount']
            res = swap_agent.approve_transaction(token, chain_id, amount)
            return jsonify({"response": res})
        else:
            return jsonify({"error": "Missing required parameters"}), 400

    except Exception as e:
        return jsonify({"Error": str(e)}), 500 
    
@app.route('/swap_agent/swap', methods=['POST'])
def transaction_payload():   
    try:
        data = request.get_json()
        if 'src' in data:  
            token1 = data['src']
            token2 = data['dst']
            wallet_address = data['walletAddress']
            amount = data['amount']
            slippage = data['slippage']
            chain_id = data['chain_id']
            swap_params = {
                "src": token1,
                "dst": token2,
                "amount": amount,
                "from": wallet_address,
                "slippage": slippage,
                "disableEstimate": False,
                "allowPartialFill": False,
            }
            swap_transaction = swap_agent.build_tx_for_swap(swap_params, chain_id)
            return swap_transaction
        else:
            return jsonify({"error": "Missing required parameters"}), 400

    except Exception as e:
        return jsonify({"Error": str(e)}), 500 

@app.route('/data_agent/', methods=['POST'])
def generate_response_dataagent():
    global llm
    try:
        data = request.get_json()
        if 'prompt' in data:
            prompt = data['prompt']
            response,role = data_agent.generate_response(prompt,llm)
            return jsonify({"role":role,"content":response})
        else:
            return jsonify({"error": "Missing required parameters"}), 400

    except Exception as e:
        return jsonify({"Error": str(e)}), 500 


@app.route('/data_agent/messages', methods=['GET'])
def get_messages_dataagent():
    try:
        messages_ui=data_agent.get_messages()
        return jsonify({"messages":messages_ui})
    except Exception as e:
        return jsonify({"Error": str(e)}), 500 

@app.route('/data_agent/clear_messages', methods=['GET'])
def clear_messages_dataagent():
    data_agent.clear_messages()
    try:
        return jsonify({"response":"successfully cleared message history"})
    except Exception as e:
        return jsonify({"Error": str(e)}), 500 
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)