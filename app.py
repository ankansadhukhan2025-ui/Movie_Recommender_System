import streamlit as st
import pickle
import requests
import pandas as pd
from urllib.parse import quote


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* -----------------------------
       Main Background
    ----------------------------- */

    .stApp {
        background: linear-gradient(
            135deg,
            #0f0f0f 0%,
            #141414 50%,
            #080808 100%
        );
        color: white;
    }


    /* -----------------------------
       Main Content
    ----------------------------- */

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }


    /* -----------------------------
       Select Box
    ----------------------------- */

    div[data-baseweb="select"] {
        border-radius: 10px;
    }


    /* -----------------------------
       Recommend Button
    ----------------------------- */

    .stButton > button {
        background-color: #e50914;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.65rem 1.5rem;
        font-size: 16px;
        font-weight: 600;
        transition: 0.3s;
    }

    .stButton > button:hover {
        background-color: #b20710;
        color: white;
        transform: scale(1.03);
    }


    /* -----------------------------
       Movie Card
    ----------------------------- */

    .movie-title {
        text-align: center;
        font-size: 17px;
        font-weight: 600;
        color: white;
        margin-top: 10px;
        margin-bottom: 10px;
        min-height: 45px;
    }


    /* -----------------------------
       Trailer Button
    ----------------------------- */

    div.stLinkButton > a {
        background-color: #e50914;
        color: white !important;
        border-radius: 8px;
        font-weight: 600;
        text-align: center;
        border: none;
    }

    div.stLinkButton > a:hover {
        background-color: #b20710;
    }


    /* -----------------------------
       Footer
    ----------------------------- */

    .footer {
        text-align: center;
        color: #888888;
        font-size: 14px;
        margin-top: 60px;
        padding-top: 20px;
        border-top: 1px solid #333333;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TMDB API KEY
# ============================================================

try:
    api_key = st.secrets["TMDB_API_KEY"]
except Exception:
    st.error(
        "TMDB API key not found. Please add TMDB_API_KEY "
        "inside .streamlit/secrets.toml"
    )
    st.stop()


# ============================================================
# LOAD MOVIE DATA
# ============================================================

try:

    movies = pickle.load(
        open("movie_dict.pkl", "rb")
    )

    similarity = pickle.load(
        open("similarity.pkl", "rb")
    )

except FileNotFoundError:

    st.error(
        "movie_dict.pkl or similarity.pkl was not found. "
        "Make sure these files are inside the same folder as app.py."
    )

    st.stop()


# ============================================================
# CREATE MOVIE DATAFRAME
# ============================================================

movies = pd.DataFrame(movies)

movie_list = movies["title"].values


# ============================================================
# TMDB REQUEST FUNCTION
# ============================================================

@st.cache_data(show_spinner=False)
def tmdb_request(endpoint, params=None):

    url = f"https://api.themoviedb.org/3/{endpoint}"

    if params is None:
        params = {}

    params["api_key"] = api_key

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10,
            headers={
                "User-Agent": "Movie-Recommender-App"
            }
        )

        if response.status_code == 200:
            return response.json()

    except requests.exceptions.RequestException:
        pass

    return None


# ============================================================
# NORMALIZE MOVIE TITLE
# ============================================================

def normalize_title(title):

    if not title:
        return ""

    return (
        title.lower()
        .replace(":", "")
        .replace("-", "")
        .replace(",", "")
        .replace(".", "")
        .strip()
    )


# ============================================================
# FIND MOVIE ON TMDB
# ============================================================

