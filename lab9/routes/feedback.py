from flask import Blueprint, render_template, request, redirect
from models import db, Feedback

feedback_bp = Blueprint('feedback_bp', __name__)

@feedback_bp.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        fb = Feedback(
            name=request.form['name'],
            email=request.form['email'],
            message=request.form['message']
        )
        db.session.add(fb)
        db.session.commit()
        return redirect('/feedback')

    feedbacks = Feedback.query.all()
    return render_template('feedback.html', feedbacks=feedbacks)

