import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import sqlite3

class LongTermMemory:
    def __init__(self, db_path='memory.db', model_name='all-MiniLM-L6-v2'):
        self.db_path = db_path
        self.model = SentenceTransformer(model_name)
        self.initialize_db()

    def initialize_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS memories
                     (channel_id TEXT, embedding BLOB, content TEXT)''')
        conn.commit()
        conn.close()

    def add_memory(self, channel_id, content):
        embedding = self.model.encode([content])[0]
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO memories VALUES (?, ?, ?)",
                  (channel_id, embedding.tobytes(), content))
        conn.commit()
        conn.close()
        print(f"Memory added for channel {channel_id}: {content[:50]}...")

    def get_relevant_memories(self, channel_id, query, top_k=5, similarity_threshold=0.3):
        query_embedding = self.model.encode([query])[0]
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT embedding, content FROM memories WHERE channel_id = ?", (channel_id,))
        results = c.fetchall()
        conn.close()

        print(f"Found {len(results)} total memories for channel {channel_id}")

        if not results:
            return []

        embeddings = [np.frombuffer(r[0], dtype=np.float32) for r in results]
        contents = [r[1] for r in results]

        similarities = cosine_similarity([query_embedding], embeddings)[0]

        # Filter memories based on similarity threshold
        relevant_indices = [i for i, sim in enumerate(similarities) if sim >= similarity_threshold]

        print(f"Found {len(relevant_indices)} memories above similarity threshold {similarity_threshold}")

        # Sort relevant memories by similarity
        relevant_indices.sort(key=lambda i: similarities[i], reverse=True)

        # Return top_k relevant memories
        top_indices = relevant_indices[:top_k]

        relevant_memories = [contents[i] for i in top_indices]
        print(f"Returning {len(relevant_memories)} relevant memories")

        return relevant_memories


def process_memories(memories):
    processed = []
    for memory in memories:
        if "User:" in memory and "Bot:" in memory:
            user_message = memory.split("User:")[1].split("Bot:")[0].strip()
            processed.append(f"User mentioned: {user_message}")
    return "; ".join(processed)