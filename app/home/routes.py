from app.home import blueprint
from flask import render_template, request
from jinja2 import TemplateNotFound
import urllib.request
from app import zmq, db, analyzed_domains


def domains_to_domain_processor(urls, user_domain=False):
    if isinstance(urls, list):
        data = {
            'action': 'add_bulk',
            'urls': urls,
            'user_domain': user_domain
        }
        s = zmq.send(data)
        print(s)
    else:
        raise ValueError


@blueprint.route('/my_domains', methods=['GET', 'POST'])
def my_domains():
    if request.method == 'GET':
        urls = [x['url'] for x in list(analyzed_domains.find({'user_domain': True})).copy()]
        print(urls)
        return render_template('my_domains.html', urls=urls)
    if request.method == 'POST':
        urls = request.form['domains'].replace('\r', '').split('\n')
        try:
            domains_to_domain_processor(urls, user_domain=True)
        except Exception as e:
            print(e)
            return render_template('my_domains.html', error=e, urls=urls)
        return render_template('my_domains.html', add_msg=True, urls=urls)


@blueprint.route('/manual/add_bulk', methods=['POST'])
def manual_add_bulk():
    urls = request.form['urls'].replace('\r', '').split('\n')
    try:
        print(urls)
        domains_to_domain_processor(urls)
    except Exception as e:
        print(e)
        return render_template('manual.html', test=False, urls=urls, error=e)
    return render_template('manual.html', urls=urls, add_msg=True)


@blueprint.route('/manual/add')
def manual_add():
    url = request.args.get('url', type=str)
    try:
        urllib.request.urlopen(url)
        data = {
            'action': 'add',
            'url': url
        }
        zmq.send(data)
        print('Sended')
    except Exception as e:
        print(e)
        return render_template('manual.html', test=False, url=url, error=e)
    return render_template('manual.html', url=url, add=True)


@blueprint.route('/settings')
def settings():
    modules_list = [x['module'] for x in db['modules_list'].find({})]
    return render_template('settings.html', result=dict((k, None) for k in modules_list))


@blueprint.route('/module/<name>')
def module(name):
    modules_list = [x['module'] for x in db['modules_list'].find({})]
    if name in modules_list:
        settings = db['modules_list'].find({'module': name})[0]['settings']
        return render_template('modules/base.html', settings=settings, module_name=name)
    else:
        return render_template('404.html'), 404


@blueprint.route('/<template>')
def route_template(template):
    try:
        if not template.endswith('.html'):
            template += '.html'
        # Serve the file (if exists) from app/templates/FILE.html
        return render_template(template)
    except TemplateNotFound:
        return render_template('404.html'), 404
    except:
        return render_template('500.html'), 500
