from sentence_transformers import SentenceTransformer
model = SentenceTransformer(
    r"C:\Users\vinit\Downloads\Finetuned-gte-large-en-v1.5",
    trust_remote_code=True
)
functions = {
    "shell_open": "shell_open: Opens applications, files, or system resources.",
    "shell_clean": "shell_clean: Cleans temporary files, cache, and unused system data.",
    "shell_make": "shell_make: Creates files, folders, or new system resources.",
    "shell_read": "shell_read: Reads files or displays file contents.",
    "shell_search": "shell_search: Searches files, folders, or information.",
    "shell_news": "shell_news: Fetches latest news and headlines.",
    "shell_weather": "shell_weather: Provides weather information and forecasts.",
    "shell_stocks": "shell_stocks: Fetches stock prices and market data.",
    "shell_download": "shell_download: Downloads files from the internet."
}
from sklearn.metrics.pairwise import cosine_similarity

fn_names = list(functions.keys())
fn_descs = list(functions.values())

fn_embeddings = model.encode(
    fn_descs,
    normalize_embeddings=True
)
def predict_intent(query, top_k=3):
    q_emb = model.encode(query, normalize_embeddings=True)

    scores = cosine_similarity([q_emb], fn_embeddings)[0]

    results = sorted(
        zip(fn_names, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return results[:top_k]

def route_command(query):
    top1, top2 = predict_intent(query, top_k=2)

    fn1, score1 = top1
    _, score2 = top2

    if score1 >= 0.75 and (score1 - score2) >= 0.08:
        return fn1, "AUTO_EXECUTE"

    if score1 >= 0.60:
        return fn1, "CONFIRM"

    return None, "REJECT"

# queries = [
#     "open chrome",
#     "clean the junk in temp folder",
#     "what are the headlines of delhi today?"
# ]
#
# for q in queries:
#     intent, action = route_command(q)
#     print(q, "→", intent, action)

