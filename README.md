\# 🎬 Movie Recommender System



A \*\*content-based movie recommendation system\*\* built with \*\*Python,

Machine Learning, Pandas, Scikit-learn, Streamlit, and the TMDB API\*\*.



This project recommends movies similar to a movie selected by the user.

It demonstrates practical skills in data preprocessing, NLP, feature

engineering, similarity-based recommendation, API integration, and

Streamlit application development.



\---



\## 🖥️ Application Screenshots



\### 🏠 Movie Recommender — Home Page



!\[Movie Recommender Home Page](screenshots/home.png)



\### 🎬 Movie Recommendations



!\[Movie Recommendations](screenshots/recommendations.png)



\---



\## 📌 Project Overview



The system uses movie metadata from the \*\*TMDB 5000 Movies and Credits

datasets\*\*.



For every movie, information such as:



\- Movie overview

\- Genres

\- Keywords

\- Top 3 cast members

\- Director



is combined into a single \*\*`tags`\*\* feature.



The text is then processed using NLP techniques and converted into

numerical vectors using \*\*CountVectorizer\*\*. Finally, \*\*cosine

similarity\*\* is used to measure how similar movies are.



When a user selects a movie, the application returns the \*\*top 5 similar

movies\*\*.



The Streamlit application also uses the \*\*TMDB API\*\* to retrieve movie

posters and trailer information.



\---



\## ✨ Features



\- 🎬 Select a movie from a searchable dropdown

\- 🤖 Content-based movie recommendation

\- 🔎 Uses movie metadata rather than user ratings

\- 🧠 NLP-based text preprocessing

\- 📊 CountVectorizer for feature extraction

\- 📐 Cosine similarity for finding similar movies

\- 🖼️ TMDB poster retrieval

\- ▶️ TMDB/YouTube trailer retrieval

\- 🎨 Custom Streamlit UI

\- 🔐 TMDB API key stored using Streamlit secrets

\- ☁️ Ready for Streamlit-based deployment



\---



\## 🧠 Recommendation Workflow



```text

TMDB Movies Dataset

&#x20;       +

TMDB Credits Dataset

&#x20;       ↓

&#x20;    Merge Data

&#x20;       ↓

&#x20;Select Required Columns

&#x20;       ↓

&#x20;Handle Missing Values

&#x20;       ↓

&#x20;Extract:

&#x20;  • Genres

&#x20;  • Keywords

&#x20;  • Top 3 Cast

&#x20;  • Director

&#x20;  • Overview

&#x20;       ↓

&#x20;Combine into "tags"

&#x20;       ↓

&#x20;   Text Cleaning

&#x20;       ↓

&#x20;  Porter Stemmer

&#x20;       ↓

&#x20;  CountVectorizer

&#x20;  (max\_features = 5000)

&#x20;       ↓

&#x20;Movie Feature Vectors

&#x20;       ↓

&#x20; Cosine Similarity

&#x20;       ↓

Find Top 5 Similar Movies

&#x20;       ↓

&#x20;Streamlit Application

&#x20;       ↓

&#x20;     TMDB API

&#x20;  • Posters

&#x20;  • Trailers

```



\---



\## 🛠️ Tech Stack



| Technology | Purpose |

|---|---|

| Python | Core programming language |

| Pandas | Data loading and preprocessing |

| NumPy | Numerical operations |

| Scikit-learn | CountVectorizer and cosine similarity |

| NLTK | Porter stemming |

| Streamlit | Web application/UI |

| Requests | TMDB API requests |

| TMDB API | Posters and trailer information |

| Pickle | Saving processed data and similarity matrix |

| Jupyter Notebook | Model development and experimentation |

| Git \& GitHub | Version control and project hosting |



\---



\## 📂 Project Structure



```text

Movie\_Recommender\_System/

│

├── app.py

├── Movie\_Recommender\_System.ipynb

│

├── tmdb\_5000\_movies.csv

├── tmdb\_5000\_credits.csv

│

├── movies.pkl

├── movie\_dict.pkl

├── similarity.pkl

│

├── requirements.txt

├── Procfile

├── setup.sh

├── .gitignore

├── .gitattributes

│

├── screenshots/

│   ├── home.png

│   └── recommendations.png

│

└── README.md

```



\### Important Files



\*\*`Movie\_Recommender\_System.ipynb`\*\*



Contains the complete data preprocessing and machine-learning workflow.



\*\*`movies.pkl`\*\*



Stores the processed movie DataFrame.



\*\*`movie\_dict.pkl`\*\*



Stores the processed movie data in dictionary form for use by the

Streamlit application.



\*\*`similarity.pkl`\*\*



Stores the cosine-similarity matrix used by the recommendation function.



\*\*`app.py`\*\*



Runs the Streamlit application and connects the recommendation model

with the TMDB API.



\*\*`requirements.txt`\*\*



Contains the Python dependencies required by the application.



\---



\## 🔬 Machine Learning Approach



\### 1. Data Loading



The project uses:



\- `tmdb\_5000\_movies.csv`

\- `tmdb\_5000\_credits.csv`



The two datasets are merged using the movie title.



\---



\### 2. Feature Selection



The following fields are retained:



```text

movie\_id

title

overview

genres

keywords

cast

crew

```



\---



\### 3. Data Preprocessing



