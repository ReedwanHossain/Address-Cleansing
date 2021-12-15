from flask import Flask, request,jsonify
import DSU_Parser
import test

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/parse",methods=['POST'])
def parse():
    addr=request.form.get('addr')
    if addr==None or addr=='':
        return {'messages':'Empty Request'}
    res=DSU_Parser.DSU_Parser(addr)
    resu={
        'places':res
    }
    return jsonify(resu)
    

if __name__ == "__main__":
    app.run(debug=True)