@st.cache_data(show_spinner=False)
def find_tmdb_movie(movie_id, movie_title):

    # --------------------------------------------------------
    # First try TMDB ID
    # --------------------------------------------------------

    if movie_id:

        data = tmdb_request(
            f"movie/{movie_id}"
        )

        if data and data.get("id"):

            return data


    # --------------------------------------------------------
    # If ID does not work, search by title
    # --------------------------------------------------------

    search_data = tmdb_request(
        "search/movie",
        {
            "query": movie_title,
            "language": "en-US",
            "page": 1,
            "include_adult": False
        }
    )

    if not search_data:
        return None

    results = search_data.get("results", [])

    if not results:
        return None


    # --------------------------------------------------------
    # Try exact normalized title
    # --------------------------------------------------------

    target_title = normalize_title(movie_title)

    for movie in results:

        tmdb_title = normalize_title(
            movie.get("title", "")
        )

        if tmdb_title == target_title:

            return movie


    # --------------------------------------------------------
    # Otherwise use first result
    # --------------------------------------------------------

    return results[0]


# ============================================================
# FETCH POSTER
# ============================================================

@st.cache_data(show_spinner=False)
def fetch_poster(movie_id, movie_title):

    movie_data = find_tmdb_movie(
        movie_id,
        movie_title
    )

    if movie_data:

        poster_path = movie_data.get(
            "poster_path"
        )

        if poster_path:

            return (
                "https://image.tmdb.org/t/p/w500"
                + poster_path
            )


    # --------------------------------------------------------
    # Extra fallback search
    # --------------------------------------------------------

    search_data = tmdb_request(
        "search/movie",
        {
            "query": movie_title,
            "language": "en-US",
            "page": 1
        }
    )

    if search_data:

        results = search_data.get(
            "results",
            []
        )

        if results:

            poster_path = results[0].get(
                "poster_path"
            )

            if poster_path:

                return (
                    "https://image.tmdb.org/t/p/w500"
                    + poster_path
                )


    # --------------------------------------------------------
    # Placeholder if no poster exists
    # --------------------------------------------------------

    return (
        "https://via.placeholder.com/500x750"
        "?text=No+Poster"
    )


# ============================================================
# FIND YOUTUBE VIDEO
# ============================================================

def get_youtube_video(videos):

    if not videos:
        return None


    # --------------------------------------------------------
    # First priority: Official Trailer
    # --------------------------------------------------------

    for video in videos:

        if (
            video.get("site") == "YouTube"
            and video.get("type") == "Trailer"
            and video.get("official") is True
        ):

            return (
                "https://www.youtube.com/watch?v="
                + video["key"]
            )


    # --------------------------------------------------------
    # Second priority: Any Trailer
    # --------------------------------------------------------

    for video in videos:

        if (
            video.get("site") == "YouTube"
            and video.get("type") == "Trailer"
        ):

            return (
                "https://www.youtube.com/watch?v="
                + video["key"]
            )


    # --------------------------------------------------------
    # Third priority: Teaser
    # --------------------------------------------------------

    for video in videos:

        if (
            video.get("site") == "YouTube"
            and video.get("type") == "Teaser"
        ):

            return (
                "https://www.youtube.com/watch?v="
                + video["key"]
            )


    return None


# ============================================================
# FETCH TRAILER
# ============================================================

@st.cache_data(show_spinner=False)
def fetch_trailer(movie_id, movie_title):

    movie_data = find_tmdb_movie(
        movie_id,
        movie_title
    )


    # --------------------------------------------------------
    # Try TMDB ID
    # --------------------------------------------------------

    if movie_data:

        tmdb_id = movie_data.get("id")

        if tmdb_id:

            video_data = tmdb_request(
                f"movie/{tmdb_id}/videos",
                {
                    "language": "en-US"
                }
            )

            if video_data:

                trailer = get_youtube_video(
                    video_data.get("results", [])
                )

                if trailer:
                    return trailer


            # ------------------------------------------------
            # Try without language restriction
            # ------------------------------------------------

            video_data = tmdb_request(
                f"movie/{tmdb_id}/videos"
            )

            if video_data:

                trailer = get_youtube_video(
                    video_data.get("results", [])
                )

                if trailer:
                    return trailer


    # --------------------------------------------------------
    # YouTube search fallback
    # --------------------------------------------------------

    search_text = quote(
        movie_title + " official trailer"
    )

    return (
        "https://www.youtube.com/results"
        "?search_query="
        + search_text
    )