Missing records are removed.



Structured JSON-like fields such as genres, keywords, cast, and crew are

converted into usable Python lists using `ast.literal\_eval()`.



The project extracts:



\- All genres

\- All keywords

\- Top 3 cast members

\- Director



\---



\### 4. Creating the `tags` Feature



The overview, keywords, cast, and director information are combined into

one text field:



```text

tags = overview + keywords + cast + crew

```



This allows each movie to be represented as a single text document.



\---



\### 5. Text Processing



The tags are:



\- converted into a string

\- converted to lowercase

\- processed using \*\*Porter Stemmer\*\*



Stemming helps group related word forms.



\---



\### 6. Feature Extraction



`CountVectorizer` converts the movie tags into numerical feature

vectors.



The project uses:



```python

CountVectorizer(

&#x20;   max\_features=5000,

&#x20;   stop\_words='english'

)

```



\---



\### 7. Similarity Calculation



Cosine similarity is calculated between all movie vectors:



```python

similarity = cosine\_similarity(vectors)

```



The similarity matrix is then stored in:



```text

similarity.pkl

```



\---



\### 8. Recommendation



When a movie is selected:



1\. Its index is found.

2\. Its similarity scores are retrieved.

3\. Movies are sorted by similarity.

4\. The selected movie itself is excluded.

5\. The top 5 similar movies are returned.



\---



\## 🌐 Streamlit Application



The Streamlit application provides the user interface.



The application:



1\. Loads `movie\_dict.pkl`

2\. Loads `similarity.pkl`

3\. Displays available movie titles

4\. Accepts a movie selection

5\. Generates 5 recommendations

6\. Fetches posters from TMDB

7\. Fetches trailer information from TMDB

8\. Displays the recommendations in five columns



The application also includes fallback logic for TMDB movie searching

when a direct movie ID lookup does not return the required information.



\---



\## 🔐 TMDB API Configuration



The TMDB API key should \*\*never be hard-coded or committed to GitHub\*\*.



For local Streamlit execution, create:



```text

.streamlit/secrets.toml

```



with:



```toml

TMDB\_API\_KEY = "YOUR\_TMDB\_API\_KEY"

```



The application reads the key using:



```python

st.secrets\["TMDB\_API\_KEY"]

```



For deployment, add `TMDB\_API\_KEY` through the deployment platform's

secrets configuration.



\---



\## 💻 How to Run Locally



\### 1. Clone the repository



```bash

git clone https://github.com/ankansadhukhan2025-ui/Movie\_Recommender\_System.git

cd Movie\_Recommender\_System

```



\### 2. Create a virtual environment



```bash

python -m venv .venv

```



\### 3. Activate the virtual environment



\*\*Windows:\*\*



```bash

.venv\\Scripts\\activate

```



\*\*Linux/macOS:\*\*



```bash

source .venv/bin/activate

```



\### 4. Install dependencies



```bash

pip install -r requirements.txt

```



\### 5. Add the TMDB API key



Create:



```text

.streamlit/secrets.toml

```



and add:



```toml

TMDB\_API\_KEY = "YOUR\_TMDB\_API\_KEY"

```



\### 6. Run the application



```bash

streamlit run app.py

```



The application will open in your browser.



\---



\## 📊 Dataset



This project uses the \*\*TMDB 5000 Movie Dataset\*\*, containing movie

information and credits.



The project uses:



```text

tmdb\_5000\_movies.csv

tmdb\_5000\_credits.csv

```



The application additionally uses the \*\*TMDB API\*\* for poster and

trailer information.



\---



\## 📈 What I Learned From This Project



This project helped me practice:



\- Data cleaning and preprocessing

\- Pandas DataFrame operations

\- Working with JSON-like data

\- Feature engineering

\- Natural Language Processing

\- Text vectorization

\- Stemming

\- Cosine similarity

\- Recommendation-system concepts

\- Pickle serialization

\- REST API integration

\- Streamlit application development

\- Git and GitHub

\- Deployment configuration

\- API secret management



\---



\## ⚠️ Large File Note



`similarity.pkl` can be a large binary file because it contains the

complete movie-to-movie similarity matrix.



Because the file is large, it is stored using \*\*Git LFS (Git Large File

Storage)\*\*.



\---



\## 🔮 Future Improvements



Possible future improvements include:



\- User login and personalized recommendations

\- Hybrid recommendation using ratings and content

\- Movie ratings and reviews

\- Genre-based filtering

\- More detailed movie information

\- Better recommendation evaluation

\- Recommendation history

\- Improved search experience

\- More robust TMDB matching

\- Deployment with continuous integration



\---



\## 👨‍💻 Author



\*\*Ankan Sadhukhan\*\*



M.Sc. Mathematics and Computing  

Indian Institute of Technology (Indian School of Mines), Dhanbad



\---



\## 🔗 Connect With Me



\- 💻 \*\*GitHub:\*\* \[Ankan Sadhukhan](https://github.com/ankansadhukhan2025-ui)

\- 🔗 \*\*LinkedIn:\*\* \[Ankan Sadhukhan](https://www.linkedin.com/in/ankan-sadhukhan-5b9203378)



\---



\## ⭐ If You Find This Project Useful



Feel free to explore the repository, try the application, and provide

feedback.

