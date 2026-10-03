import streamlit as st
import pickle
import requests
import pandas as pd
from urllib.parse import quote
import time


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

    .stApp {
        background-color: #101010;
        color: white;
    }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 3rem;
    }

    .stButton > button {
        background-color: #e50914;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.65rem 1.5rem;
        font-size: 16px;
        font-weight: 600;
    }

    .stButton > button:hover {
        background-color: #b20710;
        color: white;
    }

    .movie-title {
        text-align: center;
        font-size: 17px;
        font-weight: 600;
        color: white;
        margin-top: 10px;
        margin-bottom: 10px;
        min-height: 45px;
    }

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
        "TMDB API key not found. "
        "Please add TMDB_API_KEY inside "
        ".streamlit/secrets.toml"
    )

    st.stop()


# ============================================================
# LOAD MOVIE DATA
# ============================================================

try:

    with open("movie_dict.pkl", "rb") as file:
        movies = pickle.load(file)

    with open("similarity.pkl", "rb") as file:
        similarity = pickle.load(file)

except FileNotFoundError:

    st.error(
        "movie_dict.pkl or similarity.pkl was not found."
    )

    st.stop()


# ============================================================
# DATAFRAME
# ============================================================

movies = pd.DataFrame(movies)


if "title" not in movies.columns:

    st.error(
        "The movie data does not contain a 'title' column."
    )

    st.stop()


movie_list = movies["title"].values


# ============================================================
# TMDB REQUEST FUNCTION
# ============================================================

def tmdb_request(endpoint, params=None, retries=3):

    url = "https://api.themoviedb.org/3/" + endpoint

    if params is None:
        params = {}

    params = dict(params)

    params["api_key"] = api_key

    for attempt in range(retries):

        try:

            response = requests.get(
                url,
                params=params,
                timeout=20,
                headers={
                    "User-Agent": "Mozilla/5.0"
                }
            )

            # Successful request
            if response.status_code == 200:

                return response.json()


            # Rate limit
            if response.status_code == 429:

                time.sleep(1.5)

                continue


            # Temporary server error
            if response.status_code >= 500:

                time.sleep(1)

                continue


        except requests.exceptions.RequestException:

            if attempt < retries - 1:

                time.sleep(1)

                continue


    return None


# ============================================================
# NORMALIZE TITLE
# ============================================================

def normalize_title(title):

    if title is None:

        return ""

    title = str(title).lower().strip()

    characters = [
        ":",
        "-",
        ",",
        ".",
        "'",
        '"',
        "!",
        "?",
        "(",
        ")"
    ]

    for char in characters:

        title = title.replace(
            char,
            ""
        )

    return " ".join(
        title.split()
    )


# ============================================================
# CLEAN MOVIE ID
# ============================================================

def clean_movie_id(movie_id):

    if movie_id is None:

        return None

    try:

        if pd.isna(movie_id):

            return None

    except Exception:

        pass

    try:

        return int(float(movie_id))

    except Exception:

        return None


# ============================================================
# FIND MOVIE ON TMDB
# ============================================================

