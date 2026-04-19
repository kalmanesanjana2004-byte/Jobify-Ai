"""
Job Recommendation System — Flask Application
Main entry point for the web application.
"""

import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from resume_parser import extract_text_from_pdf, clean_text, extract_skills, process_resume, process_manual_input
from recommender import JobRecommender

# ─── Configuration ───────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = 'job-recommender-secret-key-2024'

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize the recommender engine (loads dataset and builds TF-IDF matrix)
recommender = JobRecommender()


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ─── Routes ──────────────────────────────────────────────────────

@app.route('/')
def index():
    """Landing page with upload and manual entry options."""
    stats = {
        'job_count': recommender.get_job_count(),
        'categories': recommender.get_categories(),
        'experience_levels': recommender.get_experience_levels(),
    }
    return render_template('index.html', stats=stats)


@app.route('/recommend', methods=['POST'])
def recommend():
    """Process user input and return job recommendations."""
    input_mode = request.form.get('input_mode', 'manual')
    user_text = ""
    user_skills = []

    if input_mode == 'upload':
        # ─── PDF Upload Mode ────────────────────────────────────
        if 'resume' not in request.files:
            flash('No file uploaded. Please select a PDF file.', 'error')
            return redirect(url_for('index'))

        file = request.files['resume']

        if file.filename == '':
            flash('No file selected. Please choose a PDF file.', 'error')
            return redirect(url_for('index'))

        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload a PDF file.', 'error')
            return redirect(url_for('index'))

        try:
            # Save uploaded file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Process the resume
            raw_text, cleaned_text, user_skills = process_resume(filepath)
            user_text = raw_text

            # Clean up uploaded file
            try:
                os.remove(filepath)
            except OSError:
                pass

            if not raw_text.strip():
                flash('Could not extract text from the PDF. The file may be image-based or empty.', 'error')
                return redirect(url_for('index'))

        except Exception as e:
            flash(f'Error processing resume: {str(e)}', 'error')
            return redirect(url_for('index'))

    else:
        # ─── Manual Entry Mode ──────────────────────────────────
        skills = request.form.get('skills', '').strip()
        experience = request.form.get('experience', '').strip()
        qualifications = request.form.get('qualifications', '').strip()

        if not skills and not experience and not qualifications:
            flash('Please enter at least your skills or experience.', 'error')
            return redirect(url_for('index'))

        user_text, cleaned_text, user_skills = process_manual_input(skills, experience, qualifications)

    # Get recommendations
    recommendations = recommender.recommend(user_text, user_skills, top_n=10)

    if not recommendations:
        flash('No matching jobs found. Try adding more details about your skills and experience.', 'warning')
        return redirect(url_for('index'))

    return render_template(
        'results.html',
        recommendations=recommendations,
        user_skills=user_skills,
        total_jobs=recommender.get_job_count(),
        input_mode=input_mode,
    )


@app.route('/api/recommend', methods=['POST'])
def api_recommend():
    """API endpoint for JSON-based recommendations."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    skills = data.get('skills', '')
    experience = data.get('experience', '')
    qualifications = data.get('qualifications', '')
    top_n = data.get('top_n', 10)

    user_text, cleaned_text, user_skills = process_manual_input(skills, experience, qualifications)
    recommendations = recommender.recommend(user_text, user_skills, top_n=top_n)

    return jsonify({
        'recommendations': recommendations,
        'user_skills': user_skills,
        'total_matched': len(recommendations),
    })


# ─── Main ────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("\n[*] Job Recommendation System is starting...")
    print(f"[+] Loaded {recommender.get_job_count()} jobs from dataset")
    print(f"[+] Categories: {', '.join(recommender.get_categories())}")
    print(f"[>] Open http://127.0.0.1:5000 in your browser\n")
    app.run(debug=True, host='127.0.0.1', port=5000)
