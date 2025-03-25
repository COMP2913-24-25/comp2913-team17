from flask import Blueprint, render_template

addons_page = Blueprint('addons_page', __name__, template_folder='templates')

@addons_page.route('/faqs')
def faqs():
    return render_template('faqs.html')

@addons_page.route('/terms')
def terms():
    return render_template('terms.html')

@addons_page.route('/privacy')
def privacy():
    return render_template('privacy.html')

@addons_page.route('/about-us')
def about_us():
    return render_template('about_us.html')