def find_tmdb_movie(movie_title, movie_id=None):

    movie_title = str(movie_title).strip()

    # ========================================================
    # TITLE SEARCH
    # ========================================================

    search_queries = []

    # Original title
    search_queries.append(movie_title)

    # Normalized title
    normalized = normalize_title(movie_title)

    if normalized != movie_title.lower():

        search_queries.append(normalized)

    # Remove text after colon
    if ":" in movie_title:

        before_colon = movie_title.split(":")[0].strip()

        if before_colon:

            search_queries.append(before_colon)

    # Remove text after hyphen
    if "-" in movie_title:

        before_hyphen = movie_title.split("-")[0].strip()

        if before_hyphen:

            search_queries.append(before_hyphen)


    # Remove duplicates
    search_queries = list(
        dict.fromkeys(search_queries)
    )


    # ========================================================
    # SEARCH USING TITLE
    # ========================================================

    for query in search_queries:

        search_data = tmdb_request(
            "search/movie",
            {
                "query": query,
                "language": "en-US",
                "page": 1,
                "include_adult": False
            }
        )


        if not search_data:

            continue


        results = search_data.get(
            "results",
            []
        )


        if not results:

            continue


        wanted_title = normalize_title(
            movie_title
        )


        # ----------------------------------------------------
        # FIRST PRIORITY:
        # Exact title + poster
        # ----------------------------------------------------

        for result in results:

            result_title = normalize_title(
                result.get(
                    "title",
                    ""
                )
            )


            if (
                result_title == wanted_title
                and result.get("poster_path")
            ):

                return result


        # ----------------------------------------------------
        # SECOND PRIORITY:
        # Similar title + poster
        # ----------------------------------------------------

        for result in results:

            result_title = normalize_title(
                result.get(
                    "title",
                    ""
                )
            )


            if (
                result.get("poster_path")
                and
                (
                    wanted_title in result_title
                    or
                    result_title in wanted_title
                )
            ):

                return result


        # ----------------------------------------------------
        # THIRD PRIORITY:
        # Any result having poster
        # ----------------------------------------------------

        for result in results:

            if result.get("poster_path"):

                return result


    # ========================================================
    # MOVIE ID FALLBACK
    # ========================================================

    movie_id = clean_movie_id(
        movie_id
    )


    if movie_id is not None:

        movie_data = tmdb_request(
            f"movie/{movie_id}",
            {
                "language": "en-US"
            }
        )


        if movie_data:

            if movie_data.get(
                "poster_path"
            ):

                return movie_data


    return None


# ============================================================
# FETCH POSTER
#
# IMPORTANT:
# We return the TMDB URL directly.
# ============================================================

def fetch_poster(movie_id, movie_title):

    movie = find_tmdb_movie(
        movie_title,
        movie_id
    )


    if movie is None:

        return None


    poster_path = movie.get(
        "poster_path"
    )


    if not poster_path:

        return None


    # --------------------------------------------------------
    # DIRECT TMDB IMAGE URL
    # --------------------------------------------------------

    poster_url = (
        "https://image.tmdb.org/t/p/w500"
        + poster_path
    )


    return poster_url


# ============================================================
# GET YOUTUBE TRAILER
# ============================================================

def get_youtube_video(videos):

    if not videos:

        return None


    # ========================================================
    # OFFICIAL TRAILER
    # ========================================================

    for video in videos:

        if (
            video.get("site") == "YouTube"
            and
            video.get("type") == "Trailer"
            and
            video.get("official") is True
            and
            video.get("key")
        ):

            return (
                "https://www.youtube.com/watch?v="
                + video["key"]
            )


    # ========================================================
    # ANY TRAILER
    # ========================================================

    for video in videos:

        if (
            video.get("site") == "YouTube"
            and
            video.get("type") == "Trailer"
            and
            video.get("key")
        ):

            return (
                "https://www.youtube.com/watch?v="
                + video["key"]
            )


    # ========================================================
    # TEASER
    # ========================================================

    for video in videos:

        if (
            video.get("site") == "YouTube"
            and
            video.get("type") == "Teaser"
            and
            video.get("key")
        ):

            return (
                "https://www.youtube.com/watch?v="
                + video["key"]
            )


    return None


# ============================================================
# FETCH TRAILER
# ============================================================

def fetch_trailer(movie_id, movie_title):

    movie = find_tmdb_movie(
        movie_title,
        movie_id
    )


    if movie:

        tmdb_id = movie.get(
            "id"
        )


        if tmdb_id:

            # ------------------------------------------------
            # Try English videos
            # ------------------------------------------------

            data = tmdb_request(
                f"movie/{tmdb_id}/videos",
                {
                    "language": "en-US"
                }
            )


            if data:

                trailer = get_youtube_video(
                    data.get(
                        "results",
                        []
                    )
                )


                if trailer:

                    return trailer


            # ------------------------------------------------
            # Try without language
            # ------------------------------------------------

            data = tmdb_request(
                f"movie/{tmdb_id}/videos"
            )


            if data:

                trailer = get_youtube_video(
                    data.get(
                        "results",
                        []
                    )
                )


                if trailer:

                    return trailer


    # ========================================================
    # YOUTUBE SEARCH FALLBACK
    # ========================================================

    search_text = quote(
        str(movie_title)
        + " official trailer"
    )


    return (
        "https://www.youtube.com/results"
        "?search_query="
        + search_text
    )


