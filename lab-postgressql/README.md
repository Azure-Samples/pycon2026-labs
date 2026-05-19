# Semantic Note Search with Azure PostgreSQL

Build and interact with a semantic search app that uses Azure PostgreSQL for vector search, structured note storage, and semantic retrieval. Explore how the app finds notes by meaning instead of exact keywords by generating embeddings with Microsoft Foundry and retrieving similar notes from a PostgreSQL database.

---

## Setup

Before you begin, complete the setup instructions in the [ADMIN.md](ADMIN.md) and either save the environment variables in an `.env` file or in the **Codespaces** > **Codespace user secrets** of your GitHub account.

---

## Explore the sample notes (2 min)

In the **Explorer** of the editor, navigate to **lab-postgressql** > **data** > **notes.json**.

Notice that these notes are written naturally. There are no keywords intentionally added.

## Run the semantic search app (1 min)

In the terminal, run the command: `python lab-postgressql/search_notes.py`

The application will:

- Send your search query to Microsoft Foundry
- Generate an embedding vector
- Compare that vector against stored note vectors
- Return the most similar notes

## Search by meaning (1 min)

In the terminal, enter: `vacation ideas`

Notice that results appear even if those exact words don't exist in the notes. The system found related concepts instead.

## Try additional searches (2 min)

Try additional search queries in the termimal.

```txt
stress
focus better
health goals
```

Once you are done, enter `Quit` into the terminal to exit the app.

## Add your own note (1 min)

You can add your own note to the app and test whether semantic search can find it.

1. In the **Explorer** of the editor, navigate to **lab-postgressql** > **data** > **notes.json**.
1. Add a new note:
    ```JSON
    {
      "title":"<insert your title>",
      "content":"<insert your note>"
    }
    ```

Right now this note exists only as text and it does not yet have an embedding.

## Generate embeddings for the new note (1 min)

Let's now generate embeddings for your new note!

1. In the terminal, run the command: `python lab-postgressql/seed_database.py`
1. In the terminal, run the command: `python lab-postgressql/generate_embeddings.py`

The embedding is now saved into the PostgreSQL `embedding` column.

## Search again (2 min)

Let's now start up the app again and enter a word/phrase to search for your note.

1. In the terminal, run the command: `python lab-postgressql/search_notes.py`
1. In the terminal, enter a phrase or word related to your new note.

You should see your newly added note returned!

## Reflection

Think about what just happened:

- **Embeddings turned note content into vectors** so the app could compare meaning, not just exact words
- **PostgreSQL stored both the notes and their embeddings** in one place, using `pgvector` for similarity search
- **Your search query was embedded at runtime** and compared to stored note vectors using vector distance
- **Semantic search surfaced related notes** even when your query used different wording than the original text
- **Adding a new note required a new embedding** before it became searchable by meaning

## 🎟️ Congratulations!

Let our staff know that you've completed the lab so that you can collect your swag!