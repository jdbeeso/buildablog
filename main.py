#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t=jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Post(db.Model):
    title = db.StringProperty(required = True)
    post = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

class MainHandler(Handler):
    def render_front(self, title='', post='', error=''):
        posts=db.GqlQuery('SELECT * FROM Post ORDER By created DESC LIMIT 5')
        self.render('front.html',title=title, post=post, error=error, posts=posts)

    def get(self):
        self.render_front()

class Newpost(Handler):
    def render_newpost(self, title='', post='', error=''):
        self.render('newpost.html', title=title, post=post, error=error)

    def get(self):
        self.render_newpost()

    def post(self):
        title = self.request.get('title')
        post = self.request.get('post')

        if title and post:
            p = Post(title=title, post=post)
            p.put()
            post_id = p.key().id()
            p.get_by_id(post_id)
            self.redirect('/blog/%s' % str(post_id))
        else:
            error = "we need both a title and a post!"
            self.render_front(title, post, error)

class ViewPostHandler(Handler):
    def render_blog_post(self, template, post):
        self.render('blog_post.html', post=post)

    def get(self, id):
        post = Post.get_by_id(int(id))
        self.render_blog_post('blog_post.html', post)


app = webapp2.WSGIApplication([
    ('/', MainHandler), ('/newpost', Newpost), webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