# ============================================================
# RECOMMEND MOVIES
# ============================================================

def recommend(movie):

    # --------------------------------------------------------
    # Find selected movie index
    # --------------------------------------------------------

    movie_index = movies[
        movies["title"] == movie
    ].index[0]


    # --------------------------------------------------------
    # Get similarity distances
    # --------------------------------------------------------

    distances = similarity[movie_index]


    # --------------------------------------------------------
    # Sort by similarity
    # --------------------------------------------------------

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]


    names = []
    posters = []
    trailers = []


    # --------------------------------------------------------
    # Get information for top 5 movies
    # --------------------------------------------------------

    for i in movies_list:

        index = i[0]

        movie_title = movies.iloc[index].title


        # ----------------------------------------------------
        # Get TMDB ID
        # ----------------------------------------------------

        movie_id = movies.iloc[index].get(
            "movie_id",
            None
        )


        # ----------------------------------------------------
        # Poster
        # ----------------------------------------------------

        poster = fetch_poster(
            movie_id,
            movie_title
        )


        # ----------------------------------------------------
        # Trailer
        # ----------------------------------------------------

        trailer = fetch_trailer(
            movie_id,
            movie_title
        )


        names.append(movie_title)

        posters.append(poster)

        trailers.append(trailer)


    return names, posters, trailers


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <h1 style="
        text-align: center;
        font-size: 48px;
        font-weight: 800;
        margin-top: 10px;
        margin-bottom: 5px;
    ">
        <span style="color:#e50914;">🎬 Movie</span>
        <span style="color:white;"> Recommender</span>
    </h1>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SUBHEADER
# ============================================================

st.markdown(
    """
    <div style="
        text-align: center;
        font-size: 22px;
        font-weight: 600;
        margin-top: 5px;
        margin-bottom: 45px;
    ">
        <span style="color:#ff4d6d;">Discover</span>
        <span style="color:#ffd166;"> movies</span>
        <span style="color:#06d6a0;"> you'll love</span>
        <span style="color:#4dabf7;"> based on your taste</span>
        <span style="color:#c77dff;"> 🍿✨</span>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CHOOSE MOVIE
# ============================================================

st.markdown(
    """
    <h2 style="
        text-align:center;
        font-size:32px;
        margin-bottom:20px;
    ">
        🍿 Choose a Movie
    </h2>
    """,
    unsafe_allow_html=True
)


selected_movie_name = st.selectbox(
    "Select a movie:",
    movie_list,
    label_visibility="collapsed"
)


# ============================================================
# RECOMMEND BUTTON
# ============================================================

if st.button(
    "🎯 Recommend Movies",
    use_container_width=False
):

    with st.spinner(
        "🎬 Finding movies similar to your choice..."
    ):

        names, posters, trailers = recommend(
            selected_movie_name
        )


    # ========================================================
    # RECOMMENDED MOVIES HEADING
    # ========================================================

    st.markdown(
        """
        <h2 style="
            text-align:center;
            font-size:32px;
            margin-top:50px;
            margin-bottom:30px;
        ">
            ✨ Recommended For You
        </h2>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # FIVE MOVIE COLUMNS
    # ========================================================

    cols = st.columns(5)


    for i in range(5):

        with cols[i]:

            # ------------------------------------------------
            # Poster
            # ------------------------------------------------

            st.image(
                posters[i],
                use_container_width=True
            )


            # ------------------------------------------------
            # Movie Name
            # ------------------------------------------------

            st.markdown(
                f"""
                <div class="movie-title">
                    {names[i]}
                </div>
                """,
                unsafe_allow_html=True
            )


            # ------------------------------------------------
            # Trailer Button
            # ------------------------------------------------

            st.link_button(
                "▶️ Watch Trailer",
                trailers[i],
                use_container_width=True
            )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        🎬 Movie Recommender System |
        Built with Python, Machine Learning & Streamlit |
        Movie data and posters provided by TMDB
    </div>
    """,
    unsafe_allow_html=True
)