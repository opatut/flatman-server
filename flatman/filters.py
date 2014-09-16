from flatman import app

@app.template_filter()
def date(s):
    return s.strftime("%a, %d %b")

@app.template_filter()
def time(s):
    return s.strftime("%H:%M")

@app.template_filter()
def datetime(s):
    return s.strftime("%a %d %b, %H:%M")

@app.template_filter()
def amount(s):
    return "%.02f" % (s/100.0)

# @app.context_processor
# def inject():
#     return dict(
#         ICONS=ICONS,
#         login_form=LoginForm(),
#         lang_form=LanguageForm()
#         )
