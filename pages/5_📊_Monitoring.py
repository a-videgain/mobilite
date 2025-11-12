import streamlit as st
import psutil
import os

st.set_page_config(page_title="📊 Monitoring", layout="wide")

st.title("📊 Ressources système")

# Mémoire
mem = psutil.virtual_memory()
st.metric("Mémoire utilisée", f"{mem.used / 1024**3:.2f} GB / {mem.total / 1024**3:.2f} GB")
st.progress(mem.percent / 100)

# CPU
cpu_percent = psutil.cpu_percent(interval=1)
st.metric("CPU", f"{cpu_percent}%")
st.progress(cpu_percent / 100)

# Processus actuel
process = psutil.Process(os.getpid())
st.metric("Mémoire app", f"{process.memory_info().rss / 1024**2:.1f} MB")

# Session state
st.metric("Taille session_state", f"{len(str(st.session_state))} caractères")
```

**Ajouter à `requirements.txt`** :
```
streamlit
pandas
plotly
psutil
