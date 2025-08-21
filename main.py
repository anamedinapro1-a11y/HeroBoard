from flask import Flask, Response

app = Flask(__name__)

# Serve the HTML directly
@app.route("/")
def home():
    html = """
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Community Service Board</title>

        <!-- Tailwind -->
        <script src="https://cdn.tailwindcss.com"></script>

        <!-- React + ReactDOM -->
        <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
        <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>

        <!-- Babel -->
        <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
      </head>
      <body class="bg-slate-50">
        <div id="root"></div>

        <script type="text/babel">
          const { useState, useEffect, useMemo } = React;

          // ⬇️ PASTE the big CommunityServiceBoard component from the canvas here
          // Make 1 tiny edit: change
          //   export default function CommunityServiceBoard() {
          // to:
          //   function CommunityServiceBoard() {

          // After that, mount it:
          function App() { return <CommunityServiceBoard />; }
          ReactDOM.createRoot(document.getElementById('root')).render(<App />);
        </script>
      </body>
    </html>
    """
    return Response(html, mimetype="text/html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
