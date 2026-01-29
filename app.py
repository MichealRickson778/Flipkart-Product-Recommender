from flask import render_template,Flask,request,Response,redirect,session
from flask import jsonify
from prometheus_client import Counter,generate_latest
from src.data_ingestion import DataIngestor
from src.rag_chain import RAGChainBuilder
from config.db_connect import get_db_connection
import bcrypt

from dotenv import load_dotenv
load_dotenv()


def create_app():

    app = Flask(__name__)
    app.secret_key = "super-secret-key"


    vector_store = DataIngestor().ingest(load_existing=True)

    @app.route("/",methods=["GET", "POST"])
    def index():
        return render_template("login.html")
    

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            firstname = request.form.get("first_name")
            lastname = request.form.get("last_name")
            username = request.form.get("username")
            email = request.form.get("email") or None 
            phone = request.form.get("phone") or None
            password = request.form.get("password") 



            hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO users_table (firstname, lastname, username, email, phone, password)
                VALUES (%s, %s, %s, %s, %s, %s)
                """, (firstname, lastname, username, email, phone, hashed_pw.decode("utf-8")))

            conn.commit()
            cur.close()
            conn.close()

            return redirect("/login")
        
        return render_template("register.html")

    #@app.route("/")
    #def index():
        #return render_template("index.html")

    @app.route("/login", methods=["GET","POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("identifier")
            password = request.form.get("password")

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("SELECT id, password FROM users_table WHERE username=%s", (username,))
            user = cur.fetchone()

            cur.close()
            conn.close()

            if user and bcrypt.checkpw(password.encode("utf-8"), user[1].encode()):
                session["user_id"] = user[0]
                return redirect("/chatbot")

            return render_template("login.html",error="Invalid username or password")
        return render_template("login.html")
    

    
    @app.route("/chatbot",methods=["GET","POST"])
    def get_response():

        if "user_id" not in session:
            return jsonify({"reply": "Please login"}), 401
    
        if request.method == "POST":

        
            rag_chain = RAGChainBuilder(vector_store).build_chain()

            user_input = request.form.get("msg")
        

            response = rag_chain.invoke(
                {"input": user_input},
                config={"configurable": {"session_id": session["user_id"]}}
            )

            reply = response.content if hasattr(response, "content") else str(response)
            return jsonify({"reply": reply})
        
        return render_template("index.html")
    
    @app.route("/logout")
    def logout():
        session.clear()        # remove user_id & chat history
        return redirect("/login")
    

    return app
    
if __name__=="__main__":
    app=create_app()
    app.run(host="0.0.0.0",port=5000,debug=True)
