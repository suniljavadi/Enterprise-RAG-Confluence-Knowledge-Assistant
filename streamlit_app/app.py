import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")
TOKEN = os.getenv("API_AUTH_TOKEN", "portfolio-demo-token")

st.set_page_config(page_title="Northstar Knowledge Assistant", page_icon="◈", layout="wide")
st.markdown("""<style> .hero {padding: 1.5rem 0 1rem; border-bottom: 1px solid #d9e2ec;} .source {border-left: 4px solid #0f766e; padding: .6rem 1rem; margin: .5rem 0; background: #f0fdfa;} </style>""", unsafe_allow_html=True)
st.markdown("<div class='hero'><h1>Northstar Knowledge Assistant</h1><p>Grounded answers from a synthetic enterprise knowledge base</p></div>", unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.subheader("Knowledge Base")
    try:
        documents = requests.get(f"{API_URL}/api/v1/documents", headers={"Authorization": f"Bearer {TOKEN}"}, timeout=5).json()
        st.metric("Indexed documents", len(documents))
        selected = st.selectbox("Explore a document", ["All documents"] + [f"{d['page_id']} · {d['title']}" for d in documents])
        if selected != "All documents":
            page_id = selected.split(" · ")[0]
            doc = requests.get(f"{API_URL}/api/v1/documents/{page_id}", headers={"Authorization": f"Bearer {TOKEN}"}, timeout=5).json()
            st.caption(f"{doc['space']} · {', '.join(doc['tags'])}")
            st.write(doc['content'])
    except requests.RequestException:
        st.warning("API unavailable. Start the FastAPI service first.")

question = st.text_area("Ask the knowledge base", placeholder="What is the rollback process?", height=90)
if st.button("Search and answer", type="primary", disabled=not question.strip()):
    response = requests.post(f"{API_URL}/api/v1/query", headers={"Authorization": f"Bearer {TOKEN}"}, json={"question": question, "roles": ["employee"], "top_k": 6}, timeout=30)
    if response.ok:
        st.session_state.history.insert(0, {"question": question, "response": response.json()})
    else:
        st.error(response.text)

for item in st.session_state.history:
    data = item["response"]
    st.subheader(item["question"])
    st.write(data["answer"])
    st.caption(f"Confidence {data['confidence']:.0%} · {data['latency_ms']} ms · grounded={data['grounded']}")
    st.markdown("**Sources**")
    for citation in data["citations"]:
        st.markdown(f"<div class='source'><b>{citation['document']}</b><br>Section: {citation['section']}<br>Page/chunk: {citation['page_chunk']}</div>", unsafe_allow_html=True)
    with st.expander("Retrieved chunks"):
        for result in data["retrieved_chunks"]:
            st.write(f"{result['chunk']['title']} · {result['chunk']['section']} · score {result['rerank_score']:.3f}")
            st.write(result["chunk"]["text"])