# ============================================================
# RECOMMEND FUNCTION
# ============================================================

def recommend(movie):

    matching_movies = movies[
        movies["title"] == movie
    ]


    if matching_movies.empty:

        return [], [], []


    movie_index = matching_movies.index[0]


    distances = similarity[
        movie_index
    ]


    # ========================================================
    # TOP 5 SIMILAR MOVIES
    # ========================================================

    movies_list = sorted(
        list(
            enumerate(distances)
        ),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]


    names = []

    posters = []

    trailers = []


    # ========================================================
    # GET EACH RECOMMENDATION
    # ========================================================

    for item in movies_list:

        index = item[0]


        # ----------------------------------------------------
        # MOVIE TITLE
        # ----------------------------------------------------

        movie_title = str(
            movies.iloc[index]["title"]
        )


        # ----------------------------------------------------
        # MOVIE ID
        # ----------------------------------------------------

        movie_id = None


        if "movie_id" in movies.columns:

            movie_id = movies.iloc[index].get(
                "movie_id",
                None
            )


        movie_id = clean_movie_id(
            movie_id
        )


        # ----------------------------------------------------
        # POSTER
        # ----------------------------------------------------

        poster = fetch_poster(
            movie_id,
            movie_title
        )


        # ----------------------------------------------------
        # TRAILER
        # ----------------------------------------------------

        trailer = fetch_trailer(
            movie_id,
            movie_title
        )


        names.append(
            movie_title
        )


        posters.append(
            poster
        )


        trailers.append(
            trailer
        )


    return (
        names,
        posters,
        trailers
    )


# ============================================================
# MAIN HEADING
# ============================================================

st.markdown(
    """
    <h1 style="
        text-align:center;
        font-size:48px;
        font-weight:800;
        margin-top:10px;
        margin-bottom:5px;
        color:white;
    ">
        🎬 Movie Recommender
    </h1>
    """,
    unsafe_allow_html=True
)


# ============================================================
# COLORFUL SUBHEADING
# ============================================================

st.markdown(
    """
    <div style="
        text-align:center;
        font-size:22px;
        font-weight:600;
        margin-top:5px;
        margin-bottom:45px;
    ">
        <span style="color:#ff4d6d;">Discover</span><span style="color:#ffd166;"> movies</span><span style="color:#06d6a0;"> you'll love</span><span style="color:#4dabf7;"> based on your taste</span><span style="color:#c77dff;"> 🍿✨</span>
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
        color:white;
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
    "🎯 Recommend Movies"
):

    with st.spinner(
        "🎬 Finding movies similar to your choice..."
    ):

        names, posters, trailers = recommend(
            selected_movie_name
        )


    # ========================================================
    # RECOMMENDED HEADING
    # ========================================================

    st.markdown(
        """
        <h2 style="
            text-align:center;
            font-size:32px;
            margin-top:50px;
            margin-bottom:30px;
            color:white;
        ">
            ✨ Recommended For You
        </h2>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # FIVE COLUMNS
    # ========================================================

    cols = st.columns(5)


    for i in range(
        len(names)
    ):

        with cols[i]:

            # =================================================
            # POSTER
            # =================================================

            if posters[i]:

                st.image(
                    posters[i],
                    use_container_width=True
                )

            else:

                st.markdown(
                    """
                    <div style="
                        height:490px;
                        background:#171717;
                        border-radius:10px;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        text-align:center;
                        color:#888;
                        font-size:16px;
                    ">
                        🎬<br>
                        Poster unavailable
                    </div>
                    """,
                    unsafe_allow_html=True
                )


            # =================================================
            # MOVIE NAME
            # =================================================

            st.markdown(
                f"""
                <div class="movie-title">
                    {names[i]}
                </div>
                """,
                unsafe_allow_html=True
            )


            # =================================================
            # TRAILER BUTTON
            # =================================================

            if trailers[i]:

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