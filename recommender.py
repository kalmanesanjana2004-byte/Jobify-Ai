"""
Job Recommender Engine
Uses TF-IDF vectorization and cosine similarity to match user profiles with job descriptions.
"""

import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from resume_parser import clean_text, extract_skills, KNOWN_SKILLS


class JobRecommender:
    """
    Content-based job recommendation engine using TF-IDF and cosine similarity.
    """

    def __init__(self, dataset_path=None):
        """Initialize the recommender with a job dataset."""
        if dataset_path is None:
            dataset_path = os.path.join(os.path.dirname(__file__), 'data', 'jobs_dataset.csv')

        self.dataset_path = dataset_path
        self.jobs_df = None
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self._load_and_prepare_data()

    def _load_and_prepare_data(self):
        """Load the dataset and build the TF-IDF matrix."""
        # Load dataset
        self.jobs_df = pd.read_csv(self.dataset_path)

        # Create a combined text field for each job (title + skills + description)
        self.jobs_df['combined_text'] = self.jobs_df.apply(
            lambda row: f"{row['job_title']} {row['required_skills']} {row['job_description']}",
            axis=1
        )

        # Clean the combined text
        self.jobs_df['cleaned_text'] = self.jobs_df['combined_text'].apply(clean_text)

        # Build TF-IDF matrix
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),  # Unigrams and bigrams
            stop_words='english',
            min_df=1,
            max_df=0.95
        )
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.jobs_df['cleaned_text'])

    def recommend(self, user_text, user_skills=None, top_n=10):
        """
        Recommend jobs based on user text (from resume or manual input).

        Args:
            user_text: Cleaned text from user's resume or manual input
            user_skills: List of skills extracted from user input
            top_n: Number of top recommendations to return

        Returns:
            List of dicts with job info and match scores
        """
        if not user_text or not user_text.strip():
            return []

        # Clean the user text
        cleaned_user_text = clean_text(user_text)

        if not cleaned_user_text.strip():
            return []

        # Transform user text using the fitted vectorizer
        user_vector = self.tfidf_vectorizer.transform([cleaned_user_text])

        # Calculate cosine similarity
        similarity_scores = cosine_similarity(user_vector, self.tfidf_matrix).flatten()

        # Get top N indices (sorted by similarity, descending)
        top_indices = similarity_scores.argsort()[::-1][:top_n]

        # Build results
        recommendations = []
        for idx in top_indices:
            job = self.jobs_df.iloc[idx]
            match_score = round(float(similarity_scores[idx]) * 100, 1)

            # Skip jobs with 0% match
            if match_score <= 0:
                continue

            # Parse required skills for this job
            job_skills = [s.strip().lower() for s in str(job['required_skills']).split(',')]

            # Determine matched and missing skills
            matched_skills = []
            missing_skills = []

            if user_skills:
                user_skills_lower = [s.lower().strip() for s in user_skills]
                for skill in job_skills:
                    skill_clean = skill.strip()
                    if any(skill_clean in us or us in skill_clean for us in user_skills_lower):
                        matched_skills.append(skill_clean.title())
                    else:
                        missing_skills.append(skill_clean.title())
            else:
                missing_skills = [s.strip().title() for s in job_skills]

            recommendations.append({
                'job_id': int(job['job_id']),
                'job_title': job['job_title'],
                'company': job['company'],
                'location': job['location'],
                'category': job['category'],
                'experience_level': job['experience_level'],
                'required_skills': job['required_skills'],
                'job_description': job['job_description'],
                'match_score': match_score,
                'matched_skills': matched_skills,
                'missing_skills': missing_skills,
                'matched_count': len(matched_skills),
                'total_skills': len(job_skills),
            })

        return recommendations

    def get_categories(self):
        """Get unique job categories from the dataset."""
        if self.jobs_df is not None:
            return sorted(self.jobs_df['category'].unique().tolist())
        return []

    def get_experience_levels(self):
        """Get unique experience levels from the dataset."""
        if self.jobs_df is not None:
            return sorted(self.jobs_df['experience_level'].unique().tolist())
        return []

    def get_job_count(self):
        """Get total number of jobs in the dataset."""
        if self.jobs_df is not None:
            return len(self.jobs_df)
        return 0
